from pathlib import Path
from typing import Iterator

import pytest

from qgis.core import QgsDataSourceUri, QgsFeatureRequest, QgsProject, QgsProviderRegistry
from qgis.utils import spatialite_connect

from cadastre.cadastre_common_base import (
    SensitiveData,
    getConnectionParameterFromDbLayer,
    getConnectorFromUri,
    getItemHtml,
    hasSpatialiteSupport,
)
from cadastre.cadastre_database import CadastreDatabase
from cadastre.cadastre_import import cadastreImport
from cadastre.cadastre_loading import CadastreLoading, LoadingOptions
from cadastre.dialogs.database_widget import DatabaseWidget
from cadastre.feedback import CadastreFeedback

from .test_import_data import CornillonMajic, import_options

pytestmark = pytest.mark.skipif(not hasSpatialiteSupport(), reason="No Spatialite support")

CONNECTION = "cadastre test.sqlite"


@pytest.fixture(scope="module")
def connection_name(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    """ An empty Spatialite database, with a QGIS connection. """
    path = tmp_path_factory.mktemp("spatialite") / CONNECTION
    con = spatialite_connect(str(path), isolation_level=None)
    con.cursor().execute("SELECT InitSpatialMetadata(1)")
    con.close()

    metadata = QgsProviderRegistry.instance().providerMetadata("spatialite")
    uri = QgsDataSourceUri()
    uri.setDatabase(str(path))
    metadata.saveConnection(metadata.createConnection(uri.uri(), {}), CONNECTION)
    yield CONNECTION
    metadata.deleteConnection(CONNECTION)


def test_widget(connection_name: str):
    widget = DatabaseWidget(creation_enabled=True)
    widget.liDbType.setCurrentIndex(widget.liDbType.findText("Spatialite"))
    widget.liDbConnection.setCurrentIndex(widget.liDbConnection.findText(connection_name))

    assert not widget.btCreateNewSpatialiteDb.isHidden()
    assert widget.btDbCreateSchema.isHidden()
    assert not widget.liDbSchema.isEnabled()

    database = widget.database()
    assert database is not None
    assert database.db_type == "spatialite"
    assert database.schema == ""
    assert not database.structure().has_structure
    widget.close_connection()


def test_import_and_load(connection_name: str, fixtures: Path):
    database = CadastreDatabase.from_connection("spatialite", connection_name)
    options = import_options(CornillonMajic, fixtures)
    options.database = database
    assert cadastreImport(options, CadastreFeedback()).run()

    structure = database.structure()
    assert structure.has_structure
    assert structure.has_data
    assert database.fetch("SELECT geo_commune, tex2 FROM geo_commune") == [
        [CornillonMajic.geo_commune, CornillonMajic.commune]
    ]
    assert database.fetch("SELECT count(*) FROM geo_parcelle")[0][0] > 0

    project = QgsProject.instance()
    project.clear()
    try:
        layers = CadastreLoading(CadastreFeedback()).process_loading(
            LoadingOptions(database, main_layers_only=True)
        )
        assert {layer.name() for layer in layers} == {"Communes", "Sections", "Parcelles", "Bâti"}
        assert all(layer.isValid() for layer in layers)
        parcelles = project.mapLayersByName("Parcelles")[0]
        assert parcelles.featureCount() > 0

        # Fiche parcellaire of a parcel with a building, the sensitive data are masked or not
        geo_parcelle = database.fetch("SELECT parcelle FROM local10 ORDER BY parcelle LIMIT 1")[0][0]
        request = QgsFeatureRequest().setFilterExpression(f"\"geo_parcelle\" = '{geo_parcelle}'")
        feature = next(parcelles.getFeatures(request))
        params = getConnectionParameterFromDbLayer(parcelles)
        connector = getConnectorFromUri(params)
        for item in ("proprietaires", "subdivisions", "locaux_detail"):
            html = getItemHtml(item, feature, params, connector)
            assert "XXX</" in html, item
            html = getItemHtml(item, feature, params, connector, SensitiveData.full())
            assert "<table" in html and "XXX" not in html, item
    finally:
        project.clear()
        database.close()
