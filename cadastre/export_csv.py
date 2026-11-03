"""Exports of the cadastre data for a list of parcelles, used by the CSV exports of Lizmap.

Two common queries, for PostgreSQL and Spatialite, in the files of cadastre/sql/export:

* the ayants droit of the parcelles: one row per parcelle and owner;
* the locaux of the parcelles: one row per local and owner.

The exports build their columns from these rows. They have the same names and values as the SQL queries
of the Lizmap module which they replace, so that the CSV files used for mail merges or by third parties
do not change: the formulas of these queries are reproduced, including how they handle NULL values,
with the module (cadastreExtraInfos.class.php) kept in sync.
"""

__copyright__ = "Copyright 2026, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import re

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from qgis.core import (
    QgsAbstractDatabaseProviderConnection,
    QgsFeatureRequest,
    QgsSqliteUtils,
    QgsVectorLayer,
)

from cadastre.cadastre_common_base import (
    SensitiveData,
    getConnectionParameterFromDbLayer,
    getConnectorFromUri,
    quoteString,
)
from cadastre.fiche import DATE_MASK, DEFAULT_MASK, Row, fetch_rows, load_sql

# Identifier of a parcelle, the field geo_parcelle, like 1320290000A0107
PARCELLE_PATTERN = re.compile(r"^[0-9A-Z]{1,20}$")

# Value of the primary key of an object selected in the spatial search of Lizmap
OBJET_PATTERN = re.compile(r"^[0-9A-Za-z_-]{1,100}$")

# Parameters of the database of a layer which must be the same as those of the cadastre data
SAME_DATABASE_PARAMETERS = ("dbType", "service", "host", "port", "dbname")

# CSV exports of the selected parcelles in QGIS: the label and the default name of the file, like Lizmap
CSV_EXPORTS = {
    "proprietaires": ("Parcelles et propriétaires", "cadastre_parcelles_et_proprietaires.csv"),
    "locaux": ("Locaux et propriétaires", "cadastre_extra_infos.csv"),
}

# Number of selected parcelles above which the user confirms the CSV export: the export runs in the interface
# of QGIS, which does not respond until it ends
CSV_EXPORT_CONFIRM_COUNT = 5000

# Characters for which a value is enclosed in double quotes in the CSV files, like the PHP function fputcsv
# used by Lizmap
CSV_ENCLOSED_CHARACTERS = (",", '"', "\n", "\r", "\t", " ", "\\")


@dataclass(frozen=True)
class RechercheSpatiale:
    """Objects selected in another layer by the spatial search of Lizmap, added to the export of the owners.

    The names are quoted for SQL: use recherche_spatiale() to build it from a layer.
    """

    # Table of the layer, with its schema for PostgreSQL
    table: str
    # Primary key of the table
    cle: str
    # Field giving the code of the objects, written in the export
    champ: str
    # Geometry column of the table
    geometrie: str
    # Values of the primary key of the selected objects
    objets: tuple[str, ...]
    # Maximum distance between an object and a parcelle, in the unit of the geometries
    distance: int


def recherche_spatiale(
    layer: QgsVectorLayer, parcelles_layer: QgsVectorLayer, champ: str, objets: list[str], distance: int
) -> RechercheSpatiale:
    """Build the spatial search of an export from the layer of the selected objects.

    :param layer: The layer of the objects, in the same database as the layer of the parcelles.
    :param parcelles_layer: The layer of the parcelles, giving the database of the cadastre data.
    :param champ: The field of the layer giving the code of the objects.
    :param objets: The values of the primary key of the selected objects.
    :param distance: The maximum distance between an object and a parcelle.
    :return: The spatial search, with the names quoted for SQL.
    :raises ValueError: If the layer is not in the same database, if it has no primary key or no such field,
        or if a value or the distance is not valid.
    """
    params = getConnectionParameterFromDbLayer(layer)
    parcelles_params = getConnectionParameterFromDbLayer(parcelles_layer)
    if layer.providerType() not in ("postgres", "spatialite") or any(
        params[name] != parcelles_params[name] for name in SAME_DATABASE_PARAMETERS
    ):
        raise ValueError(f"The layer {layer.name()} is not in the database of the cadastre data")
    if not params["key"] or "," in params["key"]:
        raise ValueError(f"The layer {layer.name()} has no primary key with a single field")
    if champ not in layer.fields().names():
        raise ValueError(f"The layer {layer.name()} has no field {champ}")
    if not objets or not all(OBJET_PATTERN.match(objet) for objet in objets):
        raise ValueError("Invalid identifiers of the selected objects")
    if not isinstance(distance, int) or distance < 0:
        raise ValueError(f"Invalid distance: {distance}")

    # The names given by QgsDataSourceUri are not quoted. The SQL quoting of QgsSqliteUtils is standard:
    # it is also valid for PostgreSQL
    quote = QgsSqliteUtils.quotedIdentifier
    table = quote(params["table"])
    if params["dbType"] == "postgis":
        table = f"{quote(params['schema'])}.{table}"
    return RechercheSpatiale(
        table=table,
        cle=quote(params["key"]),
        champ=quote(champ),
        geometrie=quote(params["geocol"]),
        objets=tuple(objets),
        distance=distance,
    )


