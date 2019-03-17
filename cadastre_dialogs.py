"""
Cadastre - Dialog classes

This plugins helps users to import the french land registry ('cadastre')
into a database. It is meant to ease the use of the data in QGIs
by providing search tools and appropriate layer symbology.

begin     : 2013-06-11
copyright : (C) 2013,2019 by 3liz
email     : info@3liz.com
 
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

"""
import csv
import os.path
import operator
import re
import tempfile
from qgis.PyQt.QtCore import (
    Qt,
    pyqtSignal,
    QObject,
    QSettings,
    QRegExp,
    QFileInfo,
    QStringListModel
)
from qgis.PyQt.QtWidgets import (
    QDialog,
    QFileDialog,
    QApplication,
    qApp,
    QCompleter,
    QDockWidget,
    QMessageBox
)
from qgis.PyQt.QtGui import (
    QCursor,
    QTextCursor,
    QPixmap
)
from qgis.PyQt.QtCore import QSortFilterProxyModel
from qgis.core import (
    QgsProject,
    QgsMessageLog,
    QgsLogger,
    QgsExpression,
    QgsDataSourceUri,
    QgsMapLayer,
    QgsFeatureRequest,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsMapSettings
)
from qgis.gui import (
    QgsProjectionSelectionTreeWidget,
    QgsProjectionSelectionDialog
)
import unicodedata

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

# db_manager scripts
from db_manager.db_plugins.plugin import (
    DBPlugin,
    Schema,
    Table,
    BaseError
)
from db_manager.db_plugins import createDbPlugin
from db_manager.dlg_db_error import DlgDbError
from db_manager.db_plugins.postgis.connector import PostGisDBConnector
import subprocess

from functools import partial

# --------------------------------------------------------
#        import - Import data from EDIGEO and MAJIC files
# --------------------------------------------------------

import time
# Fonction qui permet de calculer le temps passé par une méthode
# Pour l'activer, ajouter simplement le décorateur @timing sur la méthode.
def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('{:s} function took {:.3f} ms'.format(f.__name__, (time2-time1)*1000.0))

        return ret
    return wrap


import cadastre.cadastre_common_base as common_utils


