__copyright__ = "Copyright 2026, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import sqlite3

from dataclasses import dataclass
from typing import Any

from qgis.core import (
    QgsAbstractDatabaseProviderConnection,
    QgsDataSourceUri,
    QgsProviderConnectionException,
    QgsProviderRegistry,
)
from qgis.utils import spatialite_connect

import cadastre.cadastre_common_base as common_utils

from cadastre.logger import Logger

POSTGIS = "postgis"
SPATIALITE = "spatialite"
# QGIS provider names
PROVIDERS = {POSTGIS: "postgres", SPATIALITE: "spatialite"}


@dataclass(frozen=True)
class DatabaseStructure:
    """State of the cadastre tables in a database or schema."""

    has_structure: bool = False
    has_data: bool = False
    has_majic_data: bool = False
    has_majic_data_parcelle: bool = False
    has_majic_data_prop: bool = False
    has_majic_data_voie: bool = False


class CadastreDatabase:
    """A database (and schema for PostGIS) where cadastre data is stored.

    Metadata (schemas, tables) and PostGIS queries use the QGIS database connection API.
    SQLite queries use a Python sqlite3 connection with Spatialite, like QGIS does, because the import
    needs executemany and a REGEXP function.
    """

    def __init__(
        self,
        connection: QgsAbstractDatabaseProviderConnection,
        db_type: str,
        connection_name: str,
        schema: str = "",
    ):
        self.connection = connection
        # "postgis" or "spatialite"
        self.db_type = db_type
        self.connection_name = connection_name
        self.schema = schema if db_type == POSTGIS else ""
        self._sqlite: sqlite3.Connection | None = None

    @classmethod
    def from_connection(cls, db_type: str, connection_name: str, schema: str = "") -> "CadastreDatabase":
        """Connect to a database from a connection stored in the QGIS settings.

        Raises a QgsProviderConnectionException if the connection fails.
        """
        metadata = QgsProviderRegistry.instance().providerMetadata(PROVIDERS[db_type])
        # Use the cached connections, without reloading them
        stored = metadata.dbConnections().get(connection_name)
        if stored is None:
            raise QgsProviderConnectionException(f"La connexion '{connection_name}' n'existe pas")

        # A new connection object, owned by Python, not by the QGIS cache
        connection = metadata.createConnection(stored.uri(), stored.configuration())
        database = cls(connection, db_type, connection_name, schema)
        # Check the connection now, to report errors to the user
        database.fetch("SELECT 1")
        return database

    def with_schema(self, schema: str) -> "CadastreDatabase":
        """The same database and connection, with another schema."""
        database = CadastreDatabase(self.connection, self.db_type, self.connection_name, schema)
        database._sqlite = self._sqlite
        return database

    @property
    def is_postgis(self) -> bool:
        return self.db_type == POSTGIS

    @property
    def provider_name(self) -> str:
        """QGIS data provider name: postgres or spatialite"""
        return PROVIDERS[self.db_type]

    def uri(self) -> QgsDataSourceUri:
        """Connection URI, without table, to build layer data sources"""
        return QgsDataSourceUri(self.connection.uri())

    @property
    def sqlite_path(self) -> str:
        return self.uri().database()

    def sqlite_connection(self) -> sqlite3.Connection:
        """Python connection to the Spatialite database, with a REGEXP function."""
        if self._sqlite is None:
            self._sqlite = spatialite_connect(self.sqlite_path)
            self._sqlite.create_function("regexp", 2, common_utils.sqliteRegexp)
        return self._sqlite

    def execute(self, sql: str):
        """Execute SQL statements and commit. Raises an exception if it fails."""
        if self.is_postgis:
            self.connection.executeSql(sql)
            return

        connection = self.sqlite_connection()
        connection.executescript(sql)
        connection.commit()

    def fetch(self, sql: str) -> list[list[Any]]:
        """Execute a query and return the rows. Raises an exception if it fails.

        PostgreSQL values are returned as strings, like the db_manager plugin was doing.
        """
        if self.is_postgis:
            return common_utils.rowsFromQgis(self.connection.executeSql(sql), as_string=True)

        cursor = self.sqlite_connection().cursor()
        try:
            cursor.execute(sql)
            return [list(row) for row in cursor.fetchall()]
        finally:
            cursor.close()

    def fetch_or_empty(self, sql: str) -> list[list[Any]]:
        """Like fetch, but returns an empty list and logs the error if the query fails."""
        try:
            return self.fetch(sql)
        except (QgsProviderConnectionException, sqlite3.Error) as err:
            Logger.info(f"Erreur pour la requête {sql} : {err}")
            return []

    def schemas(self) -> list[str]:
        """List the schemas, PostGIS only"""
        if not self.is_postgis:
            return []
        return self.connection.schemas()

    def create_schema(self, schema: str):
        """Create a PostGIS schema. Raises a QgsProviderConnectionException if it fails."""
        self.connection.createSchema(schema)

    def tables(self) -> list[QgsAbstractDatabaseProviderConnection.TableProperty]:
        """List the tables of the database/schema."""
        if self.is_postgis and self.schema not in self.schemas():
            return []
        return self.connection.tables(self.schema)

    def table_exists(self, table_name: str) -> bool:
        """Check if the given table exists in the database/schema."""
        if self.is_postgis:
            sql = (
                "SELECT * FROM information_schema.tables "
                f"WHERE table_schema = '{self.schema}' AND table_name = '{table_name}'"
            )
        else:
            sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"

        return len(self.fetch_or_empty(sql)) >= 1

    def _has_rows(self, table_name: str) -> bool:
        if self.is_postgis:
            sql = f'SELECT * FROM "{self.schema}"."{table_name}" LIMIT 1'
        else:
            sql = f'SELECT * FROM "{table_name}" LIMIT 1'

        return len(self.fetch_or_empty(sql)) >= 1

    def structure(self) -> DatabaseStructure:
        """Search if there are already cadastre tables and data in the database/schema."""
        if not self.table_exists("geo_commune"):
            return DatabaseStructure()

        has_majic_data_parcelle = self._has_rows("parcelle")
        has_majic_data_prop = self._has_rows("proprietaire")
        has_majic_data_voie = self._has_rows("voie")
        return DatabaseStructure(
            has_structure=True,
            has_data=self._has_rows("geo_commune"),
            has_majic_data=has_majic_data_parcelle or has_majic_data_prop or has_majic_data_voie,
            has_majic_data_parcelle=has_majic_data_parcelle,
            has_majic_data_prop=has_majic_data_prop,
            has_majic_data_voie=has_majic_data_voie,
        )

    def close(self):
        """Close the Spatialite connection, if any"""
        if self._sqlite is not None:
            self._sqlite.close()
            self._sqlite = None
