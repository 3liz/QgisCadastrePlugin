"""Tabs Parcelle, Propriétaires and Subdivisions fiscales of the fiche parcellaire.

Like the tab of the locaux (cadastre/fiche_locaux.py), the SQL queries only return data,
the tables are described by the sections below.
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
    number,
    percent,
    surface,
    table_html,
)

# Name of an owner, from the table proprietaire with the alias pr:
# civility, usage name and first name, birth name ("née") if it is different, and denomination
SQL_NOM = """trim(
    Coalesce(trim(pr.dqualp) || ' ', '')
    || CASE
        WHEN trim(pr.dnomus) != trim(pr.dnomlp)
        THEN Coalesce(trim(pr.dnomus) || '/' || trim(pr.dprnus) || ', née ', '')
        ELSE ''
    END
    || Coalesce(trim(pr.ddenom), '')
)"""
# Address of an owner: the 4 lines of the address, without the leading zeros of the number
SQL_ADRESSE = """trim(
    Coalesce(trim(pr.dlign3) || ' ', '')
    || Coalesce(ltrim(trim(pr.dlign4), '0') || ' ', '')
    || Coalesce(trim(pr.dlign5) || ' ', '')
    || Coalesce(trim(pr.dlign6), '')
)"""

# General information of a parcel with the MAJIC data: one row.
# The buildings of the parcel are the EDIGEO buildings whose centroid is in the parcel,
# the first ST_Intersects lets PostgreSQL use the spatial index of the buildings.
SQL_PARCELLE_MAJIC = """
SELECT
    p.ccosec || p.dnupla AS code,
    c.libcom AS commune,
    p.jdatat AS date_acte,
    p.dcntpa AS contenance,
    round(ST_Area(gp.geom)) AS surface_geographique,
    p.gparbat AS batie,
    sum(round(ST_Area(b.geom))) AS surface_batie,
    round(100 * sum(ST_Area(b.geom)) / ST_Area(gp.geom)) AS pourcentage_bati,
    CASE
        WHEN v.libvoi IS NOT NULL
        THEN trim(Coalesce(ltrim(p.dnvoiri, '0'), '') || ' ' || trim(Coalesce(v.natvoi, '')) || ' ' || v.libvoi)
        ELSE trim(Coalesce(ltrim(p.cconvo, '0'), '') || ' ' || Coalesce(p.dvoilib, ''))
    END AS adresse,
    p.gurbpa AS urbaine
FROM parcelle p
INNER JOIN geo_parcelle gp ON p.parcelle = gp.geo_parcelle
LEFT JOIN geo_batiment b
    ON ST_Intersects(b.geom, gp.geom) AND ST_Intersects(ST_Centroid(b.geom), gp.geom)
LEFT JOIN commune c ON p.ccocom = c.ccocom AND c.ccodep = p.ccodep
LEFT JOIN voie v
    ON SUBSTR(p.voie, 1, 6) || SUBSTR(p.voie, 12, 4) = SUBSTR(v.voie, 1, 6) || SUBSTR(v.voie, 12, 4)
WHERE p.parcelle = {parcelle}
GROUP BY p.ccosec, p.dnupla, c.libcom, p.jdatat, p.dcntpa, gp.geom, v.libvoi, p.dnvoiri, v.natvoi,
    p.cconvo, p.dvoilib, p.gurbpa, p.gparbat
"""

# General information of a parcel without MAJIC data, from the EDIGEO tables only: one row
SQL_PARCELLE_SIMPLE = """
SELECT
    p.idu AS code,
    c.tex2 AS commune,
    round(ST_Area(p.geom)) AS surface_geographique,
    sum(round(ST_Area(b.geom))) AS surface_batie,
    round(100 * sum(ST_Area(b.geom)) / ST_Area(p.geom)) AS pourcentage_bati
FROM geo_parcelle p
INNER JOIN geo_commune c ON ST_Intersects(ST_Centroid(p.geom), c.geom)
LEFT JOIN geo_batiment b
    ON ST_Intersects(b.geom, p.geom) AND ST_Intersects(ST_Centroid(b.geom), p.geom)
