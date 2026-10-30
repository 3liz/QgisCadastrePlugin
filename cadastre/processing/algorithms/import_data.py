__copyright__ = "Copyright 2026, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import os

from abc import abstractmethod
from typing import Any

from qgis.core import (
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingOutputNumber,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterCrs,
    QgsProcessingParameterDatabaseSchema,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterFile,
    QgsProcessingParameterNumber,
    QgsProcessingParameterProviderConnection,
    QgsProcessingParameterString,
    QgsProviderConnectionException,
)

from cadastre.cadastre_database import POSTGIS, PROVIDERS, SPATIALITE, CadastreDatabase
from cadastre.cadastre_import import ImportOptions, cadastreImport
from cadastre.definitions import MAXIMUM_YEAR, MINIMUM_YEAR, URL_DOCUMENTATION
from cadastre.feedback import CadastreProcessingFeedback
from cadastre.processing.algorithms.base import BaseProcessingAlgorithm


class ImportBaseAlgorithm(BaseProcessingAlgorithm):
    """Import EDIGEO and/or MAJIC files into a database, like the import dialog."""

    # INPUTS
    CONNEXION = "CONNEXION"
    DOSSIER_EDIGEO = "DOSSIER_EDIGEO"
    DOSSIER_MAJIC = "DOSSIER_MAJIC"
    PROJECTION_SOURCE = "PROJECTION_SOURCE"
    PROJECTION_CIBLE = "PROJECTION_CIBLE"
    DEPARTEMENT = "DEPARTEMENT"
    DIRECTION = "DIRECTION"
    LOT = "LOT"
    VERSION = "VERSION"
    ANNEE = "ANNEE"
    CORRIGER_GEOMETRIES = "CORRIGER_GEOMETRIES"
    DEP_DIR_FICHIERS = "DEP_DIR_FICHIERS"

    # OUTPUTS
    SUCCESS = "SUCCESS"

    @property
    @abstractmethod
    def db_type(self) -> str:
        """postgis or spatialite"""

    def group(self):
        return "Import"

    def groupId(self):
        return "import"

    def helpUrl(self):
        return f"{URL_DOCUMENTATION}/extension-qgis/import/"

    @staticmethod
    def tags():
        return "import", "edigeo", "édigéo", "majic"

    def initDatabaseParameters(self):
        """Parameters for the database"""
        self.addParameter(
            QgsProcessingParameterProviderConnection(
                self.CONNEXION,
                "Connexion à la base de données",
                PROVIDERS[self.db_type],
            )
        )

    def initAlgorithm(self, config):
        self.initDatabaseParameters()

        parameter = QgsProcessingParameterFile(
            self.DOSSIER_EDIGEO,
            "Répertoire des fichiers EDIGEO",
            behavior=QgsProcessingParameterFile.Behavior.Folder,
            optional=True,
        )
        parameter.setHelp("Les fichiers peuvent être compressés (tar.bz2, zip)")
        self.addParameter(parameter)

        self.addParameter(
            QgsProcessingParameterFile(
                self.DOSSIER_MAJIC,
                "Répertoire des fichiers MAJIC",
                behavior=QgsProcessingParameterFile.Behavior.Folder,
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.PROJECTION_SOURCE,
                "Projection source des fichiers EDIGEO",
                defaultValue="EPSG:2154",
            )
        )
        self.addParameter(
            QgsProcessingParameterCrs(
                self.PROJECTION_CIBLE,
                "Projection cible dans la base de données",
                defaultValue="EPSG:2154",
            )
        )

        parameter = QgsProcessingParameterString(self.DEPARTEMENT, "Département")
        parameter.setHelp('Sur 2 caractères, par exemple "05" ou "2A"')
        self.addParameter(parameter)

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DIRECTION,
                "Direction",
                type=QgsProcessingParameterNumber.Type.Integer,
                defaultValue=0,
                minValue=0,
                maxValue=9,
            )
        )

        parameter = QgsProcessingParameterString(self.LOT, "Lot")
        parameter.setHelp("Identifiant de cet import : code commune, date d'import, etc.")
        self.addParameter(parameter)

        for name, description in ((self.VERSION, "Version du format"), (self.ANNEE, "Année des données")):
            self.addParameter(
                QgsProcessingParameterNumber(
                    name,
                    description,
                    type=QgsProcessingParameterNumber.Type.Integer,
                    defaultValue=MAXIMUM_YEAR,
                    minValue=MINIMUM_YEAR,
                    maxValue=MAXIMUM_YEAR,
                )
            )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.CORRIGER_GEOMETRIES,
                "Corriger les géométries invalides",
                defaultValue=True,
            )
        )

        parameter = QgsProcessingParameterBoolean(
            self.DEP_DIR_FICHIERS,
            "Utiliser le département et la direction des fichiers MAJIC s'ils sont différents",
            defaultValue=False,
        )
        parameter.setHelp(
            "Sinon, l'import des fichiers MAJIC est annulé si le département et la direction "
            "ne correspondent pas aux paramètres"
        )
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.Flag.FlagAdvanced)
        self.addParameter(parameter)

        self.addOutput(QgsProcessingOutputNumber(self.SUCCESS, "Succès"))

    def schema(self, parameters: dict[str, Any], context: QgsProcessingContext) -> str:
        """Schema where to import the data, PostGIS only"""
        return ""

    def database(
        self, parameters: dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> CadastreDatabase:
        connection_name = self.parameterAsConnectionName(parameters, self.CONNEXION, context)
        try:
            return CadastreDatabase.from_connection(
                self.db_type, connection_name, self.schema(parameters, context)
            )
        except QgsProviderConnectionException as e:
            raise QgsProcessingException(f"Impossible de se connecter à '{connection_name}' : {e}")

    def checkParameterValues(
        self, parameters: dict[str, Any], context: QgsProcessingContext
    ) -> tuple[bool, str]:
        """Same checks as the import dialog, before connecting to the database"""
        ok, message = super().checkParameterValues(parameters, context)
        if not ok:
            return ok, message

        def is_dir(name: str) -> bool:
            path = self.parameterAsFile(parameters, name, context)
            return bool(path) and os.path.isdir(path)

        errors = []
        if not is_dir(self.DOSSIER_MAJIC) and not is_dir(self.DOSSIER_EDIGEO):
            errors.append("Un répertoire existant de fichiers EDIGEO ou MAJIC est obligatoire")
        if is_dir(self.DOSSIER_EDIGEO) and not (
            self.parameterAsCrs(parameters, self.PROJECTION_SOURCE, context).isValid()
            and self.parameterAsCrs(parameters, self.PROJECTION_CIBLE, context).isValid()
        ):
            errors.append("Les projections source et cible sont obligatoires pour l'import EDIGEO")
        if len(self.parameterAsString(parameters, self.DEPARTEMENT, context).strip()) != 2:
            errors.append("Le département doit faire 2 caractères")
        if not self.parameterAsString(parameters, self.LOT, context).strip():
            errors.append("Le lot est obligatoire")

        if errors:
            return False, "\n".join(errors)
        return True, ""

    def processAlgorithm(self, parameters, context, feedback):
        def crs(name: str) -> str:
            value = self.parameterAsCrs(parameters, name, context)
            return value.authid() if value.isValid() else ""

        options = ImportOptions(
            database=self.database(parameters, context, feedback),
            data_version=str(self.parameterAsInt(parameters, self.VERSION, context)),
            data_year=str(self.parameterAsInt(parameters, self.ANNEE, context)),
            lot=self.parameterAsString(parameters, self.LOT, context).strip(),
            departement=self.parameterAsString(parameters, self.DEPARTEMENT, context).strip(),
            direction=str(self.parameterAsInt(parameters, self.DIRECTION, context)),
            majic_source_dir=self.parameterAsFile(parameters, self.DOSSIER_MAJIC, context),
            edigeo_source_dir=self.parameterAsFile(parameters, self.DOSSIER_EDIGEO, context),
            edigeo_source_proj=crs(self.PROJECTION_SOURCE),
            edigeo_target_proj=crs(self.PROJECTION_CIBLE),
            edigeo_make_valid=self.parameterAsBool(parameters, self.CORRIGER_GEOMETRIES, context),
        )

        use_files_dep_dir = self.parameterAsBool(parameters, self.DEP_DIR_FICHIERS, context)

        def confirm(question: str) -> bool:
            if use_files_dep_dir:
                feedback.pushWarning("Utilisation du département et de la direction des fichiers MAJIC")
            return use_files_dep_dir

        try:
            success = cadastreImport(options, CadastreProcessingFeedback(feedback), confirm).run()
        finally:
            options.database.close()

        if not success:
            raise QgsProcessingException(
                "Des erreurs ont été rencontrées pendant l'import, veuillez consulter le journal."
            )

        return {self.SUCCESS: 1}


class ImportPostgisAlgorithm(ImportBaseAlgorithm):
    SCHEMA = "SCHEMA"

    @property
    def db_type(self) -> str:
        return POSTGIS

    def name(self):
        return "import_postgis"

    def displayName(self):
        return "Import des données dans PostGIS"

    def shortHelpString(self):
        return (
            "Ce traitement importe les fichiers EDIGEO et/ou MAJIC dans un schéma d'une base PostGIS, "
            "comme le dialogue d'import du plugin.\n"
            "Le schéma est créé s'il n'existe pas."
        )

    def initDatabaseParameters(self):
        super().initDatabaseParameters()
        self.addParameter(
            QgsProcessingParameterDatabaseSchema(
                self.SCHEMA,
                "Schéma",
                self.CONNEXION,
                defaultValue="cadastre",
            )
        )

    def schema(self, parameters, context):
        return self.parameterAsSchema(parameters, self.SCHEMA, context)

    def database(self, parameters, context, feedback):
        database = super().database(parameters, context, feedback)
        if not database.schema:
            raise QgsProcessingException("Le schéma est obligatoire")

        if database.schema not in database.schemas():
            feedback.pushInfo(f"Création du schéma {database.schema}")
            try:
                database.create_schema(database.schema)
            except QgsProviderConnectionException as e:
                raise QgsProcessingException(f"Impossible de créer le schéma {database.schema} : {e}")
        return database


class ImportSpatialiteAlgorithm(ImportBaseAlgorithm):
    @property
    def db_type(self) -> str:
        return SPATIALITE

    def name(self):
        return "import_spatialite"

    def displayName(self):
        return "Import des données dans Spatialite"

    def shortHelpString(self):
        return (
            "Ce traitement importe les fichiers EDIGEO et/ou MAJIC dans une base Spatialite, "
            "comme le dialogue d'import du plugin."
        )