# Common queries


def parcelles_sql(parcelles: list[str]) -> str:
    """Return the identifiers of the parcelles, quoted and separated by commas, for an IN clause.

    :param parcelles: The identifiers of the parcelles, like 1320290000A0107.
    :return: The SQL list of the identifiers.
    :raises ValueError: If the list is empty or if an identifier is not valid.
    """
    if not parcelles:
        raise ValueError("No parcelle")
    for parcelle in parcelles:
        if not PARCELLE_PATTERN.match(parcelle):
            raise ValueError(f"Invalid parcelle: {parcelle}")
    return ", ".join(quoteString(parcelle) for parcelle in parcelles)


def query(name: str, parcelles: list[str], sensitive: SensitiveData) -> str:
    """Return a common query for the given parcelles, with the birth data only if they are allowed.

    :param name: The name of the query in cadastre/sql/export.
    :param parcelles: The identifiers of the parcelles.
    :param sensitive: The sensitive data the user can see, the birth data are NULL without the right.
    :return: The query, with its parameters.
    """
    return load_sql(f"export/{name}").format(
        parcelles=parcelles_sql(parcelles), naissance="TRUE" if sensitive.birth else "FALSE"
    )


def ayants_droit(
    connector: QgsAbstractDatabaseProviderConnection,
    connection_params: dict[str, str],
    parcelles: list[str],
    sensitive: SensitiveData,
) -> list[Row]:
    """Return the ayants droit of the parcelles: one row per parcelle and owner.

    :param connector: The connection to the database.
    :param connection_params: The parameters of the connection, see fetch_rows.
    :param parcelles: The identifiers of the parcelles.
    :param sensitive: The sensitive data the user can see: the birth data are NULL without the right.
    :return: The rows, with the MAJIC names of the columns.
    """
    return fetch_rows(connector, connection_params, query("ayants_droit", parcelles, sensitive))


def locaux(
    connector: QgsAbstractDatabaseProviderConnection,
    connection_params: dict[str, str],
    parcelles: list[str],
    sensitive: SensitiveData,
) -> list[Row]:
    """Return the locaux of the parcelles: one row per local and owner.

    :param connector: The connection to the database.
    :param connection_params: The parameters of the connection, see fetch_rows.
    :param parcelles: The identifiers of the parcelles.
    :param sensitive: The sensitive data the user can see: the birth data are NULL without the right.
    :return: The rows, with the MAJIC names of the columns.
    """
    return fetch_rows(connector, connection_params, query("locaux", parcelles, sensitive))


def objets_proches(
    connector: QgsAbstractDatabaseProviderConnection,
    connection_params: dict[str, str],
    parcelles: list[str],
    recherche: RechercheSpatiale,
) -> dict[str, set[str]]:
    """Return the codes of the selected objects near each parcelle.

    :param connector: The connection to the database.
    :param connection_params: The parameters of the connection, see fetch_rows.
    :param parcelles: The identifiers of the parcelles.
    :param recherche: The objects selected by the spatial search.
    :return: For each parcelle near at least one object, the codes of the objects, as text.
    """
    sql = load_sql("export/objets_proches").format(
        parcelles=parcelles_sql(parcelles),
        table=recherche.table,
        cle=recherche.cle,
        champ=recherche.champ,
        geometrie=recherche.geometrie,
        objets=", ".join(quoteString(objet) for objet in recherche.objets),
        distance=recherche.distance,
    )
    codes: dict[str, set[str]] = {}
    # The names of the layer are not parameters of fetch_rows: their braces are escaped
    for row in fetch_rows(connector, connection_params, sql.replace("{", "{{").replace("}", "}}")):
        codes.setdefault(row["parcelle"], set()).add(str(row["code"]))
    return codes


