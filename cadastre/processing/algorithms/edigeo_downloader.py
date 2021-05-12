import os

from pathlib import Path

import processing

from qgis.core import (
    QgsProcessingMultiStepFeedback,
    QgsProcessingOutputFolder,
    QgsProcessingOutputNumber,
    QgsProcessingOutputString,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterString,
)

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
            'Liste des code INSEE à télécharger, séparés par ","',
            # defaultValue='25047,05046'
        )
        self.addParameter(parameter)

        parameter = QgsProcessingParameterString(
            self.FILTRE,
            'Filtre sur les feuilles séparés par "," peut-être "050170000C03,AB" qui '
            'téléchargent toutes les feuilles AB et 050170000C03',
            # defaultValue='050170000C03,AB'
        )
        self.addParameter(parameter)

        parameter = QgsProcessingParameterFolderDestination(
            self.DOSSIER,
            'Dossier de destination'
        )
        self.addParameter(parameter)

        parameter = QgsProcessingParameterString(
            self.DATE,
            'Date, disponible sur le site cadastre.data.gouv.fr (exemple "2021-02-01")',
            defaultValue='latest',
        )
        self.addParameter(parameter)

        parameter = QgsProcessingParameterString(
            self.URL_TEMPLATE,
            'URL modèle, avec {date}, {departement}, {commune}',
            defaultValue=self.url(),
        )
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
            feedback.pushDebugInfo("Création du répertoire {}".format(directory))
            os.makedirs(directory, exist_ok=True)

        filtre = [c.strip() for c in filtre.split(',')]

        communes = [c.strip() for c in communes.split(',')]
        departements = []
        self.results = {
            self.NB_COMMUNES: len(communes),
            self.NB_FEUILLES: 0,
            self.DEPARTEMENTS: "",
        }

        multi_feedback = QgsProcessingMultiStepFeedback(len(communes), feedback)

        for i, commune_insee in enumerate(communes):

            commune = Commune(commune_insee, date=date, base_url=url)
            if not self.download_commune(directory, commune, filtre, multi_feedback, context):
                multi_feedback.reportError("Erreur sur la commune {}".format(commune.insee))
                break

            if multi_feedback.isCanceled():
                break

            multi_feedback.setCurrentStep(i)

            if commune.departement not in departements:
                departements.append(commune.departement)

        self.results[self.DEPARTEMENTS] = ','.join(departements)

        multi_feedback.pushInfo("\n")
        multi_feedback.pushInfo("\n")
        multi_feedback.pushInfo("Téléchargement terminé pour {} communes".format(len(communes)))
        multi_feedback.pushInfo("{} feuilles".format(self.results[self.NB_FEUILLES]))
        multi_feedback.pushInfo("dans {}".format(str(directory)))
        multi_feedback.pushInfo("\n")
        multi_feedback.pushInfo("\n")
        return self.results

    def download_commune(self, directory: Path, commune: Commune, filtre: list, feedback, context) -> bool:
        """ Télécharger une commune. """
        commune_directory = directory.joinpath(commune.insee)
        if commune_directory.exists():
            feedback.reportError("Omission de {}, le répertoire existe déjà.".format(commune.insee))
            return False

        feedback.pushInfo("Téléchargement de l'index concernant {}".format(commune.insee))

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
        feedback.pushInfo("  {} feuilles".format(parser.count))
        for feuille in parser.feuilles:
            feedback.pushInfo(feuille.name)

        if not commune_directory.exists():
            feedback.pushDebugInfo("Création du répertoire {}".format(commune))
            os.makedirs(commune_directory, exist_ok=True)

        for feuille in parser.feuilles:

            self.download_feuille(commune, feuille, commune_directory, feedback, context)
            if feedback.isCanceled():
                break

        self.results[self.NB_FEUILLES] += parser.count
        return True

    @staticmethod
    def download_feuille(commune, feuille, directory, feedback, context) -> bool:
        feedback.pushInfo("Téléchargement de {} {}".format(commune.insee, feuille.name))
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
