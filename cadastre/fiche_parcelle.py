"""Tabs Parcelle, Propriétaires and Subdivisions fiscales of the fiche parcellaire.

Like the tab of the locaux (cadastre/fiche_locaux.py), the SQL queries only return data,
they are in the files of cadastre/sql/fiche. The tables are described by the sections below.
"""

__copyright__ = "Copyright 2026, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from typing import Callable

from qgis.core import QgsAbstractDatabaseProviderConnection

from cadastre.fiche import (
    DATE_MASK,
    DisplayOptions,
    Field,
    Row,
    Section,
    date_fr,
    fetch_rows,
    load_sql,
    number,
    percent,
    surface,
    table_html,
)

# Values computed from a row, used as Field.value


def oui_non(name: str, code: str) -> Callable[[Row], str]:
    """Create a function writing Oui or Non for a MAJIC column.

    :param name: The name of the column.
    :param code: The code meaning Oui, like "U" for an urban parcel.
    :return: The function to use as Field.value. It returns an empty string when the column
        is not in the row, for a parcel without MAJIC data, so that the optional field is not displayed.
    """

    def value(row: Row) -> str:
        if name not in row:
            return ""
        return "Oui" if row[name] == code else "Non"

    return value


def surface_batie(row: Row) -> str:
    """Return the surface of the buildings of the parcel, 0 m² without building (the sum is NULL)"""
    return surface(str(row.get("surface_batie") or 0))


def pourcentage_bati(row: Row) -> str:
    """Return the percentage of the parcel covered by buildings, 0 % without building"""
    return percent(str(row.get("pourcentage_bati") or 0))


def quote_part(row: Row) -> str:
    """Return the share of a lot in the copropriété, like 2400/10000, or nothing if it is unknown"""
    if row.get("numerateur") and row.get("denominateur"):
        return f"{number(str(row['numerateur']))}/{number(str(row['denominateur']))}"
    return ""


def taux_pexn(value: str) -> str:
    """Write the percentage of the exoneration of a subdivision, stored like 10000 for 100 %"""
    try:
        return percent(str(float(value) / 100))
    except ValueError:
        return value


# Description of the tables


def proprietaires_section(key: str, title: str = "Propriétaires") -> Section:
    """Create the table of the owners of a compte communal.

    It is used in the tab of the owners of the parcel and for the owners of each local.

    :param key: The key of the section in the options, like "local.proprietaires".
    :param title: The title displayed above the table.
    :return: The section, for the rows of fiche/proprietaires.sql and fiche/locaux_proprietaires.sql.
    """
    return Section(
        key,
        title,
        [
            Field("Numéro", "numero"),
            Field("Code", "code"),
            Field("Nom", "nom"),
            Field("Adresse", "adresse"),
            Field("Date de naissance", "date_naissance", sensitive="birth", mask=DATE_MASK, format=date_fr),
            Field("Lieu de naissance", "lieu_naissance", sensitive="birth"),
            Field("Droit", "droit"),
            Field("Démembrement", "demembrement"),
        ],
    )


# General information of the parcel, with or without MAJIC data
PARCELLE = Section(
    "parcelle",
    "",
    [
        Field("Code", "code"),
        Field("Commune", "commune"),
        Field("Date de l'acte", "date_acte", format=date_fr, optional=True),
        Field("Surface cadastrale (contenance)", "contenance", format=surface, optional=True),
        Field("Surface géographique", "surface_geographique", format=surface),
        Field("Parcelle bâtie", "batie", value=oui_non("batie", "1"), optional=True),
        Field("Surface bâtie", "surface_batie", value=surface_batie),
        Field("Pourcentage du bâti", "pourcentage_bati", value=pourcentage_bati),
        Field("Adresse", "adresse", optional=True),
        Field("Urbaine", "urbaine", value=oui_non("urbaine", "U"), optional=True),
    ],
    layout="list",
)

# Without title, the tab has its own title
PROPRIETAIRES = proprietaires_section("proprietaires", "")

LOTS = Section(
    "lots",
    "Lots de copropriété",
    [
        Field("Lot", "lot"),
        Field("Compte propriétaire", "comptecommunal"),
        Field("Quote-part", "quote_part", value=quote_part),
        Field("Nom", "nom"),
        Field("Adresse", "adresse"),
        Field("Date de naissance", "date_naissance", sensitive="birth", mask=DATE_MASK, format=date_fr),
        Field("Lieu de naissance", "lieu_naissance", sensitive="birth"),
        Field("Droit", "droit"),
        Field("Démembrement", "demembrement"),
    ],
)

