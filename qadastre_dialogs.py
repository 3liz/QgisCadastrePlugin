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

from qadastre_library import *

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

from db_manager.db_plugins.plugin import DBPlugin, Schema, Table
from db_manager.db_plugins import createDbPlugin

# --------------------------------------------------------
#        import - Import data from EDIGEO and MAJIC files
# --------------------------------------------------------

from qadastre_import_form import *

class qadastre_import_dialog(QDialog, Ui_qadastre_import_form):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        # Signals/Slot Connections
        self.liDbType.currentIndexChanged[str].connect(self.updateConnectionList)
        self.liDbConnection.currentIndexChanged[str].connect(self.updateSchemaList)
        
        # Set initial values
        
    
    def updateLog(self, msg):
        '''
        Update the log 
        '''
        self.txtImportLog.append(msg)
        
        
    def updateConnectionList(self):
        '''
        Update the combo box containing the database connection list
        '''
        dbType = unicode(self.liDbType.currentText()).lower()
        
        # instance of db_manager plugin class
        dbpluginclass = createDbPlugin( dbType )
          
        # fill the connections combobox
        self.liDbConnection.clear()
        self.liDbConnection.addItem( u"--Choisir--")
        for c in dbpluginclass.connections():
            self.liDbConnection.addItem( unicode(c.connectionName()))


    def updateSchemaList(self):
        '''
        Update the combo box containing the schema list if relevant
        '''
        dbConnectionName = unicode(self.liDbConnection.currentText())
        dbType = unicode(self.liDbType.currentText()).lower()
        
        self.liDbSchema.clear()
        if dbConnectionName != u"--Choisir--":
            
            if dbType == 'postgis':
                # Activate schema fields
                self.liDbSchema.setEnabled(True)              
                self.liDbSchema.addItem( u"--Choisir--")
                
                # Get schema list
                dbpluginclass = createDbPlugin( dbType, dbConnectionName )
                con = dbpluginclass.connect()
                db = dbpluginclass.database()
                for s in db.schemas():
                    self.liDbSchema.addItem( unicode(s.name))                
            else:
                # Deactivate schema fields
                self.liDbSchema.setEnabled(False)
        
        

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



