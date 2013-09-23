# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Qadastre - Dialog classes
                                                                 A QGIS plugin
 This plugins helps users to import the french land registry ('cadastre')
 into a database. It is meant to ease the use of the data in QGIs
 by providing search tools and appropriate layer symbology.
                                                            -------------------
                begin                                : 2013-06-11
                copyright                        : (C) 2013 by 3liz
                email                                : info@3liz.com
 ***************************************************************************/

/***************************************************************************
 *                                                                                                                                                 *
 *     This program is free software; you can redistribute it and/or modify    *
 *     it under the terms of the GNU General Public License as published by    *
 *     the Free Software Foundation; either version 2 of the License, or         *
 *     (at your option) any later version.                                                                     *
 *                                                                                                                                                 *
 ***************************************************************************/
"""

import csv
import os.path
import operator
import re
import tempfile
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import QgsGenericProjectionSelector

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

from db_manager.db_plugins.plugin import DBPlugin, Schema, Table
from db_manager.db_plugins import createDbPlugin
from db_manager.db_plugins.postgis.connector import PostGisDBConnector

from functools import partial

# --------------------------------------------------------
#        import - Import data from EDIGEO and MAJIC files
# --------------------------------------------------------


class qadastre_common():

    def __init__(self, dialog):

        self.dialog = dialog

        # plugin directory path
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/Qadastre"

        # default auth id for layers
        self.defaultAuthId = 'EPSG:2154'


    def updateLog(self, msg):
        '''
        Update the log
        '''
        self.dialog.txtLog.append(msg)


    def updateProgressBar(self):
        '''
        Update the progress bar
        '''
        if self.dialog.go:
            self.dialog.step+=1
            self.dialog.pbProcess.setValue(int(self.dialog.step * 100/self.dialog.totalSteps))


    def updateConnectionList(self):
        '''
        Update the combo box containing the database connection list
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)

        dbType = unicode(self.dialog.liDbType.currentText()).lower()
        self.dialog.liDbConnection.clear()

        if self.dialog.liDbType.currentIndex() != 0:
            self.dialog.dbType = dbType
            # instance of db_manager plugin class
            dbpluginclass = createDbPlugin( dbType )
            self.dialog.dbpluginclass = dbpluginclass

            # fill the connections combobox
            for c in dbpluginclass.connections():
                self.dialog.liDbConnection.addItem( unicode(c.connectionName()))
        QApplication.restoreOverrideCursor()

    def toggleSchemaList(self, t):
        '''
        Toggle Schema list and inputs
        '''
        self.dialog.liDbSchema.setEnabled(t)
        if hasattr(self.dialog, "inDbCreateSchema"):
            self.dialog.inDbCreateSchema.setEnabled(t)
            self.dialog.btDbCreateSchema.setEnabled(t)


    def updateSchemaList(self):
        '''
        Update the combo box containing the schema list if relevant
        '''
        self.dialog.liDbSchema.clear()

        QApplication.setOverrideCursor(Qt.WaitCursor)
        connectionName = unicode(self.dialog.liDbConnection.currentText())
        self.dialog.connectionName = connectionName
        dbType = unicode(self.dialog.liDbType.currentText()).lower()

        # Deactivate schema fields
        self.toggleSchemaList(False)

        if dbType == 'postgis' and connectionName:

            # Activate schema fields
            self.toggleSchemaList(True)

            # Get schema list
            dbpluginclass = createDbPlugin( dbType, connectionName )
            self.dialog.dbpluginclass = dbpluginclass
            connection = dbpluginclass.connect()
            if connection:
                self.dialog.connection = connection
                db = dbpluginclass.database()
                if db:
                    self.dialog.db = db
                    self.dialog.schemaList = []
                    for s in db.schemas():
                        self.dialog.liDbSchema.addItem( unicode(s.name))
                        self.dialog.schemaList.append(unicode(s.name))
        QApplication.restoreOverrideCursor()


    def checkDatabaseForExistingStructure(self):
        '''
        Search among a database / schema
        if there are alreaday Cadastre data
        in it
        '''
        hasData = False
        searchTable = u'geo_commune'
        if self.dialog.db:
            schemaSearch = [s for s in self.dialog.db.schemas() if s.name == self.dialog.schema]
            schemaInst = schemaSearch[0]
            getSearchTable = [a for a in self.dialog.db.tables(schemaInst) if a.name == searchTable]
            if getSearchTable:
                hasData = True

        self.dialog.dbHasData = hasData


    def getLayerFromLegendByTableProps(self, tableName, geomCol='geom', sql=''):
        '''
        Get the layer from QGIS legend
        corresponding to a database
        table name (postgis or sqlite)
        '''

        layer = None
        layers = self.dialog.iface.legendInterface().layers()
        for l in layers:
            if not l.type() == QgsMapLayer.VectorLayer:
                pass
            if not l.providerType() in (u'postgres', u'spatialite'):
                pass
            connectionParams = self.getConnectionParameterFromDbLayer(l)
            if connectionParams['table'] == tableName and \
                connectionParams['geocol'] == geomCol and \
                connectionParams['sql'] == sql:
                return l

        return layer

    def getConnectionParameterFromDbLayer(self, layer):
        '''
        Get connection parameters
        from the layer datasource
        '''
        connectionParams = None

        # Get params via regex
        uri = layer.dataProvider().dataSourceUri()
        reg = "dbname='([^ ]+)' (?:host=([^ ]+) )?(?:port=([0-9]+) )?(?:user='([^ ]+)' )?(?:password='([^ ]+)' )?(?:sslmode=([^ ]+) )?(?:key='([^ ]+)' )?(?:estimatedmetadata=([^ ]+) )?(?:srid=([0-9]+) )?(?:type=([a-zA-Z]+) )?(?:table=\"(.+)\" \()?(?:([^ ]+)\) )?(?:sql=(.*))?"
        result = re.findall(r'%s' % reg, uri)
        res = result[0]
        if res:
            dbname = res[0]
            host = res[1]
            port = res[2]
            user = res[3]
            password = res[4]
            sslmode = res[5]
            key = res[6]
            estimatedmetadata = res[7]
            srid = res[8]
            gtype = res[9]
            table = res[10]
            geocol = res[11]
            sql = res[12]

            schema = ''
            if re.search('"\."', table):
                table = '"' + table + '"'
                sp = table.replace('"', '').split('.')
                schema = sp[0]
                table = sp[1]

            connectionParams = {
                'dbname' : dbname,
                'host' : host,
                'port': port,
                'user' : user,
                'password': password,
                'sslmode' : sslmode,
                'key': key,
                'estimatedmetadata' : estimatedmetadata,
                'srid' : srid,
                'type': gtype,
                'schema': schema,
                'table' : table,
                'geocol' : geocol,
                'sql' : sql,
            }

        return connectionParams


    def fetchDataFromSqlQuery(self, connector, sql):
        '''
        Execute a SQL query and
        return [header, data, rowCount]
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)

        data = []
        header = []
        rowCount = 0
        c = None


        try:
            c = connector._execute(None,unicode(sql))
            data = []
            header = connector._get_cursor_columns(c)

            if header == None:
                header = []

            if len(header) > 0:
                data = connector._fetchall(c)

            rowCount = c.rowcount

        except BaseError as e:

            DlgDbError.showError(e, self.dialog)
            self.dialog.go = False
            self.updateLog(e.msg)
            return

        finally:
            QApplication.restoreOverrideCursor()
            if c:
                c.close()
                del c

        return [header, data, rowCount]


    def chooseDataPath(self, key):
        '''
        Ask the user to select a folder
        and write down the path to appropriate field
        '''
        ipath = QFileDialog.getExistingDirectory(
            None,
            "Choisir le répertoire contenant les fichiers",
            str(self.dialog.pathSelectors[key]['input'].text().encode('utf-8')).strip(' \t')
        )
        if os.path.exists(unicode(ipath)):
            self.dialog.pathSelectors[key]['input'].setText(unicode(ipath))


from qadastre_import_form import *
from qadastre_import import *

class qadastre_import_dialog(QDialog, Ui_qadastre_import_form):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        # common qadastre methods
        self.qc = qadastre_common(self)

        # Signals/Slot Connections
        self.liDbType.currentIndexChanged[str].connect(self.qc.updateConnectionList)
        self.liDbConnection.currentIndexChanged[str].connect(self.qc.updateSchemaList)
        self.btDbCreateSchema.clicked.connect(self.createSchema)
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
        for key, item in self.pathSelectors.items():
            control = item['button']
            slot = partial(self.qc.chooseDataPath, key)
            control.clicked.connect(slot)

        # projection selector
        self.projSelectors = {
            "edigeoSourceProj" : {
                "button" : self.btEdigeoSourceProj,
                "input" : self.inEdigeoSourceProj,
                "sentence" : "Choisir la projection des fichiers Edigeo"
            },
            "edigeoTargetProj" : {
                "button" : self.btEdigeoTargetProj,
                "input" : self.inEdigeoTargetProj,
                "sentence" : "Choisir la projection de destination"
            }
        }
        for key, item in self.projSelectors.items():
            control = item['button']
            slot = partial(self.chooseProjection, key)
            control.clicked.connect(slot)

        # Set initial values
        self.dataVersionList = [ '2011', '2012']
        self.dataVersion = None
        self.dataYear = None
        self.dbType = None
        self.dbpluginclass = None
        self.connectionName = None
        self.connection = None
        self.db = None
        self.schema = None
        self.schemaList = None
        self.dbHasData = None
        self.edigeoSourceProj = None
        self.edigeoTargetProj = None
        self.edigeoDepartement = None
        self.edigeoDirection = None
        self.edigeoLot = None
        self.majicSourceDir = None
        self.edigeoSourceDir = None

        # set input values from settings
        self.sList = {
            'dataVersion': {
                'widget': self.liDataVersion,
                'wType': 'combobox',
                'property': self.dataVersion,
                'list': self.dataVersionList
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
                'wType': 'text',
                'property': self.edigeoDirection
            },
            'edigeoLot': {
                'widget': self.inEdigeoLot,
                'wType': 'text',
                'property': self.edigeoLot
            },
            'edigeoSourceProj': {
                'widget': self.inEdigeoSourceProj,
                'wType': 'text',
                'property': self.edigeoSourceProj
            },
            'edigeoTargetProj': {
                'widget': self.inEdigeoTargetProj,
                'wType': 'text',
                'property': self.edigeoTargetProj
            }
        }
        self.getValuesFromSettings()

        self.qadastreImportOptions = {
            'dataVersion' : '2012',
            'dataYear' : '2011',
            'edigeoSourceDir' : None,
            'edigeoSourceProj' : None,
            'edigeoTargetProj' : None,
            'majicSourceDir' : None
        }

        s = QSettings()
        self.majicSourceFileNames = [
            {'key': '[FICHIER_BATI]',
                'value': s.value("qadastre/batiFileName", 'REVBATI.800', type=str)},
            {'key': '[FICHIER_FANTOIR]',
                'value': s.value("qadastre/fantoirFileName", 'TOPFANR.800', type=str)},
            {'key': '[FICHIER_LOTLOCAL]',
                'value': s.value("qadastre/lotlocalFileName", 'REVD166.800', type=str)},
            {'key': '[FICHIER_NBATI]',
                'value': s.value("qadastre/nbatiFileName", 'REVNBAT.800', type=str)},
            {'key': '[FICHIER_PDL]',
                'value': s.value("qadastre/pdlFileName", 'REVFPDL.800', type=str)},
            {'key': '[FICHIER_PROP]',
                'value': s.value("qadastre/propFileName", 'REVPROP.800', type=str)}
        ]


    def onClose(self):
        '''
        Close dialog
        '''
        self.close()


    def getValuesFromSettings(self):
        '''
        get values from QGIS settings
        and set input fields appropriately
        '''
        s = QSettings()
        for k,v in self.sList.items():
            value = s.value("qadastre/%s" % k, '', type=str)
            if value and value != 'None' and v['widget']:
                if v['wType'] == 'text':
                    v['widget'].setText(str(value))
                if v['wType'] == 'spinbox':
                    v['widget'].setValue(int(value))
                if v['wType'] == 'combobox':
                    listDic = {v['list'][i]:i for i in range(0, len(v['list']))}
                    v['widget'].setCurrentIndex(listDic[value])

    def populateDataVersionCombobox(self):
        '''
        Populate the list of data version (representing a year)
        '''
        self.liDataVersion.clear()
        for year in self.dataVersionList:
            self.liDataVersion.addItem(year)




    def createSchema(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            if self.db == None:
                QMessageBox.information(
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


    def chooseProjection(self, key):
        '''
        Let the user choose a SCR
        '''
        header = u"Choisir la projection"
        sentence = self.projSelectors[key]['sentence']
        projSelector = QgsGenericProjectionSelector(self)
        projSelector.setMessage( "<h2>%s</h2>%s" % (header.encode('UTF8'), sentence.encode('UTF8')) )
        projSelector.setSelectedAuthId(self.qc.defaultAuthId)
        if projSelector.exec_():
            self.crs = QgsCoordinateReferenceSystem( projSelector.selectedCrsId(), QgsCoordinateReferenceSystem.InternalCrsId )
            if len(projSelector.selectedAuthId()) == 0:
                QMessageBox.information(
                    self,
                    self.tr("Qadastre"),
                    self.tr(u"Aucun système de coordonnée de référence valide n'a été sélectionné")
                )
                return
            else:
                self.projSelectors[key]['input'].clear()
                self.projSelectors[key]['input'].setText(self.crs.authid() + " - " + self.crs.description())
        else:
            return

    def processImport(self):
        '''
        Lancement du processus d'import
        '''
        if not self.db:
            msg = u'Veuillez sélectionner une base de données'
            QMessageBox.critical(self, self.tr("Qadatre"), self.tr(msg))
            return None

        self.dataVersion = unicode(self.liDataVersion.currentText())
        self.dataYear = unicode(self.inDataYear.text())
        self.schema = unicode(self.liDbSchema.currentText())
        self.majicSourceDir = str(self.inMajicSourceDir.text().encode('utf-8')).strip(' \t')
        self.edigeoSourceDir = str(self.inEdigeoSourceDir.text().encode('utf-8')).strip(' \t')
        self.edigeoDepartement = unicode(self.inEdigeoDepartement.text())
        self.edigeoDirection = unicode(self.inEdigeoDirection.text())
        self.edigeoLot = unicode(self.inEdigeoLot.text())
        self.edigeoSourceProj = unicode(self.inEdigeoSourceProj.text().split( " - " )[ 0 ])
        self.edigeoTargetProj = unicode(self.inEdigeoTargetProj.text().split( " - " )[ 0 ])

        # store chosen data in QGIS settings
        s = QSettings()
        s.setValue("qadastre/dataVersion", str(self.dataVersion))
        s.setValue("qadastre/dataYear", int(self.dataYear))
        s.setValue("qadastre/majicSourceDir", str(self.majicSourceDir))
        s.setValue("qadastre/edigeoSourceDir", str(self.edigeoSourceDir))
        s.setValue("qadastre/edigeoDepartement", str(self.edigeoDepartement))
        s.setValue("qadastre/edigeoDirection", str(self.edigeoDirection))
        s.setValue("qadastre/edigeoLot", str(self.edigeoLot))
        s.setValue("qadastre/edigeoSourceProj", str(self.edigeoSourceProj))
        s.setValue("qadastre/edigeoTargetProj", str(self.edigeoTargetProj))


        # qadastreImport instance
        qi = qadastreImport(self)

        # Check if structure already exists in the database/schema
        self.qc.checkDatabaseForExistingStructure()

        #~ # Run Script for creating tables
        if not self.dbHasData:
            qi.installOpencadastreStructure()

        # Run MAJIC import
        if os.path.exists(self.majicSourceDir):
            qi.importMajic()

        # Run Edigeo import
        if os.path.exists(self.edigeoSourceDir):
            qi.importEdigeo()

        qi.endImport()

# --------------------------------------------------------
#        load - Load data from database
# --------------------------------------------------------

from qadastre_load_form import *
from qadastre_loading import *

class qadastre_load_dialog(QDockWidget, Ui_qadastre_load_form):
    def __init__(self, iface):
        QDockWidget.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self)
        self.mc = self.iface.mapCanvas()

        # common qadastre methods
        self.qc = qadastre_common(self)

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
        self.dbHasData = None

        # default style to apply for Qadastre layers
        self.themeDir = unicode(self.liTheme.currentText())
        if not os.path.exists(os.path.join(
            self.qc.plugin_dir,
            "styles/%s" % self.themeDir
        )):
            self.themeDir = 'classique'

        # set Qadastre SVG path if not set
        qadastreSvgPath = os.path.join(
            self.qc.plugin_dir,
            "styles/%s/svg" % self.themeDir
        )
        s = QSettings()
        qgisSvgPaths = s.value("svg/searchPathsForSVG", 10, type=str)
        if not qadastreSvgPath in qgisSvgPaths:
            s.setValue("svg/searchPathsForSVG", qadastreSvgPath)
            self.qc.updateLog(u"* Le chemin contenant les SVG du plugin Qadastre a été ajouté dans les options de QGIS")

        # Signals/Slot Connections
        self.liDbType.currentIndexChanged[str].connect(self.qc.updateConnectionList)
        self.liDbConnection.currentIndexChanged[str].connect(self.qc.updateSchemaList)
        self.btProcessLoading.clicked.connect(self.onProcessLoadingClicked)

    def onProcessLoadingClicked(self):
        '''
        Activate the loading of layers
        from database tables
        when user clicked on button
        '''
        if self.connection:
            if self.db:
                ql = qadastreLoading(self)
                ql.processLoading()



# --------------------------------------------------------
#        search - search for data among database
# --------------------------------------------------------

from qadastre_search_form import *

class qadastre_search_dialog(QDockWidget, Ui_qadastre_search_form):
    def __init__(self, iface):
        QDockWidget.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self)

        # common qadastre methods
        self.qc = qadastre_common(self)

        self.mc = self.iface.mapCanvas()
        self.communeLayer = None
        self.communeFeatures = None
        self.communeRequest = None
        self.selectedCommuneFeature = None
        self.sectionLayer = None
        self.sectionFeatures = None
        self.sectionRequest = None
        self.sectionCommuneFeature = None

        self.searchComboBoxes = {
            'commune': {
                'widget': self.liCommune,
                'labelAttribute': 'tex2',
                'table': 'geo_commune', 'geomCol': 'geom', 'sql': '',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid','tex2','idu','geo_commune','geom'],
                'orderBy': ['tex2'],
                'features': None,
                'chosenFeature': None,
            },
            'section': {
                'widget': self.liSection,
                'labelAttribute': 'idu',
                'table': 'geo_section', 'geomCol': 'geom', 'sql': '',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid','tex','idu','geo_commune','geo_section','geom'],
                'orderBy': ['tex'],
                'features': None,
                'chosenFeature': None
            },
            'parcelle': {
                'widget': self.liParcelle,
                'labelAttribute': 'idu',
                'table': 'geo_parcelle', 'geomCol': 'geom', 'sql': '',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid','tex','idu','geo_section','geom'],
                'orderBy': ['geo_parcelle'],
                'features': None,
                'chosenFeature': None,
                'connector': None
            },
            'proprietaire': {
                'widget': self.liProprietaire,
                'labelAttribute': 'idu',
                'table': 'geo_parcelle',
                'layer': None,
                'request': None,
                'attributes': ['comptecommunal','idu','geom'],
                'orderBy': ['ddenom'],
                'features': None,
                'chosenFeature': None,
                'connector': None,
                'search': {
                    'button' : self.btSearchProprietaire,
                    'minlen': 3
                }
            },
            'parcelle_proprietaire': {
                'widget': self.liParcelleProprietaire,
                'labelAttribute': 'idu',
                'table': 'geo_parcelle', 'geomCol': 'geom', 'sql': '',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid','tex','idu','comptecommunal','geom'],
                'orderBy': ['geo_parcelle'],
                'features': None,
                'chosenFeature': None,
                'connector': None
            },
            'adresse': {
                'widget': self.liAdresse,
                'labelAttribute': 'dvoilib',
                'table': 'geo_parcelle',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid','dvoilib','idu','geom'],
                'orderBy': ['dvoilib'],
                'features': None,
                'chosenFeature': None,
                'connector': None,
                'search': {
                    'button' : self.btSearchAdresse,
                    'minlen': 3
                }
            },
            'parcelle_adresse': {
                'widget': self.liParcelleAdresse,
                'labelAttribute': 'idu',
                'table': 'geo_parcelle', 'geomCol': 'geom', 'sql': '',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid','tex','idu','dvoilib','geom'],
                'orderBy': ['geo_parcelle'],
                'features': None,
                'chosenFeature': None,
                'connector': None
            }
        }

        # setup some gui items
        self.setupCommuneCombobox()
        self.setupSectionCombobox()

        # signals/slots

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
                'comboboxes': ['commune', 'section', 'parcelle']
            },
            'adresse':{
                'buttons':{
                    'centre': self.btCentrerAdresse,
                    'zoom': self.btZoomerAdresse,
                    'select': self.btSelectionnerAdresse
                },
                'comboboxes': ['adresse', 'parcelle_adresse']
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
        for key, item in self.zoomButtons.items():
            for k, button in item['buttons'].items():
                control = button
                slot = partial(zoomButtonsFunctions[k], key)
                control.clicked.connect(slot)

        # Manuel search button and combo (proprietaire, adresse)
        for key, item in self.searchComboBoxes.items():
            if item.has_key('search'):
                # search button
                control = item['search']['button']
                slot = partial(self.searchItem, key)
                control.clicked.connect(slot)
                # when a search result is chosen in combobox
                control = self.searchComboBoxes[key]['widget']
                slot = partial(self.onSearchItemChoose, key)
                control.currentIndexChanged[str].connect(slot)

        # adresse combobox
        self.liParcelleAdresse.currentIndexChanged[str].connect(self.onParcelleAdresseUpdate)
        self.liParcelleAdresse.editTextChanged[str].connect(self.onParcelleAdresseEdit)
        self.btResetParcelleAdresse.clicked.connect(self.resetParcelleAdresse)
        # commune combobox
        self.liCommune.editTextChanged[str].connect(self.onCommuneUpdate)
        self.liCommune.currentIndexChanged[str].connect(self.onCommuneChoose)
        self.btResetCommune.clicked.connect(self.resetCommune)
        # section combobox
        self.liSection.currentIndexChanged[str].connect(self.onSectionUpdate)
        self.liSection.editTextChanged[str].connect(self.onSectionEdit)
        self.btResetSection.clicked.connect(self.resetSection)
        # parcelle combobox
        self.liParcelle.currentIndexChanged[str].connect(self.onParcelleUpdate)
        self.liParcelle.editTextChanged[str].connect(self.onParcelleEdit)
        self.btResetParcelle.clicked.connect(self.resetParcelle)

        # proprietaire combobox
        self.liParcelleProprietaire.currentIndexChanged[str].connect(self.onParcelleProprietaireUpdate)
        self.liParcelleProprietaire.editTextChanged[str].connect(self.onParcelleProprietaireEdit)
        self.btResetParcelleProprietaire.clicked.connect(self.resetParcelleProprietaire)


    def setupSearchCombobox(self, combo, filterExpression=None, queryMode='qgis'):
        '''
        Create and fill a line edit with town list
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
        layer = self.qc.getLayerFromLegendByTableProps(
            searchCombo['table'],
            searchCombo['geomCol'],
            searchCombo['sql']
        )
        self.searchComboBoxes[combo]['layer'] = layer
        if layer:

            # Get all features
            keepattributes = self.searchComboBoxes[combo]['attributes']
            request = QgsFeatureRequest().setSubsetOfAttributes(
                keepattributes,
                layer.pendingFields()
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
                emptyLabel = u'-- %s résultats --' % len(features)
            else:
                emptyLabel = ''
            cb.addItem('%s' % emptyLabel, '')
            for feat in features:
                keep = True
                if qe:
                    if not qe.evaluate(feat):
                        keep = False
                if keep:
                    itemList.append(feat[labelAttribute])
                    cb.addItem(feat[labelAttribute], feat)

            # Activate autocompletion
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


    def getFeaturesFromSqlQuery(self, layer, filterExpression=None, attributes='*', orderBy=None):
        '''
        Get data from a db table,
        optionnally filtered by given expression
        and get corresponding QgsFeature objects
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Get connection parameters
        connectionParams = self.qc.getConnectionParameterFromDbLayer(layer)
        if not connectionParams:
            QApplication.restoreOverrideCursor()
            return None

        # Use db_manager tool to run the query
        uri = QgsDataSourceURI()
        uri.setConnection(
            connectionParams['host'],
            connectionParams['port'],
            connectionParams['dbname'],
            connectionParams['user'],
            connectionParams['password']
        )
        connector = PostGisDBConnector(uri)

        # SQL
        sql = ' SELECT %s' % ', '.join(attributes)
        sql+= ' FROM "%s"."%s"' % (connectionParams['schema'], connectionParams['table'])
        sql+= " WHERE 2>1"
        if filterExpression:
            sql+= " AND %s" % filterExpression
        if orderBy:
            sql+= ' ORDER BY %s' % ', '.join(orderBy)

        # Get data
        [header, data, rowCount] = self.qc.fetchDataFromSqlQuery(connector, sql)

        # Get features
        features = []
        for line in data:
            request = QgsFeatureRequest().setSubsetOfAttributes(attributes, layer.pendingFields()).setFilterFid(int(line[0]))
            for feat in layer.getFeatures(request):
                features.append(feat)

        QApplication.restoreOverrideCursor()
        return features


    def setupCommuneCombobox(self):
        '''
        Create and fill a line edit with commune list
        And add autiocompletion
        '''
        self.setupSearchCombobox('commune', None, 'sql')


    def setupSectionCombobox(self):
        '''
        Create and fill a line edit with section list
        And add autiocompletion
        '''
        self.setupSearchCombobox('section', None, 'sql')


    def getFeatureFromComboboxValue(self, combo):
        '''
        Update the combo box content
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



    def onCommuneChoose(self):
        '''
        Update the section combo box content
        depending on commune selected
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Get commune feature and store it
        self.getFeatureFromComboboxValue('commune')

        # update section combobox
        communeFeature = self.searchComboBoxes['commune']['chosenFeature']
        if communeFeature:
            filterExpression = "geo_commune = '%s'" % communeFeature['geo_commune']
            self.setupSearchCombobox('section', filterExpression, 'sql')
        else:
            self.setupSearchCombobox('section', None, 'sql')
        QApplication.restoreOverrideCursor()


    def onCommuneUpdate(self):
        self.searchComboBoxes['commune']['chosenFeature'] = None


    def onSectionUpdate(self):
        '''
        Update the section combo box content
        depending on section selected
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)
        # Get commune feature and store it
        self.getFeatureFromComboboxValue('section')

        # update parcelle combobox only if section set
        sectionFeature = self.searchComboBoxes['section']['chosenFeature']
        if sectionFeature:
            filterExpression = "geo_section = '%s'" % sectionFeature['geo_section']
            self.setupSearchCombobox('parcelle', filterExpression, 'sql')

        QApplication.restoreOverrideCursor()

    def onSectionEdit(self):
        # Empty previous stored feature
        self.searchComboBoxes['section']['chosenFeature'] = None


    def onParcelleUpdate(self):
        '''
        Get commune feature from chosen item in combobox
        '''
        self.getFeatureFromComboboxValue('parcelle')

    def onParcelleEdit(self):
        # Empty previous stored feature
        self.searchComboBoxes['parcelle']['chosenFeature'] = None


    def setZoomToChosenSearchCombobox(self, combo):
        '''
        Zoom to the item
        selected in Commune Section or Parcelle
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
            self.mc.setExtent(extent)
            self.mc.refresh()


    def setCenterToChosenSearchCombobox(self, combo):
        '''
        Center to the chosen commune
        in the combo box
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
            self.mc.setExtent(extent)

            # the set the scale back
            self.mc.zoomScale(scale)
            self.mc.refresh()

    def setSelectionToChosenSearchCombobox(self, combo):
        '''
        Select the feature
        corresponding to the chosen commune
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


    def onParcelleProprietaireUpdate(self):
        '''
        Get commune feature from chosen item in combobox
        '''
        self.getFeatureFromComboboxValue('parcelle_proprietaire')

    def onParcelleProprietaireEdit(self):
        # Empty previous stored feature
        self.searchComboBoxes['parcelle_proprietaire']['chosenFeature'] = None


    def searchItem(self, key):
        '''
        Query database to get item (adresse, proprietaire)
        corresponding to given name
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Get value
        combo = self.searchComboBoxes[key]['widget']
        searchValue = unicode(combo.currentText())

        # Abort if searchValue length too small
        minlen = self.searchComboBoxes[key]['search']['minlen']
        if len(searchValue) < minlen:
            self.qc.updateLog(u"%s caractères minimum requis pour la recherche !" % minlen)
            QApplication.restoreOverrideCursor()
            return None

        # Get database connection parameters from a qgis layer
        dbtable = self.searchComboBoxes[key]['table']
        layer = self.qc.getLayerFromLegendByTableProps(dbtable)
        if not layer:
            QApplication.restoreOverrideCursor()
            return None
        connectionParams = self.qc.getConnectionParameterFromDbLayer(layer)
        if not connectionParams:
            QApplication.restoreOverrideCursor()
            return None

        # Use db_manager tool to run the query
        uri = QgsDataSourceURI()
        uri.setConnection(
            connectionParams['host'],
            connectionParams['port'],
            connectionParams['dbname'],
            connectionParams['user'],
            connectionParams['password']
        )
        connector = PostGisDBConnector(uri)

        # SQL
        if key == 'adresse':
            sql = ' SELECT DISTINCT dvoilib AS k'
            sql+= ' FROM "%s".geo_parcelle' % connectionParams['schema']
            sql+= " WHERE dvoilib LIKE '%s%%'" % searchValue.upper()
            sql+= ' ORDER BY dvoilib'
        if key == 'proprietaire':
            sql = " SELECT trim(ddenom) AS k, string_agg(comptecommunal, ',') AS v"
            sql+= ' FROM "%s".proprietaire' % connectionParams['schema']
            sql+= " WHERE ddenom LIKE '%s%%'" % searchValue.upper()
            sql+= ' GROUP BY ddenom, dlign4'
            sql+= ' ORDER BY ddenom'
        [header, data, rowCount] = self.qc.fetchDataFromSqlQuery(connector, sql)

        # Fill  combobox
        self.qc.updateLog(u"%s résultats correpondent à '%s'" % (rowCount, searchValue))
        cb = self.searchComboBoxes[key]['widget']
        cb.clear()
        cb.addItem(u'%s résultat(s)' % rowCount , '')
        itemList = []
        for line in data:
            if key == 'adresse':
                val = unicode(line[0])
            if key == 'proprietaire':
                val = ["'%s'" % a for a in line[1].split(',')]
            cb.addItem('%s' % line[0].strip(), val )

        # Restore cursor
        QApplication.restoreOverrideCursor()


    def onSearchItemChoose(self, key):
        '''
        Select parcelles corresponding
        to chosen item in combo box
        (adresse, proprietaire)
        '''

        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Get value
        combo = self.searchComboBoxes[key]['widget']
        value = combo.itemData(combo.currentIndex())
        if key == 'adresse':
            value = unicode(value).upper()
        if not value:
            QApplication.restoreOverrideCursor()
            return None

        # Set filter expression
        if key == 'adresse':
            filterExpression = "dvoilib = '%s'" % value
        if key == 'proprietaire':
            filterExpression = "comptecommunal IN (%s)" % ', '.join(value)
        self.qc.updateLog(filterExpression)

        # Get data
        [layer, features] = self.setupSearchCombobox(
            'parcelle_%s' % key,
            filterExpression,
            'sql'
        )

        # Set properties
        self.searchComboBoxes[key]['layer'] = layer
        self.searchComboBoxes[key]['features'] = features
        self.searchComboBoxes[key]['chosenFeature'] = features

        self.qc.updateLog(
            u"%s parcelle(s) trouvée(s) pour '%s'" % (
                len(features),
                combo.currentText()
            )
        )

        QApplication.restoreOverrideCursor()


    def onParcelleAdresseUpdate(self):
        '''
        Get commune feature from chosen item in combobox
        '''
        self.getFeatureFromComboboxValue('parcelle_adresse')

    def onParcelleAdresseEdit(self):
        # Empty previous stored feature
        self.searchComboBoxes['parcelle_adresse']['chosenFeature'] = None

    def setCenterToChosenItem(self, key):
        '''
        Set map center corresponding
        to the chosen feature(s)
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
        Zoom to the feature(s)
        corresponding to the chosen item
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
        Select the parcelle features
        corresponding to the chosen item
        '''
        w = None
        for item in self.zoomButtons[key]['comboboxes']:
            if self.searchComboBoxes[item]['chosenFeature'] \
            and self.searchComboBoxes[item]['layer']:
                w = item
        if w:
            self.setSelectionToChosenSearchCombobox(w)


    def resetParcelleAdresse(self):
        self.liParcelleAdresse.setCurrentIndex(0)

    def resetCommune(self):
        self.liCommune.setCurrentIndex(0)

    def resetSection(self):
        self.liSection.setCurrentIndex(0)

    def resetParcelle(self):
        self.liParcelle.setCurrentIndex(0)

    def resetParcelleProprietaire(self):
        self.liParcelleProprietaire.setCurrentIndex(0)


    def onVisibilityChange(self, visible):
        if visible:
            self.setupCommuneCombobox()
        else:
            self.txtLog.clear()



# --------------------------------------------------------
#        Option - Let the user configure options
# --------------------------------------------------------

from qadastre_option_form import *

class qadastre_option_dialog(QDialog, Ui_qadastre_option_form):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        # common qadastre methods
        self.qc = qadastre_common(self)

        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        self.buttonBox.rejected.connect(self.onReject)
        self.buttonBox.accepted.connect(self.onAccept)

        # path buttons selectors
        # paths needed to be chosen by user
        self.pathSelectors = {
            "tempDir" : {
                "button" : self.btTempDir,
                "input" : self.inTempDir
            }
        }
        from functools import partial
        for key, item in self.pathSelectors.items():
            control = item['button']
            slot = partial(self.qc.chooseDataPath, key)
            control.clicked.connect(slot)

        # Set initial widget values
        self.getValuesFromSettings()



    def getValuesFromSettings(self):
        '''
        Get majic file names and other options
        from settings and set corresponding inputs
        '''
        s = QSettings()
        batiFileName = s.value("qadastre/batiFileName", 'REVBATI.800', type=str)
        if batiFileName:
            self.inMajicBati.setText(batiFileName)
        fantoirFileName = s.value("qadastre/fantoirFileName", 'TOPFANR.800', type=str)
        if fantoirFileName:
            self.inMajicFantoir.setText(fantoirFileName)
        lotlocalFileName = s.value("qadastre/lotlocalFileName", 'REVD166.800', type=str)
        if lotlocalFileName:
            self.inMajicLotlocal.setText(lotlocalFileName)
        nbatiFileName = s.value("qadastre/nbatiFileName", 'REVNBAT.800', type=str)
        if nbatiFileName:
            self.inMajicNbati.setText(nbatiFileName)
        pdlFileName = s.value("qadastre/pdlFileName", 'REVFPDL.800', type=str)
        if pdlFileName:
            self.inMajicPdl.setText(pdlFileName)
        propFileName = s.value("qadastre/propFileName", 'REVPROP.800', type=str)
        if propFileName:
            self.inMajicProp.setText(propFileName)
        tempDir = s.value("qadastre/tempDir", '%s' % tempfile.gettempdir(), type=str)
        if tempDir:
            self.inTempDir.setText(tempDir)


    def onAccept(self):
        '''
        Save options when pressing OK button
        '''

        # Save Majic file names
        s = QSettings()
        s.setValue("qadastre/batiFileName", self.inMajicBati.text().strip(' \t\n\r'))
        s.setValue("qadastre/fantoirFileName", self.inMajicFantoir.text().strip(' \t\n\r'))
        s.setValue("qadastre/lotlocalFileName", self.inMajicLotlocal.text().strip(' \t\n\r'))
        s.setValue("qadastre/nbatiFileName", self.inMajicNbati.text().strip(' \t\n\r'))
        s.setValue("qadastre/pdlFileName", self.inMajicPdl.text().strip(' \t\n\r'))
        s.setValue("qadastre/propFileName", self.inMajicProp.text().strip(' \t\n\r'))

        # Save temp dir
        s.setValue("qadastre/tempDir", self.inTempDir.text().strip(' \t\n\r'))

        self.accept()

    def onReject(self):
        '''
        Run some actions when
        the user closes the dialog
        '''
        string = "qadastre option dialog closed"
        self.close()



# --------------------------------------------------------
#        About - Let the user display the about dialog
# --------------------------------------------------------

from qadastre_about_form import *

class qadastre_about_dialog(QDialog, Ui_qadastre_about_form):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        # common qadastre methods
        self.qc = qadastre_common(self)

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
