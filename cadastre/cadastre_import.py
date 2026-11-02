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
import os
import re
import shutil
import sqlite3 as sqlite
import sys
import tarfile
import tempfile
import zipfile

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Callable

from qgis.core import (
    Qgis,
    QgsApplication,
    QgsAuthMethodConfig,
    QgsMessageLog,
    QgsProcessingException,
    QgsProviderConnectionException,
    QgsProcessingFeedback,
)
from qgis.PyQt.QtCore import QObject, QSettings

import cadastre.cadastre_common_base as common_utils

from cadastre.definitions import (
    IMPORT_MEMORY_ERROR_MESSAGE,
    REGEX_BATI,
    REGEX_LOTLOCAL,
    REGEX_NBATI,
    REGEX_PDL,
    REGEX_PROP,
    REGEX_TOPO,
    URL_TOPO,
)
from cadastre.cadastre_database import CadastreDatabase, DatabaseStructure
from cadastre.feedback import CadastreFeedback
from cadastre.fiche_parametres import TABLE as FICHE_PARAMETRES_TABLE
from cadastre.fiche_parametres import complete_table
from cadastre.tools import plugin_path

from .logger import Logger

from processing.algs.gdal.GdalUtils import GdalUtils


class SecurityError(Exception):
    pass


@dataclass
class ImportOptions:
    """Parameters of an import of EDIGEO and/or MAJIC data."""

    database: CadastreDatabase
    data_version: str
    data_year: str
    lot: str
    departement: str
    direction: str
    majic_source_dir: str = ""
    edigeo_source_dir: str = ""
    # CRS auth id, e.g. EPSG:2154
    edigeo_source_proj: str = ""
    edigeo_target_proj: str = ""
    edigeo_make_valid: bool = False

    @property
    def do_majic_import(self) -> bool:
        return bool(self.majic_source_dir) and os.path.exists(self.majic_source_dir)

    @property
    def do_edigeo_import(self) -> bool:
        return bool(self.edigeo_source_dir) and os.path.exists(self.edigeo_source_dir)


