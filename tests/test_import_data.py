import shutil
import zipfile

from pathlib import Path
from typing import Iterator, NamedTuple

import pytest

from qgis.core import QgsCoordinateReferenceSystem, QgsProviderRegistry
from qgis.gui import QgisInterface

from cadastre.cadastre_database import CadastreDatabase
from cadastre.cadastre_import import ImportOptions, cadastreImport
from cadastre.definitions import MAXIMUM_YEAR
from cadastre.dialogs.import_dialog import CadastreImportDialog
from cadastre.feedback import CadastreFeedback



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
def test_case(request: pytest.FixtureRequest) -> Iterator[TestCase]:
    remove_schema()
    yield request.param


def test_import(test_case: TestCase, qgis_iface: QgisInterface, fixtures: Path):
    """ Internal function for the import. """

    assert qgis_iface is not None, "No qgis interface"

    remove_schema()

    # Not the best test, it's using the UI QDialog and iface
    dialog = CadastreImportDialog(qgis_iface)

    # Set postgis
    dialog.database_widget.liDbType.setCurrentIndex(1)

    # Let the default connexion
    assert dialog.database_widget.liDbConnection.count() == 1

    # Check empty database before
    metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
    connection = metadata.findConnection("test_database")
    assert TEST_SCHEMA not in connection.schemas()

    # Create schema
    dialog.database_widget.inDbCreateSchema.setText(TEST_SCHEMA)
    dialog.database_widget.btDbCreateSchema.click()

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

    check_imported_data(test_case, connection)


def test_import_without_dialog(test_case: TestCase, fixtures: Path):
    """ Import using the import class only, without any UI. """
    metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
    connection = metadata.findConnection("test_database")
    connection.createSchema(TEST_SCHEMA)

    options = import_options(test_case, fixtures)
    assert cadastreImport(options, CadastreFeedback()).run()

    check_imported_data(test_case, connection)


@pytest.mark.parametrize("accept", [True, False], ids=["accepted", "refused"])
def test_import_majic_wrong_departement(accept: bool, fixtures: Path):
    """ The departement found in MAJIC files is different from the one given. """
    remove_schema()
    metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
    connection = metadata.findConnection("test_database")
    connection.createSchema(TEST_SCHEMA)

    options = import_options(CornillonMajic, fixtures)
    options.edigeo_source_dir = ""
    options.departement = "14"

    questions = []

    def confirm(question: str) -> bool:
        questions.append(question)
        return accept

    assert cadastreImport(options, CadastreFeedback(), confirm).run() is accept
    assert len(questions) == 1
    if accept:
        assert options.departement == CornillonMajic.dept
        results = connection.executeSql('SELECT ccodep FROM cadastre.commune_majic;')
        assert results == [[CornillonMajic.dept]]


def test_import_majic_path_with_spaces(fixtures: Path, tmp_path: Path):
    """ The TOPO file is imported with ogr2ogr, the spaces of its path must be kept """
    remove_schema()
    metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
    metadata.findConnection("test_database").createSchema(TEST_SCHEMA)

    majic_dir = tmp_path / "Fichiers MAJIC 2026" / "13029"
    shutil.copytree(fixtures.joinpath("majic", "13029"), majic_dir)
    options = import_options(CornillonMajic, fixtures)
    options.majic_source_dir = str(majic_dir)
    options.edigeo_source_dir = ""

    assert cadastreImport(options, CadastreFeedback()).run()

    connection = metadata.findConnection("test_database")
    assert connection.executeSql(f"SELECT libvoi FROM {TEST_SCHEMA}.voie WHERE ccoriv = '0870'") == [["DE CAMPREOUX"]]


def test_import_edigeo_bz2_in_zip(fixtures: Path, tmp_path: Path):
    """ The .tar.bz2 files are only in a zip file of the source folder, not in the folder (issue #588) """
    remove_schema()
    metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
    metadata.findConnection("test_database").createSchema(TEST_SCHEMA)

    edigeo_dir = tmp_path / "edigeo"
    edigeo_dir.mkdir()
    with zipfile.ZipFile(edigeo_dir / "feuilles.zip", "w") as archive:
        for sheet in fixtures.joinpath("edigeo", CornillonSansMajic.insee).glob("*.tar.bz2"):
            archive.write(sheet, sheet.name)
    options = import_options(CornillonSansMajic, fixtures)
    options.edigeo_source_dir = str(edigeo_dir)

    assert cadastreImport(options, CadastreFeedback()).run()
    check_imported_data(CornillonSansMajic, metadata.findConnection("test_database"))


def import_options(test_case: TestCase, fixtures: Path) -> ImportOptions:
    return ImportOptions(
        database=CadastreDatabase.from_connection("postgis", "test_database", TEST_SCHEMA),
        data_version=test_case.version,
        data_year=test_case.year,
        lot=test_case.lot,
        departement=test_case.dept,
        direction=test_case.direction,
        majic_source_dir=str(fixtures.joinpath('majic', test_case.insee)) if test_case.has_majic else "",
        edigeo_source_dir=str(fixtures.joinpath('edigeo', test_case.insee)),
        edigeo_source_proj=test_case.epsg,
        edigeo_target_proj=test_case.epsg,
    )


def check_imported_data(test_case: TestCase, connection):
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
