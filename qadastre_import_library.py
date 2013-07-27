# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Qadastre - import library
                                 A QGIS plugin
 This plugins helps users to import the french land registry ('cadastre') 
 into a database. It is meant to ease the use of the data in QGIs 
 by providing search tools and appropriate layer symbology.
                              -------------------
        begin                : 2013-06-11
        copyright            : (C) 2013 by 3liz
        email                : info@3liz.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import sys, os
import re
import time
import tempfile
import shutil
from distutils import dir_util
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

# db_manager scripts
from db_manager.db_plugins.plugin import DBPlugin, Schema, Table, BaseError
from db_manager.db_plugins import createDbPlugin
from db_manager.dlg_db_error import DlgDbError



class qadastreImportTools(QObject):

    def __init__(self, dialog, scriptDir):
        self.dialog = dialog
        self.connector = self.dialog.db.connector    
        self.scriptDir = scriptDir


    def copyFileToTemp(self, source, target):
        '''
        Copy opencadastre scripts
        into a temporary folder
        '''
        
        # copy script directory
        try:
            dir_util.copy_tree(source, target)
        except IOError, e:
            msg = u"Erreur lors de la copie des scripts d'import: %s" % e
            QMessageBox.information(self.dialog, 
            "Qadastre", msg)
            self.go = False
            return msg
    
        return None



    def replaceParametersInScript(self, scriptPath, replaceDict):
        '''
        Replace all parameters in sql scripts
        with given values
        '''

        def replfunc(match):
            return replaceDict[match.group(0)]
        regex = re.compile('|'.join(re.escape(x) for x in replaceDict))
        
        fin = open(scriptPath)
        data = fin.read()
        fin.close()
        fout = open(scriptPath, 'w')
        data = regex.sub(replfunc, data)
        fout.write(data)
        fout.close()
        
        return None

        
    def setSearchPath(self, sql, schema):
        '''
        Set the search_path parameters if postgis database
        '''        
        prefix = u'SET search_path = %s, public, pg_catalog;' % schema
        sql = prefix + sql

        return sql


    def executeSqlScript(self, scriptName):
        '''
        Execute an SQL script file
        from opencadastre
        '''
    
        QApplication.setOverrideCursor(Qt.WaitCursor)
        
        # Read sql script
        sql = open(os.path.join(self.scriptDir, scriptName)).read()
        sql = sql.decode("utf-8-sig")
        
        # Set schema if needed
        if self.dialog.dbType == 'postgis':
            sql = self.setSearchPath(sql, self.dialog.schema)
            
        if scriptName == 'create_metier.sql':
            sup = u'''
              SET search_path = %s, public, pg_catalog;
              CREATE TABLE om_parametre (
              om_parametre serial,
              libelle character varying(20) NOT NULL,
              valeur character varying(50) NOT NULL,
              om_collectivite integer NOT NULL
              );
            ''' % self.dialog.schema
            sql = sup + sql
        
        # Execute query
        c = None
        try:
            c = self.connector._execute_and_commit(sql)

        except BaseError as e:
        
            DlgDbError.showError(e, self.dialog)
            return

        finally:
            QApplication.restoreOverrideCursor()
            if c:
                c.close()
                del c
    
        return None
