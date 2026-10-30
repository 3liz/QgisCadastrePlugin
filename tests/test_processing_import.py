from pathlib import Path

import processing
import pytest

from qgis.core import (
    QgsApplication,
    QgsDataSourceUri,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProviderRegistry,
)
from qgis.utils import spatialite_connect

from cadastre.cadastre_common_base import hasSpatialiteSupport
from cadastre.cadastre_database import CadastreDatabase
from cadastre.feedback import CadastreProcessingFeedback, html_to_text

from .test_import_data import CornillonMajic
from .test_import_data import TestCase as ImportCase

SCHEMA = "cadastre_processing"


def pg_connection():
    # Do not keep the connection object, it is invalidated when connections are reloaded
    metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
    return metadata.findConnection("test_database")


@pytest.fixture()
def drop_schema():
    yield
    if SCHEMA in pg_connection().schemas():
        pg_connection().dropSchema(SCHEMA, True)


def parameters(test_case: ImportCase, fixtures: Path, **kwargs) -> dict:
    params = {
        "DOSSIER_EDIGEO": str(fixtures.joinpath("edigeo", test_case.insee)),
        "DOSSIER_MAJIC": str(fixtures.joinpath("majic", test_case.insee)),
        "PROJECTION_SOURCE": test_case.epsg,
        "PROJECTION_CIBLE": test_case.epsg,
        "DEPARTEMENT": test_case.dept,
        "DIRECTION": int(test_case.direction),
        "LOT": test_case.lot,
        "VERSION": int(test_case.version),
        "ANNEE": int(test_case.year),
    }
    params.update(kwargs)
    return params


def test_html_to_text():
    assert html_to_text("<h3>MAJIC</h3>") == "MAJIC"
    assert html_to_text("<b>a</b><br/>b &amp; c") == "a\nb & c"


def test_feedback_forward():
    """ Messages and progress are forwarded to the Processing feedback. """
    infos = []
    progress = []

    class Recorder(QgsProcessingFeedback):
        def pushInfo(self, info):
            infos.append(info)

    recorder = Recorder()
    recorder.progressChanged.connect(progress.append)
    feedback = CadastreProcessingFeedback(recorder)
    feedback.pushInfo("<b>Import terminé</b>")
    feedback.setProgress(50)

    assert infos == ["Import terminé"]
    assert progress == [50]


def test_import_postgis(fixtures: Path, drop_schema: None):
    assert SCHEMA not in pg_connection().schemas()

    results = processing.run(
        "cadastre:import_postgis",
        parameters(CornillonMajic, fixtures, CONNEXION="test_database", SCHEMA=SCHEMA),
    )

    assert results["SUCCESS"] == 1
    rows = pg_connection().executeSql(f'SELECT geo_commune, tex2 FROM "{SCHEMA}".geo_commune')
    assert rows == [[CornillonMajic.geo_commune, CornillonMajic.commune]]
    rows = pg_connection().executeSql(f'SELECT count(*) FROM "{SCHEMA}".commune_majic')
    assert rows == [[1]]


def test_import_postgis_wrong_departement(fixtures: Path, drop_schema: None):
    """ MAJIC files are for 13, the import fails unless the files values are accepted. """
    params = parameters(CornillonMajic, fixtures, CONNEXION="test_database", SCHEMA=SCHEMA, DEPARTEMENT="14")
    params["DOSSIER_EDIGEO"] = ""

    with pytest.raises(QgsProcessingException):
        processing.run("cadastre:import_postgis", params)

    params["DEP_DIR_FICHIERS"] = True
    assert processing.run("cadastre:import_postgis", params)["SUCCESS"] == 1
    rows = pg_connection().executeSql(f'SELECT ccodep FROM "{SCHEMA}".commune_majic')
    assert rows == [[CornillonMajic.dept]]


@pytest.mark.parametrize(
    "changes, error",
    [
        ({"DOSSIER_EDIGEO": "", "DOSSIER_MAJIC": ""}, "Un répertoire existant de fichiers EDIGEO ou MAJIC"),
        ({"DOSSIER_MAJIC": "/not/a/directory", "DOSSIER_EDIGEO": ""}, "Un répertoire existant"),
        ({"DEPARTEMENT": "123"}, "Le département doit faire 2 caractères"),
        ({"LOT": " "}, "Le lot est obligatoire"),
    ],
    ids=["no-files", "missing-directory", "departement", "lot"],
)
def test_import_invalid_parameters(fixtures: Path, drop_schema: None, changes: dict, error: str):
    params = parameters(CornillonMajic, fixtures, CONNEXION="test_database", SCHEMA=SCHEMA, **changes)

    algorithm = QgsApplication.processingRegistry().algorithmById("cadastre:import_postgis")
    ok, message = algorithm.checkParameterValues(params, QgsProcessingContext())
    assert not ok
    assert error in message

    with pytest.raises(QgsProcessingException):
        processing.run("cadastre:import_postgis", params)

    # Checked before connecting to the database: the schema is not created
    assert SCHEMA not in pg_connection().schemas()


def test_import_valid_parameters(fixtures: Path):
    params = parameters(CornillonMajic, fixtures, CONNEXION="test_database", SCHEMA=SCHEMA)
    algorithm = QgsApplication.processingRegistry().algorithmById("cadastre:import_postgis")

    assert algorithm.checkParameterValues(params, QgsProcessingContext()) == (True, "")


@pytest.mark.skipif(not hasSpatialiteSupport(), reason="No Spatialite support")
def test_import_spatialite(fixtures: Path, tmp_path: Path):
    path = tmp_path / "processing.sqlite"
    con = spatialite_connect(str(path), isolation_level=None)
    con.cursor().execute("SELECT InitSpatialMetadata(1)")
    con.close()

    metadata = QgsProviderRegistry.instance().providerMetadata("spatialite")
    uri = QgsDataSourceUri()
    uri.setDatabase(str(path))
    metadata.saveConnection(metadata.createConnection(uri.uri(), {}), "processing.sqlite")
    try:
        results = processing.run(
            "cadastre:import_spatialite",
            parameters(CornillonMajic, fixtures, CONNEXION="processing.sqlite"),
        )
        assert results["SUCCESS"] == 1

        database = CadastreDatabase.from_connection("spatialite", "processing.sqlite")
        assert database.fetch("SELECT geo_commune FROM geo_commune") == [[CornillonMajic.geo_commune]]
        database.close()
    finally:
        metadata.deleteConnection("processing.sqlite")