class cadastreImport(QObject):
    def __init__(
        self,
        options: ImportOptions,
        feedback: QgsProcessingFeedback,
        confirm: Callable[[str], bool] | None = None,
    ):
        """
        :param options: Import parameters
        :param feedback: Feedback for logs, progress and sub steps (see CadastreFeedback)
        :param confirm: Function asking the user a yes/no question, when no function given, answer is no
        """
        super().__init__()
        self.options = options
        self.database = options.database
        self.feedback = feedback
        self.confirm = confirm

        self.pScriptSourceDir = str(plugin_path("scripts", "plugin"))

        # projections
        if self.options.do_edigeo_import:
            self.sourceSridFull = self.options.edigeo_source_proj
            self.targetSridFull = self.options.edigeo_target_proj
            self.sourceAuth = self.sourceSridFull.split(":")[0]
            self.sourceSrid = self.sourceSridFull.split(":")[1]
            self.targetSrid = self.targetSridFull.split(":")[1]

            # Check IGNF code
            if self.sourceAuth == "IGNF":
                sqlsearch = '%%AUTHORITY["IGNF","%s"]%%' % self.sourceSrid.upper()
                sql = (
                    "SELECT auth_srid FROM spatial_ref_sys WHERE auth_name='IGNF' AND  srtext LIKE '%s' LIMIT 1"
                    % sqlsearch
                )
                data = self.database.fetch_or_empty(sql)
                if len(data) == 1:
                    self.sourceSrid = str(data[0][0])

        else:
            self.targetSrid = "2154"

        # create temporary directories
        s = QSettings()
        temp_dir = s.value("cadastre/tempDir", type=str)
        if not temp_dir or not Path(temp_dir).exists():
            temp_dir = tempfile.gettempdir()
        self.pScriptDir = tempfile.mkdtemp("", "cad_p_script_", temp_dir)
        self.edigeoPlainDir = tempfile.mkdtemp("", "cad_edigeo_plain_", temp_dir)
        self.replaceDict = {
            "VERSION": self.options.data_version,
            "ANNEE": self.options.data_year,
            "LOT": self.options.lot,
            "SRID": "2154",  # The default
        }
        self.maxInsertRows = s.value("cadastre/maxInsertRows", 50000, type=int)
        self.spatialiteTempStore = s.value("cadastre/spatialiteTempStore", "MEMORY", type=str)

        self.geoTableList = [
            "geo_zoncommuni",
            "geo_ptcanv",
            "geo_commune",
            "geo_parcelle",
            "geo_symblim",
            "geo_tronfluv",
            "geo_tronroute",
            "geo_label",
            "geo_subdsect",
            "geo_batiment",
            "geo_borne",
            "geo_croix",
            "geo_tpoint",
            "geo_lieudit",
            "geo_section",
            "geo_subdfisc",
            "geo_tsurf",
            "geo_tline",
            "geo_unite_fonciere",
        ]

        s = QSettings()
        self.majicSourceFileNames = [
            {
                "key": "[FICHIER_BATI]",
                "regex": s.value("cadastre/regexBati", REGEX_BATI, type=str),
                "table": "bati",
                "required": True,
            },
            {
                "key": "[FICHIER_TOPO]",
                "regex": s.value("cadastre/regexTopo", REGEX_TOPO, type=str),
                "table": "topo",
                "required": True,
            },
            {
                "key": "[FICHIER_LOTLOCAL]",
                "regex": s.value("cadastre/regexLotLocal", REGEX_LOTLOCAL, type=str),
                "table": "lloc",
                "required": False,
            },
            {
                "key": "[FICHIER_NBATI]",
                "regex": s.value("cadastre/regexNbati", REGEX_NBATI, type=str),
                "table": "nbat",
                "required": True,
            },
            {
                "key": "[FICHIER_PDL]",
                "regex": s.value("cadastre/regexPdl", REGEX_PDL, type=str),
                "table": "pdll",
                "required": False,
            },
            {
                "key": "[FICHIER_PROP]",
                "regex": s.value("cadastre/regexProp", REGEX_PROP, type=str),
                "table": "prop",
                "required": True,
            },
        ]

        if self.database.db_type == "postgis":
            self.replaceDict["PREFIXE"] = '"%s".' % self.database.schema
        else:
            self.replaceDict["PREFIXE"] = ""
        self.go = True
        self.startTime = datetime.now()
        self.step = 0
        self.totalSteps = 0

        self.multiPolygonUpdated = 0

        self.structure: DatabaseStructure = self.database.structure()
        self.hasConstraints = self.structure.has_structure

        # Remove MAJIC from tables bati|topo|lloc|nbat|pdll|prop
        self.removeMajicRawData = True

        self.beginImport()

    def run(self) -> bool:
        """
        Run the full import, returns False if errors occurred
        """
        # Run Script for creating tables
        if not self.structure.has_structure:
            self.installCadastreStructure()
        else:
            # Run update script which add some missing tables when needed
            self.updateCadastreStructure()

        # Run MAJIC import
        if self.options.do_majic_import:
            self.importMajic()

        # Run Edigeo import
        if self.options.do_edigeo_import:
            self.importEdigeo()

        self.endImport()
        return self.go

    def setSubStep(self, text: str):
        """
        Display the current sub step, if the feedback supports it
        """
        if isinstance(self.feedback, CadastreFeedback):
            self.feedback.setSubStepText(text)

    def beginJobLog(self, step_number, title):
        """
        reinit progress bar
        """
        self.totalSteps = step_number
        self.step = 0
        self.feedback.setProgressText(title)
        self.feedback.pushInfo("<h3>%s</h3>" % title)

    def updateProgressBar(self):
        """
        Update the progress bar
        """
        if self.go:
            self.step += 1
            self.feedback.setProgress(self.step * 100 / self.totalSteps)

    def updateTimer(self):
        """
        Update the timer for each process
        """
        if self.go:
            b = datetime.now()
            diff = b - self.startTime
            self.feedback.pushInfo("%s s" % diff.seconds)

    def beginImport(self):
        """
        Process to run before importing data
        """
        # Log
        job_title = "INITIALISATION"
        self.beginJobLog(2, job_title)

        # Set postgresql synchronous_commit to off
        # to speed up bulk inserts
        if self.database.db_type == "postgis":
            sql = "SET LOCAL synchronous_commit TO off;"
        else:
            sql = (
                "PRAGMA synchronous = OFF;PRAGMA journal_mode = OFF;PRAGMA temp_store = %s;PRAGMA cache_size = 500000"
                % self.spatialiteTempStore
            )

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
            return

        # Log
        job_title = "STRUCTURATION BDD"
        self.beginJobLog(6, job_title)

        # Replace dictionary
        replace_dict = self.replaceDict.copy()
        replace_dict["SRID"] = self.targetSrid

        # Suppression des éventuelles tables edigeo import
        # laissées suite à bug par exemple
        self.dropEdigeoRawData()

        # install cadastre structure
        script_list = [
            {
                "title": "Création des tables",
                "script": "%s" % os.path.join(self.pScriptDir, "commun_create_metier.sql"),
            },
            {
                "title": "Création des tables edigeo",
                "script": "%s" % os.path.join(self.pScriptDir, "edigeo_create_import_tables.sql"),
            },
            {
                "title": "Ajout de la nomenclature",
                "script": "%s" % os.path.join(self.pScriptDir, "commun_insert_nomenclatures.sql"),
            },
        ]

        for item in script_list:
            if self.go:
                s = item["script"]
                self.setSubStep(item["title"])
                self.feedback.pushInfo("%s" % item["title"])
                self.updateProgressBar()
                self.replaceParametersInScript(s, replace_dict)
                self.executeSqlScript(s, "constraints" in item)
                if "constraints" in item:
                    self.hasConstraints = item["constraints"]
            self.updateProgressBar()

        self.updateTimer()

    def updateCadastreStructure(self):
        """
        Add some tables if they do not exist
        This method is run only if structure already exists
        and if each table is not already present
        """
        # List all the tables which have been created between plugin versions
        new_tables = ["geo_tronroute", "commune_majic"]

        # Replace dictionary
        replace_dict = self.replaceDict.copy()
        replace_dict["SRID"] = self.targetSrid

        # Run the table creation scripts
        for table in new_tables:
            # Check if table already exists
            if self.database.table_exists(table):
                continue
            # Build path the SQL creation file and continue if it does not exist
            s = "%s" % os.path.join(self.pScriptDir, "update/create_%s.sql" % table)
            if not os.path.exists(s):
                continue
            self.replaceParametersInScript(s, replace_dict)
            self.executeSqlScript(s, False)

    def importMajic(self):
        # Log
        job_title = "MAJIC"
        self.beginJobLog(13, job_title)

        # dict for parameters replacement
        replace_dict = self.replaceDict.copy()
        # mandatoryFilesKeys = ['[FICHIER_BATI]', '[FICHIER_TOPO]', '[FICHIER_NBATI]', '[FICHIER_PROP]']
        # missingMajicFiles = False

        script_list = []
        script_list.append(
            {
                "title": "Suppression des contraintes",
                "script": os.path.join(self.pScriptDir, "commun_suppression_contraintes.sql"),
                "constraints": False,
                "divide": True,
            }
        )

        # Remove previous data
        if self.structure.has_majic_data:
            script_list.append(
                {
                    "title": "Purge des données MAJIC",
                    "script": os.path.join(self.pScriptDir, "majic3_purge_donnees.sql"),
                }
            )
            script_list.append(
                {
                    "title": "Purge des données brutes",
                    "script": os.path.join(self.pScriptDir, "majic3_purge_donnees_brutes.sql"),
                }
            )

        # Remove indexes
        script_list.append(
            {
                "title": "Suppression des indexes",
                "script": os.path.join(self.pScriptDir, "majic3_drop_indexes.sql"),
            }
        )

        # Import MAJIC files into database
        # No use of COPY FROM to allow import into distant databases
        importScript = {"title": "Import des fichiers MAJIC", "method": self.import_majic_into_database}
        script_list.append(importScript)

        # Format data
        replace_dict["DEPDIR"] = f"{self.options.departement}{self.options.direction}"
        script_list.append(
            {
                "title": "Mise en forme des données",
                "script": os.path.join(
                    self.pScriptDir, "%s/majic3_formatage_donnees.sql" % self.options.data_version
                ),
                "divide": True,
            }
        )

        # Remove MAJIC raw data
        if self.removeMajicRawData:
            script_list.append(
                {
                    "title": "Purge des données brutes",
                    "script": os.path.join(self.pScriptDir, "majic3_purge_donnees_brutes.sql"),
                }
            )

        # If MAJIC but no EDIGEO afterward
        # run SQL script to update link between EDI/MAJ
        if not self.options.do_edigeo_import:
            replace_dict["DEPDIR"] = f"{self.options.departement}{self.options.direction}"
            script_list.append(
                {
                    "title": "Suppression des indexes",
                    "script": os.path.join(self.pScriptDir, "edigeo_drop_indexes.sql"),
                }
            )

            script_list.append(
                {
                    "title": "Mise à jour des liens EDIGEO",
                    "script": os.path.join(self.pScriptDir, "edigeo_update_majic_link.sql"),
                    "divide": True,
                }
            )

            script_list.append(
                {
                    "title": "Création des indexes spatiaux",
                    "script": os.path.join(self.pScriptDir, "edigeo_create_indexes.sql"),
                    "divide": True,
                }
            )

            # Ajout de la table parcelle_info
            script_list.append(
                {
                    "title": "Ajout des champs a la table parcelle_info",
                    "script": "%s"
                    % os.path.join(self.pScriptDir, "edigeo_ajout_champs_parcelle_info_majic.sql"),
                    "divide": True,
                }
            )

            replace_dict["SRID"] = self.targetSrid
            script_list.append(
                {
                    "title": "Remplissage de la table parcelle_info",
                    "script": "%s"
                    % os.path.join(self.pScriptDir, "edigeo_create_table_parcelle_info_majic.sql"),
                    "divide": False,
                }
            )

            # Add constraints
            script_list.append(
                {
                    "title": "Ajout des contraintes",
                    "script": os.path.join(self.pScriptDir, "commun_creation_contraintes.sql"),
                    "constraints": True,
                    "divide": True,
                }
            )

        # Run previously defined SQL queries
        for item in script_list:
            if self.go:
                self.setSubStep(item["title"])
                self.feedback.pushInfo("%s" % item["title"])
                if "script" in item:
                    s = item["script"]
                    self.replaceParametersInScript(s, replace_dict)
                    self.updateProgressBar()
                    if "divide" in item:
                        self.executeSqlScript(s, True, "constraints" in item)
                    else:
                        self.executeSqlScript(s, False, "constraints" in item)
                else:
                    self.updateProgressBar()
                    item["method"]()

                if "constraints" in item and self.database.db_type != "spatialite":
                    self.hasConstraints = item["constraints"]

                self.updateTimer()
            self.updateProgressBar()

        return

    def get_available_majic_files(self) -> tuple[dict, dict]:
        """
        Get the list of MAJIC files to import
        """
        majic_files_found = {}
        dep_dirs = {}
        for item in self.majicSourceFileNames:
            table = item["table"]
            file_regex = item["regex"].upper()
            self.feedback.pushInfo(
                f"Recherche des fichiers {table} contenant {file_regex} une fois en majuscule."
            )
            # Get MAJIC files for item
            maj_list = []
            for root, dirs, files in os.walk(self.options.majic_source_dir):
                for file_sub_path in files:
                    # self.feedback.pushInfo(file_sub_path)
                    # Check if the file matches the regex given for this file type
                    if re.search(file_regex, os.path.split(file_sub_path)[1].upper()):
                        # Add file path to the list
                        file_path = os.path.join(root, file_sub_path)

                        # ignore PDF/ODT/DOC/DOCX files
                        if file_path.lower().endswith(
                            (".pdf", ".odt", ".doc", ".docx", ".zip", ".tar", ".bz", ".gz")
                        ):
                            continue

                        maj_list.append(file_path)

                        # avoid topo, since direction is not used in TOPO
                        if table == "topo":
                            continue

                        msg = f"Lecture du fichier Majic: {file_path}"
                        Logger.info(msg)
                        self.feedback.pushInfo(msg)
                        try:
                            # Get dep_dir : first line with content
                            with open(file_path, encoding="utf8") as fin:
                                for a in fin:
                                    if len(a) < 4:
                                        continue
                                    dep_dir = a[0:3]
                                    break
                                dep_dirs[dep_dir] = True
                        except Exception as err:
                            Logger.critical(f"Erreur de lecture du fichier '{file_path}': {err}")
                            raise

            self.feedback.pushInfo(
                f"Nous avons trouvé {len(maj_list)} fichier{('s' if len(maj_list) > 1 else '')} pour {table}."
            )
            majic_files_found[table] = maj_list

        return dep_dirs, majic_files_found

    def check_missing_majic_files(self, majic_files_found: dict) -> bool:
        """
        Check if the mandatory MAJIC files have been found in the directory
        """
        f_keys = [a for a in majic_files_found if majic_files_found[a]]
        r_keys = [a["table"] for a in self.majicSourceFileNames if a["required"]]
        missing_files = [a for a in r_keys if a not in f_keys]
        if missing_files:
            msg = (
                "<b>ANNULATION</b><br/>"
                "<b>Des fichiers MAJIC importants sont manquants</b> :<br/>"
                " <b>{}</b> <br/><br/>"
                "Vérifier le chemin configuré pour les fichiers MAJIC :<br/>"
                "<b>{}</b> <br/><br/>"
                "ainsi que les mots recherchés pour chaque type de fichier configurés dans les options du plugin Cadastre :<br/>"
                "<b>{}</b><br/><br/><br/>"
                "<b>NB:</b> Vous pouvez télécharger le fichier TOPO à cette adresse :<br/>"
                "<a href='{}'>{}</a><br/>"
                "Il faut ensuite le décompresser pour avoir un fichier CSV ex: <i>TOPO_34.csv</i> puis supprimer le fichier compressé ex:<i> TOPO_34.csv.gz</i>)<br/>"
            ).format(
                ", <br/>".join(missing_files),
                self.options.majic_source_dir,
                ", <br/>".join(
                    [
                        f"* {a['key'].strip('[]')}: {a['regex'].upper()}"
                        for a in self.majicSourceFileNames
                        if a["table"] in missing_files
                    ]
                ),
                URL_TOPO,
                URL_TOPO,
            )
            self.feedback.pushInfo(msg)
            self.go = False

            return False

        return True

    def check_majic_departement_direction(self, dep_dirs: dict) -> bool:
        """
        Check if departement and direction are the same for every MAJIC file.
        Check if departement and direction are different from those
        given by the user in dialog
        """
        # Check if departement and direction are the same for every file
        if len(list(dep_dirs.keys())) > 1:
            self.go = False
            lst = ",<br/> ".join(f"département : {a[0:2]} et direction : {a[2:3]}" for a in dep_dirs)
            self.feedback.pushInfo(
                "<b>"
                "ERREUR : MAJIC - Les données concernent des départements et codes direction différents :"
                "</b>\n<br/> {}".format(lst)
            )
            self.feedback.pushInfo(
                "<b>Veuillez réaliser l'import en %s fois.</b>" % len(list(dep_dirs.keys()))
            )

            return False

        # Check if departement and direction are different from those given by the user in dialog
        # TODO: Check range in first slice, maybe wrong !!!
        f_dep = next(iter(dep_dirs.keys()))[0:2]
        f_dir = next(iter(dep_dirs.keys()))[2:3]
        if self.options.departement != f_dep or self.options.direction != f_dir:
            msg = (
                "<b>ERREUR : MAJIC</b> - Les numéros de <b>département</b> et de <b>direction</b> trouvés dans les fichiers "
                "ne correspondent pas à ceux renseignés dans les options du dialogue d'import:\n"
                "<br/>"
                "* fichiers : <b>{}</b> et <b>{}</b> <br/> "
                "* options : <b>{}</b> et <b>{}</b>"
            ).format(f_dep, f_dir, self.options.departement, self.options.direction)
            question = msg + (
                "\n\n<br/><br/>Voulez-vous continuer l'import avec les numéros trouvés dans les fichiers ?"
            )
            if self.confirm and self.confirm(question):
                self.options.departement = f_dep
                self.options.direction = f_dir
            else:
                self.go = False
                self.feedback.pushInfo(msg)

                return False

        return True

    def chunk(self, iterable, pieces_number=100000, padvalue=None):
        """
        Chunks an iterable (file, etc.)
        into pieces
        """
        try:
            from itertools import zip_longest

            return zip_longest(*[iter(iterable)] * pieces_number, fillvalue=padvalue)
        except MemoryError:
            self.feedback.pushInfo(IMPORT_MEMORY_ERROR_MESSAGE)
            self.go = False

            return None

    def import_majic_file_into_database(self, table_name: str, file_path: str, dep_dir: str) -> bool:
        """
        Import a single MAJIC file into the corresponding database table

        For example, import a file REVPROP.txt into the "prop" table
        """
        # Regex to remove all chars not in the range in ASCII table from space to ~
        # http://www.catonmat.net/blog/my-favorite-regex/
        regex_remove_non_ascii = re.compile(r"[^ -~]")

        # read file content
        with open(file_path, encoding="ascii", errors="replace") as fin:
            # Divide file into chunks
            for a in self.chunk(fin, self.maxInsertRows):
                # Build sql INSERT query depending on database
                if self.database.db_type == "postgis":
                    try:
                        sql = "BEGIN;"
                        sql = common_utils.setSearchPath(sql, self.database.schema)
                        # Build INSERT list
                        sql += "\n".join(
                            [
                                'INSERT INTO "{}" VALUES ({});'.format(
                                    table_name,
                                    common_utils.quoteString(
                                        regex_remove_non_ascii.sub(" ", x.strip("\r\n"))
                                    ),
                                )
                                for x in a
                                if x and x[0:3] == dep_dir
                            ]
                        )
                        sql += "COMMIT;"
                    except MemoryError:
                        # Issue #326
                        self.feedback.pushInfo(IMPORT_MEMORY_ERROR_MESSAGE)
                        self.go = False

                        return False

                    self.executeSqlQuery(sql)
                else:
                    try:
                        connection = self.database.sqlite_connection()
                        connection.executemany(
                            f'INSERT INTO "{table_name}" VALUES (?)',
                            [
                                (regex_remove_non_ascii.sub(" ", x.strip("\r\n")),)
                                for x in a
                                if x and x[0:3] == dep_dir
                            ],
                        )
                        connection.commit()
                    except MemoryError as err:
                        # Issue #326
                        Logger.critical(f"{err}")
                        self.feedback.pushInfo(IMPORT_MEMORY_ERROR_MESSAGE)
                        self.go = False

                        return False
                    except Exception as err:
                        Logger.log_exception(err)
                        self.feedback.pushInfo(f"<b>ERREUR : l'import du fichier '{file_path}' a échoué</b>")
                        self.go = False

                        return False

            # Return False if chunk returned an error
            if not self.go:
                return False

        return True

    def import_majic_into_database(self) -> bool:
        """
        Method which read each majic file
        and bulk import data into temp tables

        Returns False if no file processed
        """
        processed_files_count = 0
        majic_files_key: list[str] = []

        # Loop through all majic files

        # 1st path to build the complet list for each majic source type (nbat, bati, lloc, etc.)
        # and read 1st line to get departement and direction to compare to inputs
        dep_dirs, majic_files_found = self.get_available_majic_files()

        # Check if some important majic files are missing
        check_missing = self.check_missing_majic_files(majic_files_found)
        if not check_missing:
            return False

        # Check departement & direction
        check_depdir = self.check_majic_departement_direction(dep_dirs)
        if not check_depdir:
            return False

        # 2nd path to insert data
        dep_dir = f"{self.options.departement}{self.options.direction}"
        for item in self.majicSourceFileNames:
            table = item["table"]
            self.totalSteps += len(majic_files_found[table])
            processed_files_count += len(majic_files_found[table])
            for file_path in majic_files_found[table]:
                self.feedback.pushInfo(f"<b>{table}</b>")
                self.feedback.pushInfo(file_path)
                if table == "topo":
                    import_file = self.import_file_with_ogr(file_path, "topo")
                else:
                    import_file = self.import_majic_file_into_database(table, file_path, dep_dir)
                if not import_file:
                    continue

        if not processed_files_count:
            self.feedback.pushInfo(
                "<b>"
                "ERREUR : MAJIC - aucun fichier trouvé. Vérifier les noms de fichiers dans les paramètres "
                "du plugin et que le répertoire"
                "</b>'{}' <b>contient bien des fichiers qui correspondent</b>\n : {}".format(
                    self.options.majic_source_dir, ", ".join(majic_files_key)
                )
            )
            self.go = False

        return True

    def importEdigeo(self):
        """
        Import EDIGEO data
        into database
        """
        if not self.go:
            return False

        # Log : Print connection parameters to database
        jobTitle = "EDIGEO"
        self.beginJobLog(21, jobTitle)
        self.feedback.pushInfo(
            "Type de base : {}, Connexion: {}, Schéma: {}".format(
                self.database.db_type, self.database.connection_name, self.database.schema
            )
        )
        self.updateProgressBar()

        if self.go:
            # unzip edigeo files in temp dir
            self.setSubStep("Extraction des fichiers")
            self.updateProgressBar()
            self.unzipFolderContent(self.options.edigeo_source_dir)
            self.updateTimer()
        self.updateProgressBar()

        scriptList = []
        replaceDict = self.replaceDict.copy()

        # Add geo_unite_foncieres if needed
        if not self.database.table_exists("geo_unite_fonciere") and self.database.db_type == "postgis":
            scriptList.append(
                {
                    "title": "Ajout de la table geo_unite_foncieres",
                    "script": "%s" % os.path.join(self.pScriptDir, "edigeo_create_table_unite_fonciere.sql"),
                    "constraints": False,
                }
            )

        # Drop constraints
        scriptList.append(
            {
                "title": "Suppression des contraintes",
                "script": "%s" % os.path.join(self.pScriptDir, "commun_suppression_contraintes.sql"),
                "constraints": False,
                "divide": True,
            }
        )

        # Suppression et recréation des tables edigeo pour import
        if self.structure.has_data:
            replaceDict["SRID"] = self.targetSrid
            # Drop edigeo data
            self.dropEdigeoRawData()
            scriptList.append(
                {
                    "title": "Création des tables edigeo",
                    "script": "%s" % os.path.join(self.pScriptDir, "edigeo_create_import_tables.sql"),
                }
            )
        # Suppression des indexes
        if self.structure.has_data:
            scriptList.append(
                {
                    "title": "Suppression des indexes",
                    "script": "%s" % os.path.join(self.pScriptDir, "edigeo_drop_indexes.sql"),
                }
            )

        for item in scriptList:
            if self.go:
                self.setSubStep(item["title"])
                self.feedback.pushInfo("%s" % item["title"])
                s = item["script"]
                self.replaceParametersInScript(s, replaceDict)
                self.updateProgressBar()
                self.executeSqlScript(s, "divide" in item, "constraints" in item)
                if "constraints" in item:
                    self.hasConstraints = item["constraints"]
                self.updateTimer()
            self.updateProgressBar()

        # import edigeo *.thf and *.vec files into database
        if self.go:
            self.setSubStep("Import des fichiers")
            self.updateProgressBar()
            self.importAllEdigeoToDatabase()
            self.updateTimer()
        self.updateProgressBar()

        # Format edigeo data
        replaceDict = self.replaceDict.copy()
        replaceDict["DEPDIR"] = f"{self.options.departement}{self.options.direction}"

        scriptList = []

        scriptList.append(
            {
                "title": "Mise en forme des données",
                "script": os.path.join(self.pScriptDir, "edigeo_formatage_donnees.sql"),
                "divide": True,
            }
        )

        scriptList.append(
            {
                "title": "Placement des étiquettes",
                "script": os.path.join(self.pScriptDir, "edigeo_add_labels_xy.sql"),
            }
        )
        scriptList.append(
            {
                "title": "Création des indexes spatiaux",
                "script": os.path.join(self.pScriptDir, "edigeo_create_indexes.sql"),
                "divide": True,
            }
        )

        scriptList.append(
            {
                "title": "Ajout des contraintes",
                "script": os.path.join(self.pScriptDir, "commun_creation_contraintes.sql"),
                "constraints": True,
                "divide": True,
            }
        )

        # ajout des unités foncières
        # seulement si on a des données MAJIC de propriétaire
        self.structure = self.database.structure()
        if (
            self.options.do_majic_import or self.structure.has_majic_data_prop
        ) and self.database.db_type == "postgis":
            scriptList.append(
                {
                    "title": "Création Unités foncières",
                    "script": os.path.join(
                        self.pScriptDir, "edigeo_unites_foncieres_%s.sql" % self.database.db_type
                    ),
                }
            )

        # Ajout de la table parcelle_info
        if self.options.do_majic_import or self.structure.has_majic_data_prop:
            replaceDict["SRID"] = self.targetSrid
            scriptList.append(
                {
                    "title": "Ajout des champs a la table parcelle_info",
                    "script": "%s"
                    % os.path.join(self.pScriptDir, "edigeo_ajout_champs_parcelle_info_majic.sql"),
                    "divide": True,
                }
            )

            scriptList.append(
                {
                    "title": "Remplissage de la table parcelle_info",
                    "script": "%s"
                    % os.path.join(self.pScriptDir, "edigeo_create_table_parcelle_info_majic.sql"),
                }
            )
        else:
            replaceDict["SRID"] = self.targetSrid
            scriptList.append(
                {
                    "title": "Remplissage de la table parcelle_info",
                    "script": "%s"
                    % os.path.join(self.pScriptDir, "edigeo_create_table_parcelle_info_simple.sql"),
                }
            )

        for item in scriptList:
            if self.go:
                self.setSubStep(item["title"])
                self.feedback.pushInfo("%s" % item["title"])
                s = item["script"]
                self.replaceParametersInScript(s, replaceDict)
                self.updateProgressBar()

                self.executeSqlScript(s, "divide" in item, "constraints" in item)
                if "constraints" in item:
                    self.hasConstraints = item["constraints"]

                self.updateTimer()
                self.updateProgressBar()

        # drop edigeo raw data
        self.setSubStep("Suppression des fichiers temporaires")
        self.dropEdigeoRawData()
        self.updateTimer()
        self.updateProgressBar()

        return None

    def endImport(self):
        """
        Actions done when import has finished
        """
        # Log
        jobTitle = "FINALISATION"
        self.beginJobLog(1, jobTitle)

        # Debug spatialite
        if self.database.db_type == "spatialite":
            sql = (
                "SELECT RecoverGeometryColumn( 'parcelle_info', 'geom', %s, 'MULTIPOLYGON', 2 );"
                % self.targetSrid
            )
            sql += (
                "SELECT RecoverGeometryColumn( 'geo_batiment', 'geom', %s, 'MULTIPOLYGON', 2 );"
                % self.targetSrid
            )
            self.executeSqlQuery(sql)

        # Re-set SQL optimization parameters to default
        if self.database.db_type == "postgis":
            sql = "SET LOCAL synchronous_commit TO on;"
            self.executeSqlQuery(sql)
        else:
            sql = "PRAGMA journal_mode = MEMORY;"
            self.executeSqlQuery(sql)

        # Remove the temp folders
        self.setSubStep("Suppression des données temporaires")
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
            self.feedback.pushInfo(delmsg)
            self.go = False

        # Delete labels outside commune bbox
        if self.database.db_type == "spatialite":
            sql = "DELETE FROM geo_label WHERE NOT MbrWithin(geom, ( SELECT ST_Buffer(ST_Envelope(Collect(geom)), 100 ) AS geom FROM geo_commune ));"
        else:
            sql = "DELETE FROM geo_label WHERE NOT ST_Within(geom, ( SELECT ST_Buffer(ST_Envelope(ST_Collect(geom)), 100 ) AS geom FROM geo_commune ));"
            sql = common_utils.setSearchPath(sql, self.database.schema)
        self.executeSqlQuery(sql)

        # Add parcelle_info index for postgis only (not capability of that type for spatialite)
        if self.database.db_type == "postgis":
            sql = 'CREATE INDEX IF NOT EXISTS parcelle_info_geo_parcelle_sub ON parcelle_info( substr("geo_parcelle", 1, 10));'
            sql = common_utils.setSearchPath(sql, self.database.schema)
            self.executeSqlQuery(sql)

            # Add index on geo_parcelle and geo_batiment centroids
            sql = """
            CREATE INDEX IF NOT EXISTS geo_parcelle_centroide_geom_idx ON geo_parcelle USING gist (ST_Centroid(geom));
            CREATE INDEX IF NOT EXISTS geo_batiment_centroide_geom_idx ON geo_batiment USING gist (ST_Centroid(geom));
            """
            sql = common_utils.setSearchPath(sql, self.database.schema)
            self.executeSqlQuery(sql)

        # Parameters of the fiche parcellaire: the table is created, or completed with the new fields,
        # the parameters already set in the database are kept
        self.setSubStep("Paramètres de la fiche parcellaire")
        try:
            added = complete_table(self.database)
            if added:
                self.feedback.pushInfo(f"{added} paramètres ajoutés dans la table {FICHE_PARAMETRES_TABLE}")
        except (QgsProviderConnectionException, sqlite.Error) as e:
            self.feedback.pushInfo(
                f"<b>Erreur lors de l'écriture de la table {FICHE_PARAMETRES_TABLE} : {e}</b>"
            )

        # Refresh spatialite layer statistics
        if self.database.db_type == "spatialite":
            sql = ""
            for layer in self.geoTableList:
                sql += "SELECT UpdateLayerStatistics('%s', 'geom');" % layer
            self.executeSqlQuery(sql)

        if self.go:
            msg = "Import terminé"
        else:
            msg = "Des erreurs ont été rencontrées pendant l'import. Veuillez consulter le log."

        self.updateProgressBar()
        self.updateTimer()
        self.feedback.pushInfo(f"<b>{msg}</b>")

    #
    # TOOLS
    #

    def copyFilesToTemp(self, source: str, target: str) -> str | None:
        """
        Copy cadastre scripts
        into a temporary folder
        """
        if self.go:
            self.feedback.pushInfo(f"* Copie du répertoire {source} vers {target}")

            # copy script directory
            try:
                # Avoid hang from shutil.copytree() with dirs_exist_ok=True
                shutil.copytree(source, target, dirs_exist_ok=True)
                os.chmod(target, 0o740)
            except OSError as e:
                msg = "<b>Erreur lors de la copie des scripts d'import: %s</b>" % e
                self.feedback.reportError(msg)
                self.go = False
                return msg

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
                                file_path, ", ".join(extension_list)
                            ),
                            "cadastre",
                            Qgis.MessageLevel.Info,
                        )
                else:
                    if os.path.splitext(i)[1][1:].lower() not in extension_list:
                        file_list.append(file_path)
                    else:
                        QgsMessageLog.logMessage(
                            "Omission du fichier {} car il s'agit d'une extension non souhaitée "
                            '"{}"'.format(file_path, ", ".join(extension_list)),
                            "cadastre",
                            Qgis.MessageLevel.Info,
                        )

        return file_list

    def safe_zip_extract(self, zip_path, target_dir):
        abs_target = os.path.abspath(target_dir)

        with zipfile.ZipFile(zip_path, "r") as zf:
            for member in zf.namelist():
                # Construire le chemin complet de destination
                member_path = os.path.abspath(os.path.join(abs_target, member))

                # Vérifier que le fichier reste bien dans le dossier cible
                if not member_path.startswith(abs_target + os.sep) and member_path != abs_target:
                    raise SecurityError(f"Chemin suspect détecté : {member}")

                # Créer les sous-dossiers si besoin et extraire
                if member.endswith("/"):
                    os.makedirs(member_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(member_path), exist_ok=True)
                    with zf.open(member) as source, open(member_path, "wb") as target:
                        target.write(source.read())

    def safe_extract_tar(self, tf: tarfile.TarFile, target_dir: str, arguments: dict | None = None) -> None:
        """Extrait de manière sécurisée une archive TAR ouverte dans un répertoire cible en validant chaque chemin."""
        abs_target: str = os.path.abspath(target_dir)
        extract_kwargs = arguments.copy() if arguments else {}

        if "filter" in extract_kwargs and not hasattr(tarfile, "data_filter"):
            extract_kwargs.pop("filter")

        for member in tf.getmembers():
            member_path: str = os.path.abspath(os.path.join(abs_target, member.name))

            if not member_path.startswith(abs_target + os.sep) and member_path != abs_target:
                continue

            if member.issym() or member.islnk():
                link_path: str = os.path.abspath(os.path.join(abs_target, member.linkname))
                if not link_path.startswith(abs_target + os.sep) and link_path != abs_target:
                    continue

            tf.extract(member, path=abs_target, **extract_kwargs)

    def unzipFolderContent(self, path: str) -> str | None:
        """
        Scan content of specified path
        and unzip all content into a single folder
        """
        if self.go:
            self.feedback.pushInfo("* Décompression des fichiers")

            # get all the zip files
            zipFileList = self.list_files_in_directory(path, ["zip"])

            # unzip all files
            try:
                # unzip all zip in source folder
                for z in zipFileList:
                    # Extract file from edigeoDir into edigeoPlainDir
                    self.safe_zip_extract(z, self.edigeoPlainDir)

                # unzip all new zip in edigeoPlainDir
                inner_zips_pattern = os.path.join(self.edigeoPlainDir, "*.zip")
                for i, filename in enumerate(glob.glob(inner_zips_pattern)):
                    inner_folder = f"{filename[:-4]}_{i}"
                    self.safe_extract_zip(filename, inner_folder)
                    try:
                        os.remove(filename)
                    except OSError:
                        self.feedback.pushInfo("<b>Erreur lors de la suppression de %s</b>" % str(filename))
                        pass  # in Windows, sometime file is not unlocked

                error_message = (
                    "<b>Erreur</b> lors de l'ouverture du fichier {}. Un re-téléchargement du dossier "
                    "EDIGEO peut résoudre le problème"
                )

                i = 0
                # untar all tar.bz2 in source folder
                self.feedback.pushInfo("* Recherche des fichiers .bz2")
                tarFileListA = self.list_files_in_directory(path, ["bz2"])
                self.feedback.pushInfo(f"{len(tarFileListA)} fichier(s) .bz2 dans {path}")
                for z in tarFileListA:
                    with tarfile.open(z) as t:
                        try:
                            # See https://docs.python.org/3.10/library/tarfile.html#tarfile.TarFile.extractall
                            # See https://peps.python.org/pep-0706/
                            arguments = {"filter": "data"}
                            if sys.version_info < (3, 10, 12):
                                msg = (
                                    "Version de Python obsolète, votre version comporte une faille de sécurité "
                                    "concernant l'extraction d'une archive. Veuillez monter votre version de QGIS afin "
                                    "de passer à une version plus récente dès que possible."
                                )
                                self.feedback.pushInfo(f"<b>{msg}</b>")
                                # noinspection PyTypeChecker
                                QgsMessageLog.logMessage(msg, "cadastre", Qgis.MessageLevel.Warning)
                                arguments.pop("filter")

                            self.safe_extract_tar(
                                t,
                                os.path.join(self.edigeoPlainDir, "tar_%s" % i),
                                arguments,
                            )
                        except tarfile.ReadError:
                            # Issue GitHub #339
                            self.go = False
                            t.close()
                            error = error_message.format(z)
                            self.feedback.pushInfo(error)
                            return error
                        i += 1
                        t.close()

                # untar all new tar.bz2 found in self.edigeoPlainDir
                tarFileListB = self.list_files_in_directory(self.edigeoPlainDir, ["bz2"])
                self.feedback.pushInfo(f"{len(tarFileListA)} fichier(s) .bz2 dans {self.edigeoPlainDir}")
                for z in tarFileListB:
                    with tarfile.open(z) as t:
                        try:
                            self.safe_extract_tar(
                                t,
                                os.path.join(self.edigeoPlainDir, f"tar_{i}"),
                                arguments,
                            )
                        except tarfile.ReadError as err:
                            # Issue GitHub #339
                            Logger.log_exception(err)
                            self.go = False
                            t.close()
                            error = error_message.format(z)
                            self.feedback.pushInfo(error)
                            return error
                        i += 1
                        t.close()
                    try:
                        os.remove(z)
                    except OSError as err:
                        Logger.log_exception(err)
                        self.feedback.pushInfo(f"<b>Erreur lors de la suppression de {z}</b>")
                        pass  # in Windows, sometime file is not unlocked

            except OSError as err:
                Logger.log_exception(err)
                msg = "<b>Erreur lors de l'extraction des fichiers EDIGEO</b>"
                self.go = False
                self.feedback.pushInfo(msg)
                return msg

        return None

    def replaceParametersInScript(self, scriptPath, replaceDict):
        """
        Replace all parameters in sql scripts
        with given values
        """

        if self.go:
            try:
                data = ""
                scriptPath = Path(scriptPath)
                with scriptPath.open() as fin:
                    data = fin.read()
                # Will raise a KeyError exception for
                # unmatched placeholder (we *want* this, because otherwise
                # we would have an invalid sql script)
                data = Template(data).substitute(replaceDict)
                with scriptPath.open("w") as fout:
                    fout.write(data)

            except OSError as e:
                msg = "<b>Erreur lors du paramétrage des scripts d'import: %s</b>" % e
                self.go = False
                self.feedback.pushInfo(msg)
                return msg

            except KeyError as e:
                msg = "<b>Erreur lors du paramétrage des scripts d'import: %s</b>" % e
                self.go = False
                self.feedback.pushInfo(msg)
                return msg

        return None

    def executeSqlScript(self, scriptPath, divide=False, ignoreError=False):
        """
        Execute an SQL script file
        """

        if self.go:
            # Read sql script
            sql = ""
            try:
                with open(scriptPath, encoding="utf-8-sig") as f:
                    sql = f.read()
            except Exception as err:
                Logger.log_exception(err)
                with open(scriptPath, encoding="ISO-8859-15") as f:
                    sql = f.read()

            # Set schema if needed
            if self.database.db_type == "postgis":
                sql = common_utils.setSearchPath(sql, self.database.schema)

            # Remove make valid if asked
            if not self.options.edigeo_make_valid:
                mvReplaceDic = [
                    {"in": r"ST_CollectionExtract\(ST_MakeValid\(geom\),{2,3}\)", "out": r"geom"},
                    {"in": r"ST_CollectionExtract\(ST_MakeValid\(p\.geom\),{2,3}\)", "out": r"p.geom"},
                ]
                for a in mvReplaceDic:
                    r = re.compile(a["in"], re.IGNORECASE | re.MULTILINE)
                    sql = r.sub(a["out"], sql)

            # Convert SQL into spatialite syntax
            if self.database.db_type == "spatialite":
                sql = common_utils.postgisToSpatialite(sql, self.targetSrid)
                sql = common_utils.postgisToSpatialiteLocal10(sql, self.options.data_year)

            # Execute query
            if not divide:
                # self.feedback.pushInfo('|%s|' % sql)
                self.executeSqlQuery(sql, ignoreError)
            else:
                # Split all SQL into single queries
                statements = sql.split(";")
                self.totalSteps += len(statements)
                self.updateProgressBar()
                # Regex to find valid SQL queries
                r = re.compile(
                    r"select |insert |update |delete |alter |create |drop |truncate |comment |copy |vacuum |analyze ",
                    re.IGNORECASE | re.MULTILINE,
                )

                # Loop through for each individual statement
                for sqla in statements:
                    # Break if an error has been raised before
                    if not self.go:
                        break

                    # Regex to find comments which will be written in log
                    cr = re.compile(r"^-- (.+)", re.IGNORECASE | re.MULTILINE)

                    # Write comment taken from "-- some comment" lines
                    for comment in cr.findall(sqla):
                        # Update timer before writing the comment
                        # it will show the time taken by the previous statement
                        self.updateTimer()

                        # Write item. Ex: geo_borne_parcelle
                        self.feedback.pushInfo("  - %s" % comment.strip(" \n\r\t"))

                    # Do nothing if sql is only comment
                    if not r.search(sqla) or sqla.startswith("--~"):
                        continue

                    # Get SQL query
                    sql = "%s" % sqla
                    # self.feedback.pushInfo('@@%s$$' % sql)
                    # self.updateProgressBar()

                    # Spatialite performance adaptations
                    # This is fragile as Sqlite perf evolves a lot through time & versions
                    # Some queries runing fast earlier can perform poorly in some contexts
                    # ex: https://github.com/3liz/QgisCadastrePlugin/issues/262
                    avoid_query = False
                    if self.database.db_type == "spatialite":
                        spatialite_avoid_list = [
                            "geo_borne_annee_idx",
                            "geo_tpoint_object_rid_idx",
                            "geo_tpoint_annee_idx",
                            "geo_tline_object_rid_idx",
                            "geo_tline_annee_idx",
                            "geo_tsurf_object_rid_idx",
                            "geo_tsurf_annee_idx",
                        ]
                        for avoid_item in spatialite_avoid_list:
                            if avoid_item in sql:
                                avoid_query = True
                    if avoid_query:
                        # self.feedback.pushInfo('AVOID FOR SPATIALITE')
                        continue

                    # Execute query
                    self.executeSqlQuery(sql, ignoreError)

                    self.updateProgressBar()

        return

    def executeSqlQuery(self, sql, ignoreError=False):
        """
        Execute a SQL string query
        And commit
        """
        if not self.go:
            return

        try:
            self.database.execute(sql)
        except QgsProviderConnectionException as e:
            # PostgreSQL
            if not ignoreError and not re.search(r"CREATE INDEX ", sql, re.IGNORECASE):
                self.go = False
                self.feedback.reportError(str(e))
        except sqlite.Error as e:
            if not re.search(r"CREATE INDEX ", sql, re.IGNORECASE) and "duplicate column name" not in str(e):
                self.go = False
                self.feedback.pushInfo("<b>Erreur rencontrée pour la requête:</b> <p>%s</p>" % sql)
                self.feedback.pushInfo("<b>Erreur </b> <p>%s</p>" % format(e))

    def importAllEdigeoToDatabase(self):
        """
        Loop through all THF files
        and import each one into database
        """

        if self.go:
            self.feedback.pushInfo("* Import des fichiers EDIGEO dans la base")

            initialStep = self.step
            initialTotalSteps = self.totalSteps

            # THF
            self.setSubStep("Import des fichiers via ogr2ogr (*.thf)")
            self.feedback.pushInfo("  - Import des fichiers via ogr2ogr")
            # Get plain files in source directory
            thfList1 = self.list_files_in_directory(self.options.edigeo_source_dir, ["thf"])
            # Get files which have been uncompressed by plugin in temp folder
            thfList2 = self.list_files_in_directory(self.edigeoPlainDir, ["thf"])
            thfList = list(set(thfList1) | set(thfList2))
            self.step = 0
            self.totalSteps = len(thfList)
            for thf in thfList:
                self.import_file_with_ogr(thf, "thf")
                self.updateProgressBar()
                if not self.go:
                    break

        if self.go:
            # VEC - import relations between objects
            self.setSubStep("Import des relations (*.vec)")
            self.feedback.pushInfo("  - Import des relations (*.vec)")
            # Get plain files in source directory
            vecList1 = self.list_files_in_directory(self.options.edigeo_source_dir, ["vec"])
            # Get files which have been uncompressed by plugin in temp folder
            vecList2 = self.list_files_in_directory(self.edigeoPlainDir, ["vec"])
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
                self.feedback.pushInfo(
                    "  - %s multipolygones mis à jours dans la base de données" % self.multiPolygonUpdated
                )

        # Reinit progress var
        self.step = initialStep
        self.totalSteps = initialTotalSteps

    def import_file_with_ogr(self, file_path: str, file_type: str):
        """
        Import file into the database.

        It can either be an EDIGEO THF file or a TOPO file.
        """
        if not self.go:
            return

        # SRID configurations
        if file_type == "thf":
            targetSridOption = "-t_srs"
            if self.sourceSridFull == self.targetSridFull:
                targetSridOption = "-a_srs"

        # Build ogr2ogr command
        conn_name = self.database.connection_name
        uri = self.database.uri()

        # normalising file path
        file_path = os.path.normpath(file_path)
        # runGdal joins args with spaces then re-splits them (QProcess rules): wrap in double quotes
        file_path = f'"{file_path}"'
        if self.database.db_type == "postgis":
            service = uri.service()
            host = uri.host()
            port = uri.port()
            database = uri.database()
            username = uri.username()
            password = uri.password()
            authcfg = uri.authConfigId()

            # Get username/password from QGIS auth manager
            if authcfg:
                auth_mgr = QgsApplication.authManager()
                cfg_obj = QgsAuthMethodConfig()

                # loadAuthenticationConfig attend deux arguments en PyQGIS :
                # 1. ID authcfg
                # 2. un QStringList (ici, une simple liste Python vide)
                success, cfg = auth_mgr.loadAuthenticationConfig(authcfg, cfg_obj, True)
                if success and cfg.isValid():
                    auth_info = cfg.configMap()
                    username = auth_info.get("username", "")
                    password = auth_info.get("password", "")

                else:
                    QgsMessageLog.logMessage(
                        f"⚠️ Auth config '{authcfg}' invalide pour la connexion '{conn_name}'",
                        level=Qgis.Warning,
                    )

            # Build PG acess string for ogr2ogr command
            if service:
                pg_access = '"PG:service={} active_schema={}"'.format(service, self.database.schema)
            else:
                # qgis can connect to postgis DB without a specified host param connection, but ogr2ogr cannot
                if not host:
                    host = "localhost"

                pg_access = '"PG:host={} port={} dbname={} active_schema={} user={} password={}"'.format(
                    host, port, database, self.database.schema, username, password
                )
            cmdArgs = [
                "ogr2ogr",
                "",
            ]
            if file_type == "thf":
                cmdArgs += [
                    "-s_srs",
                    self.sourceSridFull,
                    targetSridOption,
                    self.targetSridFull,
                ]
            cmdArgs += [
                "-append",
                "-f",
                "PostgreSQL",
                pg_access,
                file_path,
                "-lco",
                "PG_USE_COPY=YES",
                "-gt",
                "50000",
                "--config",
                "PG_USE_COPY",
                "YES",
            ]
            if file_type == "thf":
                cmdArgs += [
                    "-lco",
                    "GEOMETRY_NAME=geom",
                    "-nlt",
                    "GEOMETRY",
                    "--config",
                    "OGR_EDIGEO_CREATE_LABEL_LAYERS",
                    "NO",
                ]
            if file_type == "topo":
                cmdArgs += [
                    "-nln",
                    "topo",
                ]
            # -c client_encoding=latin1
            # self.feedback.pushInfo(' '.join(cmdArgs))

        if self.database.db_type == "spatialite":
            database = '"{}"'.format(os.path.normpath(self.database.sqlite_path))

            cmdArgs = [
                "ogr2ogr",
                "",
            ]
            if file_type == "thf":
                cmdArgs += [
                    "-s_srs",
                    self.sourceSridFull,
                    targetSridOption,
                    self.targetSridFull,
                ]
            cmdArgs += [
                "-append",
                "-f",
                "SQLite",
                database,
                file_path,
                "-gt",
                "50000",
                "--config",
                "OGR_SQLITE_SYNCHRONOUS",
                "OFF",
                "--config",
                "OGR_SQLITE_CACHE",
                "512",
            ]
            if file_type == "thf":
                cmdArgs += [
                    "-lco",
                    "GEOMETRY_NAME=geom",
                    "-nlt",
                    "GEOMETRY",
                    "-dsco",
                    "SPATIALITE=YES",
                    "--config",
                    "OGR_EDIGEO_CREATE_LABEL_LAYERS",
                    "NO",
                ]
            if file_type == "topo":
                cmdArgs += [
                    "-nln",
                    "topo",
                ]

        # self.feedback.pushInfo( ' '.join(cmdArgs))
        if not self.go:
            return

        # Use GdalUtils to run ogr2ogr command
        loglines = []
        error_message = ""
        try:
            loglines = GdalUtils.runGdal(cmdArgs, None)
        except QgsProcessingException as e:
            self.go = False
            error_message = f"Erreur lors de l'exécution d'ogr2ogr : {e}"
            self.feedback.pushInfo(error_message)

        for line in loglines:
            if "ERROR" in line or "error" in line:
                self.go = False
                error_message = f"Erreur lors de l'exécution d'ogr2ogr : {line}"
                self.feedback.pushInfo(error_message)
                break

        if not self.go:
            self.feedback.pushInfo(
                "<b>Erreur - L'import des données via OGR2OGR a échoué:</b>\n\n{}\n\n{}".format(
                    error_message, cmdArgs
                )
            )

        return

    def importEdigeoVecToDatabase(self, path):
        """
        Get edigeo relations between objects
        from a .VEC file
        and add them in edigeo_rel table
        """
        if self.go:
            reg = "^RID[a-zA-z]{1}[a-zA-z]{1}[0-9]{2}:(Rel_.+)_(Objet_[0-9]+)_(Objet_[0-9]+)"
            try:
                with open(path, encoding="utf8") as inputFile:
                    # Get a list of RID relations combining a "Rel" and two "_Objet"
                    la = [a[0] for a in [re.findall(r"%s" % reg, line) for line in inputFile] if a]
            except Exception as err:
                Logger.log_exception(err)
                with open(path, encoding="ISO-8859-15") as inputFile:
                    # Get a list of RID relations combining a "Rel" and two "_Objet"
                    la = [a[0] for a in [re.findall(r"%s" % reg, line) for line in inputFile] if a]

            if la:
                # Create a sql script to insert all items
                if self.database.db_type == "postgis":
                    sql = "BEGIN;"
                    for item in la:
                        sql += "INSERT INTO edigeo_rel ( nom, de, vers) VALUES ( '{}', '{}', '{}');".format(
                            item[0], item[1], item[2]
                        )
                    sql += "COMMIT;"
                    sql = common_utils.setSearchPath(sql, self.database.schema)
                    self.executeSqlQuery(sql)
                if self.database.db_type == "spatialite":
                    connection = self.database.sqlite_connection()
                    query = "INSERT INTO edigeo_rel (nom, de, vers) VALUES (?, ?, ?)"
                    try:
                        connection.executemany(query, [(item[0], item[1], item[2]) for item in la])
                        connection.commit()
                    except Exception as err:
                        Logger.log_exception(err)
                        self.feedback.pushInfo("<b>Erreurs pendant la requête :</b> %s" % query)

    def updateMultipolygonFromVec(self, path, layerType="edigeo"):
        """
        Run the update multipolygon query
        for each VEC files on the given layer type
        (edigeo = import tables, cadastre = cadastre geo_* tables)
        """
        # Get SQL update queries
        sqlList = self.getUpdateMultipolygonFromVecQuery(path, layerType)

        # Run each query
        for sql in sqlList:
            if self.database.db_type == "postgis":
                sql = common_utils.setSearchPath(sql, self.database.schema)
            self.executeSqlQuery(sql)

    def getUpdateMultipolygonFromVecQuery(self, path, layerType="edigeo"):
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
            "batiment_id": "geo_batiment",
            "commune_id": "geo_commune",
            "lieudit_id": "geo_lieudit",
            "parcelle_id": "geo_parcelle",
            "section_id": "geo_section",
            "subdfisc_id": "geo_subdfisc",
            "subdsect_id": "geo_subdsect",
            "tronfluv_id": "geo_tronfluv",
            "tronroute_id": "geo_tronroute",
            "tsurf_id": "geo_tsurf",
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
                if layerType == "cadastre":
                    table = impCadRel[table]

                # Build SQL
                sql = ""
                for obj, wkt in list(item.items()):
                    self.multiPolygonUpdated += 1
                    sql += " UPDATE {} SET geom = ST_Transform(ST_GeomFromText('{}', {}), {})".format(
                        table, wkt, self.sourceSrid, self.targetSrid
                    )
                    # only for given object id
                    sql += " WHERE object_rid = '%s' " % str(obj)
                    # only if the 2 geometries are indeed different. To be debbuged : geom <> geom : operator is not unique
                    # ~ sql+= " AND geom != ST_Transform(ST_GeomFromText('%s', %s), %s) " % (wkt, self.sourceSrid, self.targetSrid)
                    # only if the 2 geometries are related (object_rid is not unique)
                    if self.database.db_type == "postgis":
                        sql += " AND geom @ ST_Transform(ST_GeomFromText('{}', {}), {}) ; ".format(
                            wkt, self.sourceSrid, self.targetSrid
                        )
                    else:
                        sql += (
                            " AND ST_Intersects(geom, ST_Transform(ST_GeomFromText('{}', {}), {}) ); ".format(
                                wkt, self.sourceSrid, self.targetSrid
                            )
                        )
                sqlList.append(sql)

        return sqlList

    def dropEdigeoRawData(self):
        """
        Drop Edigeo raw data tables
        """

        if self.go:
            # DROP edigeo import tables
            edigeoImportTables = [
                "batiment_id",
                "borne_id",
                "boulon_id",
                "commune_id",
                "croix_id",
                "id_s_obj_z_1_2_2",
                "lieudit_id",
                "numvoie_id",
                "parcelle_id",
                "ptcanv_id",
                "section_id",
                "subdfisc_id",
                "subdsect_id",
                "symblim_id",
                "tline_id",
                "tpoint_id",
                "tronfluv_id",
                "tronroute_id",
                "tsurf_id",
                "voiep_id",
                "zoncommuni_id",
                # ~ 'edigeo_rel',
            ]
            sql = ""
            for table in edigeoImportTables:
                sql += 'DROP TABLE IF EXISTS "%s";' % table
            if self.database.db_type == "postgis":
                sql = common_utils.setSearchPath(sql, self.database.schema)
            self.executeSqlQuery(sql)