class cadastre_common(object):

    def __init__(self, dialog):

        self.dialog = dialog

        # plugin directory path
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))

        # default auth id for layers
        self.defaultAuthId = '2154'

    # Bind as class propertis for compatibility
    hasSpatialiteSupport = common_utils.hasSpatialiteSupport
    openFile = common_utils.openFile

    def updateLog(self, msg):
        '''
        Update the log
        '''
        t = self.dialog.txtLog
        t.ensureCursorVisible()
        prefix = '<span style="font-weight:normal;">'
        suffix = '</span>'
        t.append( '%s %s %s' % (prefix, msg, suffix) )
        c = t.textCursor()
        c.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        t.setTextCursor(c)
        qApp.processEvents()

    def updateProgressBar(self):
        '''
        Update the progress bar
        '''
        if self.dialog.go:
            self.dialog.step+=1
            self.dialog.pbProcess.setValue(int(self.dialog.step * 100/self.dialog.totalSteps))
            qApp.processEvents()

    def updateConnectionList(self):
        '''
        Update the combo box containing the database connection list
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)

        dbType = str(self.dialog.liDbType.currentText()).lower()
        self.dialog.liDbConnection.clear()

        if self.dialog.liDbType.currentIndex() != 0:
            self.dialog.dbType = dbType
            # instance of db_manager plugin class
            dbpluginclass = createDbPlugin( dbType )
            self.dialog.dbpluginclass = dbpluginclass

            # fill the connections combobox
            self.dialog.connectionDbList = []
            for c in dbpluginclass.connections():
                self.dialog.liDbConnection.addItem( str(c.connectionName()))
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
        '''
        Toggle Schema list and inputs
        '''
        self.dialog.liDbSchema.setEnabled(t)
        if hasattr(self.dialog, "inDbCreateSchema"):
            self.dialog.inDbCreateSchema.setEnabled(t)
            self.dialog.btDbCreateSchema.setEnabled(t)
            self.dialog.databaseSpecificOptions.setTabEnabled(0, t)
            self.dialog.databaseSpecificOptions.setTabEnabled(1, not t)
            self.dialog.btCreateNewSpatialiteDb.setEnabled(not t)


    def updateSchemaList(self):
        '''
        Update the combo box containing the schema list if relevant
        '''
        self.dialog.liDbSchema.clear()

        QApplication.setOverrideCursor(Qt.WaitCursor)
        connectionName = str(self.dialog.liDbConnection.currentText())
        self.dialog.connectionName = connectionName
        dbType = str(self.dialog.liDbType.currentText()).lower()

        # Deactivate schema fields
        self.toggleSchemaList(False)

        connection = None
        if connectionName:
            # Get schema list
            dbpluginclass = createDbPlugin( dbType, connectionName )
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
                msg = u"Impossible de récupérer les schémas de la base. Vérifier les informations de connexion."
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
                    self.dialog.liDbSchema.addItem( str(s.name))
                    self.dialog.schemaList.append(str(s.name))
            else:
                self.toggleSchemaList(False)
        else:
            self.toggleSchemaList(False)

        QApplication.restoreOverrideCursor()

    def checkDatabaseForExistingStructure(self):
        '''
        Search among a database / schema
        if there are alreaday Cadastre structure tables
        in it
        '''
        hasStructure = False
        hasData = False
        hasMajicData = False
        hasMajicDataProp = False
        hasMajicDataParcelle = False
        hasMajicDataVoie = False

        searchTable = u'geo_commune'
        majicTableParcelle = u'parcelle'
        majicTableProp = u'proprietaire'
        majicTableVoie = u'voie'
        if self.dialog.db:
            if self.dialog.dbType == 'postgis':
                schemaSearch = [s for s in self.dialog.db.schemas() if s.name == self.dialog.schema]
                schemaInst = schemaSearch[0]
                getSearchTable = [a for a in self.dialog.db.tables(schemaInst) if a.name == searchTable]
            if self.dialog.dbType == 'spatialite':
                getSearchTable = [a for a in self.dialog.db.tables() if a.name == searchTable]
            if getSearchTable:
                hasStructure = True

                # Check for data in it
                sql = 'SELECT * FROM "%s" LIMIT 1' % searchTable
                if self.dialog.dbType == 'postgis':
                    sql = cadastre_common.setSearchPath(sql, self.dialog.schema)
                [header, data, rowCount, ok] = cadastre_common.fetchDataFromSqlQuery(self.dialog.db.connector, sql)
                if ok and rowCount >= 1:
                    hasData = True

                # Check for Majic data in it
                sql = 'SELECT * FROM "%s" LIMIT 1' % majicTableParcelle
                if self.dialog.dbType == 'postgis':
                    sql = cadastre_common.setSearchPath(sql, self.dialog.schema)
                [header, data, rowCount, ok] = cadastre_common.fetchDataFromSqlQuery(self.dialog.db.connector, sql)
                if ok and rowCount >= 1:
                    hasMajicData = True
                    hasMajicDataParcelle = True

                # Check for Majic data in it
                sql = 'SELECT * FROM "%s" LIMIT 1' % majicTableProp
                if self.dialog.dbType == 'postgis':
                    sql = cadastre_common.setSearchPath(sql, self.dialog.schema)
                [header, data, rowCount, ok] = cadastre_common.fetchDataFromSqlQuery(self.dialog.db.connector, sql)
                if ok and rowCount >= 1:
                    hasMajicData = True
                    hasMajicDataProp = True

                # Check for Majic data in it
                sql = 'SELECT * FROM "%s" LIMIT 1' % majicTableVoie
                if self.dialog.dbType == 'postgis':
                    sql = cadastre_common.setSearchPath(sql, self.dialog.schema)
                [header, data, rowCount, ok] = cadastre_common.fetchDataFromSqlQuery(self.dialog.db.connector, sql)
                if ok and rowCount >= 1:
                    hasMajicData = True
                    hasMajicDataVoie = True

        # Set global properties
        self.dialog.hasStructure = hasStructure
        self.dialog.hasData = hasData
        self.dialog.hasMajicData = hasMajicData
        self.dialog.hasMajicDataParcelle = hasMajicDataParcelle
        self.dialog.hasMajicDataProp = hasMajicDataProp
        self.dialog.hasMajicData = hasMajicDataVoie


    def checkDatabaseForExistingTable(self, tableName, schemaName=''):
        '''
        Check if the given table
        exists in the database
        '''
        tableExists = False

        if not self.dialog.db:
            return False

        if self.dialog.dbType == 'postgis':
            sql = "SELECT * FROM information_schema.tables WHERE table_schema = '%s' AND table_name = '%s'" % (schemaName, tableName)

        if self.dialog.dbType == 'spatialite':
            sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % tableName

        [header, data, rowCount, ok] = cadastre_common.fetchDataFromSqlQuery(self.dialog.db.connector, sql)
        if ok and rowCount >= 1:
            tableExists = True

        return tableExists

    # Bind as class properties for compatibility
    getLayerFromLegendByTableProps    = common_utils.getLayerFromLegendByTableProps
    getConnectionParameterFromDbLayer = common_utils.getConnectionParameterFromDbLayer
    setSearchPath = common_utils.setSearchPath
    fetchDataFromSqlQuery = common_utils.fetchDataFromSqlQuery
    getConnectorFromUri = common_utils.getConnectorFromUri

    def normalizeString(self, s):
        '''
        Removes all accents from
        the given string and
        replace e dans l'o
        '''
        p = re.compile( '(œ)')
        s = p.sub('oe', s)

        s=unicodedata.normalize('NFD',s)
        s = s.encode('ascii','ignore')
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
        '''
        Choose a file path to save
        create the sqlite database with
        spatial tools and create QGIS connection
        '''
        # Let the user choose new file path
        ipath, __ = QFileDialog.getSaveFileName (
            None,
            u"Choisir l'emplacement du nouveau fichier",
            str(os.path.expanduser("~").encode('utf-8')).strip(' \t'),
            "Sqlite database (*.sqlite)"
        )
        if not ipath:
            self.updateLog(u"Aucune base de données créée (annulation)")
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
            self.updateLog(u"Échec lors de la création du fichier Spatialite !")
            return None

        # Create QGIS connexion
        baseKey = "/SpatiaLite/connections/"
        settings = QSettings()
        myName = os.path.basename(ipath);
        baseKey+= myName;
        myFi = QFileInfo(ipath)
        settings.setValue( baseKey + "/sqlitepath", myFi.canonicalFilePath());

        # Update connections combo box and set new db selected
        self.updateConnectionList()
        listDic = { self.dialog.connectionDbList[i]:i for i in range(0, len(self.dialog.connectionDbList)) }
        self.dialog.liDbConnection.setCurrentIndex(listDic[myName])


    # Bind as class properties for compatibility
    getCompteCommunalFromParcelleId = common_utils.getCompteCommunalFromParcelleId
    getProprietaireComptesCommunaux = common_utils.getProprietaireComptesCommunaux
    getItemHtml = common_utils.getItemHtml


from .cadastre_import import cadastreImport
from qgis.PyQt import uic
IMPORT_FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        os.path.dirname(__file__),
        'forms/cadastre_import_form.ui'
    )
)
class cadastre_import_dialog(QDialog, IMPORT_FORM_CLASS):
    def __init__(self, iface, parent=None):
        self.iface = iface
        super(cadastre_import_dialog, self).__init__(parent)
        self.setupUi(self)

        self.connectionDbList = []
        # common cadastre methods
        from .cadastre_dialogs import cadastre_common
        self.qc = cadastre_common(self)

        # first disable database specifi tabs
        self.databaseSpecificOptions.setTabEnabled(0, False)
        self.databaseSpecificOptions.setTabEnabled(1, False)

        # spatialite support
        self.hasSpatialiteSupport = cadastre_common.hasSpatialiteSupport()
        if not self.hasSpatialiteSupport:
            self.liDbType.removeItem(2)
            self.databaseSpecificOptions.setTabEnabled(1, False)
            self.btCreateNewSpatialiteDb.setEnabled(False)


        # Signals/Slot Connections
        self.liDbType.currentIndexChanged[str].connect(self.qc.updateConnectionList)
        self.liDbConnection.currentIndexChanged[str].connect(self.qc.updateSchemaList)
        self.btDbCreateSchema.clicked.connect(self.createSchema)
        self.btCreateNewSpatialiteDb.clicked.connect(self.qc.createNewSpatialiteDatabase)
        self.btProcessImport.clicked.connect(self.processImport)
        self.rejected.connect(self.onClose)
        self.buttonBox.rejected.connect(self.onClose)

        # path buttons selectors
        # paths needed to be chosen by user
        self.pathSelectors = {
            "edigeoSourceDir" : {
                "button" : self.btEdigeoSourceDir,
                "input" : self.inEdigeoSourceDir
            },
            "majicSourceDir" : {
                "button" : self.btMajicSourceDir,
                "input" : self.inMajicSourceDir
            }
        }
        for key, item in list(self.pathSelectors.items()):
            control = item['button']
            slot = partial(self.chooseDataPath, key)
            control.clicked.connect(slot)

        # Set initial values
        self.doMajicImport = False
        self.doEdigeoImport = False
        self.dataVersion = None
        self.dataYear = None
        self.dbType = None
        self.dbpluginclass = None
        self.connectionName = None
        self.connection = None
        self.db = None
        self.schema = None
        self.schemaList = None
        self.hasStructure = None
        self.hasData = None
        self.hasMajicData = None
        self.hasMajicDataParcelle = None
        self.hasMajicDataVoie = None
        self.hasMajicDataProp = None
        self.edigeoSourceProj = None
        self.edigeoTargetProj = None
        self.edigeoDepartement = None
        self.edigeoDirection = None
        self.edigeoLot = None
        self.majicSourceDir = None
        self.edigeoSourceDir = None
        self.edigeoMakeValid = False

        # set input values from settings
        self.sList = {
            'dataVersion': {
                'widget': self.inDataVersion,
                'wType': 'spinbox',
                'property': self.dataVersion
            },
            'dataYear': {
                'widget': self.inDataYear,
                'wType': 'spinbox',
                'property': self.dataYear
            } ,
            'schema': {
                'widget': None
            } ,
            'majicSourceDir': {
                'widget': self.inMajicSourceDir,
                'wType': 'text',
                'property': self.majicSourceDir
            },
            'edigeoSourceDir': {
                'widget': self.inEdigeoSourceDir,
                'wType': 'text',
                'property': self.edigeoSourceDir
            },
            'edigeoDepartement': {
                'widget': self.inEdigeoDepartement,
                'wType': 'text',
                'property': self.edigeoDepartement
            },
            'edigeoDirection': {
                'widget': self.inEdigeoDirection,
                'wType': 'spinbox',
                'property': self.edigeoDirection
            },
            'edigeoLot': {
                'widget': self.inEdigeoLot,
                'wType': 'text',
                'property': self.edigeoLot
            },
            'edigeoSourceProj': {
                'widget': self.inEdigeoSourceProj,
                'wType': 'crs',
                'property': self.edigeoSourceProj
            },
            'edigeoTargetProj': {
                'widget': self.inEdigeoTargetProj,
                'wType': 'crs',
                'property': self.edigeoTargetProj
            }
        }
        self.getValuesFromSettings()


    def onClose(self):
        '''
        Close dialog
        '''
        if self.db:
            self.db.connector.__del__()

        # Store settings
        msg = self.checkImportInputData()
        if not msg:
            self.storeSettings()

        self.close()


    def chooseDataPath(self, key):
        '''
        Ask the user to select a folder
        and write down the path to appropriate field
        '''
        ipath = QFileDialog.getExistingDirectory(
            None,
            u"Choisir le répertoire contenant les fichiers",
            str(self.pathSelectors[key]['input'].text().encode('utf-8')).strip(' \t')
        )
        if os.path.exists(str(ipath)):
            self.pathSelectors[key]['input'].setText(str(ipath))



    def getValuesFromSettings(self):
        '''
        get values from QGIS settings
        and set input fields appropriately
        '''
        s = QSettings()
        for k,v in list(self.sList.items()):
            value = s.value("cadastre/%s" % k, '', type=str)
            if value and value != 'None' and v['widget']:
                if v['wType'] == 'text':
                    v['widget'].setText(value)
                if v['wType'] == 'spinbox':
                    v['widget'].setValue(int(value))
                if v['wType'] == 'combobox':
                    listDic = {v['list'][i]:i for i in range(0, len(v['list']))}
                    v['widget'].setCurrentIndex(listDic[value])
                if v['wType'] == 'crs':
                    v['widget'].setCrs(QgsCoordinateReferenceSystem(value))


    def createSchema(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            if self.db == None:
                QMessageBox.warning(
                    self,
                    QApplication.translate("DBManagerPlugin", "Sorry"),
                    QApplication.translate("DBManagerPlugin", "No database selected or you are not connected to it.")
                )
                return
            schema = self.inDbCreateSchema.text()
        finally:
            QApplication.restoreOverrideCursor()

        if schema:
            try:
                self.db.createSchema(schema)

            except BaseError as e:

                DlgDbError.showError(e, self)
                self.qc.updateLog(e.msg)
                return

            finally:
                self.qc.updateSchemaList()
                listDic = { self.schemaList[i]:i for i in range(0, len(self.schemaList)) }
                self.liDbSchema.setCurrentIndex(listDic[schema])
                self.inDbCreateSchema.clear()
                QApplication.restoreOverrideCursor()

    def checkImportInputData(self):
        '''
        Check the user defined inpu data
        '''

        self.dataVersion = str(self.inDataVersion.text())
        self.dataYear = str(self.inDataYear.text())
        self.schema = str(self.liDbSchema.currentText())
        self.majicSourceDir = str(self.inMajicSourceDir.text()).strip(' \t')
        self.edigeoSourceDir = str(self.inEdigeoSourceDir.text()).strip(' \t')
        self.edigeoDepartement = str(self.inEdigeoDepartement.text()).strip(' \t')
        self.edigeoDirection = str(self.inEdigeoDirection.text()).strip(' \t')
        self.edigeoLot = str(self.inEdigeoLot.text()).strip(' \t')
        self.edigeoSourceProj = self.inEdigeoSourceProj.crs().authid()
        self.edigeoTargetProj = self.inEdigeoTargetProj.crs().authid()

        # defined properties
        self.doMajicImport = os.path.exists(self.majicSourceDir)
        self.doEdigeoImport =  os.path.exists(self.edigeoSourceDir)

        if self.cbMakeValid.isChecked():
            self.edigeoMakeValid = True

        msg = ''
        if not self.db:
            msg+= u'Veuillez sélectionner une base de données\n'

        if not self.doMajicImport and not self.doEdigeoImport:
            msg+= u'Veuillez sélectionner le chemin vers les fichiers à importer !\n'

        if self.edigeoSourceDir and not self.doEdigeoImport:
            msg+= u"Le chemin spécifié pour les fichiers EDIGEO n'existe pas\n"

        if self.majicSourceDir and not self.doMajicImport:
            msg+= u"Le chemin spécifié pour les fichiers MAJIC n'existe pas\n"

        if self.doEdigeoImport and not self.edigeoSourceProj:
            msg+= u'La projection source doit être renseignée !\n'
        if self.doEdigeoImport and not self.edigeoTargetProj:
            msg+= u'La projection cible doit être renseignée !\n'
        if len(self.edigeoDepartement) != 2 :
            msg+= u'Le département ne doit pas être vide !\n'
        if not self.edigeoDirection:
            msg+= u'La direction doit être un entier (0 par défaut) !\n'
        if not self.edigeoLot:
            msg+= u'Merci de renseigner un lot pour cet import (code commune, date d\'import, etc.)\n'

        self.qc.updateLog(msg.replace('\n','<br/>'))
        return msg

    def processImport(self):
        '''
        Lancement du processus d'import
        '''

        msg = self.checkImportInputData()
        if msg:
            QMessageBox.critical(self, u"Cadastre", msg)
            return

        # Store settings
        self.storeSettings()

        # cadastreImport instance
        qi = cadastreImport(self)

        # Check if structure already exists in the database/schema
        self.qc.checkDatabaseForExistingStructure()

        # Run Script for creating tables
        if not self.hasStructure:
            qi.installCadastreStructure()
        else:
            # Run update script which add some missing tables when needed
            qi.updateCadastreStructure()

        # Run MAJIC import
        if self.doMajicImport:
            qi.importMajic()

        # Run Edigeo import
        if self.doEdigeoImport:
                qi.importEdigeo()

        qi.endImport()


    def storeSettings(self):
        '''
        Store cadastre settings in QGIS
        '''
        # store chosen data in QGIS settings
        s = QSettings()
        s.setValue("cadastre/dataVersion", str(self.dataVersion))
        s.setValue("cadastre/dataYear", int(self.dataYear))
        s.setValue("cadastre/majicSourceDir", self.majicSourceDir)
        s.setValue("cadastre/edigeoSourceDir", self.edigeoSourceDir)
        s.setValue("cadastre/edigeoDepartement", str(self.edigeoDepartement))
        s.setValue("cadastre/edigeoDirection", int(self.edigeoDirection))
        s.setValue("cadastre/edigeoLot", str(self.edigeoLot))
        s.setValue("cadastre/edigeoSourceProj", str(self.edigeoSourceProj))
        s.setValue("cadastre/edigeoTargetProj", str(self.edigeoTargetProj))

# --------------------------------------------------------
#        load - Load data from database
# --------------------------------------------------------


from .cadastre_loading import cadastreLoading
from qgis.PyQt import uic
LOAD_FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        os.path.dirname(__file__),
        'forms/cadastre_load_form.ui'
    )
)
class cadastre_load_dialog(QDialog, LOAD_FORM_CLASS):
    def __init__(self, iface, cadastre_search_dialog, parent=None):
        super(cadastre_load_dialog, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)
        self.mc = self.iface.mapCanvas()

        self.cadastre_search_dialog = cadastre_search_dialog

        # common cadastre methods
        from .cadastre_dialogs import cadastre_common
        self.qc = cadastre_common(self)
        self.ql = cadastreLoading(self)

        # spatialite support
        self.hasSpatialiteSupport = cadastre_common.hasSpatialiteSupport()
        if not self.hasSpatialiteSupport:
            self.liDbType.removeItem(2)

        # Set initial values
        self.go = True
        self.step = 0
        self.totalSteps = 0
        self.dbType = None
        self.dbpluginclass = None
        self.connectionName = None
        self.connection = None
        self.db = None
        self.schema = None
        self.schemaList = None
        self.hasStructure = None

        # Get style list
        self.getStyleList()

        # Signals/Slot Connections
        self.liDbType.currentIndexChanged[str].connect(self.qc.updateConnectionList)
        self.liDbConnection.currentIndexChanged[str].connect(self.qc.updateSchemaList)
        self.btProcessLoading.clicked.connect(self.onProcessLoadingClicked)
        self.ql.cadastreLoadingFinished.connect(self.onLoadingEnd)

        self.btLoadSqlLayer.clicked.connect(self.onLoadSqlLayerClicked)

        self.rejected.connect(self.onClose)
        self.buttonBox.rejected.connect(self.onClose)

    def onClose(self):
        '''
        Close dialog
        '''
        if self.db:
            self.db.connector.__del__()
        self.close()


    def getStyleList(self):
        '''
        Get the list of style directories
        inside the plugin dir
        and add combobox item
        '''
        spath = os.path.join(self.qc.plugin_dir, "styles/")
        dirs = os.listdir(spath)
        dirs = [a for a in dirs if os.path.isdir(os.path.join(spath, a))]
        dirs.sort()
        cb = self.liTheme
        cb.clear()
        for d in dirs:
            cb.addItem('%s' % d, d)

    def onProcessLoadingClicked(self):
        '''
        Activate the loading of layers
        from database tables
        when user clicked on button
        '''
        if self.connection:
            if self.db:
                self.ql.processLoading()

    def onLoadSqlLayerClicked(self):
        '''
        Loads a layer
        from given SQL
        when user clicked on button
        '''
        if self.connection:
            if self.db:
                self.ql.loadSqlLayer()

    def onLoadingEnd(self):
        '''
        Actions to trigger
        when all the layers
        have been loaded
        '''
        self.cadastre_search_dialog.checkMajicContent()
        self.cadastre_search_dialog.clearComboboxes()
        self.cadastre_search_dialog.setupSearchCombobox('commune', None, 'sql')
        #self.cadastre_search_dialog.setupSearchCombobox('section', None, 'sql')



#Custom completer (to allow completion when string found anywhere
class CustomQCompleter(QCompleter):
    """
    adapted from: http://stackoverflow.com/a/7767999/2156909
    """
    def __init__(self, *args):#parent=None):
        super(CustomQCompleter, self).__init__(*args)
        self.local_completion_prefix = ""
        self.source_model = None
        self.filterProxyModel = QSortFilterProxyModel(self)
        self.usingOriginalModel = False

    def setModel(self, model):
        self.source_model = model
        self.filterProxyModel = QSortFilterProxyModel(self)
        self.filterProxyModel.setSourceModel(self.source_model)
        super(CustomQCompleter, self).setModel(self.filterProxyModel)
        self.usingOriginalModel = True

    def updateModel(self):
        if not self.usingOriginalModel:
            self.filterProxyModel.setSourceModel(self.source_model)

        pattern = QRegExp(self.local_completion_prefix,
                                Qt.CaseInsensitive
                                ,QRegExp.FixedString
                                )

        self.filterProxyModel.setFilterRegExp(pattern)

    def splitPath(self, path):
        self.local_completion_prefix = path
        self.updateModel()
        if self.filterProxyModel.rowCount() == 0:
            self.usingOriginalModel = False
            self.filterProxyModel.setSourceModel(QStringListModel([path]))
            return [path]

        return []

# ---------------------------------------------------------
#        search - search for data among database ans export
# ---------------------------------------------------------

from .cadastre_import import cadastreImport
from qgis.PyQt import uic
SEARCH_FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        os.path.dirname(__file__),
        'forms/cadastre_search_form.ui'
    )
)
class cadastre_search_dialog(QDockWidget, SEARCH_FORM_CLASS):
    def __init__(self, iface, parent=None):
        #QDockWidget.__init__(self)
        super(cadastre_search_dialog, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self)

        # common cadastre methods
        from .cadastre_dialogs import cadastre_common
        self.qc = cadastre_common(self)

        # database properties
        self.connectionParams = None
        self.connector = None
        self.dbType = None
        self.schema = None

        self.mc = self.iface.mapCanvas()
        self.communeLayer = None
        self.communeFeatures = None
        self.communeRequest = None
        self.selectedCommuneFeature = None
        self.sectionLayer = None
        self.sectionFeatures = None
        self.sectionRequest = None
        self.sectionCommuneFeature = None

        aLayer = cadastre_common.getLayerFromLegendByTableProps('geo_commune')
        if aLayer:
            self.connectionParams = cadastre_common.getConnectionParameterFromDbLayer(aLayer)
            self.connector = cadastre_common.getConnectorFromUri( self.connectionParams )

        # signals/slots
        self.searchComboBoxes = {
            'commune': {
                'widget': self.liCommune,
                'labelAttribute': 'tex2',
                'table': 'geo_commune',
                'geomCol': 'geom',
                'sql': '',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid','tex2','idu','geo_commune','geom', 'lot'],
                'orderBy': ['tex2'],
                'features': None,
                'chosenFeature': None,
                'resetWidget': self.btResetCommune,
                'children': [
                    {
                        'key': 'section',
                        'fkey': 'geo_commune',
                        'getIfNoFeature': True
                    }
                ]
            },
            'section': {
                'widget': self.liSection,
                'labelAttribute': 'idu',
                'table': 'geo_section',
                'geomCol': 'geom',
                'sql': '',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid','tex','idu','geo_commune','geo_section','geom','lot'],
                'orderBy': ['geo_section'],
                'features': None,
                'chosenFeature': None,
                'resetWidget': self.btResetSection,
                'children': [
                    {
                        'key': 'parcelle',
                        'fkey': 'geo_section',
                        'getIfNoFeature': False
                    }
                ]
            },
            'adresse': {
                'widget': self.liAdresse,
                'labelAttribute': 'voie',
                'table': 'parcelle_info',
                'layer': None,
                'geomCol': None,
                'sql': '',
                'request': None,
                'attributes': ['ogc_fid','voie','idu','geom'],
                'orderBy': ['voie'],
                'features': None,
                'chosenFeature': None,
                'resetWidget': self.btResetAdresse,
                'connector': None,
                'search': {
                    'parcelle_child': 'parcelle',
                    'minlen': 3
                },
                'children': [
                    {
                        'key': 'parcelle',
                        'fkey': 'voie',
                        'getIfNoFeature': False
                    }
                ]
            },
            'parcelle': {
                'widget': self.liParcelle,
                'labelAttribute': 'idu',
                'table': 'parcelle_info',
                'geomCol': 'geom',
                'sql': '',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid','tex','idu','geo_section','geom', 'comptecommunal', 'geo_parcelle'],
                'orderBy': ['geo_parcelle'],
                'features': None,
                'chosenFeature': None,
                'connector': None,
                'resetWidget': self.btResetParcelle
            },
            'proprietaire': {
                'widget': self.liProprietaire,
                'labelAttribute': 'idu',
                'table': 'parcelle_info',
                'layer': None,
                'request': None,
                'attributes': ['comptecommunal','idu','dnupro','geom'],
                'orderBy': ['ddenom'],
                'features': None,
                'id': None,
                'chosenFeature': None,
                'connector': None,
                'search': {
                    'parcelle_child': 'parcelle_proprietaire',
                    'minlen': 3
                },
                'resetWidget': self.btResetProprietaire,
            },
            'parcelle_proprietaire': {
                'widget': self.liParcelleProprietaire,
                'labelAttribute': 'idu',
                'table': 'parcelle_info',
                'geomCol': 'geom',
                'sql': '',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid','tex','idu','comptecommunal','geom', 'geo_parcelle'],
                'orderBy': ['geo_parcelle'],
                'features': None,
                'chosenFeature': None,
                'connector': None,
                'resetWidget': self.btResetParcelleProprietaire
            }
        }

        # Detect that the user has hidden/showed the dock
        self.visibilityChanged.connect(self.onVisibilityChange)

        # center/zoom/selection buttons
        self.zoomButtons = {
            'lieu':{
                'buttons':{
                    'centre': self.btCentrerLieu,
                    'zoom': self.btZoomerLieu,
                    'select': self.btSelectionnerLieu
                },
                'comboboxes': ['commune', 'section', 'adresse', 'parcelle']
            },
            'proprietaire':{
                'buttons':{
                    'centre': self.btCentrerProprietaire,
                    'zoom': self.btZoomerProprietaire,
                    'select': self.btSelectionnerProprietaire
                },
                'comboboxes': ['proprietaire', 'parcelle_proprietaire']
            }

        }
        zoomButtonsFunctions = {
            'centre': self.setCenterToChosenItem,
            'zoom': self.setZoomToChosenItem,
            'select': self.setSelectionToChosenItem
        }
        for key, item in list(self.zoomButtons.items()):
            for k, button in list(item['buttons'].items()):
                control = button
                slot = partial(zoomButtonsFunctions[k], key)
                control.clicked.connect(slot)

        # Manuel search button and combo (proprietaire, adresse)
        for key, item in list(self.searchComboBoxes.items()):
            # Combobox not prefilled (too much data proprietaires & adresse
            if 'search' in item:

                # when the user add some text : autocomplete
                # the search comboboxes are not filled in with item
                # only autocompletion popup is filled while typing
                # Activate autocompletion
                completer = CustomQCompleter([], self)
                #completer.setCompletionMode(QCompleter.PopupCompletion) # does not work with regex custom completer
                completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
                completer.setMaxVisibleItems(20)
                completer.setCaseSensitivity(Qt.CaseInsensitive)
                #completer.popup().setStyleSheet("background-color: lightblue")
                completer.activated.connect(partial(self.onCompleterActivated, key))
                control = item['widget']
                li = control.lineEdit()
                li.setCompleter(completer)
                li.textEdited.connect(partial(self.refreshAutocomplete, key))

                # when the user resets the entered value
                control = item['resetWidget']
                slot = partial(self.onSearchItemReset, key)
                control.clicked.connect(slot)

            else:
                control = item['widget']
                # when the user edits the combobox content
                slot = partial(self.onNonSearchItemEdit, key)
                control.editTextChanged[str].connect(slot)

                # when the user chooses in the list
                slot = partial(self.onNonSearchItemChoose, key)
                control.currentIndexChanged[str].connect(slot)

                # when the user reset the entered value
                control = item['resetWidget']
                slot = partial(self.onNonSearchItemReset, key)
                control.clicked.connect(slot)



        # export buttons
        self.btExportProprietaire.clicked.connect(self.exportProprietaire)
        self.exportParcelleButtons = {
            'parcelle': self.btExportParcelle,
            'parcelle_proprietaire': self.btExportParcelleProprietaire
        }
        for key, item in list(self.exportParcelleButtons.items()):
            control = item
            slot = partial(self.exportParcelle, key)
            control.clicked.connect(slot)

        # setup some gui items
        self.setupSearchCombobox('commune', None, 'sql')
        #self.setupSearchCombobox('section', None, 'sql')

        # Check majic content
        self.hasMajicDataProp = False
        self.hasMajicDataVoie = False
        self.hasMajicDataParcelle = False
        self.checkMajicContent()

        # signals



    def clearComboboxes(self):
        '''
        Clear comboboxes content
        '''
        self.txtLog.clear()
        for key, item in list(self.searchComboBoxes.items()):
            # manual search widgets
            if 'widget' in item:
                item['widget'].clear()

    def checkMajicContent(self):
        '''
        Check if database contains
        any MAJIC data
        '''
        self.hasMajicDataProp = False
        self.hasMajicDataVoie = False
        self.hasMajicDataParcelle = False

        from .cadastre_dialogs import cadastre_common
        aLayer = cadastre_common.getLayerFromLegendByTableProps('geo_commune')
        if aLayer:
            self.connectionParams = cadastre_common.getConnectionParameterFromDbLayer(aLayer)

        # Get connection parameters
        if self.connectionParams:

            # Get Connection params
            connector = cadastre_common.getConnectorFromUri(self.connectionParams)
            if connector:
                # Get data from table proprietaire
                sql = 'SELECT * FROM "proprietaire" LIMIT 1'
                if self.connectionParams['dbType'] == 'postgis':
                    sql = cadastre_common.setSearchPath(sql, self.connectionParams['schema'])
                [header, data, rowCount, ok] = cadastre_common.fetchDataFromSqlQuery(connector, sql)
                if ok and rowCount >= 1:
                    self.hasMajicDataProp = True

                # Get data from table voie
                sql = 'SELECT * FROM "voie" LIMIT 1'
                if self.connectionParams['dbType'] == 'postgis':
                    sql = cadastre_common.setSearchPath(sql, self.connectionParams['schema'])
                [header, data, rowCount, ok] = cadastre_common.fetchDataFromSqlQuery(connector, sql)
                if ok and rowCount >= 1:
                    self.hasMajicDataVoie = True

                # Get data from table parcelle
                sql = 'SELECT * FROM "parcelle" LIMIT 1'
                if self.connectionParams['dbType'] == 'postgis':
                    sql = cadastre_common.setSearchPath(sql, self.connectionParams['schema'])
                [header, data, rowCount, ok] = cadastre_common.fetchDataFromSqlQuery(connector, sql)
                if ok and rowCount >= 1:
                    self.hasMajicDataParcelle = True

                connector.__del__()

        self.liAdresse.setEnabled(self.hasMajicDataVoie and self.hasMajicDataParcelle)
        self.grpProprietaire.setEnabled(self.hasMajicDataProp)
        self.btExportParcelle.setEnabled(self.hasMajicDataProp)

        if not self.hasMajicDataParcelle or not self.hasMajicDataVoie:
            self.qc.updateLog(u"<b>Pas de données MAJIC non bâties et/ou fantoir</b> -> désactivation de la recherche d'adresse")
        if not self.hasMajicDataProp:
            self.qc.updateLog(u"<b>Pas de données MAJIC propriétaires</b> -> désactivation de la recherche de propriétaires")


    def setupSearchCombobox(self, combo, filterExpression=None, queryMode='qgis'):
        '''
        Fil given combobox with data
        from sql query or QGIS layer query
        And add autocompletion
        '''
        layer = None
        features = None

        # Get widget
        searchCombo = self.searchComboBoxes[combo]
        cb = searchCombo['widget']
        cb.clear()

        # Get corresponding QGIS layer
        itemList = []
        table = searchCombo['table']
        layer = cadastre_common.getLayerFromLegendByTableProps(
            table,
            searchCombo['geomCol'],
            searchCombo['sql']
        )

        self.searchComboBoxes[combo]['layer'] = layer
        if layer:

            # Get all features
            keepattributes = self.searchComboBoxes[combo]['attributes']
            request = QgsFeatureRequest().setSubsetOfAttributes(
                keepattributes,
                layer.fields()
            )

            self.searchComboBoxes[combo]['request'] = request
            labelAttribute = self.searchComboBoxes[combo]['labelAttribute']

            # Get features
            if queryMode == 'sql':
                features = self.getFeaturesFromSqlQuery(
                    layer,
                    filterExpression,
                    keepattributes,
                    self.searchComboBoxes[combo]['orderBy']
                )
            else:
                features = layer.getFeatures(request)

            self.searchComboBoxes[combo]['features'] = features

            # Loop through features
            # optionnaly filter by QgsExpression
            qe = None
            if filterExpression and queryMode == 'qgis':
                qe = QgsExpression(filterExpression)
            if queryMode == 'sql':
                emptyLabel = u'%s item(s)' % len(features)
            else:
                emptyLabel = ''
            cb.addItem('%s' % emptyLabel, '')

            for feat in features:
                keep = True
                if qe:
                    if not qe.evaluate(feat):
                        keep = False
                if keep:
                    if feat and feat[labelAttribute]:
                        itemList.append(feat[labelAttribute])
                        cb.addItem(feat[labelAttribute], feat)

            # style cb to adjust list width to max length content
            pView = cb.view()
            pView.setMinimumWidth(pView.sizeHintForColumn(0))

            # Activate autocompletion ( based on combobox content, match only first letters)
            completer = QCompleter(itemList, self)
            completer.setCompletionMode(QCompleter.PopupCompletion)
            completer.setMaxVisibleItems(30)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            #~ completer.popup().setStyleSheet("background-color: lightblue")
            cb.setEditable(True)
            cb.setCompleter(completer)

        else:
            #~ self.qc.updateLog(u'Veuillez charger des données cadastrales dans QGIS pour pouvoir effectuer une recherche')
            self.searchComboBoxes[combo]['layer'] = None
            self.searchComboBoxes[combo]['request'] = None
            self.searchComboBoxes[combo]['features'] = None
            self.searchComboBoxes[combo]['chosenFeature'] = None

        return [layer, features]


    def refreshAutocomplete(self, key):
        '''
        Refresh autocompletion while the users add more chars in line edit
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Get value
        combo = self.searchComboBoxes[key]['widget']
        searchValue = str(combo.currentText())

        # Abort if searchValue length too small
        minlen = self.searchComboBoxes[key]['search']['minlen']
        if len(self.qc.normalizeString(searchValue)) < minlen:
            #self.qc.updateLog(u"%s caractères minimum requis pour la recherche !" % minlen)
            QApplication.restoreOverrideCursor()
            return None

        # Get database connection parameters from a qgis layer
        dbtable = self.searchComboBoxes[key]['table']
        layer = cadastre_common.getLayerFromLegendByTableProps( dbtable.replace('v_', '') )
        if not layer:
            QApplication.restoreOverrideCursor()
            return None
        connectionParams = cadastre_common.getConnectionParameterFromDbLayer(layer)
        if not connectionParams:
            QApplication.restoreOverrideCursor()
            return None

        # Use db_manager tool to run the query
        connector = cadastre_common.getConnectorFromUri(connectionParams)
        self.connector = connector

        # Format searchValue
        # get rid of contextual info
        sp = searchValue.split('|')
        if len(sp) > 1:
            searchValue = sp[1]

        # get rid of double spaces
        r = re.compile(r'[ ,]+', re.IGNORECASE)
        searchValue = r.sub(' ', searchValue).strip(' \t\n')

        if key == 'adresse':
            # get rid of stopwords
            stopwords = ['ALLEE', 'AQUEDUC', 'ARCEAUX', 'AVENUE', 'AVENUES', 'BOULEVARD', 'CARREFOUR', 'CARRER', 'CHEMIN', 'CHEMINS', 'CHEMIN RURAL', 'CLOS', 'COUR', 'COURS', 'DESCENTE', 'ENCLOS', 'ESCALIER', 'ESPACE', 'ESPLANADE', 'GRAND RUE', 'IMPASSE', 'MAIL', 'MONTEE', 'PARVIS', 'PASSAGE', 'PASSERELLE', 'PLACE', 'PLAN', 'PONT', 'QUAI', 'ROND-POINT', 'ROUTE', 'RUE', 'RUISSEAU', 'SENTE', 'SENTIER', 'SQUARE', 'TERRASSE', 'TRABOULE', 'TRAVERSE', 'TRAVERSEE', 'TRAVERSIER', 'TUNNEL', 'VOIE', 'VOIE COMMUNALE', 'VIADUC', 'ZONE',
            'ACH', 'ALL', 'ANGL', 'ART', 'AV', 'AVE', 'BD', 'BV', 'CAMP', 'CAR', 'CC', 'CD', 'CH', 'CHE', 'CHEM', 'CHS ', 'CHV', 'CITE', 'CLOS', 'COTE', 'COUR', 'CPG', 'CR', 'CRS', 'CRX', 'D', 'DIG', 'DOM', 'ECL', 'ESC', 'ESP', 'FG', 'FOS', 'FRM', 'GARE', 'GPL', 'GR', 'HAM', 'HLE', 'HLM ', 'IMP', 'JTE ', 'LOT', 'MAIL', 'MAIS', 'N', 'PARC', 'PAS', 'PCH', 'PL', 'PLE ', 'PONT', 'PORT', 'PROM', 'PRV', 'PTA', 'PTE', 'PTR', 'PTTE', 'QUA', 'QUAI', 'REM', 'RES', 'RIVE', 'RLE', 'ROC', 'RPE ', 'RPT ', 'RTE ', 'RUE', 'RULT', 'SEN', 'SQ', 'TOUR', 'TSSE', 'VAL', 'VC', 'VEN', 'VLA', 'VOIE', 'VOIR', 'VOY', 'ZONE'
            ]
            sp = searchValue.split(' ')
            if len(sp)>0 and self.qc.normalizeString(sp[0]) in stopwords:
                searchValue = ' '.join(sp[1:])
                if len(self.qc.normalizeString(searchValue)) < minlen:
                    self.qc.updateLog(u"%s caractères minimum requis pour la recherche !" % minlen)
                    QApplication.restoreOverrideCursor()
                    return None

        sqlSearchValue = self.qc.normalizeString(searchValue)
        searchValues = sqlSearchValue.split(' ')

        # Build SQL query
        hasCommuneFilter = None
        if key == 'adresse':
            sql = ' SELECT DISTINCT v.voie, c.tex2 AS libcom, v.natvoi, v.libvoi'
            sql+= ' FROM voie v'
            # filter among commune existing in geo_commune
            sql+= ' INNER JOIN geo_commune c ON c.commune = v.commune'
            sql+= " WHERE 2>1"
            for sv in searchValues:
                sql+= " AND libvoi LIKE %s" % self.connector.quoteString('%'+sv+'%')

            # filter on the chosen commune in the combobox, if any
            communeCb = self.searchComboBoxes['commune']
            searchCom = str(self.liCommune.currentText())
            if communeCb and communeCb['chosenFeature'] and not isinstance(communeCb['chosenFeature'], list) and not 'item(s)' in searchCom:
                geo_commune = communeCb['chosenFeature']['geo_commune']
                sql+= ' AND trim(c.geo_commune) = %s' % self.connector.quoteString(geo_commune)
                hasCommuneFilter = True

            # order
            sql+= ' ORDER BY c.tex2, v.natvoi, v.libvoi'

        if key == 'proprietaire':
            sql = " SELECT trim(ddenom) AS k, MyStringAgg(comptecommunal, ',') AS cc, dnuper" #, c.ccocom"
            sql+= ' FROM proprietaire p'
            #~ sql+= ' INNER JOIN commune c ON c.ccocom = p.ccocom'
            sql+= " WHERE 2>1"
            for sv in searchValues:
                sql+= " AND ddenom LIKE %s" % self.connector.quoteString('%'+sv+'%')
            sql+= ' GROUP BY dnuper, ddenom, dlign4' #, c.ccocom'
            sql+= ' ORDER BY ddenom' #, c.ccocom'
        self.dbType = connectionParams['dbType']
        if self.dbType == 'postgis':
            sql = cadastre_common.setSearchPath(sql, connectionParams['schema'])
            sql = sql.replace('MyStringAgg', 'string_agg')
        else:
            sql = sql.replace('MyStringAgg', 'group_concat')
        #self.qc.updateLog(sql)

        sql+= ' LIMIT 20'

        [header, data, rowCount, ok] = cadastre_common.fetchDataFromSqlQuery(connector,sql)

        # Write message in log
        msg = u"%s résultats correpondent à '%s'" % (rowCount, searchValue)
        if key == 'adresse' and hasCommuneFilter:
            msg+=  ' pour la commune %s' % searchCom
        #self.qc.updateLog(msg)

        # Fill in the combobox
        cb = self.searchComboBoxes[key]['widget']
        itemList = []
        foundValues = {}

        maxString = ''
        maxStringSize = 0
        for line in data:
            if key == 'adresse':
                label = '%s | %s %s' % (
                    line[1].strip(),
                    line[2].strip(),
                    line[3].strip()
                )
                val = {'voie' : line[0]}

            if key == 'proprietaire':
                #~ label = '%s - %s | %s' % (line[3], line[2], line[0].strip())
                label = '%s | %s' % (line[2], line[0].strip())
                val = {
                    'cc' : ["'%s'" % a for a in line[1].split(',')],
                    'dnuper' : line[2]
                }

            itemList.append(label)
            ll = len(label)
            if ll > maxStringSize:
                maxString = label
                maxStringSize = ll

            # Add found values in object
            foundValues[label] = val

        self.searchComboBoxes[key]['foundValues'] = foundValues


        # Refresh list of item in completer
        li = cb.lineEdit()
        co = li.completer()
        co.model().setStringList(itemList)
        co.updateModel()

        #print(co.model().stringList())

        # change width of completer popup
        p = co.popup()
        w = (p.width() - p.viewport().width()) + 2 * p.frameWidth() + p.fontMetrics().boundingRect(maxString).width()
        p.setMinimumWidth(w)

        #cr = QRect() # must define qrect to move it & show popup on left (not working)
        #co.complete(cr)

        # Highlight first item
        #todo

        # We do not fill the combobox (cause it overrides autocompletion)

        # Restore cursor
        QApplication.restoreOverrideCursor()





    def getFeaturesFromSqlQuery(self, layer, filterExpression=None, attributes='*', orderBy=None):
        '''
        Get data from a db table,
        optionnally filtered by given expression
        and get corresponding QgsFeature objects
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Get connection parameters
        connectionParams = cadastre_common.getConnectionParameterFromDbLayer(layer)
        if not connectionParams:
            QApplication.restoreOverrideCursor()
            return None

        # set properties
        self.dbType = connectionParams['dbType']
        self.schema = connectionParams['schema']

        # Use db_manager tool to run the query
        connector = cadastre_common.getConnectorFromUri(connectionParams)

        # SQL
        sql = ' SELECT %s' % ', '.join(attributes)

        # Replace geo_parcelle by parcelle_info if necessary
        table = connectionParams['table']
        if table == 'geo_parcelle':
            table = 'parcelle_info'
        f = '"%s"' % table
        sql+= ' FROM %s' % f
        sql+= " WHERE 2>1"
        if filterExpression:
            sql+= " AND %s" % filterExpression
        if orderBy:
            sql+= ' ORDER BY %s' % ', '.join(orderBy)

        if self.dbType == 'postgis':
            sql = cadastre_common.setSearchPath(sql, connectionParams['schema'])
        # Get data
        #self.qc.updateLog(sql)
        [header, data, rowCount, ok] = cadastre_common.fetchDataFromSqlQuery(connector, sql)

        # Get features
        features = []
        if rowCount > 0:
            fids = [str(a[0]) for a in data]
            exp = ' "%s" IN ( %s ) ' % (
                attributes[0],
                ','.join(fids)
            )
            request = QgsFeatureRequest().setSubsetOfAttributes(attributes, layer.fields()).setFilterExpression(exp)
            if orderBy:
                request.addOrderBy(orderBy[0])
            for feat in layer.getFeatures(request):
                features.append(feat)

        connector.__del__()

        QApplication.restoreOverrideCursor()
        return features


    def getFeatureFromComboboxValue(self, combo):
        '''
        Get the feature corresponding to
        the chosen combobox value
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Get widget
        searchCombo = self.searchComboBoxes[combo]
        cb = searchCombo['widget']

        # Reinit
        self.searchComboBoxes[combo]['chosenFeature'] = None
        feature = cb.itemData(cb.currentIndex())
        if feature:
            self.searchComboBoxes[combo]['chosenFeature'] = feature

        QApplication.restoreOverrideCursor()


    def onCompleterActivated(self, key):
        '''
        Triggered when the users chooses an item in the combobox completer popup
        '''
        cb = self.searchComboBoxes[key]['widget']
        label = cb.currentText()
        li = cb.lineEdit()
        co = li.completer()
        labellist = []
        labellist.append(label.split('|')[0].strip())
        co.model().setStringList(labellist)
        co.updateModel()
        if label in self.searchComboBoxes[key]['foundValues']:
            chosenValue = self.searchComboBoxes[key]['foundValues'][label]
            self.onSearchItemChoose(key, label, chosenValue)



    def onSearchItemChoose(self, key, label, value):
        '''
        Select parcelles corresponding
        to chosen item in combo box
        (adresse, proprietaire)
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Get value
        #combo = self.searchComboBoxes[key]['widget']
        #value = combo.itemData(combo.currentIndex())
        if not value:
            QApplication.restoreOverrideCursor()
            return None

        # Set filter expression for parcell child data
        ckey = self.searchComboBoxes[key]['search']['parcelle_child']
        if key == 'adresse':
            filterExpression = "voie = '%s'" % value['voie']

        if key == 'proprietaire':
            filterExpression = "comptecommunal IN (%s)" % ', '.join(value['cc'])

        [layer, features] = self.setupSearchCombobox(
            ckey,
            filterExpression,
            'sql'
        )

        # Set properties
        self.searchComboBoxes[key]['layer'] = layer
        self.searchComboBoxes[key]['features'] = features
        self.searchComboBoxes[key]['chosenFeature'] = features

        # Set proprietaire id
        if key == 'proprietaire':
            self.searchComboBoxes[key]['id'] = value['cc']

        if features:
            self.qc.updateLog(
                u"%s parcelle(s) trouvée(s) pour '%s'" % (
                    len(features),
                    label
                )
            )
            self.setZoomToChosenSearchCombobox(key)

        QApplication.restoreOverrideCursor()


    def onNonSearchItemChoose(self, key):
        '''
        Get feature from chosen item in combobox
        and optionnaly fill its children combobox
        '''
        # get feature from the chosen value
        self.getFeatureFromComboboxValue(key)

        # optionnaly also update children combobox
        item = self.searchComboBoxes[key]
        if 'children' in item:
            if not isinstance(item['children'], list):
                return
            for child in item['children']:
                feature = item['chosenFeature']
                ckey = child['key']
                fkey = child['fkey']
                if feature:
                    filterExpression = "%s = '%s' AND lot = '%s'" % (fkey, feature[fkey], feature['lot'])
                    self.setupSearchCombobox(ckey, filterExpression, 'sql')
                else:
                    if child['getIfNoFeature']:
                        self.setupSearchCombobox(ckey, None, 'sql')


    def onNonSearchItemEdit(self, key):
        '''
        Empty previous stored feature
        for the combobox every time
        the user edit its content
        '''
        self.searchComboBoxes[key]['chosenFeature'] = None


    def onNonSearchItemReset(self, key):
        '''
        Unchoose item in combobox
        which also trigger onNonSearchItemChoose above
        '''
        self.searchComboBoxes[key]['chosenFeature'] = None
        self.searchComboBoxes[key]['widget'].setCurrentIndex(0)


    def onSearchItemReset(self, key):
        '''
        Unchoose item in a searchable combobox
        which also trigger
        '''
        self.searchComboBoxes[key]['chosenFeature'] = None
        self.searchComboBoxes[key]['widget'].setCurrentIndex(0)
        self.searchComboBoxes[key]['widget'].lineEdit().selectAll()
        self.searchComboBoxes[key]['widget'].lineEdit().setFocus()
        self.searchComboBoxes[key]['widget'].lineEdit().setText(u'')


    def onSearchItemFocus(self, key):
        '''
        Select all content on focus by click
        '''
        self.searchComboBoxes[key]['widget'].lineEdit().selectAll()
        self.searchComboBoxes[key]['widget'].lineEdit().setFocus()



    def setZoomToChosenSearchCombobox(self, combo):
        '''
        Zoom to the feature(s)
        selected in the give combobox
        '''
        # Get widget
        searchCombo = self.searchComboBoxes[combo]
        cb = searchCombo['widget']

        # Zoom
        if searchCombo['chosenFeature']:
            if isinstance(searchCombo['chosenFeature'], list):
                # buid virtual geom
                f = searchCombo['chosenFeature'][0]
                extent = f.geometry().boundingBox()
                for feat in searchCombo['chosenFeature']:
                    extent.combineExtentWith(feat.geometry().boundingBox())
            else:
                extent = searchCombo['chosenFeature'].geometry().boundingBox()

            # reproject extent if needed
            crsDest = QgsMapSettings().destinationCrs()
            layer = searchCombo['layer']
            crsSrc = layer.crs()
            if crsSrc.authid() != crsDest.authid():
              xform = QgsCoordinateTransform(crsSrc, crsDest,QgsProject.instance())
              extent = xform.transform(extent)

            self.mc.setExtent(extent)
            self.mc.refresh()


    def setCenterToChosenSearchCombobox(self, combo):
        '''
        Center to the feature(s)
        chosen in the corresponding combobox
        '''
        # Get widget
        searchCombo = self.searchComboBoxes[combo]
        cb = searchCombo['widget']

        # Center
        if searchCombo['chosenFeature']:
            # first get scale
            scale = self.mc.scale()

            # then zoom to geometry extent
            if isinstance(searchCombo['chosenFeature'], list):
                # buid virtual geom
                f = searchCombo['chosenFeature'][0]
                extent = f.geometry().boundingBox()
                for feat in searchCombo['chosenFeature']:
                    extent.combineExtentWith(feat.geometry().boundingBox())
            else:
                extent = searchCombo['chosenFeature'].geometry().boundingBox()

            # reproject extent if needed
            crsDest = QgsMapSettings().destinationCrs()
            layer = searchCombo['layer']
            crsSrc = layer.crs()
            if crsSrc.authid() != crsDest.authid():
              xform = QgsCoordinateTransform(crsSrc, crsDest,QgsProject.instance())
              extent = xform.transform(extent)

            self.mc.setExtent(extent)

            # the set the scale back
            self.mc.zoomScale(scale)
            self.mc.refresh()


    def setSelectionToChosenSearchCombobox(self, combo):
        '''
        Select the feature(s)
        corresponding to the chosen item
        '''
        # Get widget
        searchCombo = self.searchComboBoxes[combo]
        cb = searchCombo['widget']

        # Select
        if searchCombo['chosenFeature'] and searchCombo['layer']:
            searchCombo['layer'].removeSelection()
            if isinstance(searchCombo['chosenFeature'], list):
                i = [feat.id() for feat in searchCombo['chosenFeature']]
            else:
                i = searchCombo['chosenFeature'].id()
            searchCombo['layer'].select(i)


    def setCenterToChosenItem(self, key):
        '''
        Set map center corresponding
        to the chosen feature(s) for the
        last not null item in the list
        '''
        w = None
        for item in self.zoomButtons[key]['comboboxes']:
            if self.searchComboBoxes[item]['chosenFeature'] \
            and self.searchComboBoxes[item]['layer']:
                w = item
        if w:
            self.setCenterToChosenSearchCombobox(w)

    def setZoomToChosenItem(self, key):
        '''
        Zoom to the chosen feature(s) for the
        last not null item in the list
        '''
        w = None
        for item in self.zoomButtons[key]['comboboxes']:
            if self.searchComboBoxes[item]['chosenFeature'] \
            and self.searchComboBoxes[item]['layer']:
                w = item
        if w:
            self.setZoomToChosenSearchCombobox(w)

    def setSelectionToChosenItem(self, key):
        '''
        Select the feature(s) for the
        last non null item in the list
        '''
        w = None
        for item in self.zoomButtons[key]['comboboxes']:
            if self.searchComboBoxes[item]['chosenFeature'] \
            and self.searchComboBoxes[item]['layer']:
                w = item
        if w:
            self.setSelectionToChosenSearchCombobox(w)

    def exportProprietaire(self):
        '''
        Export the selected proprietaire
        as PDF using the template composer
        filled with appropriate data
        '''
        if not self.connector:
            return

        # Search proprietaire by dnuper
        cc = self.searchComboBoxes['proprietaire']['id']
        if cc:
            layer = self.searchComboBoxes['proprietaire']['layer']
            qex = cadastreExport(layer, 'proprietaire', cc)
            qex.exportAsPDF()
        else:
            self.qc.updateLog(u'Aucune donnée trouvée pour ce propriétaire !')


    def exportParcelle(self, key):
        '''
        Export the selected parcelle
        as PDF using the template composer
        filled with appropriate data
        '''
        if not self.connector:
            return

        feat = self.searchComboBoxes[key]['chosenFeature']
        layer = self.searchComboBoxes[key]['layer']
        if feat:
            comptecommunal = cadastre_common.getCompteCommunalFromParcelleId( feat['geo_parcelle'], self.connectionParams, self.connector)
            qex = cadastreExport(layer, 'parcelle', comptecommunal, feat['geo_parcelle'])
            qex.exportAsPDF()
        else:
            self.qc.updateLog(u'Aucune parcelle sélectionnée !')

    def onVisibilityChange(self, visible):
        '''
        Fill commune combobox when the dock
        becomes visible
        '''
        if visible:
            # fix_print_with_import
            print("visible")
            #~ self.setupSearchCombobox('commune', None, 'sql')
        else:
            self.txtLog.clear()



# --------------------------------------------------------
#        Option - Let the user configure options
# --------------------------------------------------------


from qgis.PyQt import uic
OPTION_FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        os.path.dirname(__file__),
        'forms/cadastre_option_form.ui'
    )
)
class cadastre_option_dialog(QDialog, OPTION_FORM_CLASS):
    def __init__(self, iface, parent=None):
        super(cadastre_option_dialog, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)

        self.plugin_dir = os.path.dirname(__file__)

        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        self.buttonBox.rejected.connect(self.onReject)
        self.buttonBox.accepted.connect(self.onAccept)

        # interface change buttons
        self.interfaceSelectors = {
            "Cadastre" : {
                "button" : self.btInterfaceCadastre
            },
            "QGIS" : {
                "button" : self.btInterfaceQgis
            }
        }
        from functools import partial
        for key, item in list(self.interfaceSelectors.items()):
            control = item['button']
            slot = partial(self.applyInterface, key)
            control.clicked.connect(slot)

        # path buttons selectors
        # paths needed to be chosen by user
        self.pathSelectors = {
            "tempDir" : {
                "button" : self.btTempDir,
                "input" : self.inTempDir,
                "type": "dir"
            },
            "composerTemplateFile" : {
                "button" : self.btComposerTemplateFile,
                "input" : self.inComposerTemplateFile,
                "type": "file"
            }
        }
        from functools import partial
        for key, item in list(self.pathSelectors.items()):
            control = item['button']
            slot = partial(self.chooseDataPath, key)
            control.clicked.connect(slot)

        # Set initial widget values
        self.getValuesFromSettings()


    def chooseDataPath(self, key):
        '''
        Ask the user to select a folder
        and write down the path to appropriate field
        '''
        if self.pathSelectors[key]['type'] == 'dir':
            ipath = QFileDialog.getExistingDirectory(
                None,
                u"Choisir le répertoire contenant les fichiers",
                str(self.pathSelectors[key]['input'].text().encode('utf-8')).strip(' \t')
            )
        else:
            ipath, __ = QFileDialog.getOpenFileName(
                None,
                u"Choisir le modèle de composeur utilisé pour l'export",
                str(self.pathSelectors[key]['input'].text().encode('utf-8')).strip(' \t'),
                u"Composeur (*.qpt)"
            )

        if os.path.exists(str(ipath)):
            self.pathSelectors[key]['input'].setText(str(ipath))


    def getValuesFromSettings(self):
        '''
        Get majic file names and other options
        from settings and set corresponding inputs
        '''
        s = QSettings()
        batiFileName = s.value("cadastre/batiFileName", 'REVBATI.800', type=str)
        if batiFileName:
            self.inMajicBati.setText(batiFileName)
        fantoirFileName = s.value("cadastre/fantoirFileName", 'TOPFANR.800', type=str)
        if fantoirFileName:
            self.inMajicFantoir.setText(fantoirFileName)
        lotlocalFileName = s.value("cadastre/lotlocalFileName", 'REVD166.800', type=str)
        if lotlocalFileName:
            self.inMajicLotlocal.setText(lotlocalFileName)
        nbatiFileName = s.value("cadastre/nbatiFileName", 'REVNBAT.800', type=str)
        if nbatiFileName:
            self.inMajicNbati.setText(nbatiFileName)
        pdlFileName = s.value("cadastre/pdlFileName", 'REVFPDL.800', type=str)
        if pdlFileName:
            self.inMajicPdl.setText(pdlFileName)
        propFileName = s.value("cadastre/propFileName", 'REVPROP.800', type=str)
        if propFileName:
            self.inMajicProp.setText(propFileName)
        tempDir = s.value("cadastre/tempDir", '%s' % tempfile.gettempdir(), type=str)
        if tempDir:
            self.inTempDir.setText(tempDir)
        maxInsertRows = s.value("cadastre/maxInsertRows", 100000, type=int)
        if maxInsertRows:
            self.inMaxInsertRows.setValue(maxInsertRows)
        spatialiteTempStore = s.value("cadastre/spatialiteTempStore", 'MEMORY', type=str)
        if spatialiteTempStore and hasattr(self, 'inSpatialiteTempStore'):
            if spatialiteTempStore == 'MEMORY':
                self.inSpatialiteTempStore.setCurrentIndex(0)
            else:
                self.inSpatialiteTempStore.setCurrentIndex(1)
        composerTemplateFile = s.value(
            "cadastre/composerTemplateFile",
            '%s/composers/paysage_a4.qpt' % self.plugin_dir,
            type=str
        )
        if composerTemplateFile:
            self.inComposerTemplateFile.setText(composerTemplateFile)


    def applyInterface(self, key):
        '''
        Help the user to select
        and apply personalized interface
        '''

        item = self.interfaceSelectors[key]
        iniPath = os.path.join(
            self.plugin_dir,
            'interface/'
        )
        interfaceInfo = u'''
        Pour appliquer l'interface <b>%s</b>
        <ul>
            <li>Menu Préférences > Personnalisation</li>
            <li>Bouton <b>Charger depuis le fichier</b> (icône dossier ouvert)</li>
            <li>Sélectionner le fichier <b>%s.ini</b> situé dans le dossier : <b>%s</b></li>
            <li>Appliquer et fermer la fenêtre</li>
            <li>Redémarer QGIS</li>
        </ul>
        ''' % (key, key.lower(), iniPath)
        QMessageBox.information(
            self,
            u"Cadastre - Personnalisation",
            interfaceInfo
        )


    def onAccept(self):
        '''
        Save options when pressing OK button
        '''

        # Save Majic file names
        s = QSettings()
        s.setValue("cadastre/batiFileName", self.inMajicBati.text().strip(' \t\n\r'))
        s.setValue("cadastre/fantoirFileName", self.inMajicFantoir.text().strip(' \t\n\r'))
        s.setValue("cadastre/lotlocalFileName", self.inMajicLotlocal.text().strip(' \t\n\r'))
        s.setValue("cadastre/nbatiFileName", self.inMajicNbati.text().strip(' \t\n\r'))
        s.setValue("cadastre/pdlFileName", self.inMajicPdl.text().strip(' \t\n\r'))
        s.setValue("cadastre/propFileName", self.inMajicProp.text().strip(' \t\n\r'))

        # Save temp dir
        s.setValue("cadastre/tempDir", self.inTempDir.text().strip(' \t\n\r'))
        # Save composer template dir
        s.setValue("cadastre/composerTemplateFile", self.inComposerTemplateFile.text().strip(' \t\n\r'))

        # Save performance tuning
        s.setValue("cadastre/maxInsertRows", int(self.inMaxInsertRows.value()))
        s.setValue("cadastre/spatialiteTempStore", self.inSpatialiteTempStore.currentText().upper())

        self.accept()

    def onReject(self):
        '''
        Run some actions when
        the user closes the dialog
        '''
        string = "cadastre option dialog closed"
        self.close()



# --------------------------------------------------------
#        About - Let the user display the about dialog
# --------------------------------------------------------


from qgis.PyQt import uic
ABOUT_FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        os.path.dirname(__file__),
        'forms/cadastre_about_form.ui'
    )
)
class cadastre_about_dialog(QDialog, ABOUT_FORM_CLASS):
    def __init__(self, iface, parent=None):
        super(cadastre_about_dialog, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)

        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        self.buttonBox.rejected.connect(self.onReject)
        self.buttonBox.accepted.connect(self.onAccept)

    def onAccept(self):
        '''
        Save options when pressing OK button
        '''
        self.accept()

    def onReject(self):
        '''
        Run some actions when
        the user closes the dialog
        '''
        self.close()


# --------------------------------------------------------
#        Parcelle - Show parcelle information
# --------------------------------------------------------

from .cadastre_export_dialog import cadastreExport, cadastrePrintProgress 

from qgis.PyQt import uic
PARCELLE_FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        os.path.dirname(__file__),
        'forms/cadastre_parcelle_form.ui'
    )
)
class cadastre_parcelle_dialog(QDialog, PARCELLE_FORM_CLASS):
    def __init__(self, iface, layer, feature, cadastre_search_dialog, parent=None):
        super(cadastre_parcelle_dialog, self).__init__(parent)
        self.iface = iface
        self.feature = feature
        self.layer = layer
        self.mc = iface.mapCanvas()
        self.setupUi(self)
        self.cadastre_search_dialog = cadastre_search_dialog

        # common cadastre methods
        from .cadastre_dialogs import cadastre_common
        self.qc = cadastre_common(self)

        # Get connection parameters
        connectionParams = cadastre_common.getConnectionParameterFromDbLayer(layer)
        if not connectionParams:
            return
        self.connectionParams = connectionParams
        self.dbType = connectionParams['dbType']
        self.schema = connectionParams['schema']
        connector = cadastre_common.getConnectorFromUri(connectionParams)
        self.connector = connector


        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        self.buttonBox.rejected.connect(self.onReject)
        self.buttonBox.accepted.connect(self.onAccept)
        # Export buttons
        exportButtons = {
            'parcelle' : self.btExportParcelle,
            'proprietaire': self.btExportProprietaire
        }
        for key, item in list(exportButtons.items()):
            control = item
            slot = partial(self.exportAsPDF, key)
            control.clicked.connect(slot)

        # Parcelle action button
        self.btCentrer.clicked.connect(self.centerToParcelle)
        self.btZoomer.clicked.connect(self.zoomToParcelle)
        self.btSelectionner.clicked.connect(self.selectParcelle)

        # Select parcelle from proprietaire action
        self.btParcellesProprietaire.clicked.connect(self.selectParcellesProprietaire)

        # Check majic content
        self.hasMajicDataProp = False
        self.checkMajicContent()

        # Get CSS
        self.css = None
        self.getCss()

        # Set dialog content
        self.setParcelleContent()
        self.setProprietairesContent()
        self.setSubdivisionsContent()
        self.setLocauxContent()

    def getCss(self):
        '''
        Get CSS from CSS file
        '''
        css = ''
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(plugin_dir, 'scripts/css/cadastre.css'), 'r') as f:
            css = f.read()
        self.css = css

    def checkMajicContent(self):
        '''
        Check if database contains
        any MAJIC data
        '''
        self.hasMajicDataProp = False
        sql = 'SELECT * FROM "proprietaire" LIMIT 1'
        if self.connectionParams['dbType'] == 'postgis':
            sql = cadastre_common.setSearchPath(sql, self.connectionParams['schema'])
        [header, data, rowCount, ok] = cadastre_common.fetchDataFromSqlQuery(self.connector, sql)
        if ok and rowCount >= 1:
            self.hasMajicDataProp = True

    # @timing
    def setParcelleContent(self):
        '''
        Get parcelle data
        and set the dialog content
        '''
        if self.feature.fieldNameIndex('proprietaire') > 0:
            item = 'parcelle_majic'
        else:
            item = 'parcelle_simple'

        html = cadastre_common.getItemHtml(item, self.feature, self.connectionParams, self.connector)
        self.parcelleInfo.setStyleSheet( self.css )
        self.parcelleInfo.setHtml('%s' % html)

    # @timing
    def setProprietairesContent(self):
        '''
        Get proprietaires data
        and set the dialog content
        '''
        if self.feature.fieldNameIndex('proprietaire') == -1:
            html = 'Les données MAJIC n\'ont pas été trouvées dans la base de données'
        else:
            item = 'proprietaires'
            html = cadastre_common.getItemHtml(item, self.feature, self.connectionParams, self.connector)
        self.proprietairesInfo.setStyleSheet( self.css )
        self.proprietairesInfo.setText('%s' % html)

    # @timing
    def setSubdivisionsContent(self):
        '''
        Get subdivision data
        and set the dialog content
        '''
        if self.feature.fieldNameIndex('proprietaire') == -1:
            html = 'Les données MAJIC n\'ont pas été trouvées dans la base de données'
        else:
            item = 'subdivisions'
            html = cadastre_common.getItemHtml(item, self.feature, self.connectionParams, self.connector)
        self.subdivisionsInfo.setStyleSheet( self.css )
        self.subdivisionsInfo.setText('%s' % html)

    # @timing
    def setLocauxContent(self):
        '''
        Get locaux data
        and set the dialog content
        '''
        if self.feature.fieldNameIndex('proprietaire') == -1:
            html = 'Les données MAJIC n\'ont pas été trouvées dans la base de données'
        else:
            item = 'locaux'
            html = cadastre_common.getItemHtml(item, self.feature, self.connectionParams, self.connector)
            item = 'locaux_detail'
            html+= cadastre_common.getItemHtml(item, self.feature, self.connectionParams, self.connector)
        self.locauxInfo.setStyleSheet( self.css )
        self.locauxInfo.setText('%s' % html)

    def exportAsPDF(self, key):
        '''
        Export the parcelle or proprietaire
        information as a PDF file
        '''
        if not self.connector:
            return

        if not self.hasMajicDataProp:
            self.proprietairesInfo.setText(u'Pas de données de propriétaires dans la base')
            return

        if self.feature:
            comptecommunal = cadastre_common.getCompteCommunalFromParcelleId(
                self.feature['geo_parcelle'],
                self.connectionParams,
                self.connector
            )
            if comptecommunal:
                if key == 'proprietaire' and self.cbExportAllCities.isChecked():
                    comptecommunal = cadastre_common.getProprietaireComptesCommunaux(
                        comptecommunal,
                        self.connectionParams,
                        self.connector
                    )
                if self.layer:
                    qe = cadastreExport(
                        self.layer,
                        key,
                        comptecommunal,
                        self.feature['geo_parcelle']
                    )
                    qe.exportAsPDF()


    def centerToParcelle(self):
        '''
        Centre to parcelle feature
        '''
        if self.feature:
            # first get scale
            scale = self.mc.scale()
            extent = self.feature.geometry().boundingBox()

            # reproject extent if needed
            crsDest = QgsMapSettings().destinationCrs()
            layer = self.layer
            crsSrc = layer.crs()
            if crsSrc.authid() != crsDest.authid():
              xform = QgsCoordinateTransform(crsSrc, crsDest,QgsProject.instance())
              extent = xform.transform(extent)

            self.mc.setExtent(extent)

            # the set the scale back
            self.mc.zoomScale(scale)
            self.mc.refresh()

    def zoomToParcelle(self):
        '''
        Zoom to parcelle feature
        '''
        if self.feature:
            extent = self.feature.geometry().boundingBox()

            # reproject extent if needed
            crsDest = QgsMapSettings().destinationCrs()
            layer = self.layer
            crsSrc = layer.crs()
            if crsSrc.authid() != crsDest.authid():
              xform = QgsCoordinateTransform(crsSrc, crsDest,QgsProject.instance())
              extent = xform.transform(extent)

            self.mc.setExtent(extent)
            self.mc.refresh()

    def selectParcelle(self):
        '''
        Zoom to parcelle feature
        '''
        if self.layer and self.feature:
            self.layer.removeSelection()
            self.layer.select(self.feature.id())

    def selectParcellesProprietaire(self):
        '''
        Select all parcelles from this parcelle proprietaire.
        Use search class tools.
        Needs refactoring
        '''
        if not self.hasMajicDataProp:
            self.proprietairesInfo.setText(u'Pas de données de propriétaires dans la base')
            return

        qs = self.cadastre_search_dialog
        key = 'proprietaire'

        comptecommunal = cadastre_common.getCompteCommunalFromParcelleId( self.feature['geo_parcelle'], self.connectionParams, self.connector )
        if not comptecommunal:
            # fix_print_with_import
            print("Aucune parcelle trouvée pour ce propriétaire")
        value = comptecommunal
        filterExpression = "comptecommunal IN ('%s')" % value

        # Get data for child parcelle combo and fill it
        ckey = qs.searchComboBoxes[key]['search']['parcelle_child']
        [layer, features] = qs.setupSearchCombobox(
            ckey,
            filterExpression,
            'sql'
        )

        # Set properties
        qs.searchComboBoxes[key]['layer'] = layer
        qs.searchComboBoxes[key]['features'] = features
        qs.searchComboBoxes[key]['chosenFeature'] = features

        # Select all parcelles from proprietaire
        qs.setSelectionToChosenSearchCombobox('proprietaire')


    def onAccept(self):
        '''
        Save options when pressing OK button
        '''
        self.accept()

    def onReject(self):
        '''
        Run some actions when
        the user closes the dialog
        '''
        self.connector.__del__()
        self.close()


# --------------------------------------------------------
#        Messages - Displays a message to the user
# --------------------------------------------------------

from qgis.PyQt import uic
MESSAGE_FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        os.path.dirname(__file__),
        'forms/cadastre_message_form.ui'
    )
)
class cadastre_message_dialog(QDialog, MESSAGE_FORM_CLASS):
    def __init__(self, iface, message, parent=None):
        super(cadastre_message_dialog, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)

        self.teMessage.setText(message)

        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        self.buttonBox.rejected.connect(self.onReject)
        self.buttonBox.accepted.connect(self.onAccept)

    def onAccept(self):
        '''
        Save options when pressing OK button
        '''
        self.accept()

    def onReject(self):
        '''
        Run some actions when
        the user closes the dialog
        '''
        self.close()
