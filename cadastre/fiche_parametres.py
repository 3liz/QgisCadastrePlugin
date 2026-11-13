"""Parameters of the fiche parcellaire: the sections and the fields which are displayed.

The parameters are stored in 2 places:

* the options of the plugin (QgsSettings), set in the options dialog. They are the model used
  for a new database;
* the table cadastre_parametre_fiche_parcelle of each database, created or completed by each import,
  or written from the options dialog. It is used by QGIS Desktop and by QGIS Server (Lizmap),
  and it can be edited like any table, with one row per section and per field.

When the database has the table, it is used, otherwise the options of the plugin are used.
The parameters never give access to the sensitive data: a sensitive field can be hidden by the table,
but its value is still masked if the user does not have the right to see it.
"""

__copyright__ = "Copyright 2026, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from dataclasses import dataclass

from qgis.core import QgsAbstractDatabaseProviderConnection, QgsProviderConnectionException, QgsSettings

from cadastre.cadastre_common_base import SensitiveData, executeSql, quoteString
from cadastre.cadastre_database import PROVIDERS, CadastreDatabase
from cadastre.fiche import DisplayOptions, Section, fetch_rows
from cadastre.fiche_locaux import (
    DEPENDANCES,
    EVALUATION,
    EXONERATIONS,
    HABITATION,
    LOCAL,
    PEVS,
    PROFESSIONNEL,
    SUMMARY,
)
from cadastre.fiche_locaux import PROPRIETAIRES as LOCAL_PROPRIETAIRES
from cadastre.fiche_parcelle import LOTS, PARCELLE, PROPRIETAIRES, SUBDIVISIONS, SUBDIVISIONS_EXONERATIONS
from cadastre.logger import Logger

TABLE = "cadastre_parametre_fiche_parcelle"

# Keys of the options of the plugin: the sections and fields hidden, and those hidden by default but shown
SETTINGS_HIDDEN = "cadastre/fiche/hidden"
SETTINGS_SHOWN = "cadastre/fiche/shown"

# The tabs of the fiche, with the label and the description of each section, in the order of the fiche.
# The label is used when the section has no title in the fiche.
TABS: list[tuple[str, list[tuple[str, Section]]]] = [
    ("Parcelle", [("Informations générales", PARCELLE)]),
    ("Propriétaires", [("Propriétaires", PROPRIETAIRES), ("Lots de copropriété", LOTS)]),
    (
        "Subdivisions fiscales",
        [("Subdivisions fiscales", SUBDIVISIONS), ("Exonérations", SUBDIVISIONS_EXONERATIONS)],
    ),
    (
        "Locaux",
        [
            ("Récapitulatif des locaux", SUMMARY),
            ("Description générale", LOCAL),
            ("Propriétaires du local", LOCAL_PROPRIETAIRES),
            ("Parties d'évaluation (PEV)", PEVS),
            ("Évaluation de la PEV", EVALUATION),
            ("Habitation", HABITATION),
            ("Dépendances", DEPENDANCES),
            ("Local professionnel", PROFESSIONNEL),
            ("Exonérations de la PEV", EXONERATIONS),
        ],
    ),
]

