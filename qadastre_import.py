# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Qadastre - import main methods
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
from datetime import datetime

# db_manager scripts
from db_manager.db_plugins.plugin import DBPlugin, Schema, Table, BaseError
from db_manager.db_plugins import createDbPlugin
from db_manager.dlg_db_error import DlgDbError
       



class qadastreImport(QObject):

    def __init__(self, dialog):
        self.dialog = dialog
        
        self.connector = self.dialog.db.connector    
        self.scriptSourceDir = os.path.join(self.dialog.plugin_dir, "scripts/opencadastre/trunk/data/pgsql")
        self.scriptDir = tempfile.mkdtemp()
        self.edigeoDir = tempfile.mkdtemp()
        self.majicDir = tempfile.mkdtemp()
        self.replaceDict = {
            '[PREFIXE]': '"%s".' % self.dialog.schema, 
            '[VERSION]': self.dialog.dataVersion,
            '[ANNEE]': self.dialog.dataYear,
            '[FICHIER_BATI]': self.dialog.majicSourceFileNames['bati'],
            '[FICHIER_FANTOIR]': self.dialog.majicSourceFileNames['fantoir'],
            '[FICHIER_LOTLOCAL]': self.dialog.majicSourceFileNames['lotlocal'],
            '[FICHIER_NBATI]': self.dialog.majicSourceFileNames['nbati'],
            '[FICHIER_PDL]': self.dialog.majicSourceFileNames['pdl'],
            '[FICHIER_PROP]': self.dialog.majicSourceFileNames['prop']
        }
        self.go = True
        self.startTime = datetime.now()
        self.step = 0
        self.totalSteps = 10
        
        self.beginImport()
        
    def beginImport(self):
        '''
        Process to run before importing data
        '''
        self.dialog.updateLog(u'<h3>Initialisation</h3>')
        self.updateProgressBar(False)
        
        # copy opencadastre script files to temporary dir
        self.copyFilesToTemp(self.scriptSourceDir, self.scriptDir)        

    def updateProgressBar(self, move=True):
        '''
        Update the progress bar
        '''
        self.step+=1
        self.dialog.pbProcessImport.setValue(int(self.step * 100/self.totalSteps))
        if not move:
            self.step-=1
            
    def updateTimer(self):
        '''
        Update the timer for each process
        '''
        b = datetime.now()
        diff = b - self.startTime
        self.dialog.updateLog(u'%s s' % diff.seconds)

    def installOpencadastreStructure(self):
        '''
        Create the empty db structure
        '''        
        # install opencadastre structure
        scriptList = [
            {'title' : u'Création des tables', 'script': 'create_metier.sql'},
            {'title' : u'Ajout des contraintes', 'script': 'create_constraints.sql'},
            {'title' : u'Ajout de la nomenclature', 'script': 'insert_nomenclatures.sql'}
        ]
        for item in scriptList:
            s = item['script']
            self.executeSqlScript(s, item['title'])
        
        return None



    def importEdigeo(self):
    
        # copy files in temp dir
        self.copyFilesToTemp(self.dialog.edigeoSourceDir, self.edigeoDir)
    
        return None
        

    def importMajic(self):
    
        self.dialog.updateLog(u'<h3>Données MAJIC3</h3>')
        self.updateProgressBar(False)
        
        # copy files in temp dir
        self.copyFilesToTemp(self.dialog.majicSourceDir, self.majicDir)
        
        # replace parameters
        replaceDict = self.replaceDict.copy()
        replaceDict['[CHEMIN]'] = os.path.realpath(self.majicDir) + '/'
        
        scriptList = [
            {'title' : u'Suppression des contraintes', 'script' : 'COMMUN/suppression_constraintes.sql'},
            {'title' : u'Purge des données', 'script' : 'COMMUN/majic3_purge_donnees.sql'},
            {'title' : u'Import des fichiers', 'script' : 'COMMUN/majic3_import_donnees_brutes.sql'},
            {'title' : u'Formatage des données', 'script' : '%s/majic3_formatage_donnees.sql' % self.dialog.dataVersion},
            {'title' : u'Restauration des contraintes', 'script' : 'COMMUN/creation_contraintes.sql'},
            {'title' : u'Purge des données brutes', 'script' : 'COMMUN/majic3_purge_donnees_brutes.sql'}
        ]
        for item in scriptList:
            s = item['script']
            scriptPath = os.path.join(self.scriptDir, s)
            self.replaceParametersInScript(scriptPath, replaceDict)
            self.executeSqlScript(s, item['title'])
        
        self.endImport()
        
        return None

        
    def endImport(self):
        '''
        Actions done when import has finished
        '''

        # Remove the temp folders
        try:            
            shutil.rmtree(self.scriptDir)
            shutil.rmtree(self.edigeoDir)
            shutil.rmtree(self.majicDir)
            
        except IOError, e:
            msg = u"Erreur lors de la suppresion des répertoires temporaires: %s" % e
            self.go = False
            return msg

        if self.go:
            msg = u"Import terminé"
        else:
            msg = u"Des erreurs ont été rencontrées pendant l'import. Veuillez consulter le log."

        QMessageBox.information(self.dialog, "Qadastre", msg)
        self.step = self.totalSteps
        self.updateProgressBar()
        
        return None
        
    #
    # TOOLS
    #


    def copyFilesToTemp(self, source, target):
        '''
        Copy opencadastre scripts
        into a temporary folder
        '''
        if self.go:
        
            self.dialog.updateLog(u'* Copie du répertoire %s' % source.decode('UTF8'))
            self.updateProgressBar(False)
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # copy script directory
            try:
                dir_util.copy_tree(source, target)
                os.chmod(target, 0777)
            except IOError, e:
                msg = u"Erreur lors de la copie des scripts d'import: %s" % e
                QMessageBox.information(self.dialog, 
                "Qadastre", msg)
                self.go = False
                return msg
        
            finally:
                QApplication.restoreOverrideCursor()
                self.updateTimer()
                self.updateProgressBar()
        
        return None



    def replaceParametersInScript(self, scriptPath, replaceDict):
        '''
        Replace all parameters in sql scripts
        with given values
        '''
        
        if self.go:

            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            def replfunc(match):
                return replaceDict[match.group(0)]
            regex = re.compile('|'.join(re.escape(x) for x in replaceDict))

            try:       
                fin = open(scriptPath)
                data = fin.read().decode("utf-8-sig")
                fin.close()
                fout = open(scriptPath, 'w')
                data = regex.sub(replfunc, data).encode('utf-8')
                fout.write(data)
                fout.close()
                
            except IOError, e:
                msg = u"Erreur lors du paramétrage des scripts d'import: %s" % e
                self.go = False
                self.dialog.updateLog(msg)
                return msg
                
            finally:
                QApplication.restoreOverrideCursor()            
        
        return None

        
    def setSearchPath(self, sql, schema):
        '''
        Set the search_path parameters if postgis database
        '''        
        prefix = u'SET search_path = %s, public, pg_catalog;' % schema
        if re.search('^BEGIN;', sql):
            sql = sql.replace('BEGIN;', 'BEGIN;%s' % prefix)
        else:
            sql = prefix + sql

        return sql


    def executeSqlScript(self, scriptName, scriptTitle):
        '''
        Execute an SQL script file
        from opencadastre
        '''
        
        if self.go:

            self.dialog.updateLog(u'* %s' % scriptTitle)
            self.updateProgressBar(False)
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # Read sql script
            sql = open(os.path.join(self.scriptDir, scriptName)).read()
            sql = sql.decode("utf-8-sig")
            
            # Set schema if needed
            if self.dialog.dbType == 'postgis':
                sql = self.setSearchPath(sql, self.dialog.schema)

            # Execute query
            c = None
            try:
                c = self.connector._execute_and_commit(sql)

            except BaseError as e:
            
                DlgDbError.showError(e, self.dialog)
                self.go = False
                self.dialog.updateLog(e.msg)
                return

            finally:
                QApplication.restoreOverrideCursor()
                if c:
                    c.close()
                    del c
                self.updateTimer()
                self.updateProgressBar()
    
        return None
