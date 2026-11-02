""" Exports of the cadastre data for a list of parcelles, used by the CSV exports of Lizmap """

import pytest

from qgis.core import QgsProject, QgsVectorLayer

import cadastre.cadastre_common_base as common_utils

from cadastre.cadastre_common_base import SensitiveData
from cadastre.export_csv import (
    locaux,
    locaux_proprietaires_export,
    parcelles_proprietaires_export,
    parcelles_sql,
    recherche_spatiale,
)

from .test_majic_data import COPROPRIETE, database, fetch, parcelles  # noqa: F401

# A parcel with 2 locaux in the fictitious data
PARCELLE = "1320290000A1088"

# Columns of the export of the locaux
LOCAUX_COLUMNS = [
    "parcelle", "l_batiment", "l_numero_entree", "l_niveau_etage", "l_numero_local", "l_invariant",
    "l_identifiant", "l_numero_voirie", "l_adresse", "l10_compte_proprietaire", "l10_type_local",
    "l10_type_local_lib", "l10_nature_local", "l10_nature_local_lib", "l10_nature_construction_particuliere",
    "l10_nature_construction_particuliere_lib", "l10_annee_construction", "l10_nombre_niveaux",
    "l10_nature_occupation", "l10_nature_occupation_lib", "p_ordre", "p_numero", "p_nom", "p_adresse",
    "p_date_naissance", "p_lieu_naissance", "p_code_droit", "p_code_droit_lib", "p_code_demembrement", "p_code_demembrement_lib",
]

# Columns of the export of the owners
PARCELLES_COLUMNS = [
    "commune", "code_proprietaire", "qualite", "nom", "prenom", "denomination", "adresse",
    "complement_adresse", "code_postal", "ville", "adresse_complete", "date_naissance", "lieu_naissance",
    "parcelles",
]


@pytest.fixture(scope="module")
def connection(parcelles: QgsVectorLayer) -> tuple:  # noqa: F811
    """ The connection to the test database and its parameters, from the layer of the parcelles """
    params = common_utils.getConnectionParameterFromDbLayer(parcelles)
    return common_utils.getConnectorFromUri(params), params


def test_parcelles_sql():
    assert parcelles_sql([COPROPRIETE, PARCELLE]) == f"'{COPROPRIETE}', '{PARCELLE}'"
    for invalid in ([], [""], [f"{COPROPRIETE}') OR ('1'='1"], ["1320290000a0107"]):
        with pytest.raises(ValueError):
            parcelles_sql(invalid)


def test_locaux_export(connection: tuple):
    """ One row per local and owner, the birth data are masked without the right """
    columns, rows = locaux_proprietaires_export(*connection, [COPROPRIETE, PARCELLE], SensitiveData())
    assert columns == LOCAUX_COLUMNS
    result = [dict(zip(columns, row)) for row in rows]
    assert {row["parcelle"] for row in result} == {COPROPRIETE, PARCELLE}
    assert len({row["l_invariant"] for row in result}) == 7
    assert all(row["p_code_droit_lib"] is not None for row in result)

    assert {(row["p_date_naissance"], row["p_lieu_naissance"]) for row in result} == {("XX/XX/XXXX", "XXX")}

    columns, rows = locaux_proprietaires_export(*connection, [COPROPRIETE], SensitiveData.full())
    assert columns == LOCAUX_COLUMNS
    assert not any("XX" in str(value) for row in rows for value in row)


def test_parcelles_export(connection: tuple):
    """ One row per owner, with the list of his parcelles """
    columns, rows = parcelles_proprietaires_export(*connection, [COPROPRIETE, PARCELLE], SensitiveData())
    assert columns == PARCELLES_COLUMNS
    parcelles = {parcelle for row in rows for parcelle in row[-1].split(", ")}
    assert parcelles == {COPROPRIETE, PARCELLE}

    assert {(row[11], row[12]) for row in rows} == {("XX/XX/XXXX", "XXX")}

    columns, rows = parcelles_proprietaires_export(*connection, [COPROPRIETE], SensitiveData.full())
    assert columns == PARCELLES_COLUMNS
    assert not any("XX" in str(value) for row in rows for value in row)


def test_locaux(connection: tuple):
    """ The common query of the locaux gives also the lots, used by the carte d'identité of the parcel """
    rows = locaux(*connection, [COPROPRIETE], SensitiveData())
    assert any(row["dnulot"] and row["ddenql"] for row in rows)
    # The birth data are not read without the right
    assert all(row["jdatnss"] is None for row in rows)
    assert any(row["jdatnss"] for row in locaux(*connection, [COPROPRIETE], SensitiveData.full()))


def test_recherche_spatiale(connection: tuple, parcelles: QgsVectorLayer):  # noqa: F811
    """ The codes of the buildings selected near the parcelles are added to the owners """
    bati = QgsProject.instance().mapLayersByName("Bâti")[0]
    # The buildings in the copropriété, and the farthest building
    near = fetch(
        "SELECT b.ogc_fid, b.geo_batiment FROM cadastre.geo_batiment b "
        "JOIN cadastre.geo_parcelle p ON ST_Intersects(b.geom, p.geom) "
        f"WHERE p.geo_parcelle = '{COPROPRIETE}'"
    )
    far = fetch(
        "SELECT b.ogc_fid FROM cadastre.geo_batiment b, cadastre.geo_parcelle p "
        f"WHERE p.geo_parcelle = '{COPROPRIETE}' ORDER BY ST_Distance(b.geom, p.geom) DESC LIMIT 1"
    )
    assert near
    objets = [str(fid) for fid, _code in near] + [str(far[0][0])]

    recherche = recherche_spatiale(bati, parcelles, "geo_batiment", objets, 0)
    columns, rows = parcelles_proprietaires_export(*connection, [COPROPRIETE, PARCELLE], SensitiveData(), recherche)
    assert columns[-1] == "code_objet"
    result = {row[-2]: row[-1] for row in rows}
    assert result[COPROPRIETE] == ", ".join(sorted(code for _fid, code in near))
    # No selected building near the other parcel
    assert result[PARCELLE] is None

    # The values used in the SQL query are checked
    for args in (
        ("geo_batiment", [f"{objets[0]}') OR ('1'='1"], 0),
        ("unknown_field", objets, 0),
        ("geo_batiment", objets, -1),
        ("geo_batiment", [], 0),
    ):
        with pytest.raises(ValueError):
            recherche_spatiale(bati, parcelles, *args)
    # The layer of the objects must be in the database of the cadastre data
    with pytest.raises(ValueError):
        recherche_spatiale(QgsVectorLayer("Point?crs=EPSG:2154", "memory", "memory"), parcelles, "x", objets, 0)
