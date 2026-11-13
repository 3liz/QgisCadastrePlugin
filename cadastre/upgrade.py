"""Messages displayed once after an update of the plugin, depending on the versions.

Each message is linked to the version of the plugin which introduces it, in UPGRADE_MESSAGES.
After an update, the messages of the versions between the previous and the current versions
are displayed, the oldest first. A message for a future version is added to UPGRADE_MESSAGES.

A message may give SQL commands to run in the databases of the cadastre data, for example to
create indexes: the dialog of the message lets the user choose a database and run them.
"""

__copyright__ = "Copyright 2026, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import html
import re

from dataclasses import dataclass
from typing import Callable

from cadastre.cadastre_database import CadastreDatabase
from cadastre.tools import plugin_path

# Tables of the MAJIC data read by the fiche parcellaire, whose indexes are given in the message of 2.5.3
FICHE_TABLES = (
    "local00",
    "local10",
    "proprietaire",
    "pev",
    "pevtaxation",
    "pevexoneration",
    "pevprincipale",
    "pevdependances",
    "pevprofessionnelle",
    "lots",
    "lotslocaux",
)


def version_tuple(text: str | None) -> tuple[int, ...] | None:
    """Return the numbers of a version of the plugin, to compare versions.

    :param text: A version like "2.5.2" or "v2.5.2".
    :return: The numbers like (2, 5, 2), None if the text is empty or not a released version, like "master".
    """
    match = re.fullmatch(r"v?(\d+(?:\.\d+)*)", (text or "").strip())
    if not match:
        return None
    return tuple(int(n) for n in match[1].split("."))


def indexes_statements(postgis: bool) -> list[str]:
    """Return the SQL commands creating the indexes of the fiche parcellaire, if they do not exist.

    The commands are read in the script of the import, edigeo_create_indexes.sql, for the tables
    of the fiche only. The statistics of the tables are then updated.

    :param postgis: True for PostgreSQL, False for Spatialite. The tables are not prefixed by a schema.
    :return: The SQL commands, one per item.
    """
    script = plugin_path("scripts", "plugin", "edigeo_create_indexes.sql").read_text(encoding="utf-8")
    pattern = re.compile(r"CREATE INDEX IF NOT EXISTS \w+ ON (\w+) .*;")

    # The indexes of the tables of the fiche, in the order of the script
    statements = []
    for line in script.splitlines():
        match = pattern.fullmatch(line.strip())
        if match and match[1] in FICHE_TABLES:
            statements.append(match[0])

    # The statistics: of these tables only with PostgreSQL, ANALYZE has no list of tables in SQLite
    if postgis:
        return [*statements, f"ANALYZE {', '.join(FICHE_TABLES)};"]
    return [*statements, "ANALYZE;"]


def indexes_sql(postgis: bool) -> str:
    """Return the SQL commands of indexes_statements, to run them by hand.

    :param postgis: True for PostgreSQL, with the schema to set first, False for Spatialite.
    :return: The SQL commands, one per line.
    """
    lines = indexes_statements(postgis)
    if postgis:
        lines = [
            "-- Remplacer cadastre par le nom du schéma des données cadastrales",
            "SET search_path = cadastre;",
            *lines,
        ]
    return "\n".join(lines)


def indexes_message() -> str:
    """Return the message of the version 2.5.3: the SQL commands creating the missing indexes.

    It was first given by 2.5.2, without the button to run the commands: it is displayed again.

    The indexes are created by the import, a database imported with an older version of the
    plugin does not have the indexes added since, and the fiche of a parcel with many locaux is slow.

    :return: The HTML of the message.
    """
    return (
        "<p>De nouveaux index rendent la fiche parcellaire beaucoup plus rapide, notamment pour "
        "les parcelles avec beaucoup de locaux. Ils sont créés par l'import des données.</p>"
        "<p>Pour des données importées avec une version précédente du plugin, il faut les créer "
        "dans la base de données, sans réimporter les données : choisir la base ci-dessous puis "
        "cliquer sur « Exécuter le SQL ». Les commandes ne modifient pas les données, et les index "
        "qui existent déjà sont conservés. Cela peut prendre quelques minutes sur une grosse base.</p>"
        "<p>Les commandes peuvent aussi être lancées à la main. En Spatialite, avec « Exécuter SQL » "
        "de QGIS, il faut les lancer une par une.</p>"
        "<h5>PostgreSQL</h5>"
        f"<pre>{html.escape(indexes_sql(postgis=True))}</pre>"
        "<h5>Spatialite</h5>"
        f"<pre>{html.escape(indexes_sql(postgis=False))}</pre>"
    )


@dataclass(frozen=True)
class UpgradeMessage:
    """Message of a version of the plugin, with SQL commands to run in the databases if needed."""

    # HTML of the message, built when it is displayed: it may read files of the plugin
    text: Callable[[], str]
    # SQL commands for PostgreSQL (True) or Spatialite (False), without schema, None if there are none
    sql: Callable[[bool], list[str]] | None = None


# Message of each version, displayed once after an update from an older version
UPGRADE_MESSAGES: dict[tuple[int, ...], UpgradeMessage] = {
    # First given by 2.5.2, displayed again by 2.5.3 with the button to run the SQL commands
    (2, 5, 3): UpgradeMessage(indexes_message, indexes_statements),
}


