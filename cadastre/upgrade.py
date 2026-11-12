"""Messages displayed once after an update of the plugin, depending on the versions.

Each message is linked to the version of the plugin which introduces it, in UPGRADE_MESSAGES.
After an update, the messages of the versions between the previous and the current versions
are displayed, the oldest first. A message for a future version is added to UPGRADE_MESSAGES.
"""

__copyright__ = "Copyright 2026, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import html
import re

from typing import Callable

from cadastre.tools import plugin_path

# Tables of the MAJIC data read by the fiche parcellaire, whose indexes are given in the message of 2.5.2
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


def indexes_sql(postgis: bool) -> str:
    """Return the SQL commands creating the indexes of the fiche parcellaire, if they do not exist.

    The commands are read in the script of the import, edigeo_create_indexes.sql, for the tables
    of the fiche only. The statistics of the tables are then updated.

    :param postgis: True for PostgreSQL, with the schema to set, False for Spatialite.
    :return: The SQL commands, one per line.
    """
    script = plugin_path("scripts", "plugin", "edigeo_create_indexes.sql").read_text(encoding="utf-8")
    pattern = re.compile(r"CREATE INDEX IF NOT EXISTS \w+ ON (\w+) .*;")

    # The indexes of the tables of the fiche, in the order of the script
    lines = []
    for line in script.splitlines():
        match = pattern.fullmatch(line.strip())
        if match and match[1] in FICHE_TABLES:
            lines.append(match[0])

    # PostgreSQL: the schema of the cadastre data, then the statistics of these tables only
    if postgis:
        return "\n".join(
            [
                "-- Remplacer cadastre par le nom du schéma des données cadastrales",
                "SET search_path = cadastre;",
                *lines,
                f"ANALYZE {', '.join(FICHE_TABLES)};",
            ]
        )
    return "\n".join([*lines, "ANALYZE;"])


def indexes_message() -> str:
    """Return the message of the version 2.5.2: the SQL commands creating the missing indexes.

    The indexes are created by the import, a database imported with an older version of the
    plugin does not have the indexes added since, and the fiche of a parcel with many locaux is slow.

    :return: The HTML of the message.
    """
    return (
        "<p>De nouveaux index rendent la fiche parcellaire beaucoup plus rapide, notamment pour "
        "les parcelles avec beaucoup de locaux. Ils sont créés par l'import des données.</p>"
        "<p>Pour des données importées avec une version précédente du plugin, il faut les créer "
        "dans la base de données avec les commandes SQL suivantes, sans réimporter les données. "
        "Elles ne modifient pas les données, et les index qui existent déjà sont conservés.</p>"
        "<h5>PostgreSQL</h5>"
        f"<pre>{html.escape(indexes_sql(postgis=True))}</pre>"
        "<h5>Spatialite</h5>"
        f"<pre>{html.escape(indexes_sql(postgis=False))}</pre>"
    )


# Message of each version, displayed once after an update from an older version.
# The messages are built when they are displayed, they may read files of the plugin
UPGRADE_MESSAGES: dict[tuple[int, ...], Callable[[], str]] = {
    (2, 5, 2): indexes_message,
}


def upgrade_message(previous: str | None, current: str) -> str | None:
    """Return the messages to display after an update of the plugin, if there are some.

    The messages of the versions newer than the previous version, up to the current one, are
    displayed, the oldest first, each one with its version as title.

    :param previous: The version used before, None for a first installation of the plugin.
        An empty string is a version older than the recording of the versions, added in 2.5.2.
    :param current: The version of the plugin.
    :return: The HTML of the messages, None if there is nothing to display: first installation,
        development version, or no message since the previous version.
    """
    current_numbers = version_tuple(current)
    if previous is None or current_numbers is None:
        return None
    previous_numbers = version_tuple(previous) or (0,)

    # The messages of the versions in ]previous, current]
    versions = [v for v in UPGRADE_MESSAGES if previous_numbers < v <= current_numbers]
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
        text += UPGRADE_MESSAGES[v]()
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
    current_numbers = version_tuple(current)
    versions = [v for v in UPGRADE_MESSAGES if current_numbers is None or v <= current_numbers]
    if versions:
        text += "<h3>Messages de mise à jour</h3>" + messages_html(versions)
    return text
