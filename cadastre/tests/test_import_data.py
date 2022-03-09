import unittest

import psycopg2

from qgis.core import QgsCoordinateReferenceSystem, QgsProviderRegistry
from qgis.utils import iface

from cadastre.dialogs.import_dialog import CadastreImportDialog
from cadastre.tools import plugin_test_data_path


class TestImportData(unittest.TestCase):

    def test_import(self):
        """Test to import data into a PostgreSQL database. """
        # Not the best test, it's using the UI QDialog and iface
        dialog = CadastreImportDialog(iface)
        schema = "cadastre"

        # Set postgis
        dialog.liDbType.setCurrentIndex(1)

        # Let the default connexion
        self.assertEqual(dialog.liDbConnection.count(), 1)

        # Check empty database before
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection = metadata.findConnection("test_database")
        connection: QgsAbstractDatabaseProviderConnection
        if schema in connection.schemas():
            connection.dropSchema(schema, True)
        self.assertNotIn(schema, connection.schemas())

        # Create schema
        dialog.inDbCreateSchema.setText(schema)
        dialog.btDbCreateSchema.click()

        # Check the schema exists
        self.assertIn(schema, connection.schemas())

        # Set the path for edigeo
        dialog.inEdigeoSourceDir.setText(str(plugin_test_data_path('edigeo', '13029')))

        # Set CRS
        crs = QgsCoordinateReferenceSystem("EPSG:2154")
        dialog.inEdigeoSourceProj.setCrs(crs)
        dialog.inEdigeoTargetProj.setCrs(crs)

        # Set MAJIC
        dialog.inMajicSourceDir.setText(str(plugin_test_data_path('majic', '13029')))

        # Set lot
        dialog.inEdigeoLot.setText('1')

        # Set departement
        dialog.inEdigeoDepartement.setText('13')

        # Set direction
        dialog.inEdigeoDirection.setValue(2)

        # Version
        dialog.inDataVersion.setValue(2019)

        # Year
        dialog.inDataYear.setValue(2019)

        # Import
        dialog.btProcessImport.click()

        # Check we have a town in edigeo
        results = connection.executeSql('SELECT "geo_commune", "tex2" FROM cadastre.geo_commune;')
        self.assertEqual(1, len(results))
        row = results[0]
        self.assertEqual("132029", row[0])
        self.assertEqual("CORNILLON-CONFOUX", row[1])

        # Check we have a town in majic
        results = connection.executeSql('SELECT * FROM cadastre.commune_majic;')
        self.assertEqual(1, len(results))
        row = results[0]
        self.assertEqual("132029", row[0])  # commune
        self.assertEqual("2019", row[1])  # annee
        self.assertEqual("13", row[2])  # ccodep
        self.assertEqual("2", row[3])  # ccodir
        self.assertEqual("029", row[4])  # ccocom
        self.assertEqual("CORNILLON-CONFOUX", row[5])  # libcom
        self.assertEqual("1", row[6])  # lot