def upgrade_versions(previous: str | None, current: str) -> list[tuple[int, ...]]:
    """Return the versions whose messages are displayed after an update of the plugin.

    :param previous: The version used before, None for a first installation of the plugin.
        An empty string is a version older than the recording of the versions, added in 2.5.2.
    :param current: The version of the plugin.
    :return: The versions of UPGRADE_MESSAGES newer than the previous version, up to the current one,
        the oldest first. Empty for a first installation or a development version.
    """
    current_numbers = version_tuple(current)
    if previous is None or current_numbers is None:
        return []
    previous_numbers = version_tuple(previous) or (0,)
    return sorted(v for v in UPGRADE_MESSAGES if previous_numbers < v <= current_numbers)


def release_versions(current: str) -> list[tuple[int, ...]]:
    """Return the versions whose messages are given by the release notes of the menu.

    :param current: The version of the plugin, all the messages are given for a development version.
    :return: The versions of UPGRADE_MESSAGES up to the current one, the oldest first.
    """
    current_numbers = version_tuple(current)
    return sorted(v for v in UPGRADE_MESSAGES if current_numbers is None or v <= current_numbers)


def sql_statements(versions: list[tuple[int, ...]], postgis: bool) -> list[str]:
    """Return the SQL commands of the messages of some versions, the oldest first.

    :param versions: Versions of UPGRADE_MESSAGES.
    :param postgis: True for PostgreSQL, False for Spatialite.
    :return: The SQL commands, without schema, empty if the messages have none.
    """
    statements: list[str] = []
    for v in sorted(versions):
        sql = UPGRADE_MESSAGES[v].sql
        if sql:
            statements.extend(sql(postgis))
    return statements


def run_sql(database: CadastreDatabase, versions: list[tuple[int, ...]]) -> int:
    """Run the SQL commands of the messages of some versions in a database of the cadastre.

    The commands are run one by one, in the schema of the database with PostgreSQL.

    :param database: The database and its schema, with the cadastre data.
    :param versions: Versions of UPGRADE_MESSAGES.
    :return: The number of commands run.
    :raises ValueError: If the database or its schema has no cadastre data.
    :raises QgsProviderConnectionException: If a command fails, the next ones are not run.
    """
    # The commands are written for the tables of the cadastre: check they are in this schema
    if not database.table_exists("parcelle_info"):
        where = f"le schéma « {database.schema} »" if database.is_postgis else "cette base"
        raise ValueError(f"Aucune donnée cadastrale trouvée dans {where}")

    statements = sql_statements(versions, database.is_postgis)
    for statement in statements:
        if database.is_postgis:
            # SET LOCAL in a transaction: the search_path of the QGIS connection is not changed
            schema = database.schema.replace('"', '""')
            statement = f'BEGIN; SET LOCAL search_path = "{schema}", public; {statement} COMMIT;'
        database.execute(statement)
    return len(statements)


def upgrade_message(previous: str | None, current: str) -> str | None:
    """Return the messages to display after an update of the plugin, if there are some.

    :param previous: The version used before, see upgrade_versions.
    :param current: The version of the plugin.
    :return: The HTML of the messages, each one with its version as title, None if there is nothing
        to display: first installation, development version, or no message since the previous version.
    """
    versions = upgrade_versions(previous, current)
    if not versions:
        return None
    return f"<h3>Mise à jour du plugin Cadastre, version {html.escape(current)}</h3>" + messages_html(versions)


def messages_html(versions: list[tuple[int, ...]]) -> str:
    """Return the HTML of the messages of some versions, the oldest first, with their version as title.

    :param versions: Versions of UPGRADE_MESSAGES.
    :return: The HTML of the messages.
    """
    text = ""
    for v in sorted(versions):
        text += f"<h4>Version {'.'.join(str(n) for n in v)}</h4>"
        text += UPGRADE_MESSAGES[v].text()
    return text


def release_notes(current: str, changelog: str | None, url: str) -> str:
    """Return the release notes of the menu: the changes of the version and all the update messages.

    The update messages are displayed only once after an update: the release notes allow to read
    them again, for example the SQL commands of the indexes.

    :param current: The version of the plugin, all the messages are given for a development version.
    :param changelog: The changelog of the version, written in metadata.txt by the packaging, if any.
        The items start with "*", the text before the first one is a title.
    :param url: The page of the documentation with the changelog of all the versions.
    :return: The HTML of the release notes.
    """
    text = f"<h3>Notes de version, version {html.escape(current)}</h3>"

    # Changes of the version, when the package contains them
    if changelog and changelog.strip():
        title, *items = changelog.split("*")
        if title.strip():
            text += f"<p><b>{html.escape(title.strip())}</b></p>"
        text += "<ul>" + "".join(f"<li>{html.escape(item.strip())}</li>" for item in items) + "</ul>"
    text += f'<p>Toutes les versions : <a href="{html.escape(url)}">{html.escape(url)}</a></p>'

    # Update messages of the versions up to the current one
    versions = release_versions(current)
    if versions:
        text += "<h3>Messages de mise à jour</h3>" + messages_html(versions)
    return text