# SQL functions, with the same handling of NULL values as PostgreSQL


def text(value: Any) -> str | None:
    """Return the value as a string, like PostgreSQL returns it to PHP, NULL stays None"""
    return None if value is None else str(value)


def concat(*values: Any) -> str | None:
    """The SQL operator ||: None if one value is None"""
    if any(value is None for value in values):
        return None
    return "".join(str(value) for value in values)


def coalesce(*values: Any) -> str | None:
    """The SQL function coalesce: the first value which is not None"""
    return next((text(value) for value in values if value is not None), None)


def trim(value: Any) -> str | None:
    """The SQL function trim: the spaces at both ends are removed, None stays None"""
    return None if value is None else str(value).strip(" ")


def ltrim_zeros(value: str | None) -> str | None:
    """The SQL function ltrim(value, '0'): the leading zeros are removed"""
    return None if value is None else value.lstrip("0")


# Exports


def nom_proprietaire(row: Row) -> str:
    """Name of the owner in the export of the locaux, p_nom: civility, usage and birth names, denomination"""
    nom_usage = ""
    if row["dnomus"] is not None and row["dnomlp"] is not None and trim(row["dnomus"]) != trim(row["dnomlp"]):
        nom_usage = coalesce(concat(trim(row["dnomus"]), "/", trim(row["dprnus"]), ", née "), "") or ""
    return (
        (trim(coalesce(row["dqualp"], "")) or "")
        + " "
        + nom_usage
        + (trim(coalesce(row["ddenom"], "")) or "")
    )


def adresse_proprietaire(row: Row) -> str:
    """Address of the owner in the export of the locaux, p_adresse: the lines 4 to 6 separated by spaces.

    The number of the street is written without its leading zeros, the empty lines are ignored.
    """
    lines = [ltrim_zeros(trim(row["dlign4"])), trim(row["dlign5"]), trim(row["dlign6"])]
    return " ".join(line for line in lines if line)


def adresse_local(row: Row) -> str | None:
    """Street of the local in the export of the locaux, l_adresse: from the table voie, otherwise from the parcel.

    The nature of the street, like RUE, is optional.
    """
    if row["libvoi"] is not None:
        return (concat(row["natvoi"], " ") or "") + str(row["libvoi"])
    return concat(row["cconvo"], " ", row["dvoilib"])


def numero_voirie(row: Row) -> str | None:
    """Number of the local in the street, l_numero_voirie: without its leading zeros, with its optional index"""
    return concat(ltrim_zeros(text(row["dnvoiri"])), coalesce(row["dindic"], ""))


def naissance(row: Row, sensitive: SensitiveData) -> list[str | None]:
    """Birth date and place of the owner, - if they are unknown.

    Without the right, they are masked like in the fiche parcellaire, so that the user knows that
    some data are not given to him. The query does not read them in this case.
    """
    if not sensitive.birth:
        return [DATE_MASK, DEFAULT_MASK]
    return [coalesce(trim(row["jdatnss"]), "-"), coalesce(trim(row["dldnss"]), "-")]


