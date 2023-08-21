import os

from pathlib import Path

import processing

from qgis.core import (
    QgsProcessingMultiStepFeedback,
    QgsProcessingOutputNumber,
    QgsProcessingOutputString,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterString,
)

from cadastre.definitions import URL_DOCUMENTATION
from cadastre.edigeo_parser import Commune, Parser
from cadastre.processing.algorithms.base import BaseProcessingAlgorithm

__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"


class EdigeoDownloader(BaseProcessingAlgorithm):

    # INPUTS
    LISTE_CODE_INSEE = 'LISTE_CODE_INSEE'
    FILTRE = 'FILTRE'
    DATE = 'DATE'
    URL_TEMPLATE = 'URL_TEMPLATE'
    DOSSIER = 'DOSSIER'

    # OUTPUTS
    NB_COMMUNES = 'NB_COMMUNES'
    NB_FEUILLES = 'NB_FEUILLES'
    DEPARTEMENTS = 'DEPARTEMENTS'

    @classmethod
    def url(cls):
        return (
            "https://cadastre.data.gouv.fr/data/dgfip-pci-vecteur/{date}/edigeo/feuilles/{"
            "departement}/{commune}/"
        )

    def __init__(self):
        self.results = {}
        super().__init__()

    def initAlgorithm(self, config):
        parameter = QgsProcessingParameterString(
            self.LISTE_CODE_INSEE,
            'Liste des codes INSEE à télécharger',
            # defaultValue='25047,05046'
        )
        self.set_tooltip_parameter(parameter, 'séparés par ","')
        self.addParameter(parameter)

        parameter = QgsProcessingParameterString(
            self.FILTRE,
            'Filtre sur les feuilles',
            # defaultValue='050170000C03,AB',
            optional=True,
        )
        self.set_tooltip_parameter(
            parameter,
            'séparés par ",", peut-être "050170000C03,AB" qui téléchargent toutes les feuilles AB et '
            '050170000C03'
        )
        self.addParameter(parameter)

        parameter = QgsProcessingParameterFolderDestination(
            self.DOSSIER,
            'Dossier de destination'
        )
        self.set_tooltip_parameter(parameter, 'Dossier de destination pour les fichiers Edigeo')
        self.addParameter(parameter, createOutput=True)

        parameter = QgsProcessingParameterString(
            self.DATE,
            'Date, disponible sur le site cadastre.data.gouv.fr (exemple "2023-01-01")',
            defaultValue='latest',
        )
        self.set_tooltip_parameter(parameter, 'Par défaut "latest"')
        self.addParameter(parameter)

        parameter = QgsProcessingParameterString(
            self.URL_TEMPLATE,
            'URL modèle, avec {date}, {departement}, {commune}',
            defaultValue=self.url(),
        )
        self.set_tooltip_parameter(parameter, 'À ne changer que si l\'URL change')
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(parameter)

        self.addOutput(QgsProcessingOutputNumber(self.NB_COMMUNES, 'Nombre de communes'))
        self.addOutput(QgsProcessingOutputNumber(self.NB_FEUILLES, 'Nombre de feuilles'))
        self.addOutput(QgsProcessingOutputString(self.DEPARTEMENTS, 'Départements, séparés par ","'))

    def processAlgorithm(self, parameters, context, feedback):
        communes = self.parameterAsString(parameters, self.LISTE_CODE_INSEE, context)
        filtre = self.parameterAsString(parameters, self.FILTRE, context)
        date = self.parameterAsString(parameters, self.DATE, context)
        url = self.parameterAsString(parameters, self.URL_TEMPLATE, context)
        directory = Path(self.parameterAsString(parameters, self.DOSSIER, context))

        if not directory.exists():
            feedback.pushDebugInfo(f"Création du répertoire {directory}")
            os.makedirs(directory, exist_ok=True)

        filtre = [c.strip() for c in filtre.split(',')]

        communes = [c.strip() for c in communes.split(',')]
        departements = []
        self.results = {
            self.DOSSIER: str(directory),
            self.NB_COMMUNES: len(communes),
            self.NB_FEUILLES: 0,
            self.DEPARTEMENTS: "",
        }

        multi_feedback = QgsProcessingMultiStepFeedback(len(communes), feedback)

        for i, commune_insee in enumerate(communes):

            commune = Commune(commune_insee, date=date, base_url=url)
            if not self.download_commune(directory, commune, filtre, multi_feedback, context):
                multi_feedback.reportError(f"Erreur sur la commune {commune.insee}")
                break

            if multi_feedback.isCanceled():
                break

            multi_feedback.setCurrentStep(i)

            if commune.departement not in departements:
                departements.append(commune.departement)

        self.results[self.DEPARTEMENTS] = ','.join(departements)

        multi_feedback.pushInfo("\n")
        multi_feedback.pushInfo("\n")
        multi_feedback.pushInfo(f"Téléchargement terminé pour {len(communes)} communes")
        multi_feedback.pushInfo(f"{self.results[self.NB_FEUILLES]} feuilles")
        multi_feedback.pushInfo(f"dans {str(directory)}")
        multi_feedback.pushInfo("\n")
        multi_feedback.pushInfo("\n")
        return self.results

    def download_commune(self, directory: Path, commune: Commune, filtre: list, feedback, context) -> bool:
        """ Télécharger une commune. """
        commune_directory = directory.joinpath(commune.insee)
        if commune_directory.exists():
            feedback.reportError(f"Omission de {commune.insee}, le répertoire existe déjà.")
            return False

        feedback.pushInfo(f"Téléchargement de l'index concernant {commune.insee}")
        feedback.pushDebugInfo(commune.url)

        params = {
            'URL': commune.url,
            'OUTPUT': 'TEMPORARY_OUTPUT',
        }
        data = processing.run(
            "native:filedownloader",
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True,
        )
        parser = Parser(data['OUTPUT'], commune, feuille_filter=filtre)
        parser.parse()
        feedback.pushInfo(f"  {parser.count} feuilles")
        for feuille in parser.feuilles:
            feedback.pushInfo(feuille.name)

        if not commune_directory.exists():
            feedback.pushDebugInfo(f"Création du répertoire {commune}")
            os.makedirs(commune_directory, exist_ok=True)

        for feuille in parser.feuilles:

            self.download_feuille(commune, feuille, commune_directory, feedback, context)
            if feedback.isCanceled():
                break

        self.results[self.NB_FEUILLES] += parser.count
        return True

    @staticmethod
    def download_feuille(commune, feuille, directory, feedback, context) -> bool:
        feedback.pushInfo(f"Téléchargement de {commune.insee} {feuille.name}")
        params = {
            'URL': commune.url_feuille(feuille),
            'OUTPUT': str(directory.joinpath(feuille.link).absolute()),
        }
        processing.run(
            "native:filedownloader",
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True,
        )
        return True

    def name(self):
        return 'telechargeur_edigeo_communal'

    def displayName(self):
        return 'Téléchargeur Édigéo communal'

    def shortHelpString(self):
        return (
            'Ce traitement permet de télécharger toutes les feuilles Edigéo sur plusieurs communes.\n'
            'La date peut-être "latest" ou alors une date disponible sur '
            'https://cadastre.data.gouv.fr/datasets/plan-cadastral-informatise\n'
            'L\'URL ne doit pas être changé, sauf si l\'API de cadastre.gouv.fr change.'
        )

    def helpUrl(self):
        return f"{URL_DOCUMENTATION}/extension-qgis/donnees/#edigeo"
