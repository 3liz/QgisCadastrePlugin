import unittest

from collections import namedtuple

from qgis.core import QgsCoordinateReferenceSystem, QgsProviderRegistry
from qgis.utils import iface

from cadastre.dialogs.import_dialog import CadastreImportDialog
from cadastre.tools import plugin_test_data_path


class TestCase(namedtuple('TestCase', [
        'insee', 'lot', 'dept', 'commune', 'epsg', 'has_majic', 'direction', 'version', 'year', 'geo_commune',
        'ccodir', 'ccocom',
])):
    """ Test case for import. """
    pass


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
    version='2019',
    year='2019',
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
    version='2019',
    year='2019',
    geo_commune='132029',
)

TEST_SCHEMA = 'cadastre'


class TestImportData(unittest.TestCase):

    def setUp(self) -> None:
        self._remove_schema()

    def tearDown(self) -> None:
        self._remove_schema()

    def _remove_schema(self):
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection = metadata.findConnection("test_database")
        connection: QgsAbstractDatabaseProviderConnection
        if TEST_SCHEMA in connection.schemas():
            connection.dropSchema(TEST_SCHEMA, True)

    def test_import(self):
        """Test to import data into a PostgreSQL database. """
        for test_case in (CornillonMajic, CornillonSansMajic):
            with self.subTest(i=test_case.commune):
                self._test_import(test_case)

    def _test_import(self, test_case):
        """ Internal function for the import. """
        self._remove_schema()

        # Not the best test, it's using the UI QDialog and iface
        dialog = CadastreImportDialog(iface)

        # Set postgis
        dialog.liDbType.setCurrentIndex(1)

        # Let the default connexion
        self.assertEqual(dialog.liDbConnection.count(), 1)

        # Check empty database before
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection = metadata.findConnection("test_database")
        self.assertNotIn(TEST_SCHEMA, connection.schemas())

        # Create schema
        dialog.inDbCreateSchema.setText(TEST_SCHEMA)
        dialog.btDbCreateSchema.click()

        # Check the schema exists
        self.assertIn(TEST_SCHEMA, connection.schemas())

        # Set the path for edigeo
        dialog.inEdigeoSourceDir.setText(str(plugin_test_data_path('edigeo', test_case.insee)))

        # Set CRS
        crs = QgsCoordinateReferenceSystem(test_case.epsg)
        dialog.inEdigeoSourceProj.setCrs(crs)
        dialog.inEdigeoTargetProj.setCrs(crs)

        # Set MAJIC
        if test_case.has_majic:
            dialog.inMajicSourceDir.setText(str(plugin_test_data_path('majic', test_case.insee)))
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
        self.assertTrue(dialog.processImport())

        # Check we have a town in edigeo
        results = connection.executeSql('SELECT "geo_commune", "tex2" FROM cadastre.geo_commune;')
        self.assertEqual(1, len(results))
        row = results[0]
        self.assertEqual(test_case.geo_commune, row[0])
        self.assertEqual(test_case.commune, row[1])

        # Check we have a town in majic
        if test_case.has_majic:
            results = connection.executeSql('SELECT * FROM cadastre.commune_majic;')
            self.assertEqual(1, len(results))
            row = results[0]
            self.assertEqual(test_case.geo_commune, row[0])  # commune
            self.assertEqual(test_case.year, row[1])  # annee
            self.assertEqual(test_case.dept, row[2])  # ccodep
            self.assertEqual(test_case.ccodir, row[3])  # ccodir
            self.assertEqual(test_case.ccocom, row[4])  # ccocom
            self.assertEqual(test_case.commune, row[5])  # libcom
            self.assertEqual(test_case.lot, row[6])  # lot
