"""Exports of the cadastre data for a list of parcelles, used by the CSV exports of Lizmap.

Two common queries, for PostgreSQL and Spatialite, in the files of cadastre/sql/export:

* the ayants droit of the parcelles: one row per parcelle and owner;
* the locaux of the parcelles: one row per local and owner.

The exports build their columns from these rows. They have the same names and values as the SQL queries
of the Lizmap module which they replace, so that the CSV files used for mail merges or by third parties
do not change: the formulas of these queries are reproduced, including how they handle NULL values.
"""

__copyright__ = "Copyright 2026, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import re

from typing import Any

from qgis.core import QgsAbstractDatabaseProviderConnection

from cadastre.cadastre_common_base import SensitiveData, quoteString
from cadastre.fiche import DATE_MASK, DEFAULT_MASK, Row, fetch_rows, load_sql

# Identifier of a parcelle, the field geo_parcelle, like 1320290000A0107
PARCELLE_PATTERN = re.compile(r"^[0-9A-Z]{1,20}$")

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
    """Address of the owner in the export of the locaux, p_adresse"""
    return (
        (ltrim_zeros(trim(coalesce(row["dlign4"], ""))) or "")
        + (trim(coalesce(row["dlign5"], "")) or "")
        + " "
        + (trim(coalesce(row["dlign6"], "")) or "")
    )


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
        if row["libvoi"] is not None:
            # The Lizmap query uses coalesce(natvoi || ' '): the address is NULL without nature of the street
            adresse = concat(concat(row["natvoi"], " "), row["libvoi"])
        else:
            adresse = concat(row["cconvo"], " ", row["dvoilib"])
        values = [
            text(row["parcelle"]),
            text(row["dnubat"]),
            text(row["descr"]),
            text(row["dniv"]),
            text(row["dpor"]),
            text(row["invar"]),
            concat(row["dnubat"], "-", row["descr"], "-", row["dniv"], "-", row["dpor"]),
            concat(ltrim_zeros(text(row["dnvoiri"])), row["dindic"]),
            adresse,
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
) -> tuple[list[str], list[list[str | None]]]:
    """Export of the owners of the parcelles, for mail merges: one row per owner, with the list of his parcelles.

    :param connector: The connection to the database.
    :param connection_params: The parameters of the connection, see fetch_rows.
    :param parcelles: The identifiers of the parcelles.
    :param sensitive: The sensitive data the user can see: the birth data are only exported with the right.
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
        rows.append(values)

    # Ordered by commune and denomination, the NULL values at the end like PostgreSQL
    rows.sort(key=lambda values: [(value is None, value or "") for value in (values[0], values[5])])
    return columns, rows