WHERE p.geo_parcelle = {parcelle}
GROUP BY p.idu, p.geom, c.tex2
"""

# Owners of the compte communal of the parcel: one row per owner
SQL_PROPRIETAIRES = f"""
SELECT
    pr.dnulp AS numero,
    pr.dnuper AS code,
    {SQL_NOM} AS nom,
    {SQL_ADRESSE} AS adresse,
    pr.jdatnss AS date_naissance,
    pr.dldnss AS lieu_naissance,
    ccodro.ccodro_lib AS droit,
    ccodem.ccodem_lib AS demembrement
FROM parcelle p
JOIN proprietaire pr ON pr.comptecommunal = p.comptecommunal
LEFT JOIN ccodro ON ccodro.ccodro = pr.ccodro
LEFT JOIN ccodem ON ccodem.ccodem = pr.ccodem
WHERE p.parcelle = {{parcelle}}
ORDER BY pr.dnulp, pr.dnuper
"""

# Lots of a copropriété (propriété divisée en lots): one row per owner of each lot
SQL_LOTS = f"""
SELECT
    l.dnulot AS lot,
    l.comptecommunal AS comptecommunal,
    l.dnumql AS numerateur,
    l.ddenql AS denominateur,
    {SQL_NOM} AS nom,
    {SQL_ADRESSE} AS adresse,
    pr.jdatnss AS date_naissance,
    pr.dldnss AS lieu_naissance,
    ccodro.ccodro_lib AS droit,
    ccodem.ccodem_lib AS demembrement
FROM lots l
LEFT JOIN proprietaire pr ON pr.comptecommunal = l.comptecommunal
LEFT JOIN ccodro ON ccodro.ccodro = pr.ccodro
LEFT JOIN ccodem ON ccodem.ccodem = pr.ccodem
WHERE l.parcelle = {{parcelle}}
ORDER BY l.dnulot, pr.dnulp, pr.dnuper
"""

# Subdivisions fiscales of the parcel: one row per subdivision
SQL_SUBDIVISIONS = """
SELECT
    s.ccosub AS lettre,
    cgrnum.cgrnum_lib AS groupe,
    dsgrpf.dsgrpf_lib AS sous_groupe,
    Coalesce(cnatsp.cnatsp_lib, s.cnatsp) AS nature,
    s.dclssf AS classe,
    s.dcntsf AS contenance,
    s.drcsuba AS revenu
FROM suf s
LEFT JOIN cgrnum ON cgrnum.cgrnum = s.cgrnum
LEFT JOIN dsgrpf ON dsgrpf.dsgrpf = s.dsgrpf
LEFT JOIN cnatsp ON cnatsp.cnatsp = s.cnatsp
WHERE s.parcelle = {parcelle}
ORDER BY s.ccosub
"""

# Exonerations of the subdivisions fiscales: one row per exoneration, 4 at most per subdivision
SQL_SUBDIVISIONS_EXONERATIONS = """
SELECT
    s.ccosub AS lettre,
    ccolloc.ccolloc_lib AS collectivite,
    Coalesce(gnexts.gnexts_lib, se.gnexts) AS nature,
    se.jandeb AS annee_debut,
    se.jfinex AS annee_retour,
    se.pexn AS taux,
    se.rcexnba AS revenu
FROM suf s
JOIN sufexoneration se ON se.suf = s.suf
LEFT JOIN gnexts ON trim(gnexts.gnexts) = se.gnexts
LEFT JOIN ccolloc ON ccolloc.ccolloc = se.ccolloc
WHERE s.parcelle = {parcelle}
ORDER BY s.ccosub, se.rnuexn
"""


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
    :return: The section, for the rows of SQL_PROPRIETAIRES.
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
    sql = SQL_PARCELLE_MAJIC if majic else SQL_PARCELLE_SIMPLE
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
    rows = fetch_rows(connector, connection_params, SQL_PROPRIETAIRES, parcelle=parcelle)
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
    rows = fetch_rows(connector, connection_params, SQL_LOTS, parcelle=parcelle)
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
    rows = fetch_rows(connector, connection_params, SQL_SUBDIVISIONS, parcelle=parcelle)
    exonerations = fetch_rows(connector, connection_params, SQL_SUBDIVISIONS_EXONERATIONS, parcelle=parcelle)
    return (
        "<h2>Subdivisions fiscales</h2>"
        + table_html(SUBDIVISIONS, rows, options)
        + table_html(SUBDIVISIONS_EXONERATIONS, exonerations, options, "h3")
    )
