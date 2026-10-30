__copyright__ = "Copyright 2026, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from dataclasses import dataclass
from typing import TYPE_CHECKING

from db_manager.db_plugins import createDbPlugin

import cadastre.cadastre_common_base as common_utils

if TYPE_CHECKING:
    from db_manager.db_plugins.connector import DBConnector
    from db_manager.db_plugins.plugin import Database, DBPlugin


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
    """A database (and schema for PostGIS) where cadastre data is stored."""

    def __init__(self, db: "Database", db_type: str, connection_name: str, schema: str = ""):
        self.db = db
        # "postgis" or "spatialite"
        self.db_type = db_type
        self.connection_name = connection_name
        self.schema = schema if db_type == "postgis" else ""
        # db_manager plugin owning the database, when created by from_connection
        self._dbplugin: DBPlugin | None = None

    @classmethod
    def from_connection(cls, db_type: str, connection_name: str, schema: str = "") -> "CadastreDatabase":
        """Connect to a database from a connection stored in the QGIS settings.

        Raises a db_manager BaseError if the connection fails.
        """
        dbpluginclass = createDbPlugin(db_type, connection_name)
        dbpluginclass.connect()
        database = cls(dbpluginclass.database(), db_type, connection_name, schema)
        # The db_manager database is owned by the plugin object, keep it alive
        database._dbplugin = dbpluginclass
        return database

    @property
    def connector(self) -> "DBConnector":
        return self.db.connector

    @property
    def is_postgis(self) -> bool:
        return self.db_type == "postgis"

    def table_exists(self, table_name: str) -> bool:
        """Check if the given table exists in the database/schema."""
        if self.is_postgis:
            sql = (
                "SELECT * FROM information_schema.tables "
                f"WHERE table_schema = '{self.schema}' AND table_name = '{table_name}'"
            )
        else:
            sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"

        _data, row_count, ok = common_utils.fetchDataFromSqlQuery(self.connector, sql)
        return bool(ok and row_count >= 1)

    def _has_rows(self, table_name: str) -> bool:
        if self.is_postgis:
            sql = f'SELECT * FROM "{self.schema}"."{table_name}" LIMIT 1'
        else:
            sql = f'SELECT * FROM "{table_name}" LIMIT 1'

        _data, row_count, ok = common_utils.fetchDataFromSqlQuery(self.connector, sql)
        return bool(ok and row_count >= 1)

    def structure(self) -> DatabaseStructure:
        """Search if there are already cadastre tables and data in the database/schema."""
        if self.is_postgis:
            schemas = [s for s in self.db.schemas() if s.name == self.schema]
            tables = self.db.tables(schemas[0]) if schemas else []
        else:
            tables = self.db.tables()

        if not [t for t in tables if t.name == "geo_commune"]:
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
