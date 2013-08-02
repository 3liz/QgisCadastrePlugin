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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import QgsGenericProjectionSelector

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

from db_manager.db_plugins.plugin import DBPlugin, Schema, Table
from db_manager.db_plugins import createDbPlugin

# --------------------------------------------------------
#        import - Import data from EDIGEO and MAJIC files
# --------------------------------------------------------


from qadastre_import_form import *
from qadastre_import import *

class qadastre_import_dialog(QDialog, Ui_qadastre_import_form):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        
        # Signals/Slot Connections
        self.liDbType.currentIndexChanged[str].connect(self.updateConnectionList)
        self.liDbConnection.currentIndexChanged[str].connect(self.updateSchemaList)
        self.btProcessImport.clicked.connect(self.processImport)
        self.btDbCreateSchema.clicked.connect(self.createSchema)
        
        # path buttons selectors
        from functools import partial
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
            slot = partial(self.chooseDataPath, key)
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
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/Qadastre"
        
        self.dbType = None
        self.dbpluginclass = None
        self.connectionName = None
        self.connection = None
        self.db = None
        self.schema = None
        self.schemaList = None
        self.edigeoSourceProj = None
        self.edigeoTargetProj = None
        
        self.qadastreImportOptions = {
            'dataVersion' : '2012',
            'dataYear' : '2011',
            'edigeoSourceDir' : None,
            'edigeoSourceProj' : None,
            'edigeoTargetProj' : None,
            'majicSourceDir' : None
        }
        
        self.majicSourceFileNames = {
            'bati' : 'REVBATI.800',
            'fantoir' : 'TOPFANR.800',
            'lotlocal': 'REVD166.800',
            'nbati': 'REVNBAT.800',
            'pdl': 'REVFPDL.800',
            'prop': 'REVPROP.800'
        }
        
    def populateDataVersionCombobox(self):
        '''
        Populate the list of data version (representing a year)
        '''
        self.liDataVersion.clear()
        for year in self.dataVersionList:
            self.liDataVersion.addItem(year)
    
    def updateLog(self, msg):
        '''
        Update the log 
        '''
        self.txtImportLog.append(msg)
        
        
    def updateConnectionList(self):
        '''
        Update the combo box containing the database connection list
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)
        
        dbType = unicode(self.liDbType.currentText()).lower()       
        self.liDbConnection.clear()
        
        if self.liDbType.currentIndex() != 0:
            self.dbType = dbType
            # instance of db_manager plugin class
            dbpluginclass = createDbPlugin( dbType )
            self.dbpluginclass = dbpluginclass
          
            # fill the connections combobox
            for c in dbpluginclass.connections():
                self.liDbConnection.addItem( unicode(c.connectionName()))
        QApplication.restoreOverrideCursor()

    def toggleSchemaList(self, t):
        '''
        Toggle Schema list and inputs
        '''
        self.liDbSchema.setEnabled(t)
        self.inDbCreateSchema.setEnabled(t)
        self.btDbCreateSchema.setEnabled(t)   
        

    def updateSchemaList(self):
        '''
        Update the combo box containing the schema list if relevant
        '''
        self.liDbSchema.clear()
        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        connectionName = unicode(self.liDbConnection.currentText())
        self.connectionName = connectionName
        dbType = unicode(self.liDbType.currentText()).lower()

        # Deactivate schema fields
        self.toggleSchemaList(False)
        
        if dbType == 'postgis':            
            
            # Activate schema fields
            self.toggleSchemaList(True)
            
            # Get schema list
            dbpluginclass = createDbPlugin( dbType, connectionName )
            self.dbpluginclass = dbpluginclass
            connection = dbpluginclass.connect()
            if connection:
                self.connection = connection
                db = dbpluginclass.database()
                if db:
                    self.db = db
                    self.schemaList = []
                    for s in db.schemas():
                        self.liDbSchema.addItem( unicode(s.name))
                        self.schemaList.append(unicode(s.name))
        QApplication.restoreOverrideCursor()


    def createSchema(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            if self.db == None:
                QMessageBox.information(self, QApplication.translate("DBManagerPlugin", "Sorry"), QApplication.translate("DBManagerPlugin", "No database selected or you are not connected to it."))
                return
            schema = self.inDbCreateSchema.text()
        finally:
            QApplication.restoreOverrideCursor()

        if schema:
            try:
                self.db.createSchema(schema)

            except BaseError as e:
            
                DlgDbError.showError(e, self)
                self.updateLog(e.msg)
                return

            finally:        
                self.updateSchemaList()
                listDic = { self.schemaList[i]:i for i in range(0, len(self.schemaList)) }
                self.liDbSchema.setCurrentIndex(listDic[schema])
                self.inDbCreateSchema.clear()
                QApplication.restoreOverrideCursor()

            
    def chooseDataPath(self, key):
        '''
        Ask the user to select a folder 
        and write down the path to appropriate field
        '''
        ipath = QFileDialog.getExistingDirectory( 
            None, 
            "Choisir le répertoire contenant les fichiers", 
            str(self.pathSelectors[key]['input'].text().encode('utf-8')).strip(' \t') 
        )
        if os.path.exists(unicode(ipath)):
            self.pathSelectors[key]['input'].setText(unicode(ipath))
            
    def chooseProjection(self, key):
        '''
        Let the user choose a SCR
        '''
        header = u"Choisir la projection"
        sentence = self.projSelectors[key]['sentence']
        projSelector = QgsGenericProjectionSelector(self)
        projSelector.setMessage( "<h2>%s</h2>%s" % (header.encode('UTF8'), sentence.encode('UTF8')) )
        if projSelector.exec_():
            self.crs = QgsCoordinateReferenceSystem( projSelector.selectedCrsId(), QgsCoordinateReferenceSystem.InternalCrsId )
            if len(projSelector.selectedAuthId()) == 0:
                QMessageBox.information(self, self.tr("Export to new projection"), self.tr("No Valid CRS selected"))
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
               
        # qadastreImport instance
        qi = qadastreImport(self)
               
        # Run Script for creating tables
        qi.installOpencadastreStructure()

        # Run Edigeo import
        if os.path.exists(self.edigeoSourceDir):
            qi.importEdigeo()

        # Run MAJIC import
        if os.path.exists(self.majicSourceDir):
            qi.importMajic()
        
        qi.endImport()

# --------------------------------------------------------
#        load - Load data from database
# --------------------------------------------------------

from qadastre_load_form import *

class qadastre_load_dialog(QDialog, Ui_qadastre_load_form):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        # Signals/Slot Connections
        
        # Set initial widget values





# --------------------------------------------------------
#        Interface - Let the user choose QGIS interface
# --------------------------------------------------------

from qadastre_interface_form import *

class qadastre_interface_dialog(QDialog, Ui_qadastre_interface_form):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        # Signals/Slot Connections
        self.btInterfaceQadastre.clicked.connect(self.change_interface)

        
        # Set initial widget values
        
    def change_interface(self):
        onetext = unicode(self.lineEdit.text())
        qadastre_interface(self, onetext)



