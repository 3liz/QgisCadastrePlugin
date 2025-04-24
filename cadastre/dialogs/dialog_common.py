__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import os.path
import re
import unicodedata

from collections import namedtuple
from pathlib import Path

from db_manager.db_plugins import createDbPlugin
from db_manager.db_plugins.plugin import BaseError
from db_manager.dlg_db_error import DlgDbError
from qgis.core import QgsMapLayer, QgsProject, QgsSettings
from qgis.PyQt.QtCore import QFileInfo, Qt
from qgis.PyQt.QtGui import QTextCursor
from qgis.PyQt.QtWidgets import QApplication, QFileDialog

import cadastre.cadastre_common_base as common_utils


class CadastreCommon:

    """ Import data from EDIGEO and MAJIC files. """

    def __init__(self, dialog):

        self.dialog = dialog

        # plugin directory path
        self.plugin_dir = str(Path(__file__).resolve().parent.parent)

        # default auth id for layers
        self.defaultAuthId = '2154'

    # Bind as class properties for compatibility
    hasSpatialiteSupport = common_utils.hasSpatialiteSupport
    openFile = common_utils.openFile

    def updateLog(self, msg):
        """
        Update the log
        """
        if os.getenv("CI", "").lower() == 'true':
            # Running headless, hack to see logs
            print(msg)
            return

        t = self.dialog.txtLog
        t.ensureCursorVisible()
        prefix = '<span style="font-weight:normal;">'
        suffix = '</span>'
        t.append(f'{prefix} {msg} {suffix}')
        c = t.textCursor()
        c.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.MoveAnchor)
        t.setTextCursor(c)
        QApplication.instance().processEvents()

    def updateProgressBar(self):
        """
        Update the progress bar
        """
        if self.dialog.go:
            self.dialog.step += 1
            self.dialog.pbProcess.setValue(int(self.dialog.step * 100 / self.dialog.totalSteps))
            QApplication.instance().processEvents()

    def load_default_values(self):
        """ Try to load values in the UI which are stored in QGIS settings.

        The function will return as soon as it is missing a value in the QGIS Settings.
        The order is DB Type, connection name and then the schema.
        """
        settings = QgsSettings()
        WidgetSettings = namedtuple('WidgetSettings', ('ui', 'settings'))
        widgets = [
            WidgetSettings('liDbType', 'databaseType'),
            WidgetSettings('liDbConnection', 'connection'),
            WidgetSettings('liDbSchema', 'schema'),
        ]
        # Default to PostGIS ticket #302
        is_postgis = settings.value("cadastre/databaseType", type=str, defaultValue='postgis') == 'postgis'
        for widget in widgets:
            # Widgets are ordered by hierarchy, so we quit the loop as soon as a value is not correct
            if widget.settings == 'schema' and not is_postgis:
                return

            if not hasattr(self.dialog, widget.ui):
                return

            value = settings.value("cadastre/" + widget.settings, type=str, defaultValue='')
            if not value:
                return

            combo = getattr(self.dialog, widget.ui)
            index = combo.findText(value, Qt.MatchFlag.MatchFixedString)
            if not index:
                return

            combo.setCurrentIndex(index)

    def updateConnectionList(self):
        """
        Update the combo box containing the database connection list
        """
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        dbType = str(self.dialog.liDbType.currentText()).lower()
        self.dialog.liDbConnection.clear()

        if self.dialog.liDbType.currentIndex() != 0:
            self.dialog.dbType = dbType
            # instance of db_manager plugin class
            dbpluginclass = createDbPlugin(dbType)
            self.dialog.dbpluginclass = dbpluginclass

            # fill the connections combobox
            self.dialog.connectionDbList = []
            for c in dbpluginclass.connections():
                self.dialog.liDbConnection.addItem(str(c.connectionName()))
                self.dialog.connectionDbList.append(str(c.connectionName()))

            # Show/Hide database specific pannel
            if hasattr(self.dialog, 'databaseSpecificOptions'):
                if dbType == 'postgis':
                    self.dialog.databaseSpecificOptions.setCurrentIndex(0)
                else:
                    self.dialog.databaseSpecificOptions.setCurrentIndex(1)
                    self.toggleSchemaList(False)
        else:
            if hasattr(self.dialog, "inDbCreateSchema"):
                self.dialog.databaseSpecificOptions.setTabEnabled(0, False)
                self.dialog.databaseSpecificOptions.setTabEnabled(1, False)

        QApplication.restoreOverrideCursor()

    def toggleSchemaList(self, t):
        """
        Toggle Schema list and inputs
        """
        self.dialog.liDbSchema.setEnabled(t)
        if hasattr(self.dialog, "inDbCreateSchema"):
            self.dialog.inDbCreateSchema.setEnabled(t)
            self.dialog.btDbCreateSchema.setEnabled(t)
            self.dialog.databaseSpecificOptions.setTabEnabled(0, t)
            self.dialog.databaseSpecificOptions.setTabEnabled(1, not t)
            self.dialog.btCreateNewSpatialiteDb.setEnabled(not t)

    def updateSchemaList(self):
        """
        Update the combo box containing the schema list if relevant
        """
        self.dialog.liDbSchema.clear()

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        connectionName = str(self.dialog.liDbConnection.currentText())
        self.dialog.connectionName = connectionName
        dbType = str(self.dialog.liDbType.currentText()).lower()

        # Deactivate schema fields
        self.toggleSchemaList(False)

        connection = None
        if connectionName:
            # Get schema list
            dbpluginclass = createDbPlugin(dbType, connectionName)
            self.dialog.dbpluginclass = dbpluginclass

            try:
                connection = dbpluginclass.connect()
            except BaseError as e:

                DlgDbError.showError(e, self.dialog)
                self.dialog.go = False
                self.updateLog(e.msg)
                QApplication.restoreOverrideCursor()
                return
            except:
                self.dialog.go = False
                msg = "Impossible de récupérer les schémas de la base. Vérifier les informations de connexion."
                self.updateLog(msg)
                QApplication.restoreOverrideCursor()
                return
            finally:
                QApplication.restoreOverrideCursor()

        if connection:
            self.dialog.connection = connection
            db = dbpluginclass.database()
            if db:
                self.dialog.db = db
                self.dialog.schemaList = []

            if dbType == 'postgis':
                # Activate schema fields
                self.toggleSchemaList(True)
                for s in db.schemas():
                    self.dialog.liDbSchema.addItem(str(s.name))
                    self.dialog.schemaList.append(str(s.name))
            else:
                self.toggleSchemaList(False)
        else:
            self.toggleSchemaList(False)

        QApplication.restoreOverrideCursor()

    def check_database_for_existing_structure(self):
        """
        Search among a database / schema
        if there are already Cadastre structure tables
        in it
        """
        has_structure = False
        has_data = False
        has_majic_data = False
        has_majic_data_prop = False
        has_majic_data_parcelle = False
        has_majic_data_voie = False

        search_table = 'geo_commune'
        majic_table_parcelle = 'parcelle'
        majic_table_prop = 'proprietaire'
        majic_table_voie = 'voie'
        if self.dialog.db:
            if self.dialog.dbType == 'postgis':
                schema_search = [s for s in self.dialog.db.schemas() if s.name == self.dialog.schema]
                schema_inst = schema_search[0]
                get_search_table = [a for a in self.dialog.db.tables(schema_inst) if a.name == search_table]
            else:
                get_search_table = [a for a in self.dialog.db.tables() if a.name == search_table]

            if get_search_table:
                has_structure = True

                # Check for data in it
                sql = f'SELECT * FROM "{search_table}" LIMIT 1'
                if self.dialog.dbType == 'postgis':
                    sql = f'SELECT * FROM "{self.dialog.schema}"."{search_table}" LIMIT 1'
                data, row_count, ok = CadastreCommon.fetchDataFromSqlQuery(self.dialog.db.connector, sql)
                if ok and row_count >= 1:
                    has_data = True

                # Check for Majic data in it
                sql = f'SELECT * FROM "{majic_table_parcelle}" LIMIT 1'
                if self.dialog.dbType == 'postgis':
                    sql = f'SELECT * FROM "{self.dialog.schema}"."{majic_table_parcelle}" LIMIT 1'
                data, row_count, ok = CadastreCommon.fetchDataFromSqlQuery(self.dialog.db.connector, sql)
                if ok and row_count >= 1:
                    has_majic_data = True
                    has_majic_data_parcelle = True

                # Check for Majic data in it
                sql = f'SELECT * FROM "{majic_table_prop}" LIMIT 1'
                if self.dialog.dbType == 'postgis':
                    sql = f'SELECT * FROM "{self.dialog.schema}"."{majic_table_prop}" LIMIT 1'
                data, row_count, ok = CadastreCommon.fetchDataFromSqlQuery(self.dialog.db.connector, sql)
                if ok and row_count >= 1:
                    has_majic_data = True
                    has_majic_data_prop = True

                # Check for Majic data in it
                sql = f'SELECT * FROM "{majic_table_voie}" LIMIT 1'
                if self.dialog.dbType == 'postgis':
                    sql = f'SELECT * FROM "{self.dialog.schema}"."{majic_table_voie}" LIMIT 1'
                data, row_count, ok = CadastreCommon.fetchDataFromSqlQuery(self.dialog.db.connector, sql)
                if ok and row_count >= 1:
                    has_majic_data = True
                    has_majic_data_voie = True

        # Set global properties
        self.dialog.hasStructure = has_structure
        self.dialog.hasData = has_data
        self.dialog.hasMajicData = has_majic_data
        self.dialog.hasMajicDataParcelle = has_majic_data_parcelle
        self.dialog.hasMajicDataProp = has_majic_data_prop
        self.dialog.hasMajicDataVoie = has_majic_data_voie

    def checkDatabaseForExistingTable(self, tableName, schemaName=''):
        """
        Check if the given table
        exists in the database
        """
        tableExists = False

        if not self.dialog.db:
            return False

        if self.dialog.dbType == 'postgis':
            sql = "SELECT * FROM information_schema.tables WHERE table_schema = '{}' AND table_name = '{}'".format(
            schemaName, tableName)

        if self.dialog.dbType == 'spatialite':
            sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % tableName

        data, rowCount, ok = CadastreCommon.fetchDataFromSqlQuery(self.dialog.db.connector, sql)
        if ok and rowCount >= 1:
            tableExists = True

        return tableExists

    # Bind as class properties for compatibility
    def getLayerFromLegendByTableProps(*args, **kwargs) -> QgsMapLayer:
        return common_utils.getLayerFromLegendByTableProps(QgsProject.instance(), *args, **kwargs)

    getConnectionParameterFromDbLayer = common_utils.getConnectionParameterFromDbLayer
    setSearchPath = common_utils.setSearchPath
    fetchDataFromSqlQuery = common_utils.fetchDataFromSqlQuery
    getConnectorFromUri = common_utils.getConnectorFromUri

    def normalizeString(self, s):
        """
        Removes all accents from
        the given string and
        replace e dans l'o
        """
        p = re.compile('(œ)')
        s = p.sub('oe', s)

        s = unicodedata.normalize('NFD', s)
        s = s.encode('ascii', 'ignore')
        s = s.upper()
        s = s.decode().strip(' \t\n')
        r = re.compile(r"[^ -~]")
        s = r.sub(' ', s)
        s = s.replace("'", " ")

        return s

    # Bind as class properties for compatibility
    postgisToSpatialite = common_utils.postgisToSpatialite
    postgisToSpatialiteLocal10 = common_utils.postgisToSpatialiteLocal10

    def createNewSpatialiteDatabase(self):
        """
        Choose a file path to save
        create the sqlite database with
        spatial tools and create QGIS connection
        """
        # Let the user choose new file path
        ipath, __ = QFileDialog.getSaveFileName(
            None,
            "Choisir l'emplacement du nouveau fichier",
            str(os.path.expanduser("~").encode('utf-8')).strip(' \t'),
            "Sqlite database (*.sqlite)"
        )
        if not ipath:
            self.updateLog("Aucune base de données créée (annulation)")
            return None

        # Delete file if exists (question already asked above)
        if os.path.exists(str(ipath)):
            os.remove(str(ipath))

        # Create the spatialite database
        try:
            # Create a connection (which will create the file automatically)
            from qgis.utils import spatialite_connect
            con = spatialite_connect(str(ipath), isolation_level=None)
            cur = con.cursor()
            sql = "SELECT InitSpatialMetadata(1)"
            cur.execute(sql)
            con.close()
            del con
        except:
            self.updateLog("Échec lors de la création du fichier Spatialite !")
            return None

        # Create QGIS connexion
        baseKey = "/SpatiaLite/connections/"
        settings = QgsSettings()
        myName = os.path.basename(ipath)
        baseKey += myName
        myFi = QFileInfo(ipath)
        settings.setValue(baseKey + "/sqlitepath", myFi.canonicalFilePath())

        # Update connections combo box and set new db selected
        self.updateConnectionList()
        listDic = {self.dialog.connectionDbList[i]: i for i in range(0, len(self.dialog.connectionDbList))}
        self.dialog.liDbConnection.setCurrentIndex(listDic[myName])

    # Bind as class properties for compatibility
    getCompteCommunalFromParcelleId = common_utils.getCompteCommunalFromParcelleId
    getProprietaireComptesCommunaux = common_utils.getProprietaireComptesCommunaux
    getItemHtml = common_utils.getItemHtml
