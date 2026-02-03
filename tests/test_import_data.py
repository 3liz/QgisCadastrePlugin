from pathlib import Path
from typing import NamedTuple

import pytest

from qgis.core import QgsCoordinateReferenceSystem, QgsProviderRegistry
from qgis.gui import QgisInterface

from cadastre.definitions import MAXIMUM_YEAR
from cadastre.dialogs.import_dialog import CadastreImportDialog



class TestCase(NamedTuple):
    insee: str
    lot: str
    dept: str
    commune: str
    epsg: str
    has_majic: bool
    direction: str
    version: str
    year: str
    geo_commune: str
    ccodir: str
    ccocom: str


CornillonMajic = TestCase(
    insee='13029',
    commune='CORNILLON-CONFOUX',
    epsg='EPSG:2154',
    has_majic=True,
    lot='1',
    dept='13',
    ccocom='029',
    ccodir='2',
    direction='2',
    version=str(MAXIMUM_YEAR),
    year=str(MAXIMUM_YEAR),
    geo_commune='132029',
)

CornillonSansMajic = TestCase(
    insee='13029',
    commune='CORNILLON-CONFOUX',
    epsg='EPSG:2154',
    has_majic=False,
    lot='1',
    dept='13',
    ccocom='029',
    ccodir='2',
    direction='2',
    version=str(MAXIMUM_YEAR),
    year=str(MAXIMUM_YEAR),
    geo_commune='132029',
)


TEST_SCHEMA = 'cadastre'


def remove_schema():
    metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
    #connection: QgsAbstractDatabaseProviderConnection
    connection = metadata.findConnection("test_database")
    assert connection is not None, "No database connection"
    if TEST_SCHEMA in connection.schemas():
        connection.dropSchema(TEST_SCHEMA, True)


@pytest.fixture(params=[CornillonMajic, CornillonSansMajic], ids=["Majic", "SansMajic"])
def test_case(request: pytest.FixtureRequest) -> TestCase:
    remove_schema()
    yield request.param


def test_import(test_case: TestCase, qgis_iface: QgisInterface, fixtures: Path):
    """ Internal function for the import. """

    assert qgis_iface is not None, "No qgis interface"

    remove_schema()

    # Not the best test, it's using the UI QDialog and iface
    dialog = CadastreImportDialog(qgis_iface)

    # Set postgis
    dialog.liDbType.setCurrentIndex(1)

    # Let the default connexion
    assert dialog.liDbConnection.count() == 1

    # Check empty database before
    metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
    connection = metadata.findConnection("test_database")
    assert TEST_SCHEMA not in connection.schemas()

    # Create schema
    dialog.inDbCreateSchema.setText(TEST_SCHEMA)
    dialog.btDbCreateSchema.click()

    # Check the schema exists
    assert TEST_SCHEMA in connection.schemas()

    # Set the path for edigeo
    dialog.inEdigeoSourceDir.setText(str(fixtures.joinpath('edigeo', test_case.insee)))

    # Set CRS
    crs = QgsCoordinateReferenceSystem(test_case.epsg)
    dialog.inEdigeoSourceProj.setCrs(crs)
    dialog.inEdigeoTargetProj.setCrs(crs)

    # Set MAJIC
    if test_case.has_majic:
        dialog.inMajicSourceDir.setText(str(fixtures.joinpath('majic', test_case.insee)))
    else:
        dialog.inMajicSourceDir.setText("")

    # Set lot
    dialog.inEdigeoLot.setText(test_case.lot)

    # Set departement
    dialog.inEdigeoDepartement.setText(test_case.dept)

    # Set direction
    dialog.inEdigeoDirection.setValue(int(test_case.direction))

    # Version
    dialog.inDataVersion.setValue(int(test_case.version))

    # Year
    dialog.inDataYear.setValue(int(test_case.year))

    # Import
    # As we want to the return of the self.go, we call the slot directly
    assert dialog.processImport()

    # Check we have a town in edigeo
    results = connection.executeSql('SELECT "geo_commune", "tex2" FROM cadastre.geo_commune;')

    assert len(results) == 1
    row = results[0]
    assert test_case.geo_commune == row[0]
    assert test_case.commune == row[1]

    # Check we have a town in majic
    if test_case.has_majic:
        results = connection.executeSql('SELECT * FROM cadastre.commune_majic;')
        assert len(results) == 1
        row = results[0]
        assert test_case.geo_commune == row[0]  # commune
        assert test_case.year == row[1]  # annee
        assert test_case.dept == row[2]  # ccodep
        assert test_case.ccodir == row[3]  # ccodir
        assert test_case.ccocom == row[4]  # ccocom
        assert test_case.commune == row[5]  # libcom
        assert test_case.lot == row[6]  # lot
