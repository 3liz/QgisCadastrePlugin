# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Cadastre - import main methods
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

import sys, os, glob
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


class cadastreImport(QObject):

    def __init__(self, dialog):
        self.dialog = dialog

        # common cadastre methods
        self.qc = self.dialog.qc

        self.db = self.dialog.db
        self.connector = self.db.connector
        self.scriptSourceDir = os.path.join(self.qc.plugin_dir, "scripts/opencadastre/trunk/data/pgsql")

        # projections
        if self.dialog.doEdigeoImport:
            self.sourceSridFull = self.dialog.edigeoSourceProj
            self.targetSridFull = self.dialog.edigeoTargetProj
            self.sourceSrid = self.sourceSridFull.split(":")[1]
            self.targetSrid = self.targetSridFull.split(":")[1]

        # create temporary directories
        s = QSettings()
        tempDir = s.value("cadastre/tempDir", '%s' % tempfile.gettempdir(), type=str)
        self.scriptDir = tempfile.mkdtemp('', 'cad_script_', tempDir)
        self.edigeoDir = tempfile.mkdtemp('', 'cad_edigeo_source_', tempDir)
        self.edigeoPlainDir = tempfile.mkdtemp('', 'cad_edigeo_plain_', tempDir)
        self.majicDir = tempfile.mkdtemp('', 'cad_majic_source_', tempDir)
        os.chmod(self.majicDir, 0o755)
        self.replaceDict = {
            '[VERSION]' : self.dialog.dataVersion,
            '[ANNEE]' : self.dialog.dataYear,
            '[LOT]' : self.dialog.edigeoLot
        }
        self.maxInsertRows = s.value("cadastre/maxInsertRows", 50000, type=int)
        self.spatialiteTempStore = s.value("cadastre/spatialiteTempStore", 'MEMORY', type=str)

        self.geoTableList = ['geo_zoncommuni', 'geo_ptcanv', 'geo_commune', 'geo_parcelle', 'geo_symblim', 'geo_tronfluv', 'geo_label', 'geo_subdsect', 'geo_batiment', 'geo_borne', 'geo_croix', 'geo_tpoint', 'geo_lieudit', 'geo_section', 'geo_subdfisc', 'geo_tsurf', 'geo_tline']


        if self.dialog.dbType == 'postgis':
            self.replaceDict['[PREFIXE]'] = '"%s".' % self.dialog.schema
        else:
            self.replaceDict['[PREFIXE]'] = ''
        self.go = True
        self.startTime = datetime.now()
        self.step = 0
        self.totalSteps = 0

        self.multiPolygonUpdated = 0

        self.qc.checkDatabaseForExistingStructure()
        self.hasConstraints = False
        if self.dialog.hasStructure:
            self.hasConstraints = True

        self.beginImport()


    def beginJobLog(self, stepNumber, title):
        '''
        reinit progress bar
        '''
        self.totalSteps = stepNumber
        self.step = 0
        self.dialog.stepLabel.setText('<b>%s</b>' % title)
        self.qc.updateLog('<h3>%s</h3>' % title)


    def updateProgressBar(self):
        '''
        Update the progress bar
        '''
        if self.go:
            self.step+=1
            self.dialog.pbProcess.setValue(int(self.step * 100/self.totalSteps))


    def updateTimer(self):
        '''
        Update the timer for each process
        '''
        if self.go:
            b = datetime.now()
            diff = b - self.startTime
            self.qc.updateLog(u'%s s' % diff.seconds)


    def beginImport(self):
        '''
        Process to run before importing data
        '''

        # Log
        jobTitle = u'INITIALISATION'
        self.beginJobLog(2, jobTitle)

        # Set postgresql synchronous_commit to off
        # to speed up bulk inserts
        if self.dialog.dbType == 'postgis':
            sql = "SET LOCAL synchronous_commit TO off;"

        if self.dialog.dbType == 'spatialite':
            sql = 'PRAGMA synchronous = OFF;PRAGMA journal_mode = MEMORY;PRAGMA temp_store = %s;PRAGMA cache_size = 500000' % self.spatialiteTempStore

        self.executeSqlQuery(sql)

        # copy opencadastre script files to temporary dir
        self.updateProgressBar()
        self.copyFilesToTemp(self.scriptSourceDir, self.scriptDir)
        self.updateTimer()
        self.updateProgressBar()


    def installOpencadastreStructure(self):
        '''
        Create the empty db structure
        '''

        # Log
        jobTitle = u'STRUCTURATION BDD'
        self.beginJobLog(6, jobTitle)

        # Replace dictionnary
        replaceDict = self.replaceDict.copy()
        replaceDict['2154'] = self.targetSrid

        # copy edige_create_import_tables in scriptDir
        a = os.path.join(self.qc.plugin_dir, 'scripts/edigeo_create_import_tables.sql')
        b = os.path.join(self.scriptDir, 'edigeo_create_import_tables.sql')
        shutil.copy2(a, b)

        # Suppression des éventuelles tables edigeo import
        # laissées suite à bug par exemple
        self.dropEdigeoRawData()

        # install opencadastre structure
        scriptList = [
            {
                'title' : u'Création des tables',
                'script': '%s' % os.path.join(self.scriptDir, 'create_metier.sql')
            },
            {
                'title': u'Création des tables edigeo',
                'script': '%s' % b
            },
            {
                'title' : u'Ajout de la nomenclature',
                'script': '%s' % os.path.join(self.scriptDir, 'insert_nomenclatures.sql')
            }
        ]

        #~ scriptList.append(
            #~ {
                #~ 'title' : u'Ajout des contraintes',
                #~ 'script': '%s' % os.path.normpath(os.path.join(self.scriptDir,
                #~ 'COMMUN/creation_contraintes.sql')),
                #~ 'constraints': True,
                #~ 'divide': True
            #~ }
        #~ )

        for item in scriptList:
            if self.go:
                s = item['script']
                self.dialog.subStepLabel.setText(item['title'])
                self.qc.updateLog('%s' % item['title'])
                self.updateProgressBar()
                self.replaceParametersInScript(s, replaceDict)
                self.executeSqlScript(s, item.has_key('constraints'))
                if item.has_key('constraints'):
                    self.hasConstraints = item['constraints']
            self.updateProgressBar()

        self.updateTimer()


    def importMajic(self):

        # Log
        jobTitle = u'MAJIC'
        self.beginJobLog(12, jobTitle)

        # dict for parameters replacement
        replaceDict = self.replaceDict.copy()
        mandatoryFilesKeys =  ['[FICHIER_BATI]', '[FICHIER_FANTOIR]', '[FICHIER_NBATI]', '[FICHIER_PROP]']
        missingMajicFiles = False

        scriptList = []
        scriptList.append(
            {
            'title' : u'Suppression des contraintes',
            'script' : 'COMMUN/suppression_constraintes.sql',
            'constraints': False,
            'divide': True
            }
        )

        # Remove previous data
        if self.dialog.hasData:
            scriptList.append(
                {
                'title' : u'Purge des données MAJIC',
                'script' : 'COMMUN/majic3_purge_donnees.sql'
                }
            )
            scriptList.append(
                {
                'title' : u'Purge des données brutes',
                'script' : 'COMMUN/majic3_purge_donnees_brutes.sql'
                }
            )

        scriptList.append(
            {
            'title' : u'Suppression des indexes',
            'script' : '%s/majic_drop_indexes.sql' % os.path.join(
                self.qc.plugin_dir,
                "scripts/"
            )
            }
        )

        # Import MAJIC files into database
        # No use of COPY FROM to allow import into distant databases
        importScript = {
            'title' : u'Import des fichiers majic',
            'method' : self.importMajicIntoDatabase
        }
        scriptList.append(importScript)

        # Format data
        scriptList.append(
            {
            'title' : u'Mise en forme des données',
            'script' : '%s/majic3_formatage_donnees.sql' % self.dialog.dataVersion,
            'divide': True
            }
        )

        # Remove MAJIC raw data
        removeRawData = True
        if removeRawData:
            scriptList.append(
                {
                'title' : u'Purge des données brutes',
                'script' : 'COMMUN/majic3_purge_donnees_brutes.sql'
                }
            )

        # If MAJIC but no EDIGEO afterward
        # run SQL script to update link between EDI/MAJ
        if not self.dialog.doEdigeoImport:
            replaceDict['[DEPDIR]'] = '%s%s' % (self.dialog.edigeoDepartement, self.dialog.edigeoDirection)
            shutil.copy2(
                '%s/edigeo_drop_indexes.sql' % os.path.join(self.qc.plugin_dir,"scripts/"),
                os.path.join(self.scriptDir, 'edigeo_drop_indexes.sql')
            )
            scriptList.append(
                {
                'title' : u'Suppression des indexes',
                'script' : 'edigeo_drop_indexes.sql'
                }
            )
            shutil.copy2(
                '%s/edigeo_update_majic_link.sql' % os.path.join(self.qc.plugin_dir,"scripts/"),
                os.path.join(self.scriptDir, 'edigeo_update_majic_link.sql')
            )
            scriptList.append(
                {
                    'title' : u'Mise à jour des liens EDIGEO',
                    'script' : 'edigeo_update_majic_link.sql',
                    'divide': True
                }
            )
            shutil.copy2(
                '%s/edigeo_create_indexes.sql' % os.path.join(self.qc.plugin_dir,"scripts/"),
                os.path.join(self.scriptDir, 'edigeo_create_indexes.sql')
            )
            scriptList.append(
                {
                    'title' : u'Création des indexes spatiaux',
                    'script' : 'edigeo_create_indexes.sql',
                    'divide': True
                }
            )


        # Add constraints : only if no EDIGEO import afterwards
        if not self.dialog.doEdigeoImport :
            scriptList.append(
                {
                    'title' : u'Ajout des contraintes',
                    'script' : 'COMMUN/creation_contraintes.sql',
                    'constraints': True,
                    'divide': True
                }
            )

        # Run previously defined SQL queries
        for item in scriptList:
            if self.go:
                self.dialog.subStepLabel.setText(item['title'])
                self.qc.updateLog('%s' % item['title'])
                if item.has_key('script'):
                    s = item['script']
                    scriptPath = os.path.join(self.scriptDir, s)
                    self.replaceParametersInScript(scriptPath, replaceDict)
                    self.updateProgressBar()
                    if item.has_key('divide'):
                        self.executeSqlScript(scriptPath, True, item.has_key('constraints'))
                    else:
                        self.executeSqlScript(scriptPath, False, item.has_key('constraints'))
                else:
                    self.updateProgressBar()
                    item['method']()

                if item.has_key('constraints') \
                and not self.dialog.dbType == 'spatialite':
                    self.hasConstraints = item['constraints']

                self.updateTimer()
            self.updateProgressBar()

        return None


    def chunk(self, iterable, n=100000, padvalue=None):
        '''
        Chunks an iterable (file, etc.)
        into pieces
        '''
        from itertools import izip_longest
        return izip_longest(*[iter(iterable)]*n, fillvalue=padvalue)


    def importMajicIntoDatabase(self):
        '''
        Method wich read each majic file
        and bulk import data intp temp tables
        - Specific for sqlite cause to COPY statement
        '''

        # Regex to remove all chars not in the range in ASCII table from space to ~
        # http://www.catonmat.net/blog/my-favorite-regex/
        r = re.compile(r"[^ -~]")

        # Loop through all majic files
        for item in self.dialog.majicSourceFileNames:
            # Get majic files for item
            majList = []
            for root, dirs, files in os.walk(self.dialog.majicSourceDir):
                for i in files:
                    if os.path.split(i)[1] == item['value']:
                        majList.append(os.path.join(root, i))

            table = item['table']
            self.totalSteps+= len(majList)

            for fpath in majList:
                self.qc.updateLog(fpath)

                # read file content
                with open(fpath) as fin:
                    # Divide file into chuncks
                    for a in self.chunk(fin, self.maxInsertRows):
                        # Build sql INSERT query depending on database
                        if self.dialog.dbType == 'postgis':
                            sql = "BEGIN;"
                            sql = self.qc.setSearchPath(sql, self.dialog.schema)
                            sql+= '\n'.join(
                                [
                                "INSERT INTO \"%s\" VALUES (%s);" % (
                                    table,
                                    self.connector.quoteString( r.sub(' ', x.strip('\r\n')) )
                                ) for x in a if x
                                ]
                            )
                            sql+= "COMMIT;"
                            self.executeSqlQuery(sql)
                        else:
                            c = self.connector._get_cursor()
                            c.executemany('INSERT INTO %s VALUES (?)' % table, [( r.sub(' ', x.strip('\r\n')) ,) for x in a if x] )
                            self.connector._commit()
                            c.close()
                            del c


    def importEdigeo(self):
        '''
        Import EDIGEO data
        into database
        '''
        # Check if ogr2ogr is found in system
        try:
            from osgeo import gdal, ogr, osr
            gdalAvailable = True
        except:
            msg = u"Erreur : la librairie GDAL n'est pas accessible"
            self.go = False
            return msg

        if not self.go:
            return

        # Log : Print connection parameters to database
        jobTitle = u'EDIGEO'
        self.beginJobLog(14, jobTitle)
        self.qc.updateLog(u'Type de base : %s, Connexion: %s, Schéma: %s' % (
                self.dialog.dbType,
                self.dialog.connectionName,
                self.dialog.schema
            )
        )
        self.updateProgressBar()

        if self.go:
            # copy files in temp dir
            self.dialog.subStepLabel.setText('Copie des fichiers')
            self.updateProgressBar()
            self.copyFilesToTemp(self.dialog.edigeoSourceDir, self.edigeoDir)
            self.updateTimer()
        self.updateProgressBar()

        if self.go:
            # unzip edigeo files in temp dir
            self.dialog.subStepLabel.setText('Extraction des fichiers')
            self.updateProgressBar()
            self.unzipFolderContent(self.edigeoDir)
            self.updateTimer()
        self.updateProgressBar()

        # Copy eventual plain edigeo files in edigeoPlainDir
        shutil.copytree(self.edigeoDir, os.path.join(self.edigeoPlainDir, 'plain'))

        scriptList = []
        replaceDict = self.replaceDict.copy()

        # Drop constraints if needed
        scriptList.append(
            {
                'title' : u'Suppression des contraintes',
                'script' : '%s' % os.path.join(self.scriptDir, 'COMMUN/suppression_constraintes.sql'),
                'constraints': False,
                'divide' : True
            }
        )

        # Suppression et recréation des tables edigeo pour import
        if self.dialog.hasData:
            replaceDict['2154'] = self.targetSrid
            # copy edige_create_import_tables in scriptDir
            a = os.path.join(self.qc.plugin_dir, 'scripts/edigeo_create_import_tables.sql')
            b = os.path.join(self.scriptDir, 'edigeo_create_import_tables.sql')
            shutil.copy2(a, b)
            self.dropEdigeoRawData()
            scriptList.append(
                {
                    'title': u'Création des tables edigeo',
                    'script': '%s' % b
                }
            )
        # Suppression des indexes
        if self.dialog.hasData:
            scriptList.append(
                {
                'title' : u'Suppression des indexes',
                'script' : '%s/edigeo_drop_indexes.sql' % os.path.join(
                    self.qc.plugin_dir,
                    "scripts/"
                )
                }
            )


        for item in scriptList:
            if self.go:
                self.dialog.subStepLabel.setText(item['title'])
                self.qc.updateLog('%s' % item['title'])
                scriptPath = item['script']
                self.replaceParametersInScript(scriptPath, replaceDict)
                self.updateProgressBar()
                self.executeSqlScript(scriptPath, item.has_key('divide'), item.has_key('constraints'))
                if item.has_key('constraints'):
                    self.hasConstraints = item['constraints']
                self.updateTimer()
            self.updateProgressBar()



        # import edigeo *.thf and *.vec files into database
        if self.go:
            self.dialog.subStepLabel.setText('Import des fichiers')
            self.updateProgressBar()
            self.importAllEdigeoToDatabase()
            self.updateTimer()
        self.updateProgressBar()

        # Format edigeo data
        replaceDict = self.replaceDict.copy()
        replaceDict['[DEPDIR]'] = '%s%s' % (self.dialog.edigeoDepartement, self.dialog.edigeoDirection)

        scriptList = []

        scriptList.append(
            {
                'title' : u'Mise en forme des données',
                'script' : '%s' % os.path.join(
                    self.scriptDir,
                    '%s/edigeo_formatage_donnees.sql' % self.dialog.dataVersion
                ),
                'divide': True
            }
        )
        if not self.dialog.dbType == 'spatialite':
            scriptList.append(
                {   'title' : u'Création Unités foncières',
                    'script' : '%s' % os.path.join(
                        self.scriptDir,
                        '%s/edigeo_unite_fonciere.sql' % self.dialog.dataVersion
                    )
                }
            )
        scriptList.append(
            {
                'title' : u'Placement des étiquettes',
                'script' : '%s/edigeo_add_labels_xy.sql' % os.path.join(
                    self.qc.plugin_dir,
                    "scripts/"
                )
            }
        )
        scriptList.append(
            {
                'title' : u'Création des indexes spatiaux',
                'script' : '%s/edigeo_create_indexes.sql' % os.path.join(
                    self.qc.plugin_dir,
                    "scripts/"
                ),
                'divide': True
            }
        )


        scriptList.append(
            {
                'title' : u'Ajout des contraintes',
                'script' : '%s' % os.path.join(
                    self.scriptDir,
                    'COMMUN/creation_contraintes.sql'
                ),
                'constraints': True,
                'divide': True
            }
        )

        for item in scriptList:
            if self.go:
                self.dialog.subStepLabel.setText(item['title'])
                self.qc.updateLog('%s' % item['title'])
                scriptPath = item['script']
                self.replaceParametersInScript(scriptPath, replaceDict)
                self.updateProgressBar()
                self.executeSqlScript(scriptPath, item.has_key('divide'), item.has_key('constraints'))
                if item.has_key('constraints'):
                    self.hasConstraints = item['constraints']

                self.updateTimer()
                self.updateProgressBar()

        # drop edigeo raw data
        self.dialog.subStepLabel.setText('Suppression des fichiers temporaires')
        self.dropEdigeoRawData()
        self.updateTimer()
        self.updateProgressBar()

        return None


    def onlyUpdateMultiPolygon(self):
        '''
        Only run the SQL Update queries
        built from VEC files
        To repair multipolygons
        '''

        # Log : Print connection parameters to database
        jobTitle = u'EDIGEO'
        self.beginJobLog(14, jobTitle)
        self.qc.updateLog(u'Type de base : %s, Connexion: %s, Schéma: %s' % (
                self.dialog.dbType,
                self.dialog.connectionName,
                self.dialog.schema
            )
        )
        self.updateProgressBar()

        if self.go:
            # copy files in temp dir
            self.dialog.subStepLabel.setText('Copie des fichiers')
            self.updateProgressBar()
            self.copyFilesToTemp(self.dialog.edigeoSourceDir, self.edigeoDir)
            self.updateTimer()
        self.updateProgressBar()

        if self.go:
            # unzip edigeo files in temp dir
            self.dialog.subStepLabel.setText('Extraction des fichiers')
            self.updateProgressBar()
            self.unzipFolderContent(self.edigeoDir)
            self.updateTimer()
        self.updateProgressBar()

        # Copy eventual plain edigeo files in edigeoPlainDir
        shutil.copytree(self.edigeoDir, os.path.join(self.edigeoPlainDir, 'plain'))

        # Get MULTIPOLYGON from VEC files and update concerned layers and objects
        if self.go:
            self.dialog.subStepLabel.setText('Correction des MULTI-POLYGONES')
            self.updateProgressBar()

            vecList = self.listFilesInDirectory(self.edigeoPlainDir, 'vec')
            self.step = 0
            self.totalSteps = len(vecList)
            for vec in vecList:
                # update mission multipolygons (ogr2ogr driver does not handle them yet)
                self.updateMultipolygonFromVec(vec, 'cadastre')
                self.updateProgressBar()
            self.qc.updateLog(u'  - %s multipolygones mis à jours dans la base de données' % self.multiPolygonUpdated)

            self.updateTimer()


    def endImport(self):
        '''
        Actions done when import has finished
        '''
        # Log
        jobTitle = u'FINALISATION'
        self.beginJobLog(1, jobTitle)

        # Re-set SQL optimization parameters to default
        if self.dialog.dbType == 'postgis':
            sql = "SET LOCAL synchronous_commit TO on;"
            self.executeSqlQuery(sql)

        # Remove the temp folders
        self.dialog.subStepLabel.setText(u'Suppression des données temporaires')
        self.updateProgressBar()
        tempFolderList = [
            self.scriptDir,
            self.edigeoDir,
            self.edigeoPlainDir,
            self.majicDir
        ]
        delmsg = ""
        try:
            for rep in tempFolderList:
                if os.path.exists(rep):
                    shutil.rmtree(rep)
                    rmt = 1
        except IOError, e:
            delmsg = u"Erreur lors de la suppression des répertoires temporaires: %s" % e
            self.qc.updateLog(delmsg)
            self.go = False

        # Refresh spatialite layer statistics
        if self.dialog.dbType == 'spatialite':
            sql = ''
            for layer in self.geoTableList:
                sql+= "SELECT UpdateLayerStatistics('%s', 'geom');" % layer
            sql+= "SELECT UpdateLayerStatistics('geo_parcelle', 'geom_uf');"
            self.executeSqlQuery(sql)

        if self.go:
            msg = u"Import terminé"
        else:
            msg = u"Des erreurs ont été rencontrées pendant l'import. Veuillez consulter le log."

        self.updateProgressBar()
        self.updateTimer()
        QMessageBox.information(self.dialog, "Cadastre", msg)


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

            self.qc.updateLog(u'* Copie du répertoire %s' % source.decode('UTF-8'))

            QApplication.setOverrideCursor(Qt.WaitCursor)

            # copy script directory
            try:
                dir_util.copy_tree(source, target)
                os.chmod(target, 0777)
            except IOError, e:
                msg = u"Erreur lors de la copie des scripts d'import: %s" % e
                QMessageBox.information(self.dialog,
                "Cadastre", msg)
                self.go = False
                return msg

            finally:
                QApplication.restoreOverrideCursor()


        return None


    def listFilesInDirectory(self, path, ext=None):
        '''
        List all files from folder and subfolder
        for a specific extension if given
        '''
        fileList = []
        for root, dirs, files in os.walk(path):
            for i in files:
                if not ext or (ext and os.path.splitext(i)[1][1:].lower() == ext):
                    fileList.append(os.path.join(root, i))
        return fileList


    def unzipFolderContent(self, path):
        '''
        Scan content of specified path
        and unzip all content into a single folder
        '''
        if self.go:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.qc.updateLog(u'* Décompression des fichiers')

            # get all the zip files
            zipFileList = self.listFilesInDirectory(path, 'zip')

            # unzip all files
            import zipfile
            import tarfile
            try:
                # unzip all zip in self.edigeoDir
                for z in zipFileList:
                    with zipfile.ZipFile(z) as azip:
                        azip.extractall(self.edigeoPlainDir)
                    try:
                        os.remove(z)
                    except OSError, e:
                        self.qc.updateLog( "Erreur lors de la suppression de %s" % str(z))
                        pass # in Windows, sometime file is not unlocked

                # unzip all zip in edigeoPlainDir
                inner_zips_pattern = os.path.join(self.edigeoPlainDir, "*.zip")
                i=0
                for filename in glob.glob(inner_zips_pattern):
                    inner_folder = filename[:-4] + '_%s' % i

                    with zipfile.ZipFile(filename) as myzip:
                        myzip.extractall(inner_folder)
                    try:
                        os.remove(filename)
                    except OSError, e:
                        self.qc.updateLog( "Erreur lors de la suppression de %s" % str(filename))
                        pass # in Windows, sometime file is not unlocked
                    i+=1
                i=0

                # untar all tar.bz2 in self.edigeoPlainDir
                tarFileListA = self.listFilesInDirectory(path, 'bz2')
                tarFileListB = self.listFilesInDirectory(self.edigeoPlainDir, 'bz2')
                tarFileList = list(set(tarFileListA) | set(tarFileListB))
                for z in tarFileList:
                    with tarfile.open(z) as t:
                        tar = t.extractall(os.path.join(self.edigeoPlainDir, 'tar_%s' % i))
                        i+=1
                        t.close()
                    try:
                        os.remove(z)
                    except OSError, e:
                        self.qc.updateLog( "Erreur lors de la suppression de %s" % str(z))
                        pass # in Windows, sometime file is not unlocked

            except IOError, e:
                msg = u"Erreur lors de l'extraction des fichiers EDIGEO"
                self.go = False
                self.qc.updateLog(msg)
                return msg

            finally:
                QApplication.restoreOverrideCursor()


    def replaceParametersInString(self, string, replaceDict):
        '''
        Replace all occurences in string
        '''

        def replfunc(match):
            if replaceDict.has_key(match.group(0)):
                return replaceDict[match.group(0)]
            else:
                return None

        regex = re.compile('|'.join(re.escape(x) for x in replaceDict), re.IGNORECASE)
        string = regex.sub(replfunc, string)
        return string


    def replaceParametersInScript(self, scriptPath, replaceDict):
        '''
        Replace all parameters in sql scripts
        with given values
        '''

        if self.go:

            QApplication.setOverrideCursor(Qt.WaitCursor)

            try:
                fin = open(scriptPath)
                data = fin.read().decode("utf-8-sig")
                fin.close()
                fout = open(scriptPath, 'w')
                data = self.replaceParametersInString(data, replaceDict)
                data = data.encode('utf-8')
                fout.write(data)
                fout.close()

            except IOError, e:
                msg = u"Erreur lors du paramétrage des scripts d'import: %s" % e
                self.go = False
                self.qc.updateLog(msg)
                return msg

            finally:
                QApplication.restoreOverrideCursor()


        return None


    def executeSqlScript(self, scriptPath, divide=False, ignoreError=False):
        '''
        Execute an SQL script file
        from opencadastre
        '''

        if self.go:

            QApplication.setOverrideCursor(Qt.WaitCursor)

            # Read sql script
            sql = open(scriptPath).read()
            sql = sql.decode("utf-8-sig")

            # Set schema if needed
            if self.dialog.dbType == 'postgis':
                sql = self.qc.setSearchPath(sql, self.dialog.schema)
            # Convert SQL into spatialite syntax
            if self.dialog.dbType == 'spatialite':
                sql = self.qc.postgisToSpatialite(sql, self.targetSrid)

            #~ self.qc.updateLog('|%s|' % sql)
            # Execute query
            if not divide:
                self.executeSqlQuery(sql, ignoreError)
            else:
                statements = sql.split(';')
                self.totalSteps+= len(statements)
                self.updateProgressBar()
                r = re.compile(r'select |insert |update |delete |alter |create |drop |truncate |comment |copy |vacuum |analyze ', re.IGNORECASE|re.MULTILINE)
                for sqla in statements:
                    if not self.go:
                        break

                    cr = re.compile(r'-- (.+)', re.IGNORECASE|re.MULTILINE)
                    ut = False
                    for comment in cr.findall(sqla):
                        self.qc.updateLog('  - %s' % comment.strip(' \n\r\t'))
                        ut = True
                    # Do nothing if sql is only comment
                    if not r.search(sqla) or not len(sqla.split('~')) == 1:
                        continue

                    sql = '%s' % sqla
                    #~ self.qc.updateLog('@@%s$$' % sql)
                    self.updateProgressBar()
                    # Avoid adding 2 times the same column for spatialite
                    if  self.dialog.dbType == 'spatialite' \
                    and re.search(r'ADD COLUMN tempo_import', sqla, re.IGNORECASE):
                        try:
                            self.executeSqlQuery(sql, ignoreError)
                        except:
                            pass
                    else:
                        self.executeSqlQuery(sql, ignoreError)
                    if ut:
                        self.updateTimer()
                    self.updateProgressBar()
            QApplication.restoreOverrideCursor()

        return None


    def executeSqlQuery(self, sql, ignoreError=False):
        '''
        Execute a SQL string query
        And commit
        '''
        if self.go:
            QApplication.setOverrideCursor(Qt.WaitCursor)

            c = None

            if self.dialog.dbType == 'postgis':
                try:
                    c = self.connector._execute_and_commit(sql)
                except BaseError as e:
                    if not ignoreError \
                    and not re.search(r'ADD COLUMN tempo_import', sql, re.IGNORECASE) \
                    and not re.search(r'CREATE INDEX ', sql, re.IGNORECASE):
                        DlgDbError.showError(e, self.dialog)
                        self.go = False
                        self.qc.updateLog(e.msg)
                finally:
                    QApplication.restoreOverrideCursor()
                    if c:
                        try:
                            c.close()
                            del c
                        except:
                            self.qc.updateLog("issue closing connection")
                            print "issue closing connection"
                            pass

            if self.dialog.dbType == 'spatialite':
                #~ self.qc.updateLog(sql)
                try:
                    c = self.connector._get_cursor()
                    c.executescript(sql)
                except BaseError as e:
                    if not re.search(r'ADD COLUMN tempo_import', sql, re.IGNORECASE) \
                    and not re.search(r'CREATE INDEX ', sql, re.IGNORECASE):
                        self.go = False
                        self.qc.updateLog(u"Erreurs rencontrées pour la requête: <p>%s</p>" % sql)
                finally:
                    QApplication.restoreOverrideCursor()
                    if c:
                        try:
                            c.close()
                            del c
                        except:
                            self.qc.updateLog("issue closing connection")
                            print "issue closing connection"
                            pass


    def importAllEdigeoToDatabase(self):
        '''
        Loop through all THF files
        and import each one into database
        '''

        if self.go:

            self.qc.updateLog(u'* Import des fichiers EDIGEO dans la base')

            initialStep = self.step
            initialTotalSteps = self.totalSteps

            # THF
            self.dialog.subStepLabel.setText(u'Import des fichiers via ogr2ogr (*.thf)')
            self.qc.updateLog(u'  - Import des fichiers via ogr2ogr')
            thfList = self.listFilesInDirectory(self.edigeoPlainDir, 'thf')
            self.step = 0
            self.totalSteps = len(thfList)
            for thf in thfList:
                self.importEdigeoThfToDatabase(thf)
                self.updateProgressBar()

            # VEC - import relations between objects
            self.dialog.subStepLabel.setText(u'Import des relations (*.vec)')
            self.qc.updateLog(u'  - Import des relations (*.vec)')
            vecList = self.listFilesInDirectory(self.edigeoPlainDir, 'vec')
            self.step = 0
            self.totalSteps = len(vecList)
            for vec in vecList:
                # import via ogr2ogr
                self.importEdigeoVecToDatabase(vec)
                # update mission multipolygons (ogr2ogr driver does not handle them yet)
                self.updateMultipolygonFromVec(vec)
                self.updateProgressBar()
            self.qc.updateLog(u'  - %s multipolygones mis à jours dans la base de données' % self.multiPolygonUpdated)

            # Reinit progress var
            self.step = initialStep
            self.totalSteps = initialTotalSteps
            QApplication.restoreOverrideCursor()


    def importEdigeoThfToDatabase(self, filename):
        '''
        Import one edigeo THF files into database
        source : db_manager/dlg_import_vector.py
        '''
        if self.go:
            # Get options
            targetSridOption = '-t_srs'
            if self.sourceSridFull == self.targetSridFull:
                targetSridOption = '-a_srs'

            # Build ogr2ogr command
            conn_name = self.dialog.connectionName
            settings = QSettings()
            settings.beginGroup( u"/%s/%s" % (self.db.dbplugin().connectionSettingsKey(), conn_name) )

            # normalising file path
            filename = os.path.normpath(filename)
            if self.dialog.dbType == 'postgis':
                if not settings.contains( "database" ): # non-existent entry?
                    raise InvalidDataException( self.tr('There is no defined database connection "%s".') % conn_name )
                settingsList = ["service", "host", "port", "database", "username", "password"]
                service, host, port, database, username, password = map(lambda x: settings.value(x), settingsList)

                ogrCommand = 'ogr2ogr -s_srs "%s" %s "%s" -append -f "PostgreSQL" PG:"host=%s port=%s dbname=%s active_schema=%s user=%s password=%s" "%s" -lco GEOMETRY_NAME=geom -lco PG_USE_COPY=YES -nlt GEOMETRY -gt 50000 --config OGR_EDIGEO_CREATE_LABEL_LAYERS NO' % (self.sourceSridFull, targetSridOption, self.targetSridFull, host, port, database, self.dialog.schema, username, password, filename)

            if self.dialog.dbType == 'spatialite':
                if not settings.contains( "sqlitepath" ): # non-existent entry?
                    raise InvalidDataException( u'there is no defined database connection "%s".' % conn_name )

                database = settings.value("sqlitepath")

                ogrCommand = 'ogr2ogr -s_srs "%s" %s "%s" -append -f "SQLite" "%s" "%s" -lco GEOMETRY_NAME=geom -nlt GEOMETRY  -dsco SPATIALITE=YES -gt 50000 --config OGR_EDIGEO_CREATE_LABEL_LAYERS NO --config OGR_SQLITE_SYNCHRONOUS OFF --config OGR_SQLITE_CACHE 512' % (self.sourceSridFull, targetSridOption, self.targetSridFull, database, filename)
            #~ self.qc.updateLog(ogrCommand)

            # Run command
            proc = QProcess()
            proc.start(ogrCommand)
            proc.waitForFinished()

        return None



    def importEdigeoVecToDatabase(self, path):
        '''
        Get edigeo relations between objects
        from a .VEC file
        and add them in edigeo_rel table
        '''
        if self.go:
            reg = '^RID[a-zA-z]{1}[a-zA-z]{1}[0-9]{2}:(Rel_.+)_(Objet_[0-9]+)_(Objet_[0-9]+)'
            with open(path) as inputFile:
                # Get a list of RID relations combining a "Rel" and two "_Objet"
                l = [ a[0] for a in [re.findall(r'%s' % reg, line) for line in inputFile] if a]

                # Create a sql script to insert all items
                if self.dialog.dbType == 'postgis':
                    sql="BEGIN;"
                    for item in l:
                        sql+= "INSERT INTO edigeo_rel ( nom, de, vers) VALUES ( '%s', '%s', '%s');" % (item[0], item[1], item[2] )
                    sql+="COMMIT;"
                    sql = self.qc.setSearchPath(sql, self.dialog.schema)
                    self.executeSqlQuery(sql)
                if self.dialog.dbType == 'spatialite':
                    c = self.connector._get_cursor()
                    query = 'INSERT INTO edigeo_rel (nom, de, vers) VALUES (?, ?, ?)'
                    try:
                        c.executemany(query, [ (item[0], item[1], item[2]) for item in l] )
                        self.connector._commit()
                    except:
                        self.qc.updateLog('Erreurs pendant la requête : %s' % sql)
                    finally:
                        c.close()
                        del c


    def updateMultipolygonFromVec(self, path, layerType='edigeo'):
        '''
        Run the update multipolygon query
        for each VEC files on the given layer type
        (edigeo = import tables, cadastre = cadastre geo_* tables)
        '''
        # Get SQL update queries
        sqlList = self.getUpdateMultipolygonFromVecQuery(path, layerType)

        # Run each query
        for sql in sqlList:
            if self.dialog.dbType == 'postgis':
                sql = self.qc.setSearchPath(sql, self.dialog.schema)
            self.executeSqlQuery(sql)


    def getUpdateMultipolygonFromVecQuery(self, path, layerType='edigeo'):
        '''
        EDIGEO ogr driver does not import multipolygon.
        This method is a patch : it parses the vec file
        and get WKT.
        Then the method build an SQL update query
        adapted on the given layer type
        (edigeo = import tables, cadastre = cadastre geo_* tables)
        '''
        sqlList = []

        # Class wich get multipolygons
        from getmultipolygonfromvec import GetMultiPolygonFromVec
        getMultiPolygon = GetMultiPolygonFromVec()

        # Relations between edigeo import tables and geo_* cadastre table
        impCadRel = {
            'batiment_id' : 'geo_batiment',
            'commune_id': 'geo_commune',
            'lieudit_id': 'geo_lieudit',
            'parcelle_id': 'geo_parcelle',
            'section_id': 'geo_section',
            'subdfisc_id': 'geo_subdfisc',
            'subdsect_id': 'geo_subdsect',
            'tronfluv_id': 'geo_tronfluv',
            'tsurf_id': 'geo_tsurf'
        }

        # Get dictionnary
        dic = getMultiPolygon( path )
        if dic:
            # Loop for each layer found in VEC with multi-polygon to update
            for layer, item in dic.items():
                table = layer.lower()

                # do the changes only for polygon layers
                if table not in impCadRel:
                    continue

                # Replace table name if the update is not done on edigeo import table
                # but on the cadastre geo_* layers instead
                if layerType == 'cadastre':
                    table = impCadRel[table]

                # Build SQL
                sql = ''
                for obj, wkt in item.items():
                    self.multiPolygonUpdated+=1
                    sql+= " UPDATE %s SET geom = ST_Transform(ST_GeomFromText('%s', %s), %s)" % (
                        table,
                        wkt,
                        self.sourceSrid,
                        self.targetSrid
                    )
                    # only for given object id
                    sql+= " WHERE object_rid = '%s' " % str(obj)
                    # only if the 2 geometries are indeed different. To be debbuged : geom <> geom : operator is not unique
                    #~ sql+= " AND geom != ST_Transform(ST_GeomFromText('%s', %s), %s) " % (wkt, self.sourceSrid, self.targetSrid)
                    # only if the 2 geometries are related (object_rid is not unique)
                    if self.dialog.dbType == 'postgis':
                        sql+= " AND geom @ ST_Transform(ST_GeomFromText('%s', %s), %s) ; " % (wkt, self.sourceSrid, self.targetSrid)
                    else:
                        sql+= " AND ST_Intersects(geom, ST_Transform(ST_GeomFromText('%s', %s), %s) ); " % (wkt, self.sourceSrid, self.targetSrid)
                sqlList.append(sql)

        return sqlList



    def dropEdigeoRawData(self):
        '''
        Drop Edigeo raw data tables
        '''

        if self.go:
            # DROP edigeo import tables
            edigeoImportTables = [
                'batiment_id',
                'borne_id',
                'boulon_id',
                'commune_id',
                'croix_id',
                'id_s_obj_z_1_2_2',
                'lieudit_id',
                'numvoie_id',
                'parcelle_id',
                'ptcanv_id',
                'section_id',
                'subdfisc_id',
                'subdsect_id',
                'symblim_id',
                'tline_id',
                'tpoint_id',
                'tronfluv_id',
                'tronroute_id',
                'tsurf_id',
                'voiep_id',
                'zoncommuni_id'
                #~ 'edigeo_rel',
            ]
            sql = ''
            for table in edigeoImportTables:
                sql+= 'DROP TABLE IF EXISTS "%s";' % table
            if self.dialog.dbType == 'postgis':
                sql = self.qc.setSearchPath(sql, self.dialog.schema)
            self.executeSqlQuery(sql)

