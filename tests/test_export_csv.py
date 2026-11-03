""" Exports of the cadastre data for a list of parcelles, used by the CSV exports of Lizmap """

import csv

from pathlib import Path

import pytest

from qgis.core import QgsAbstractDatabaseProviderConnection, QgsFeatureRequest, QgsProject, QgsVectorLayer
from qgis.gui import QgisInterface
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox

import cadastre.cadastre_common_base as common_utils
import cadastre.export_csv as export_csv

from cadastre.cadastre_common_base import SensitiveData
from cadastre.cadastre_menu import CadastreMenu
from cadastre.export_csv import (
    CSV_EXPORTS,
    adresse_local,
    adresse_proprietaire,
    locaux,
    locaux_proprietaires_export,
    parcelles_proprietaires_export,
    numero_voirie,
    csv_value,
    export_selected_parcelles,
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


# The connection to the test database and its parameters
Connection = tuple[QgsAbstractDatabaseProviderConnection, dict[str, str]]


@pytest.fixture(scope="module")
def connection(parcelles: QgsVectorLayer) -> Connection:  # noqa: F811
    """ The connection to the test database and its parameters, from the layer of the parcelles """
    params = common_utils.getConnectionParameterFromDbLayer(parcelles)
    connector = common_utils.getConnectorFromUri(params)
    assert connector is not None
    return connector, params


def test_adresse_local():
    """ The nature of the street is optional, the address of the parcel is used without street """
    assert adresse_local({"natvoi": "RUE", "libvoi": "DES OLIVIERS"}) == "RUE DES OLIVIERS"
    assert adresse_local({"natvoi": None, "libvoi": "LES AIRES"}) == "LES AIRES"
    assert adresse_local({"libvoi": None, "cconvo": "CHE", "dvoilib": "DE CAMPREOUX"}) == "CHE DE CAMPREOUX"


def test_numero_voirie():
    """ The leading zeros are removed, the index of repetition is optional """
    assert numero_voirie({"dnvoiri": "0012", "dindic": "B"}) == "12B"
    assert numero_voirie({"dnvoiri": "0012", "dindic": None}) == "12"
    assert numero_voirie({"dnvoiri": None, "dindic": "B"}) is None


def test_adresse_proprietaire():
    """ The lines 4 to 6 of the address are separated by spaces, the empty ones are ignored """
    row = {"dlign4": "0021 CHE DE CAMPREOUX ", "dlign5": "LES AIRES", "dlign6": "13250 CORNILLON CONFOUX"}
    assert adresse_proprietaire(row) == "21 CHE DE CAMPREOUX LES AIRES 13250 CORNILLON CONFOUX"
    assert adresse_proprietaire({**row, "dlign5": None}) == "21 CHE DE CAMPREOUX 13250 CORNILLON CONFOUX"
    assert adresse_proprietaire({**row, "dlign5": "  "}) == "21 CHE DE CAMPREOUX 13250 CORNILLON CONFOUX"


def test_parcelles_sql():
    assert parcelles_sql([COPROPRIETE, PARCELLE]) == f"'{COPROPRIETE}', '{PARCELLE}'"
    for invalid in ([], [""], [f"{COPROPRIETE}') OR ('1'='1"], ["1320290000a0107"]):
        with pytest.raises(ValueError):
            parcelles_sql(invalid)


def test_locaux_export(connection: Connection):
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


def test_parcelles_export(connection: Connection):
    """ One row per owner, with the list of his parcelles """
    columns, rows = parcelles_proprietaires_export(*connection, [COPROPRIETE, PARCELLE], SensitiveData())
    assert columns == PARCELLES_COLUMNS
    exported = {parcelle for row in rows for parcelle in str(row[-1]).split(", ")}
    assert exported == {COPROPRIETE, PARCELLE}

    assert {(row[11], row[12]) for row in rows} == {("XX/XX/XXXX", "XXX")}

    columns, rows = parcelles_proprietaires_export(*connection, [COPROPRIETE], SensitiveData.full())
    assert columns == PARCELLES_COLUMNS
    assert not any("XX" in str(value) for row in rows for value in row)


def test_locaux(connection: Connection):
    """ The common query of the locaux gives also the lots, used by the carte d'identité of the parcel """
    rows = locaux(*connection, [COPROPRIETE], SensitiveData())
    assert any(row["dnulot"] and row["ddenql"] for row in rows)
    # The birth data are not read without the right
    assert all(row["jdatnss"] is None for row in rows)
    assert any(row["jdatnss"] for row in locaux(*connection, [COPROPRIETE], SensitiveData.full()))


def test_recherche_spatiale(connection: Connection, parcelles: QgsVectorLayer):  # noqa: F811
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


def select(layer: QgsVectorLayer, geo_parcelles: list[str]):
    """Select parcelles of the layer"""
    values = ", ".join(f"'{geo_parcelle}'" for geo_parcelle in geo_parcelles)
    request = QgsFeatureRequest().setFilterExpression(f'"geo_parcelle" IN ({values})')
    layer.selectByIds([feature.id() for feature in layer.getFeatures(request)])


def read_csv(path: Path) -> list[list[str]]:
    """Read a CSV file written by the export"""
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.reader(f))


