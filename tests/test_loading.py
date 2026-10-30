from pathlib import Path

import pytest

from qgis.core import QgsProject, QgsProviderRegistry
from qgis.gui import QgisInterface

from cadastre.cadastre_database import CadastreDatabase
from cadastre.cadastre_import import cadastreImport
from cadastre.cadastre_loading import CadastreLoading, LoadingOptions
from cadastre.dialogs.cadastre_load_dialog import CadastreLoadDialog
from cadastre.dialogs.parcelle_dialog import CadastreParcelleDialog
from cadastre.dialogs.search_dialog import CadastreSearchDialog
from cadastre.feedback import CadastreFeedback

from .test_import_data import TEST_SCHEMA, CornillonMajic, import_options, remove_schema

MAIN_LAYERS = {"Communes", "Sections", "Parcelles", "Bâti"}


@pytest.fixture(scope="module")
def database(fixtures: Path) -> CadastreDatabase:
    """ Database with imported EDIGEO and MAJIC data. """
    remove_schema()
    metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
    connection = metadata.findConnection("test_database")
    connection.createSchema(TEST_SCHEMA)
    assert cadastreImport(import_options(CornillonMajic, fixtures), CadastreFeedback()).run()

    return CadastreDatabase.from_connection("postgis", "test_database", TEST_SCHEMA)


@pytest.fixture()
def project() -> QgsProject:
    project = QgsProject.instance()
    project.clear()
    yield project
    project.clear()


def test_load_all_layers(database: CadastreDatabase, project: QgsProject):
    layers = CadastreLoading(CadastreFeedback()).process_loading(LoadingOptions(database))

    assert len(layers) > len(MAIN_LAYERS)
    assert all(layer.isValid() for layer in layers), [layer.name() for layer in layers if not layer.isValid()]
    names = {layer.name() for layer in layers}
    assert names >= MAIN_LAYERS
    assert len(project.mapLayers()) == len(layers)

    # Layers are in the "Cadastre" group
    group = project.layerTreeRoot().findGroup("Cadastre")
    assert group is not None
    assert len(group.findLayers()) == len(layers)

    # Project variables used by the cadastre tools
    parcelles = project.mapLayersByName("Parcelles")[0]
    assert parcelles.featureCount() > 0
    variables = project.customVariables()
    assert variables["cadastre_parcelle_layer_id"] == parcelles.id()
    assert variables["cadastre_parcelle_unique_field"] == "geo_parcelle"


def test_load_main_layers_only(database: CadastreDatabase, project: QgsProject):
    options = LoadingOptions(database, main_layers_only=True)
    layers = CadastreLoading(CadastreFeedback()).process_loading(options)

    assert {layer.name() for layer in layers} == MAIN_LAYERS


@pytest.mark.parametrize(
    "expression, count",
    [("geo_commune = '132029'", 1), ("geo_commune = 'XXXXXX'", 1), ("geo_commune = ", 1)],
    ids=["filter", "no-match", "invalid"],
)
def test_load_commune_filter(database: CadastreDatabase, project: QgsProject, expression: str, count: int):
    options = LoadingOptions(database, commune_expression=expression, main_layers_only=True)
    CadastreLoading(CadastreFeedback()).process_loading(options)

    communes = project.mapLayersByName("Communes")[0]
    assert communes.featureCount() == count
    if expression == "geo_commune = '132029'":
        assert "132029" in communes.subsetString()
    else:
        # No commune found or invalid expression: no filter
        assert communes.subsetString() == ""


def test_load_sql_layer(database: CadastreDatabase, project: QgsProject):
    sql = f'SELECT ogc_fid, geo_commune, geom FROM "{TEST_SCHEMA}".geo_commune'
    layer = CadastreLoading(CadastreFeedback()).load_sql_layer(database, sql, "geom", "Ma requête")

    assert layer is not None
    assert layer.name() == "Ma requête"
    assert layer.featureCount() == 1
    assert project.mapLayersByName("Ma requête") == [layer]


def test_load_sql_layer_invalid(database: CadastreDatabase, project: QgsProject):
    layer = CadastreLoading(CadastreFeedback()).load_sql_layer(database, "SELECT * FROM unknown_table")

    assert layer is None
    assert len(project.mapLayers()) == 0


def test_load_with_dialog(database: CadastreDatabase, project: QgsProject, qgis_iface: QgisInterface):
    """ Loading from the dialog, like a user. """
    search_dialog = CadastreSearchDialog(qgis_iface)
    dialog = CadastreLoadDialog(qgis_iface, search_dialog)

    # PostGIS, default connection and test schema
    dialog.database_widget.liDbType.setCurrentIndex(1)
    assert dialog.database_widget.liDbConnection.currentText() == "test_database"
    dialog.database_widget.liDbSchema.setCurrentIndex(dialog.database_widget.liDbSchema.findText(TEST_SCHEMA))
    dialog.cbMainLayersOnly.setChecked(True)

    dialog.onProcessLoadingClicked()

    assert {layer.name() for layer in project.mapLayers().values()} == MAIN_LAYERS


def test_search_and_parcelle_dialogs(database: CadastreDatabase, project: QgsProject, qgis_iface: QgisInterface):
    """ Search and parcelle dialogs use the loaded layers. """
    CadastreLoading(CadastreFeedback()).process_loading(LoadingOptions(database, main_layers_only=True))

    search_dialog = CadastreSearchDialog(qgis_iface)
    search_dialog.checkMajicContent()
    # MAJIC fixtures only contain the TOPO file with data
    assert search_dialog.hasMajicDataVoie
    assert not search_dialog.hasMajicDataProp

    layer = project.mapLayersByName("Parcelles")[0]
    feature = next(layer.getFeatures())
    dialog = CadastreParcelleDialog(qgis_iface, layer, feature, search_dialog)

    assert not dialog.hasMajicDataProp
    assert feature["geo_parcelle"] in dialog.windowTitle()
    assert dialog.parcelleInfo.toPlainText().strip()