def locaux_proprietaires_export(
    connector: QgsAbstractDatabaseProviderConnection,
    connection_params: dict[str, str],
    parcelles: list[str],
    sensitive: SensitiveData,
) -> tuple[list[str], list[list[str | None]]]:
    """Export of the locaux of the parcelles and of their owners: one row per local and owner.

    :param connector: The connection to the database.
    :param connection_params: The parameters of the connection, see fetch_rows.
    :param parcelles: The identifiers of the parcelles.
    :param sensitive: The sensitive data the user can see: the birth data are only exported with the right.
    :return: The names of the columns and the rows, like the export locauxProprios of Lizmap.
    """
    columns = [
        "parcelle",
        "l_batiment",
        "l_numero_entree",
        "l_niveau_etage",
        "l_numero_local",
        "l_invariant",
        "l_identifiant",
        "l_numero_voirie",
        "l_adresse",
        "l10_compte_proprietaire",
        "l10_type_local",
        "l10_type_local_lib",
        "l10_nature_local",
        "l10_nature_local_lib",
        "l10_nature_construction_particuliere",
        "l10_nature_construction_particuliere_lib",
        "l10_annee_construction",
        "l10_nombre_niveaux",
        "l10_nature_occupation",
        "l10_nature_occupation_lib",
        "p_ordre",
        "p_numero",
        "p_nom",
        "p_adresse",
        "p_date_naissance",
        "p_lieu_naissance",
        "p_code_droit",
        "p_code_droit_lib",
        "p_code_demembrement",
        "p_code_demembrement_lib",
    ]

    rows = []
    for row in locaux(connector, connection_params, parcelles, sensitive):
        values = [
            text(row["parcelle"]),
            text(row["dnubat"]),
            text(row["descr"]),
            text(row["dniv"]),
            text(row["dpor"]),
            text(row["invar"]),
            concat(row["dnubat"], "-", row["descr"], "-", row["dniv"], "-", row["dpor"]),
            numero_voirie(row),
            adresse_local(row),
            concat(row["ccodep"], row["ccocom"], "-", row["dnupro"]),
            text(row["dteloc"]),
            text(row["dteloc_lib"]),
            text(row["cconlc"]),
            text(row["cconlc_lib"]),
            text(row["ccoplc"]),
            text(row["ccoplc_lib"]),
            text(row["jannat"]),
            text(row["dnbniv"]),
            text(row["dnatlc"]),
            text(row["dnatlc_lib"]),
            text(row["dnulp"]),
            text(row["dnuper"]),
            nom_proprietaire(row),
            adresse_proprietaire(row),
        ]
        values += naissance(row, sensitive)
        values += [
            text(row["ccodro"]),
            coalesce(row["ccodro_lib"], ""),
            text(row["ccodem"]),
            coalesce(row["ccodem_lib"], ""),
        ]
        rows.append(values)
    return columns, rows


def parcelles_proprietaires_export(
    connector: QgsAbstractDatabaseProviderConnection,
    connection_params: dict[str, str],
    parcelles: list[str],
    sensitive: SensitiveData,
    recherche: RechercheSpatiale | None = None,
) -> tuple[list[str], list[list[str | None]]]:
    """Export of the owners of the parcelles, for mail merges: one row per owner, with the list of his parcelles.

    :param connector: The connection to the database.
    :param connection_params: The parameters of the connection, see fetch_rows.
    :param parcelles: The identifiers of the parcelles.
    :param sensitive: The sensitive data the user can see: the birth data are masked without the right.
    :param recherche: The objects selected by the spatial search of Lizmap: their codes near the parcelles
        of each owner are added in the column code_objet.
    :return: The names of the columns and the rows, like the export parcellesProprios of Lizmap.
    """
    columns = [
        "commune",
        "code_proprietaire",
        "qualite",
        "nom",
        "prenom",
        "denomination",
        "adresse",
        "complement_adresse",
        "code_postal",
        "ville",
        "adresse_complete",
        "date_naissance",
        "lieu_naissance",
        "parcelles",
    ]
    codes = {}
    if recherche is not None:
        columns.append("code_objet")
        codes = objets_proches(connector, connection_params, parcelles, recherche)

    # Owners grouped like the GROUP BY of the Lizmap query, with their parcelles
    keys = [
        "commune",
        "dnuper",
        "dqualp",
        "dnomus",
        "dprnus",
        "ddenom",
        "dlign4",
        "dlign5",
        "dlign6",
        "ccopos",
        # NULL without the right to see them
        "jdatnss",
        "dldnss",
    ]
    owners: dict[tuple, tuple[Row, set[str]]] = {}
    for row in ayants_droit(connector, connection_params, parcelles, sensitive):
        key = tuple(row[name] for name in keys)
        owners.setdefault(key, (row, set()))[1].add(row["parcelle"])

    rows = []
    for row, owner_parcelles in owners.values():
        dlign4 = ltrim_zeros(trim(coalesce(row["dlign4"], "")))
        dlign5 = trim(coalesce(row["dlign5"], ""))
        dlign6 = trim(coalesce(row["dlign6"], ""))
        ccopos = trim(coalesce(row["ccopos"], "")) or ""
        complete = (
            (ltrim_zeros(trim(coalesce(row["dlign4"], " "))) or "")
            + " "
            + (trim(coalesce(row["dlign5"], " ")) or "")
            + " "
            + (trim(coalesce(row["dlign6"], " ")) or "")
        )
        values = [
            text(row["commune"]),
            text(row["dnuper"]),
            trim(row["dqualp"]),
            trim(row["dnomus"]),
            trim(row["dprnus"]),
            trim(row["ddenom"]),
            dlign4,
            dlign5,
            ccopos,
            (dlign6 or "").replace(ccopos, "") if ccopos else dlign6,
            complete.replace("  ", " "),
        ]
        values += naissance(row, sensitive)
        values.append(", ".join(sorted(owner_parcelles)))
        if recherche is not None:
            # The codes near the parcelles of the owner, NULL if there is none
            owner_codes = set().union(*(codes.get(parcelle, set()) for parcelle in owner_parcelles))
            values.append(", ".join(sorted(owner_codes)) or None)
        rows.append(values)

    # Ordered by commune and denomination, the NULL values at the end like PostgreSQL
    rows.sort(key=lambda values: [(value is None, value or "") for value in (values[0], values[5])])
    return columns, rows