SUBDIVISIONS = Section(
    "subdivisions",
    "",
    [
        Field("Lettre", "lettre"),
        Field("Groupe", "groupe"),
        Field("Sous-groupe", "sous_groupe"),
        Field("Nature", "nature"),
        Field("Classe", "classe"),
        Field("Contenance", "contenance", format=surface),
        Field("Revenu cadastral", "revenu", sensitive="revenue", format=number),
    ],
)

SUBDIVISIONS_EXONERATIONS = Section(
    "subdivisions.exonerations",
    "Exonérations",
    [
        Field("Lettre", "lettre"),
        Field("Collectivité", "collectivite", sensitive="exoneration"),
        Field("Nature", "nature", sensitive="exoneration"),
        Field("Année de début", "annee_debut", sensitive="exoneration"),
        Field("Année de retour à imposition", "annee_retour", sensitive="exoneration"),
        Field("Taux", "taux", sensitive="exoneration", format=taux_pexn),
        Field("Revenu cadastral exonéré", "revenu", sensitive="exoneration", format=number),
    ],
)


# HTML of the tabs, called by getItemHtml


def parcelle_html(
    connector: QgsAbstractDatabaseProviderConnection,
    connection_params: dict[str, str],
    parcelle: str,
    majic: bool = True,
    options: DisplayOptions | None = None,
) -> str:
    """Build the HTML of the tab Parcelle: the general information of the parcel.

    :param connector: The connection to the database.
    :param connection_params: The parameters of the connection, see fetch_rows.
    :param parcelle: The identifier of the parcel, like 1320290000A0107.
    :param majic: True if the MAJIC data is in the database, otherwise only the EDIGEO tables are used.
    :param options: The fields to display and the sensitive data allowed.
    :return: The HTML of the tab.
    """
    sql = load_sql("fiche/parcelle_majic" if majic else "fiche/parcelle_simple")
    rows = fetch_rows(connector, connection_params, sql, parcelle=parcelle)
    return "<h2>Parcelle</h2>" + table_html(PARCELLE, rows, options or DisplayOptions())


def proprietaires_html(
    connector: QgsAbstractDatabaseProviderConnection,
    connection_params: dict[str, str],
    parcelle: str,
    options: DisplayOptions | None = None,
) -> str:
    """Build the HTML of the owners of the parcel, at the beginning of the tab Propriétaires.

    :param connector: The connection to the database.
    :param connection_params: The parameters of the connection, see fetch_rows.
    :param parcelle: The identifier of the parcel.
    :param options: The fields to display and the sensitive data allowed.
    :return: The HTML, with the title of the tab.
    """
    rows = fetch_rows(connector, connection_params, load_sql("fiche/proprietaires"), parcelle=parcelle)
    return "<h2>Propriétaires</h2>" + table_html(PROPRIETAIRES, rows, options or DisplayOptions(), "h3")


def lots_html(
    connector: QgsAbstractDatabaseProviderConnection,
    connection_params: dict[str, str],
    parcelle: str,
    options: DisplayOptions | None = None,
) -> str:
    """Build the HTML of the lots of a copropriété and of their owners, after the owners of the parcel.

    :param connector: The connection to the database.
    :param connection_params: The parameters of the connection, see fetch_rows.
    :param parcelle: The identifier of the parcel.
    :param options: The fields to display and the sensitive data allowed.
    :return: The HTML, or an empty string for a parcel which is not divided in lots.
    """
    rows = fetch_rows(connector, connection_params, load_sql("fiche/lots"), parcelle=parcelle)
    return table_html(LOTS, rows, options or DisplayOptions(), "h3")


def subdivisions_html(
    connector: QgsAbstractDatabaseProviderConnection,
    connection_params: dict[str, str],
    parcelle: str,
    options: DisplayOptions | None = None,
) -> str:
    """Build the HTML of the tab Subdivisions fiscales: the subdivisions, then their exonerations.

    :param connector: The connection to the database.
    :param connection_params: The parameters of the connection, see fetch_rows.
    :param parcelle: The identifier of the parcel.
    :param options: The fields to display and the sensitive data allowed.
    :return: The HTML of the tab, the table of the exonerations only if there are some.
    """
    options = options or DisplayOptions()
    rows = fetch_rows(connector, connection_params, load_sql("fiche/subdivisions"), parcelle=parcelle)
    exonerations = fetch_rows(
        connector, connection_params, load_sql("fiche/subdivisions_exonerations"), parcelle=parcelle
    )
    return (
        "<h2>Subdivisions fiscales</h2>"
        + table_html(SUBDIVISIONS, rows, options)
        + table_html(SUBDIVISIONS_EXONERATIONS, exonerations, options, "h3")
    )