def test_csv_value():
    """Values written like the PHP function fputcsv used by Lizmap"""
    assert csv_value(None) == ""
    assert csv_value("") == ""
    assert csv_value("A0107") == "A0107"
    assert csv_value("CHEM DE LA COOPERATIVE") == '"CHEM DE LA COOPERATIVE"'
    assert csv_value('a"b') == '"a""b"'
    assert csv_value("a,b") == '"a,b"'


def test_export_selected_parcelles(connection: Connection, parcelles: QgsVectorLayer, tmp_path: Path):  # noqa: F811
    """The CSV files of the selected parcelles have the same columns and rows as the exports"""
    select(parcelles, [COPROPRIETE, PARCELLE])
    try:
        path = tmp_path / "proprietaires.csv"
        count = export_selected_parcelles(parcelles, "proprietaires", path, SensitiveData.full())
        columns, rows = parcelles_proprietaires_export(*connection, [COPROPRIETE, PARCELLE], SensitiveData.full())
        assert count == len(rows) > 0
        assert read_csv(path) == [columns] + [[value or "" for value in row] for row in rows]

        path = tmp_path / "locaux.csv"
        count = export_selected_parcelles(parcelles, "locaux", path, SensitiveData())
        columns, rows = locaux_proprietaires_export(*connection, [COPROPRIETE, PARCELLE], SensitiveData())
        assert count == len(rows) > 0
        assert read_csv(path) == [columns] + [[value or "" for value in row] for row in rows]

        with pytest.raises(ValueError):
            export_selected_parcelles(parcelles, "unknown", path, SensitiveData())
    finally:
        parcelles.removeSelection()

    # Without selection
    with pytest.raises(ValueError):
        export_selected_parcelles(parcelles, "locaux", tmp_path / "empty.csv", SensitiveData())


def test_csv_export_action(
    parcelles: QgsVectorLayer, qgis_iface: QgisInterface, tmp_path: Path, monkeypatch: pytest.MonkeyPatch  # noqa: F811
):
    """The button of the toolbar is enabled with selected parcelles, its menu exports them"""
    # The processing provider of the plugin loaded for the tests is kept
    monkeypatch.setattr(CadastreMenu, "initProcessing", lambda self: None)
    menu = CadastreMenu(qgis_iface)
    menu.initGui()
    try:
        assert menu.csv_export_action is not None
        assert menu.csv_export_menu is not None
        assert [action.text() for action in menu.csv_export_menu.actions()] == [
            label for label, _filename in CSV_EXPORTS.values()
        ]
        assert not menu.csv_export_action.isEnabled()

        select(parcelles, [COPROPRIETE])
        # The canvas of the tests does not emit selectionChanged: the slot is called like the signal would
        menu.update_csv_export_action()
        assert menu.csv_export_action.isEnabled()

        # Export of the locaux, in the file chosen in the dialog, the extension .csv is added
        monkeypatch.setattr(
            QFileDialog, "getSaveFileName", lambda *args, **kwargs: (str(tmp_path / "export"), "CSV (*.csv)")
        )
        menu.csv_export_menu.actions()[1].trigger()
        rows = read_csv(tmp_path / "export.csv")
        assert rows[0][0] == "parcelle"
        assert {row[0] for row in rows[1:]} == {COPROPRIETE}

        # Above the number of parcelles, the user confirms the export
        monkeypatch.setattr(export_csv, "CSV_EXPORT_CONFIRM_COUNT", 0)
        questions = []

        def question(*args, answer=QMessageBox.StandardButton.No, **kwargs):
            questions.append(args[2])
            return answer

        monkeypatch.setattr(QMessageBox, "question", question)
        (tmp_path / "export.csv").unlink()
        menu.csv_export_menu.actions()[1].trigger()
        assert "1 parcelles" in questions[0]
        assert not (tmp_path / "export.csv").exists()

        monkeypatch.setattr(
            QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Yes
        )
        menu.csv_export_menu.actions()[1].trigger()
        assert (tmp_path / "export.csv").exists()

        parcelles.removeSelection()
        menu.update_csv_export_action()
        assert not menu.csv_export_action.isEnabled()
    finally:
        parcelles.removeSelection()
        menu.unload()