# CSV files of the selected parcelles in QGIS


def csv_value(value: str | None) -> str:
    """Return a value of a CSV file, written like the PHP function fputcsv used by Lizmap.

    The value is enclosed in double quotes if it contains a comma, a double quote, a space, a tabulation,
    a backslash or a line break, the double quotes are doubled. NULL is an empty value.
    """
    if value is None:
        return ""
    value = str(value)
    if any(character in value for character in CSV_ENCLOSED_CHARACTERS):
        return '"' + value.replace('"', '""') + '"'
    return value


def write_csv(path: Path, columns: list[str], rows: list[list[str | None]]) -> None:
    """Write a CSV file like Lizmap: UTF-8, separated by commas, one line per row after the names of the columns."""
    with path.open("w", encoding="utf-8", newline="") as f:
        f.write(",".join(csv_value(column) for column in columns) + "\n")
        for values in rows:
            f.write(",".join(csv_value(value) for value in values) + "\n")


def export_selected_parcelles(
    layer: QgsVectorLayer, export_type: str, path: Path, sensitive: SensitiveData
) -> int:
    """Write the CSV file of an export of the selected parcelles of a layer, like the CSV exports of Lizmap.

    :param layer: The layer of the parcelles, from the table parcelle_info, with the field geo_parcelle.
    :param export_type: The export: proprietaires (one row per owner) or locaux (one row per local and owner),
        see CSV_EXPORTS.
    :param path: The CSV file.
    :param sensitive: The sensitive data written in the file.
    :return: The number of rows of the file, without the names of the columns.
    :raises ValueError: If the export is unknown, if no parcelle is selected or if an identifier is not valid.
    """
    if export_type not in CSV_EXPORTS:
        raise ValueError(f"Unknown export: {export_type}")
    # Only the identifiers of the parcelles are read
    request = QgsFeatureRequest().setFlags(QgsFeatureRequest.Flag.NoGeometry)
    request.setSubsetOfAttributes(["geo_parcelle"], layer.fields())
    parcelles = sorted({str(feature["geo_parcelle"]) for feature in layer.getSelectedFeatures(request)})
    connection_params = getConnectionParameterFromDbLayer(layer)
    connector = getConnectorFromUri(connection_params)
    if export_type == "locaux":
        columns, rows = locaux_proprietaires_export(connector, connection_params, parcelles, sensitive)
    else:
        columns, rows = parcelles_proprietaires_export(connector, connection_params, parcelles, sensitive)
    write_csv(path, columns, rows)
    return len(rows)
