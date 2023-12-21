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
import glob
import io
import os
import re
import shutil
import sqlite3 as sqlite
import sys
import tempfile

from datetime import datetime
from distutils import dir_util
from pathlib import Path

from db_manager.db_plugins.plugin import BaseError
from db_manager.dlg_db_error import DlgDbError
from qgis.core import Qgis, QgsMessageLog
from qgis.PyQt.QtCore import QObject, QSettings, Qt
from qgis.PyQt.QtWidgets import QApplication, QMessageBox

from cadastre.definitions import URL_DOCUMENTATION, URL_FANTOIR
from cadastre.dialogs.dialog_common import CadastreCommon

# Import ogr2ogr.py from the script folder
from .scripts.pyogr.ogr2ogr import main as ogr2ogr


class cadastreImport(QObject):

    def __init__(self, dialog):
        self.dialog = dialog

        # common cadastre methods
        self.qc = self.dialog.qc

        self.db = self.dialog.db
        self.connector = self.db.connector
        self.pScriptSourceDir = os.path.join(self.qc.plugin_dir, 'scripts/plugin')

        # projections
        if self.dialog.doEdigeoImport:
            self.sourceSridFull = self.dialog.edigeoSourceProj
            self.targetSridFull = self.dialog.edigeoTargetProj
            self.sourceAuth = self.sourceSridFull.split(":")[0]
            self.sourceSrid = self.sourceSridFull.split(":")[1]
            self.targetSrid = self.targetSridFull.split(":")[1]

            # Check IGNF code
            if self.sourceAuth == 'IGNF':
                sqlsearch = '%%AUTHORITY["IGNF","%s"]%%' % self.sourceSrid.upper()
                sql = "SELECT auth_srid FROM spatial_ref_sys WHERE auth_name='IGNF' AND  srtext LIKE '%s' LIMIT 1" % sqlsearch
                data, rowCount, ok = CadastreCommon.fetchDataFromSqlQuery(self.connector, sql)
                if rowCount == 1:
                    for line in data:
                        self.sourceSrid = str(line[0])

        else:
            self.targetSrid = '2154'

        # create temporary directories
        s = QSettings()
        tempDir = s.value("cadastre/tempDir", type=str)
        if not tempDir or not Path(tempDir).exists():
            tempDir = tempfile.gettempdir()
        self.pScriptDir = tempfile.mkdtemp('', 'cad_p_script_', tempDir)
        self.edigeoPlainDir = tempfile.mkdtemp('', 'cad_edigeo_plain_', tempDir)
        self.replaceDict = {
            '[VERSION]': self.dialog.dataVersion,
            '[ANNEE]': self.dialog.dataYear,
            '[LOT]': self.dialog.edigeoLot
        }
        self.maxInsertRows = s.value("cadastre/maxInsertRows", 50000, type=int)
        self.spatialiteTempStore = s.value("cadastre/spatialiteTempStore", 'MEMORY', type=str)

        self.geoTableList = ['geo_zoncommuni', 'geo_ptcanv', 'geo_commune', 'geo_parcelle', 'geo_symblim',
                             'geo_tronfluv', 'geo_tronroute', 'geo_label', 'geo_subdsect', 'geo_batiment', 'geo_borne',
                             'geo_croix', 'geo_tpoint', 'geo_lieudit', 'geo_section', 'geo_subdfisc', 'geo_tsurf',
                             'geo_tline', 'geo_unite_fonciere']

        s = QSettings()
        self.majicSourceFileNames = [
            {'key': '[FICHIER_BATI]',
             'value': s.value("cadastre/batiFileName", 'REVBATI.800', type=str),
             'table': 'bati',
             'required': True
             },
            {'key': '[FICHIER_FANTOIR]',
             'value': s.value("cadastre/fantoirFileName", 'TOPFANR.800', type=str),
             'table': 'fanr',
             'required': True
             },
            {'key': '[FICHIER_LOTLOCAL]',
             'value': s.value("cadastre/lotlocalFileName", 'REVD166.800', type=str),
             'table': 'lloc',
             'required': False
             },
            {'key': '[FICHIER_NBATI]',
             'value': s.value("cadastre/nbatiFileName", 'REVNBAT.800', type=str),
             'table': 'nbat',
             'required': True
             },
            {'key': '[FICHIER_PDL]',
             'value': s.value("cadastre/pdlFileName", 'REVFPDL.800', type=str),
             'table': 'pdll',
             'required': False
             },
            {'key': '[FICHIER_PROP]',
             'value': s.value("cadastre/propFileName", 'REVPROP.800', type=str),
             'table': 'prop',
             'required': True
             }
        ]

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

        # Remove MAJIC from tables bati|fanr|lloc|nbat|pdll|prop
        self.removeMajicRawData = True

        self.beginImport()

    def beginJobLog(self, stepNumber, title):
        """
        reinit progress bar
        """
        self.totalSteps = stepNumber
        self.step = 0
        self.dialog.stepLabel.setText('<b>%s</b>' % title)
        self.qc.updateLog('<h3>%s</h3>' % title)

    def updateProgressBar(self):
        """
        Update the progress bar
        """
        if self.go:
            self.step += 1
            self.dialog.pbProcess.setValue(int(self.step * 100 / self.totalSteps))

    def updateTimer(self):
        """
        Update the timer for each process
        """
        if self.go:
            b = datetime.now()
            diff = b - self.startTime
            self.qc.updateLog('%s s' % diff.seconds)

    def beginImport(self):
        """
        Process to run before importing data
        """
        # Log
        jobTitle = 'INITIALISATION'
        self.beginJobLog(2, jobTitle)

        # Set postgresql synchronous_commit to off
        # to speed up bulk inserts
        if self.dialog.dbType == 'postgis':
            sql = "SET LOCAL synchronous_commit TO off;"

        if self.dialog.dbType == 'spatialite':
            sql = 'PRAGMA synchronous = OFF;PRAGMA journal_mode = OFF;PRAGMA temp_store = %s;PRAGMA cache_size = 500000' % self.spatialiteTempStore

        self.executeSqlQuery(sql)

        # copy SQL script files to temporary dir
        self.updateProgressBar()
        self.copyFilesToTemp(self.pScriptSourceDir, self.pScriptDir)
        self.updateTimer()
        self.updateProgressBar()

    def installCadastreStructure(self):
        """
        Create the empty db structure
        """
        if not self.go:
            return False

        # Log
        jobTitle = 'STRUCTURATION BDD'
        self.beginJobLog(6, jobTitle)

        # Replace dictionnary
        replaceDict = self.replaceDict.copy()
        replaceDict['2154'] = self.targetSrid

        # Suppression des éventuelles tables edigeo import
        # laissées suite à bug par exemple
        self.dropEdigeoRawData()

        # install cadastre structure
        scriptList = [
            {
                'title': 'Création des tables',
                'script': '%s' % os.path.join(self.pScriptDir, 'commun_create_metier.sql')
            },
            {
                'title': 'Création des tables edigeo',
                'script': '%s' % os.path.join(self.pScriptDir, 'edigeo_create_import_tables.sql')
            },
            {
                'title': 'Ajout de la nomenclature',
                'script': '%s' % os.path.join(self.pScriptDir, 'commun_insert_nomenclatures.sql')
            }
        ]

        for item in scriptList:
            if self.go:
                s = item['script']
                self.dialog.subStepLabel.setText(item['title'])
                self.qc.updateLog('%s' % item['title'])
                self.updateProgressBar()
                self.replaceParametersInScript(s, replaceDict)
                self.executeSqlScript(s, 'constraints' in item)
                if 'constraints' in item:
                    self.hasConstraints = item['constraints']
            self.updateProgressBar()

        self.updateTimer()

    def updateCadastreStructure(self):
        """
        Add some tables if they do not exists
        This method is run only if structure already exists
        and if each table is not already present
        """
        # List all the tables which have been created between plugin versions
        newTables = [
            'geo_tronroute',
            'commune_majic'
        ]

        # Replace dictionnary
        replaceDict = self.replaceDict.copy()
        replaceDict['2154'] = self.targetSrid

        # Run the table creation scripts
        for table in newTables:
            # Check if table already exists
            if self.qc.checkDatabaseForExistingTable(table, self.dialog.schema):
                continue
            # Build path the the SQL creation file and continue if it does not exists
            s = '%s' % os.path.join(self.pScriptDir, 'update/create_%s.sql' % table)
            if not os.path.exists(s):
                continue
            self.replaceParametersInScript(s, replaceDict)
            self.executeSqlScript(s, False)

    def importMajic(self):

        # Log
        jobTitle = 'MAJIC'
        self.beginJobLog(13, jobTitle)

        # dict for parameters replacement
        replaceDict = self.replaceDict.copy()
        # mandatoryFilesKeys = ['[FICHIER_BATI]', '[FICHIER_FANTOIR]', '[FICHIER_NBATI]', '[FICHIER_PROP]']
        # missingMajicFiles = False

        scriptList = []
        scriptList.append(
            {
                'title': 'Suppression des contraintes',
                'script': os.path.join(self.pScriptDir, 'commun_suppression_contraintes.sql'),
                'constraints': False,
                'divide': True
            }
        )

        # Remove previous data
        if self.dialog.hasMajicData:
            scriptList.append(
                {
                    'title': 'Purge des données MAJIC',
                    'script': os.path.join(self.pScriptDir, 'majic3_purge_donnees.sql')
                }
            )
            scriptList.append(
                {
                    'title': 'Purge des données brutes',
                    'script': os.path.join(self.pScriptDir, 'majic3_purge_donnees_brutes.sql')
                }
            )

        # Remove indexes
        scriptList.append(
            {
                'title': 'Suppression des indexes',
                'script': os.path.join(self.pScriptDir, 'majic3_drop_indexes.sql')
            }
        )

        # Import MAJIC files into database
        # No use of COPY FROM to allow import into distant databases
        importScript = {
            'title': 'Import des fichiers majic',
            'method': self.import_majic_into_database
        }
        scriptList.append(importScript)

        # Format data
        scriptList.append(
            {
                'title': 'Mise en forme des données',
                'script': os.path.join(self.pScriptDir, '%s/majic3_formatage_donnees.sql' % self.dialog.dataVersion),
                'divide': True
            }
        )

        # Remove MAJIC raw data
        if self.removeMajicRawData:
            scriptList.append(
                {
                    'title': 'Purge des données brutes',
                    'script': os.path.join(self.pScriptDir, 'majic3_purge_donnees_brutes.sql')
                }
            )

        # If MAJIC but no EDIGEO afterward
        # run SQL script to update link between EDI/MAJ
        if not self.dialog.doEdigeoImport:
            replaceDict['[DEPDIR]'] = f'{self.dialog.edigeoDepartement}{self.dialog.edigeoDirection}'
            scriptList.append(
                {
                    'title': 'Suppression des indexes',
                    'script': os.path.join(self.pScriptDir, 'edigeo_drop_indexes.sql')
                }
            )

            scriptList.append(
                {
                    'title': 'Mise à jour des liens EDIGEO',
                    'script': os.path.join(self.pScriptDir, 'edigeo_update_majic_link.sql'),
                    'divide': True
                }
            )

            scriptList.append(
                {
                    'title': 'Création des indexes spatiaux',
                    'script': os.path.join(self.pScriptDir, 'edigeo_create_indexes.sql'),
                    'divide': True
                }
            )

            # Ajout de la table parcelle_info
            replaceDict['2154'] = self.targetSrid
            scriptList.append(
                {
                    'title': 'Ajout de la table parcelle_info',
                    'script': '%s' % os.path.join(self.pScriptDir, 'edigeo_create_table_parcelle_info_majic.sql'),
                    'divide': False
                }
            )

            # Add constraints
            scriptList.append(
                {
                    'title': 'Ajout des contraintes',
                    'script': os.path.join(self.pScriptDir, 'commun_creation_contraintes.sql'),
                    'constraints': True,
                    'divide': True
                }
            )

        # Run previously defined SQL queries
        for item in scriptList:
            if self.go:
                self.dialog.subStepLabel.setText(item['title'])
                self.qc.updateLog('%s' % item['title'])
                if 'script' in item:
                    s = item['script']
                    self.replaceParametersInScript(s, replaceDict)
                    self.updateProgressBar()
                    if 'divide' in item:
                        self.executeSqlScript(s, True, 'constraints' in item)
                    else:
                        self.executeSqlScript(s, False, 'constraints' in item)
                else:
                    self.updateProgressBar()
                    item['method']()

                if 'constraints' in item \
                        and not self.dialog.dbType == 'spatialite':
                    self.hasConstraints = item['constraints']

                self.updateTimer()
            self.updateProgressBar()

        return None

    def chunk(self, iterable, n=100000, padvalue=None):
        """
        Chunks an iterable (file, etc.)
        into pieces
        """
        from itertools import zip_longest
        return zip_longest(*[iter(iterable)] * n, fillvalue=padvalue)

    def import_majic_into_database(self) -> bool:
        """
        Method which read each majic file
        and bulk import data into temp tables

        Returns False if no file processed
        """
        processed_files_count = 0
        majic_files_key = []
        majic_files_found = {}

        # Regex to remove all chars not in the range in ASCII table from space to ~
        # http://www.catonmat.net/blog/my-favorite-regex/
        r = re.compile(r"[^ -~]")

        # Loop through all majic files

        # 1st path to build the complet liste for each majic source type (nbat, bati, lloc, etc.)
        # and read 1st line to get departement and direction to compare to inputs
        dep_dirs = {}
        for item in self.majicSourceFileNames:
            table = item['table']
            value = item['value']
            # Get majic files for item
            maj_list = []
            for root, dirs, files in os.walk(self.dialog.majicSourceDir):
                for i in files:
                    if os.path.split(i)[1] == value:
                        file_path = os.path.join(root, i)
                        # Add file path to the list
                        maj_list.append(file_path)

                        # Store dep_dir for this file
                        # avoid fantoir, as now it is given for the whole country
                        if table == 'fanr':
                            continue

                        # Get dep_dir : first line with content
                        with open(file_path, encoding='utf8') as fin:
                            for a in fin:
                                if len(a) < 4:
                                    continue
                                dep_dir = a[0:3]
                                break
                            dep_dirs[dep_dir] = True

            majic_files_found[table] = maj_list

        # Check if some important majic files are missing
        f_keys = [a for a in majic_files_found if majic_files_found[a]]
        r_keys = [a['table'] for a in self.majicSourceFileNames if a['required']]
        m_keys = [a for a in r_keys if a not in f_keys]
        if m_keys:
            msg = (
                "<b>Des fichiers MAJIC importants sont manquants: {} </b><br/>"
                "Vérifier le chemin des fichiers MAJIC:<br/>"
                "{} <br/>"
                "ainsi que les noms des fichiers configurés dans les options du plugin Cadastre:<br/>"
                "{}<br/><br/>"
                "Vous pouvez télécharger les fichiers fantoirs à cette adresse :<br/>"
                "<a href='{}'>{}</a><br/>"
            ).format(
                ', '.join(m_keys),
                self.dialog.majicSourceDir,
                ', '.join([a['value'].upper() for a in self.majicSourceFileNames]),
                URL_FANTOIR,
                URL_FANTOIR,
            )
            missing_majic_ignore = QMessageBox.question(
                self.dialog,
                'Cadastre',
                msg + '\n\n' + "Voulez-vous néanmoins continuer l'import ?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if missing_majic_ignore != QMessageBox.Yes:
                self.go = False
                self.qc.updateLog(msg)
                return False

        # Check if departement and direction are the same for every file
        if len(list(dep_dirs.keys())) > 1:
            self.go = False
            lst = ",<br/> ".join(
                f"département : {a[0:2]} et direction : {a[2:3]}" for a in dep_dirs)
            self.qc.updateLog(
                "<b>"
                "ERREUR : MAJIC - Les données concernent des départements et codes direction différents :"
                "</b>\n<br/> {}".format(lst)
            )
            self.qc.updateLog("<b>Veuillez réaliser l'import en %s fois.</b>" % len(list(dep_dirs.keys())))
            return False

        # Check if departement and direction are different from those given by the user in dialog
        f_dep = list(dep_dirs.keys())[0][0:2]
        f_dir = list(dep_dirs.keys())[0][2:3]
        if self.dialog.edigeoDepartement != f_dep or self.dialog.edigeoDirection != f_dir:
            msg = (
                "<b>ERREUR : MAJIC - Les numéros de département et de direction trouvés dans les fichiers "
                "ne correspondent pas à ceux renseignés dans les options du dialogue d'import:<b>\n"
                "<br/>"
                "* fichiers : {} et {} <br/>* options : {} et {}"
            ).format(
                f_dep,
                f_dir,
                self.dialog.edigeoDepartement,
                self.dialog.edigeoDirection
            )
            use_file_dep_dir = QMessageBox.question(
                self.dialog,
                'Cadastre',
                msg + (
                    "\n\n<br/><br/>"
                    "Voulez-vous continuer l'import avec les numéros trouvés dans les fichiers ?"
                ),
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if use_file_dep_dir == QMessageBox.Yes:
                self.dialog.edigeoDepartement = f_dep
                self.dialog.inEdigeoDepartement.setText(f_dep)
                self.dialog.edigeoDirection = f_dir
                self.dialog.inEdigeoDirection.setValue(int(f_dir))
            else:
                self.go = False
                self.qc.updateLog(msg)
                return False

        # 2nd path to insert data
        dep_dir = f'{self.dialog.edigeoDepartement}{self.dialog.edigeoDirection}'
        for item in self.majicSourceFileNames:
            table = item['table']
            self.totalSteps += len(majic_files_found[table])
            processed_files_count += len(majic_files_found[table])
            for file_path in majic_files_found[table]:
                self.qc.updateLog(file_path)

                # read file content
                with open(file_path, encoding='ascii', errors='replace') as fin:
                    # Divide file into chunks
                    for a in self.chunk(fin, self.maxInsertRows):
                        # Build sql INSERT query depending on database
                        if self.dialog.dbType == 'postgis':
                            try:
                                sql = "BEGIN;"
                                sql = CadastreCommon.setSearchPath(sql, self.dialog.schema)
                                # Build INSERT list
                                sql += '\n'.join(
                                    [
                                        "INSERT INTO \"{}\" VALUES ({});".format(
                                            table,
                                            self.connector.quoteString(r.sub(' ', x.strip('\r\n')))
                                        ) for x in a if x and x[0:3] == dep_dir
                                    ]
                                )
                                sql += "COMMIT;"
                            except MemoryError:
                                # Issue #326
                                self.qc.updateLog(
                                    "<b>"
                                    "ERREUR : Mémoire - Veuillez recommencer l'import en changeant le "
                                    "paramètre 'Taille maximum des requêtes INSERT' selon la "
                                    "documentation : {}{}"
                                    "</b>".format(
                                        URL_DOCUMENTATION,
                                        "/extension-qgis/configuration/#performances",
                                    )
                                )
                                self.go = False
                                return False

                            self.executeSqlQuery(sql)
                        else:
                            c = self.connector._get_cursor()
                            c.executemany(
                                f'INSERT INTO {table} VALUES (?)',
                                [(r.sub(' ', x.strip('\r\n')),) for x in a if x and x[0:3] == dep_dir])
                            self.connector._commit()
                            c.close()
                            del c

        if not processed_files_count:
            self.qc.updateLog(
                "<b>"
                "ERREUR : MAJIC - aucun fichier trouvé. Vérifier les noms de fichiers dans les paramètres "
                "du plugin et que le répertoire"
                "</b>'{}' <b>contient bien des fichiers qui correspondent</b>\n : {}".format(
                    self.dialog.majicSourceDir,
                    ', '.join(majic_files_key)
                )
            )
            self.go = False

    def importEdigeo(self):
        """
        Import EDIGEO data
        into database
        """
        if not self.go:
            return False

        # Log : Print connection parameters to database
        jobTitle = 'EDIGEO'
        self.beginJobLog(21, jobTitle)
        self.qc.updateLog('Type de base : {}, Connexion: {}, Schéma: {}'.format(
            self.dialog.dbType,
            self.dialog.connectionName,
            self.dialog.schema
        )
                          )
        self.updateProgressBar()

        if self.go:
            # unzip edigeo files in temp dir
            self.dialog.subStepLabel.setText('Extraction des fichiers')
            self.updateProgressBar()
            self.unzipFolderContent(self.dialog.edigeoSourceDir)
            self.updateTimer()
        self.updateProgressBar()

        scriptList = []
        replaceDict = self.replaceDict.copy()

        # Add geo_unite_foncieres if needed
        if not self.qc.checkDatabaseForExistingTable('geo_unite_fonciere', self.dialog.schema) \
                and self.dialog.dbType == 'postgis':
            scriptList.append(
                {
                    'title': 'Ajout de la table geo_unite_foncieres',
                    'script': '%s' % os.path.join(self.pScriptDir, 'edigeo_create_table_unite_fonciere.sql'),
                    'constraints': False
                }
            )

        # Drop constraints
        scriptList.append(
            {
                'title': 'Suppression des contraintes',
                'script': '%s' % os.path.join(self.pScriptDir, 'commun_suppression_contraintes.sql'),
                'constraints': False,
                'divide': True
            }
        )

        # Suppression et recréation des tables edigeo pour import
        if self.dialog.hasData:
            replaceDict['2154'] = self.targetSrid
            # Drop edigeo data
            self.dropEdigeoRawData()
            scriptList.append(
                {
                    'title': 'Création des tables edigeo',
                    'script': '%s' % os.path.join(self.pScriptDir, 'edigeo_create_import_tables.sql')
                }
            )
        # Suppression des indexes
        if self.dialog.hasData:
            scriptList.append(
                {
                    'title': 'Suppression des indexes',
                    'script': '%s' % os.path.join(self.pScriptDir, 'edigeo_drop_indexes.sql')
                }
            )

        for item in scriptList:
            if self.go:
                self.dialog.subStepLabel.setText(item['title'])
                self.qc.updateLog('%s' % item['title'])
                s = item['script']
                self.replaceParametersInScript(s, replaceDict)
                self.updateProgressBar()
                self.executeSqlScript(s, 'divide' in item, 'constraints' in item)
                if 'constraints' in item:
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
        replaceDict['[DEPDIR]'] = f'{self.dialog.edigeoDepartement}{self.dialog.edigeoDirection}'

        scriptList = []

        scriptList.append(
            {
                'title': 'Mise en forme des données',
                'script': os.path.join(self.pScriptDir, 'edigeo_formatage_donnees.sql'),
                'divide': True
            }
        )

        scriptList.append(
            {
                'title': 'Placement des étiquettes',
                'script': os.path.join(self.pScriptDir, 'edigeo_add_labels_xy.sql')
            }
        )
        scriptList.append(
            {
                'title': 'Création des indexes spatiaux',
                'script': os.path.join(self.pScriptDir, 'edigeo_create_indexes.sql'),
                'divide': True
            }
        )

        scriptList.append(
            {
                'title': 'Ajout des contraintes',
                'script': os.path.join(self.pScriptDir, 'commun_creation_contraintes.sql'),
                'constraints': True,
                'divide': True
            }
        )

        # ajout des unités foncières
        # seulement si on a des données MAJIC de propriétaire
        self.qc.checkDatabaseForExistingStructure()
        if (self.dialog.doMajicImport or self.dialog.hasMajicDataProp) \
                and self.dialog.dbType == 'postgis':
            scriptList.append(
                {'title': 'Création Unités foncières',
                 'script': os.path.join(self.pScriptDir, 'edigeo_unites_foncieres_%s.sql' % self.dialog.dbType)
                 }
            )

        # Ajout de la table parcelle_info
        if (self.dialog.doMajicImport or self.dialog.hasMajicDataProp):
            replaceDict['2154'] = self.targetSrid
            scriptList.append(
                {
                    'title': 'Ajout de la table parcelle_info',
                    'script': '%s' % os.path.join(self.pScriptDir, 'edigeo_create_table_parcelle_info_majic.sql')
                }
            )
        else:
            replaceDict['2154'] = self.targetSrid
            scriptList.append(
                {
                    'title': 'Ajout de la table parcelle_info',
                    'script': '%s' % os.path.join(self.pScriptDir, 'edigeo_create_table_parcelle_info_simple.sql')
                }
            )

        for item in scriptList:
            if self.go:
                self.dialog.subStepLabel.setText(item['title'])
                self.qc.updateLog('%s' % item['title'])
                s = item['script']
                self.replaceParametersInScript(s, replaceDict)
                self.updateProgressBar()

                self.executeSqlScript(s, 'divide' in item, 'constraints' in item)
                if 'constraints' in item:
                    self.hasConstraints = item['constraints']

                self.updateTimer()
                self.updateProgressBar()

        # drop edigeo raw data
        self.dialog.subStepLabel.setText('Suppression des fichiers temporaires')
        self.dropEdigeoRawData()
        self.updateTimer()
        self.updateProgressBar()

        return None

    def endImport(self):
        """
        Actions done when import has finished
        """
        # Log
        jobTitle = 'FINALISATION'
        self.beginJobLog(1, jobTitle)

        # Debug spatialite
        if self.dialog.dbType == 'spatialite':
            sql = "SELECT RecoverGeometryColumn( 'parcelle_info', 'geom', %s, 'MULTIPOLYGON', 2 );" % self.targetSrid
            sql += "SELECT RecoverGeometryColumn( 'geo_batiment', 'geom', %s, 'MULTIPOLYGON', 2 );" % self.targetSrid
            self.executeSqlQuery(sql)

        # Re-set SQL optimization parameters to default
        if self.dialog.dbType == 'postgis':
            sql = "SET LOCAL synchronous_commit TO on;"
            self.executeSqlQuery(sql)
        else:
            sql = 'PRAGMA journal_mode = MEMORY;'
            self.executeSqlQuery(sql)

        # Remove the temp folders
        self.dialog.subStepLabel.setText('Suppression des données temporaires')
        self.updateProgressBar()
        tempFolderList = [
            self.pScriptDir,
            self.edigeoPlainDir,
        ]
        delmsg = ""
        try:
            for rep in tempFolderList:
                if os.path.exists(rep):
                    shutil.rmtree(rep)
                    # rmt = 1
        except OSError as e:
            delmsg = "<b>Erreur lors de la suppression des répertoires temporaires: %s</b>" % e
            self.qc.updateLog(delmsg)
            self.go = False

        # Delete labels outside commune bbox
        if self.dialog.dbType == 'spatialite':
            sql = 'DELETE FROM geo_label WHERE NOT MbrWithin(geom, ( SELECT ST_Buffer(ST_Envelope(Collect(geom)), 100 ) AS geom FROM geo_commune ));'
        else:
            sql = 'DELETE FROM geo_label WHERE NOT ST_Within(geom, ( SELECT ST_Buffer(ST_Envelope(ST_Collect(geom)), 100 ) AS geom FROM geo_commune ));'
            sql = CadastreCommon.setSearchPath(sql, self.dialog.schema)
        self.executeSqlQuery(sql)

        # Add parcelle_info index for postgis only (not capability of that type for spatialite)
        if self.dialog.dbType == 'postgis':
            sql = 'DROP INDEX IF EXISTS parcelle_info_geo_parcelle_sub;CREATE INDEX parcelle_info_geo_parcelle_sub ON parcelle_info( substr("geo_parcelle", 1, 10));'
            sql = CadastreCommon.setSearchPath(sql, self.dialog.schema)
            self.executeSqlQuery(sql)

            # Add index on geo_parcelle and geo_batiment centroids
            sql = '''
            DROP INDEX IF EXISTS geo_parcelle_centroide_geom_idx;
            DROP INDEX IF EXISTS geo_batiment_centroide_geom_idx;
            CREATE INDEX geo_parcelle_centroide_geom_idx ON geo_parcelle USING gist (ST_Centroid(geom));
            CREATE INDEX geo_batiment_centroide_geom_idx ON geo_batiment USING gist (ST_Centroid(geom));
            '''
            sql = CadastreCommon.setSearchPath(sql, self.dialog.schema)
            self.executeSqlQuery(sql)

        # Refresh spatialite layer statistics
        if self.dialog.dbType == 'spatialite':
            sql = ''
            for layer in self.geoTableList:
                sql += "SELECT UpdateLayerStatistics('%s', 'geom');" % layer
            self.executeSqlQuery(sql)

        if self.go:
            msg = "Import terminé"
        else:
            msg = "Des erreurs ont été rencontrées pendant l'import. Veuillez consulter le log."

        self.updateProgressBar()
        self.updateTimer()
        if os.getenv("CI", "").lower() == 'true':
            # We don't want QMessagebox in test
            return True

        QMessageBox.information(self.dialog, "Cadastre", msg)

        return None

    #
    # TOOLS
    #

    def copyFilesToTemp(self, source, target):
        """
        Copy cadastre scripts
        into a temporary folder
        """
        if self.go:

            self.qc.updateLog('* Copie du répertoire %s' % source)

            QApplication.setOverrideCursor(Qt.WaitCursor)

            # copy script directory
            try:
                dir_util.copy_tree(source, target)
                os.chmod(target, 0o777)
            except OSError as e:
                msg = "<b>Erreur lors de la copie des scripts d'import: %s</b>" % e
                QMessageBox.information(self.dialog,
                                        "Cadastre", msg)
                self.go = False
                return msg

            finally:
                QApplication.restoreOverrideCursor()

        return None

    @staticmethod
    def list_files_in_directory(path, extension_list=None, invert=False):
        """
        List all files from folder and subfolder
        for a specific extension if given ( via the list extensionList ).
        If invert is True, then get all files
        but those corresponding to the given extensions.
        """
        if extension_list is None:
            extension_list = []

        file_list = []
        for root, dirs, files in os.walk(path):
            for i in files:
                file_path = os.path.join(root, i)
                if not invert:
                    if os.path.splitext(i)[1][1:].lower() in extension_list:
                        file_list.append(file_path)
                    else:
                        QgsMessageLog.logMessage(
                            "Omission du fichier {} car il ne s'agit pas d'une extension \"{}\"".format(
                                file_path, ', '.join(extension_list)
                            ),
                            'cadastre',
                            Qgis.Info
                        )
                else:
                    if os.path.splitext(i)[1][1:].lower() not in extension_list:
                        file_list.append(file_path)
                    else:
                        QgsMessageLog.logMessage(
                            "Omission du fichier {} car il s'agit d'une extension non souhaitée "
                            "\"{}\"".format(file_path, ', '.join(extension_list)),
                            'cadastre',
                            Qgis.Info
                        )

        return file_list

    def unzipFolderContent(self, path):
        """
        Scan content of specified path
        and unzip all content into a single folder
        """
        if self.go:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.qc.updateLog('* Décompression des fichiers')

            # get all the zip files
            zipFileList = self.list_files_in_directory(path, ['zip'])

            # unzip all files
            import tarfile
            import zipfile
            try:
                # unzip all zip in source folder
                for z in zipFileList:
                    # Extract file from edigeoDir into edigeoPlainDir
                    with zipfile.ZipFile(z) as azip:
                        azip.extractall(self.edigeoPlainDir)

                # unzip all new zip in edigeoPlainDir
                inner_zips_pattern = os.path.join(self.edigeoPlainDir, "*.zip")
                i = 0
                for filename in glob.glob(inner_zips_pattern):
                    inner_folder = filename[:-4] + '_%s' % i

                    with zipfile.ZipFile(filename) as myzip:
                        myzip.extractall(inner_folder)
                    try:
                        os.remove(filename)
                    except OSError:
                        self.qc.updateLog("<b>Erreur lors de la suppression de %s</b>" % str(filename))
                        pass  # in Windows, sometime file is not unlocked
                    i += 1

                error_message = (
                    "<b>Erreur</b> lors de l'ouverture du fichier {}. Un re-téléchargement du dossier "
                    "EDIGEO peut résoudre le problème"
                )

                i = 0
                # untar all tar.bz2 in source folder
                self.qc.updateLog('* Recherche des fichiers .bz2')
                tarFileListA = self.list_files_in_directory(path, ['bz2'])
                self.qc.updateLog(f"{len(tarFileListA)} fichier(s) .bz2 dans {path}")
                for z in tarFileListA:
                    with tarfile.open(z) as t:
                        try:
                            # See https://docs.python.org/3.8/library/tarfile.html#tarfile.TarFile.extractall
                            # See https://peps.python.org/pep-0706/
                            t.extractall(
                                os.path.join(self.edigeoPlainDir, 'tar_%s' % i),
                                filter='data',
                            )
                        except tarfile.ReadError:
                            # Issue GitHub #339
                            self.go = False
                            t.close()
                            error = error_message.format(z)
                            self.qc.updateLog(error)
                            return error
                        i += 1
                        t.close()

                # untar all new tar.bz2 found in self.edigeoPlainDir
                tarFileListB = self.list_files_in_directory(self.edigeoPlainDir, ['bz2'])
                self.qc.updateLog(f"{len(tarFileListA)} fichier(s) .bz2 dans {self.edigeoPlainDir}")
                for z in tarFileListB:
                    with tarfile.open(z) as t:
                        try:
                            t.extractall(os.path.join(self.edigeoPlainDir, 'tar_%s' % i))
                        except tarfile.ReadError:
                            # Issue GitHub #339
                            self.go = False
                            t.close()
                            error = error_message.format(z)
                            self.qc.updateLog(error)
                            return error
                        i += 1
                        t.close()
                    try:
                        os.remove(z)
                    except OSError:
                        self.qc.updateLog("<b>Erreur lors de la suppression de %s</b>" % str(z))
                        pass  # in Windows, sometime file is not unlocked

            except OSError:
                msg = "<b>Erreur lors de l'extraction des fichiers EDIGEO</b>"
                self.go = False
                self.qc.updateLog(msg)
                return msg

            finally:
                QApplication.restoreOverrideCursor()

    def replaceParametersInString(self, string, replaceDict):
        """
        Replace all occurences in string
        """

        def replfunc(match):
            if match.group(0) in replaceDict:
                return replaceDict[match.group(0)]
            else:
                return None

        regex = re.compile('|'.join(re.escape(x) for x in replaceDict), re.IGNORECASE)
        string = regex.sub(replfunc, string)
        return string

    def replaceParametersInScript(self, scriptPath, replaceDict):
        """
        Replace all parameters in sql scripts
        with given values
        """

        if self.go:

            QApplication.setOverrideCursor(Qt.WaitCursor)

            try:
                data = ''
                with open(scriptPath, encoding='utf-8-sig') as fin:
                    data = fin.read()  # .decode("utf-8-sig")

                data = self.replaceParametersInString(data, replaceDict)
                # data = data.encode('utf-8')
                with open(scriptPath, 'w', encoding='utf8') as fout:
                    fout.write(data)

            except OSError as e:
                msg = "<b>Erreur lors du paramétrage des scripts d'import: %s</b>" % e
                self.go = False
                self.qc.updateLog(msg)
                return msg

            finally:
                QApplication.restoreOverrideCursor()

        return None

    def executeSqlScript(self, scriptPath, divide=False, ignoreError=False):
        """
        Execute an SQL script file
        """

        if self.go:

            QApplication.setOverrideCursor(Qt.WaitCursor)

            # Read sql script
            sql = ''
            try:
                with open(scriptPath, encoding="utf-8-sig") as f:
                    sql = f.read()
            except:
                with open(scriptPath, encoding="ISO-8859-15") as f:
                    sql = f.read()

            # Set schema if needed
            if self.dialog.dbType == 'postgis':
                sql = CadastreCommon.setSearchPath(sql, self.dialog.schema)

            # Remove make valid if asked
            if not self.dialog.edigeoMakeValid:
                mvReplaceDic = [
                    {'in': r"ST_CollectionExtract\(ST_MakeValid\(geom\),{2,3}\)",
                     'out': r"geom"},
                    {'in': r"ST_CollectionExtract\(ST_MakeValid\(p\.geom\),{2,3}\)",
                     'out': r"p.geom"}
                ]
                for a in mvReplaceDic:
                    r = re.compile(a['in'], re.IGNORECASE | re.MULTILINE)
                    sql = r.sub(a['out'], sql)

            # Convert SQL into spatialite syntax
            if self.dialog.dbType == 'spatialite':
                sql = CadastreCommon.postgisToSpatialite(sql, self.targetSrid)
                sql = CadastreCommon.postgisToSpatialiteLocal10(sql, self.dialog.dataYear)

            # Execute query
            if not divide:
                # self.qc.updateLog('|%s|' % sql)
                self.executeSqlQuery(sql, ignoreError)
            else:
                # Split all SQL into single queries
                statements = sql.split(';')
                self.totalSteps += len(statements)
                self.updateProgressBar()
                # Regex to find valid SQL queries
                r = re.compile(
                    r'select |insert |update |delete |alter |create |drop |truncate |comment |copy |vacuum |analyze ',
                    re.IGNORECASE | re.MULTILINE)

                # Loop through for each individual statement
                for sqla in statements:
                    # Break if an error has been raised before
                    if not self.go:
                        break

                    # Regex to find comments which will be written in log
                    cr = re.compile(r'^-- (.+)', re.IGNORECASE | re.MULTILINE)

                    # Write comment taken from "-- some comment" lines
                    for comment in cr.findall(sqla):

                        # Update timer before writing the comment
                        # it will show the time taken by the previous statement
                        self.updateTimer()

                        # Write item. Ex: geo_borne_parcelle
                        self.qc.updateLog('  - %s' % comment.strip(' \n\r\t'))

                    # Do nothing if sql is only comment
                    if not r.search(sqla) or not len(sqla.split('~')) == 1:
                        continue

                    # Get SQL query
                    sql = '%s' % sqla
                    # self.qc.updateLog('@@%s$$' % sql)
                    # self.updateProgressBar()

                    # Spatialite performance adaptations
                    # This is fragile as Sqlite perf evolves a lot through time & versions
                    # Some queries runing fast earlier can perform poorly in some contexts
                    # ex: https://github.com/3liz/QgisCadastrePlugin/issues/262
                    avoid_query = False
                    if self.dialog.dbType == 'spatialite':
                        spatialite_avoid_list = [
                            'geo_borne_annee_idx',
                        ]
                        for avoid_item in spatialite_avoid_list:
                            if avoid_item in sql:
                                avoid_query = True
                    if avoid_query:
                        # self.qc.updateLog('AVOID FOR SPATIALITE')
                        continue

                    # Execute query
                    self.executeSqlQuery(sql, ignoreError)

                    self.updateProgressBar()
            QApplication.restoreOverrideCursor()

        return None

    def executeSqlQuery(self, sql, ignoreError=False):
        """
        Execute a SQL string query
        And commit
        NB: commit qgis/QGIS@14ab5eb changes QGIS DBmanager behaviour
        """
        if self.go:
            QApplication.setOverrideCursor(Qt.WaitCursor)

            c = None

            if self.dialog.dbType == 'postgis':
                try:
                    c = self.connector._execute_and_commit(sql)
                except BaseError as e:
                    if not ignoreError \
                            and not re.search(r'CREATE INDEX ', sql, re.IGNORECASE):
                        DlgDbError.showError(e, self.dialog)
                        self.go = False
                        self.qc.updateLog(e.msg)
                except UnicodeDecodeError:
                    try:
                        c = self.connector._execute_and_commit(sql)
                    except BaseError as e:
                        if not ignoreError \
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
                            # fix_print_with_import
                            print("issue closing connection")
                            pass

            if self.dialog.dbType == 'spatialite':
                # ~ self.qc.updateLog(sql)

                try:
                    # Get cursor
                    c = self.connector._get_cursor()

                    # Add regex function (use the above regexp python function)
                    def regexp(motif, item):
                        import re
                        a = False
                        if item is None or not item:
                            item = ''
                        try:
                            regex = re.compile(motif, re.I)  # re.I: ignore casse
                            a = regex.search(item) is not None
                        except Exception as e:
                            # fix_print_with_import
                            print(e.msg)
                        return a

                    c.connection.create_function('regexp', 2, regexp)

                    # Run query
                    c.executescript(sql)
                except BaseError as e:
                    if not re.search(r'CREATE INDEX ', sql, re.IGNORECASE):
                        self.go = False
                        self.qc.updateLog("<b>Erreur rencontrée pour la requête:</b> <p>%s</p>" % sql)
                        self.qc.updateLog("<b>Erreur </b> <p>%s</p>" % e.msg)
                except sqlite.OperationalError as e:
                    if not re.search(r'CREATE INDEX ', sql, re.IGNORECASE):
                        self.go = False
                        self.qc.updateLog("<b>Erreur rencontrée pour la requête:</b> <p>%s</p>" % sql)
                        self.qc.updateLog("<b>Erreur </b> <p>%s</p>" % format(e))
                finally:
                    QApplication.restoreOverrideCursor()
                    if c:
                        try:
                            c.close()
                            del c
                        except:
                            self.qc.updateLog("issue closing connection")
                            # fix_print_with_import
                            print("issue closing connection")
                            pass

    def importAllEdigeoToDatabase(self):
        """
        Loop through all THF files
        and import each one into database
        """

        if self.go:

            self.qc.updateLog('* Import des fichiers EDIGEO dans la base')

            initialStep = self.step
            initialTotalSteps = self.totalSteps

            # THF
            self.dialog.subStepLabel.setText('Import des fichiers via ogr2ogr (*.thf)')
            self.qc.updateLog('  - Import des fichiers via ogr2ogr')
            # Get plain files in source directory
            thfList1 = self.list_files_in_directory(self.dialog.edigeoSourceDir, ['thf'])
            # Get files which have been uncompressed by plugin in temp folder
            thfList2 = self.list_files_in_directory(self.edigeoPlainDir, ['thf'])
            thfList = list(set(thfList1) | set(thfList2))
            self.step = 0
            self.totalSteps = len(thfList)
            for thf in thfList:
                self.importEdigeoThfToDatabase(thf)
                self.updateProgressBar()
                if not self.go:
                    break

        if self.go:

            # VEC - import relations between objects
            self.dialog.subStepLabel.setText('Import des relations (*.vec)')
            self.qc.updateLog('  - Import des relations (*.vec)')
            # Get plain files in source directory
            vecList1 = self.list_files_in_directory(self.dialog.edigeoSourceDir, ['vec'])
            # Get files which have been uncompressed by plugin in temp folder
            vecList2 = self.list_files_in_directory(self.edigeoPlainDir, ['vec'])
            vecList = list(set(vecList1) | set(vecList2))
            self.step = 0
            self.totalSteps = len(vecList)
            for vec in vecList:
                # import via ogr2ogr
                self.importEdigeoVecToDatabase(vec)
                # update mission multipolygons (ogr2ogr driver does not handle them yet)
                self.updateMultipolygonFromVec(vec)
                self.updateProgressBar()
                if not self.go:
                    break
            if self.go:
                self.qc.updateLog(
                    '  - %s multipolygones mis à jours dans la base de données' % self.multiPolygonUpdated)

        # Reinit progress var
        self.step = initialStep
        self.totalSteps = initialTotalSteps
        QApplication.restoreOverrideCursor()

    def importEdigeoThfToDatabase(self, filename):
        """
        Import one edigeo THF files into database
        source : db_manager/dlg_import_vector.py
        """
        if self.go:
            # Get options
            targetSridOption = '-t_srs'
            if self.sourceSridFull == self.targetSridFull:
                targetSridOption = '-a_srs'

            # Build ogr2ogr command
            conn_name = self.dialog.connectionName
            settings = QSettings()
            settings.beginGroup(f"/{self.db.dbplugin().connectionSettingsKey()}/{conn_name}")

            # normalising file path
            filename = os.path.normpath(filename)
            if self.dialog.dbType == 'postgis':
                if not settings.contains("database"):  # non-existent entry?
                    raise Exception(self.tr('There is no defined database connection "%s".') % conn_name)
                settingsList = ["service", "host", "port", "database", "username", "password"]
                service, host, port, database, username, password = (settings.value(x) for x in settingsList)

                if service:
                    pg_access = 'PG:service={} active_schema={}'.format(
                        service,
                        self.dialog.schema
                    )
                else:
                    # qgis can connect to postgis DB without a specified host param connection, but ogr2ogr cannot
                    if not host:
                        host = "localhost"

                    pg_access = 'PG:host={} port={} dbname={} active_schema={} user={} password={}'.format(
                        host,
                        port,
                        database,
                        self.dialog.schema,
                        username,
                        password
                    )
                cmdArgs = [
                    '',
                    '-s_srs', self.sourceSridFull,
                    targetSridOption, self.targetSridFull,
                    '-append',
                    '-f', 'PostgreSQL',
                    pg_access,
                    filename,
                    '-lco', 'GEOMETRY_NAME=geom',
                    '-lco', 'PG_USE_COPY=YES',
                    '-nlt', 'GEOMETRY',
                    '-gt', '50000',
                    '--config', 'OGR_EDIGEO_CREATE_LABEL_LAYERS', 'NO',
                    '--config', 'PG_USE_COPY', 'YES',
                ]
                # -c client_encoding=latin1

            if self.dialog.dbType == 'spatialite':
                if not settings.contains("sqlitepath"):  # non-existent entry?
                    self.go = False
                    raise Exception('there is no defined database connection "%s".' % conn_name)

                database = settings.value("sqlitepath")

                cmdArgs = [
                    '',
                    '-s_srs', self.sourceSridFull,
                    targetSridOption, self.targetSridFull,
                    '-append',
                    '-f', 'SQLite',
                    database,
                    filename,
                    '-lco', 'GEOMETRY_NAME=geom',
                    '-nlt', 'GEOMETRY',
                    '-dsco', 'SPATIALITE=YES',
                    '-gt', '50000',
                    '--config', 'OGR_EDIGEO_CREATE_LABEL_LAYERS', 'NO',
                    '--config', 'OGR_SQLITE_SYNCHRONOUS', 'OFF',
                    '--config', 'OGR_SQLITE_CACHE', '512'
                ]

            # self.qc.updateLog( ' '.join(cmdArgs))
            # Run only if ogr2ogr found
            if self.go:
                # Workaround to get ogr2ogr error messages via stdout
                # as ogr2ogr.py does not return exceptions nor error messages
                # but only prints the error before returning False
                stdout = sys.stdout
                try:
                    sys.stdout = file = io.StringIO()
                    self.go = ogr2ogr(cmdArgs)
                    printedString = file.getvalue()
                finally:
                    sys.stdout = stdout

                if not self.go:
                    self.qc.updateLog(
                        "<b>Erreur - L'import des données via OGR2OGR a échoué:</b>\n\n{}\n\n{}".format(
                            printedString,
                            cmdArgs
                        )
                    )

        return None

    def importEdigeoVecToDatabase(self, path):
        """
        Get edigeo relations between objects
        from a .VEC file
        and add them in edigeo_rel table
        """
        if self.go:
            reg = '^RID[a-zA-z]{1}[a-zA-z]{1}[0-9]{2}:(Rel_.+)_(Objet_[0-9]+)_(Objet_[0-9]+)'
            try:
                with open(path, encoding='utf8') as inputFile:
                    # Get a list of RID relations combining a "Rel" and two "_Objet"
                    l = [a[0] for a in [re.findall(r'%s' % reg, line) for line in inputFile] if a]
            except:
                with open(path, encoding="ISO-8859-15") as inputFile:
                    # Get a list of RID relations combining a "Rel" and two "_Objet"
                    l = [a[0] for a in [re.findall(r'%s' % reg, line) for line in inputFile] if a]

            if l:
                # Create a sql script to insert all items
                if self.dialog.dbType == 'postgis':
                    sql = "BEGIN;"
                    for item in l:
                        sql += "INSERT INTO edigeo_rel ( nom, de, vers) VALUES ( '{}', '{}', '{}');".format(
                        item[0], item[1], item[2])
                    sql += "COMMIT;"
                    sql = CadastreCommon.setSearchPath(sql, self.dialog.schema)
                    self.executeSqlQuery(sql)
                if self.dialog.dbType == 'spatialite':
                    c = self.connector._get_cursor()
                    query = 'INSERT INTO edigeo_rel (nom, de, vers) VALUES (?, ?, ?)'
                    try:
                        c.executemany(query, [(item[0], item[1], item[2]) for item in l])
                        self.connector._commit()
                    except:
                        self.qc.updateLog('<b>Erreurs pendant la requête :</b> %s' % sql)
                    finally:
                        c.close()
                        del c

    def updateMultipolygonFromVec(self, path, layerType='edigeo'):
        """
        Run the update multipolygon query
        for each VEC files on the given layer type
        (edigeo = import tables, cadastre = cadastre geo_* tables)
        """
        # Get SQL update queries
        sqlList = self.getUpdateMultipolygonFromVecQuery(path, layerType)

        # Run each query
        for sql in sqlList:
            if self.dialog.dbType == 'postgis':
                sql = CadastreCommon.setSearchPath(sql, self.dialog.schema)
            self.executeSqlQuery(sql)

    def getUpdateMultipolygonFromVecQuery(self, path, layerType='edigeo'):
        """
        EDIGEO ogr driver does not import multipolygon.
        This method is a patch : it parses the vec file
        and get WKT.
        Then the method build an SQL update query
        adapted on the given layer type
        (edigeo = import tables, cadastre = cadastre geo_* tables)
        """
        sqlList = []

        # Class wich get multipolygons
        from .getmultipolygonfromvec import GetMultiPolygonFromVec
        getMultiPolygon = GetMultiPolygonFromVec()

        # Relations between edigeo import tables and geo_* cadastre table
        impCadRel = {
            'batiment_id': 'geo_batiment',
            'commune_id': 'geo_commune',
            'lieudit_id': 'geo_lieudit',
            'parcelle_id': 'geo_parcelle',
            'section_id': 'geo_section',
            'subdfisc_id': 'geo_subdfisc',
            'subdsect_id': 'geo_subdsect',
            'tronfluv_id': 'geo_tronfluv',
            'tronroute_id': 'geo_tronroute',
            'tsurf_id': 'geo_tsurf'
        }

        # Get dictionnary
        dic = getMultiPolygon(path)
        if dic:
            # Loop for each layer found in VEC with multi-polygon to update
            for layer, item in list(dic.items()):
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
                for obj, wkt in list(item.items()):
                    self.multiPolygonUpdated += 1
                    sql += " UPDATE {} SET geom = ST_Transform(ST_GeomFromText('{}', {}), {})".format(
                        table,
                        wkt,
                        self.sourceSrid,
                        self.targetSrid
                    )
                    # only for given object id
                    sql += " WHERE object_rid = '%s' " % str(obj)
                    # only if the 2 geometries are indeed different. To be debbuged : geom <> geom : operator is not unique
                    # ~ sql+= " AND geom != ST_Transform(ST_GeomFromText('%s', %s), %s) " % (wkt, self.sourceSrid, self.targetSrid)
                    # only if the 2 geometries are related (object_rid is not unique)
                    if self.dialog.dbType == 'postgis':
                        sql += " AND geom @ ST_Transform(ST_GeomFromText('{}', {}), {}) ; ".format(
                        wkt, self.sourceSrid, self.targetSrid)
                    else:
                        sql += " AND ST_Intersects(geom, ST_Transform(ST_GeomFromText('{}', {}), {}) ); ".format(
                        wkt, self.sourceSrid, self.targetSrid)
                sqlList.append(sql)

        return sqlList

    def dropEdigeoRawData(self):
        """
        Drop Edigeo raw data tables
        """

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
                # ~ 'edigeo_rel',
            ]
            sql = ''
            for table in edigeoImportTables:
                sql += 'DROP TABLE IF EXISTS "%s";' % table
            if self.dialog.dbType == 'postgis':
                sql = CadastreCommon.setSearchPath(sql, self.dialog.schema)
            self.executeSqlQuery(sql)