SQL_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS {table} (
    cle text PRIMARY KEY,
    onglet text,
    section text,
    champ text,
    sensible text,
    visible boolean NOT NULL,
    ordre integer
)
"""


@dataclass
class Parameter:
    """A section or a field of the fiche, a row of the table of the parameters"""

    # "local.pevs" for a section, "local.pevs.co_vlbaia" for a field
    key: str
    tab: str
    section: str
    # Label of the field, empty for a section
    field: str
    # Attribute of SensitiveData needed to see the value of the field, empty if it is not sensitive
    sensitive: str
    # Displayed by default
    default: bool
    # Order in the fiche
    order: int


def parameters() -> list[Parameter]:
    """Return all the sections and fields of the fiche, in their order in the fiche.

    :return: For each section, a parameter for the section, then one for each of its fields.
    """
    result: list[Parameter] = []
    for tab, sections in TABS:
        for label, section in sections:
            result.append(Parameter(section.key, tab, label, "", "", True, len(result) + 1))
            for f in section.fields:
                key = f"{section.key}.{f.name}"
                result.append(
                    Parameter(key, tab, label, f.label, f.sensitive or "", f.visible, len(result) + 1)
                )
    return result


def visibility_from_options(hidden: set[str], shown: set[str]) -> dict[str, bool]:
    """Return the visibility of each section and field, from the keys hidden and shown.

    :param hidden: The keys of the sections and fields hidden.
    :param shown: The keys of the fields hidden by default which are shown.
    :return: For each key, True if it is displayed.
    """
    return {p.key: p.key not in hidden and (p.default or p.key in shown) for p in parameters()}


def options_from_visibility(visibility: dict[str, bool]) -> tuple[set[str], set[str]]:
    """Return the keys hidden and shown, from the visibility of the sections and fields.

    Only the differences with the default visibility are kept, so that a field added in a new version
    of the plugin gets its default visibility.

    :param visibility: For each key, True if it is displayed.
    :return: The keys hidden, and the keys hidden by default which are shown.
    """
    defaults = {p.key: p.default for p in parameters()}
    hidden = {key for key, visible in visibility.items() if not visible and defaults.get(key) is True}
    shown = {key for key, visible in visibility.items() if visible and defaults.get(key) is False}
    return hidden, shown


# Options of the plugin


def read_settings() -> tuple[set[str], set[str]]:
    """Return the keys hidden and shown in the options of the plugin"""
    settings = QgsSettings()
    hidden = settings.value(SETTINGS_HIDDEN, [], type=list)
    shown = settings.value(SETTINGS_SHOWN, [], type=list)
    return set(hidden), set(shown)


def write_settings(hidden: set[str], shown: set[str]):
    """Store the keys hidden and shown in the options of the plugin"""
    settings = QgsSettings()
    settings.setValue(SETTINGS_HIDDEN, sorted(hidden))
    settings.setValue(SETTINGS_SHOWN, sorted(shown))


# Table of the database


def table_name(database: CadastreDatabase) -> str:
    """Return the name of the table, with its schema for PostGIS"""
    if database.is_postgis:
        return f'"{database.schema}".{TABLE}'
    return TABLE


def insert_sql(database: CadastreDatabase, rows: list[Parameter], visibility: dict[str, bool]) -> str:
    """Return the query inserting parameters in the table, with their visibility"""
    values = ",\n".join(
        "({}, {}, {}, {}, {}, {}, {})".format(
            quoteString(p.key),
            quoteString(p.tab),
            quoteString(p.section),
            quoteString(p.field),
            quoteString(p.sensitive),
            "TRUE" if visibility[p.key] else "FALSE",
            p.order,
        )
        for p in rows
    )
    return (
        f"INSERT INTO {table_name(database)} (cle, onglet, section, champ, sensible, visible, ordre) "
        f"VALUES\n{values};"
    )


def complete_table(database: CadastreDatabase, visibility: dict[str, bool] | None = None) -> int:
    """Create the table of the parameters in the database if needed, and add the missing parameters.

    The existing rows are kept: the parameters set in a database are not lost by a new import.

    :param database: The database and schema of the cadastre data.
    :param visibility: The visibility of the parameters added, by default from the options of the plugin.
    :return: The number of parameters added.
    """
    if visibility is None:
        visibility = visibility_from_options(*read_settings())
    database.execute(SQL_CREATE_TABLE.format(table=table_name(database)))
    existing = {row[0] for row in database.fetch(f"SELECT cle FROM {table_name(database)}")}
    missing = [p for p in parameters() if p.key not in existing]
    if missing:
        database.execute(insert_sql(database, missing, visibility))
    return len(missing)


def write_table(database: CadastreDatabase, visibility: dict[str, bool]):
    """Write the visibility of all the parameters in the table of the database, replacing its rows.

    :param database: The database and schema of the cadastre data.
    :param visibility: For each key, True if it is displayed.
    """
    database.execute(SQL_CREATE_TABLE.format(table=table_name(database)))
    database.execute(f"DELETE FROM {table_name(database)};" + insert_sql(database, parameters(), visibility))


def current_database_with_table() -> CadastreDatabase | None:
    """Return the database last used by the plugin, if it has the table of the parameters.

    The database is the one stored in the options of the plugin by the import and load dialogs.

    :return: The database and schema, or None if there is no database, if the connection fails,
        or if the database has no table: the options of the plugin are then used by the fiche.
    """
    settings = QgsSettings()
    db_type = settings.value("cadastre/databaseType", "", type=str)
    connection_name = settings.value("cadastre/connection", "", type=str)
    schema = settings.value("cadastre/schema", "", type=str)
    if db_type not in PROVIDERS or not connection_name:
        return None
    try:
        database = CadastreDatabase.from_connection(db_type, connection_name, schema)
    except Exception as e:
        # Any error of connection: the database is not available, the question is not asked
        Logger.warning(f"Impossible de se connecter à la base « {connection_name} » : {e!s}")
        return None
    if not database.table_exists(TABLE):
        database.close()
        return None
    return database


def database_label(database: CadastreDatabase) -> str:
    """Return the name of the database for the user: its connection, and its schema for PostGIS"""
    if database.is_postgis:
        return f"{database.connection_name} (schéma {database.schema})"
    return database.connection_name


def read_table(
    connector: QgsAbstractDatabaseProviderConnection, connection_params: dict[str, str]
) -> dict[str, bool] | None:
    """Read the visibility of the sections and fields in the table of the database.

    :param connector: The connection to the database.
    :param connection_params: The parameters of the connection, see fetch_rows.
    :return: For each key of the table, True if it is displayed, or None if the database has no table.
    """
    # The catalog is queried directly: tableExists of the QGIS Spatialite connection lists all the
    # tables of the database with their geometries, more than 1 second each time the fiche is built
    if connection_params["dbType"] == "postgis":
        sql = (
            "SELECT 1 FROM information_schema.tables "
            f"WHERE table_schema = {quoteString(connection_params.get('schema', ''))} "
            f"AND table_name = {quoteString(TABLE)}"
        )
    else:
        sql = f"SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = {quoteString(TABLE)}"
    try:
        _columns, exists = executeSql(connector, sql)
    except QgsProviderConnectionException as e:
        Logger.warning(f"Impossible de vérifier la table {TABLE} : {e!s}")
        return None
    if not exists:
        return None

    rows = fetch_rows(connector, connection_params, f"SELECT cle, visible FROM {TABLE}")
    # True or False with PostgreSQL, 1 or 0 with SQLite
    return {row["cle"]: str(row["visible"]).lower() in ("true", "1", "t") for row in rows}


def display_options(
    connector: QgsAbstractDatabaseProviderConnection,
    connection_params: dict[str, str],
    sensitive: SensitiveData | None = None,
) -> DisplayOptions:
    """Return the options of the fiche for a database: from its table, or from the options of the plugin.

    :param connector: The connection to the database.
    :param connection_params: The parameters of the connection, see fetch_rows.
    :param sensitive: The sensitive data the user can see, it does not depend on the parameters.
    :return: The options to build the fiche.
    """
    visibility = read_table(connector, connection_params)
    if visibility is None:
        hidden, shown = read_settings()
    else:
        hidden = {key for key, visible in visibility.items() if not visible}
        shown = {key for key, visible in visibility.items() if visible}
    return DisplayOptions(
        sensitive=sensitive or SensitiveData(), hidden=frozenset(hidden), shown=frozenset(shown)
    )
