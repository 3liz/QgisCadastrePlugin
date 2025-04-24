"""
/***************************************************************************
 Cadastre - Processing config algorithms
                                 A QGIS plugin
 This plugins helps users to import the french land registry ('cadastre')
 into a database. It is meant to ease the use of the data in QGIs
 by providing search tools and appropriate layer symbology.
                              -------------------
        begin                : 2019-05-15
        copyright            : (C) 2019 by 3liz
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

from qgis.core import (
    QgsProcessing,
    QgsProcessingOutputNumber,
    QgsProcessingParameterField,
    QgsProcessingParameterVectorLayer,
)

from cadastre.definitions import URL_DOCUMENTATION
from cadastre.processing.algorithms.base import BaseProcessingAlgorithm


class ConfigProjectAlgorithm(BaseProcessingAlgorithm):
    """
    Algorithm to set project variables for cadastre use
    """

    COMMUNE_LAYER = 'COMMUNE_LAYER'
    COMMUNE_UNIQUE_FIELD = 'COMMUNE_UNIQUE_FIELD'
    SECTION_LAYER = 'SECTION_LAYER'
    SECTION_UNIQUE_FIELD = 'SECTION_UNIQUE_FIELD'
    PARCELLE_LAYER = 'PARCELLE_LAYER'
    PARCELLE_UNIQUE_FIELD = 'PARCELLE_UNIQUE_FIELD'

    SUCCESS = 'SUCCESS'

    def initAlgorithm(self, config):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.COMMUNE_LAYER,
                self.tr('La couche communes'),
                [QgsProcessing.SourceType.TypeVectorPolygon],
                defaultValue='Communes'
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.COMMUNE_UNIQUE_FIELD,
                self.tr('Champs identifiant les communes'),
                parentLayerParameterName=self.COMMUNE_LAYER,
                defaultValue='geo_commune',
                type=QgsProcessingParameterField.DataType.String
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.SECTION_LAYER,
                self.tr('La couche sections'),
                [QgsProcessing.SourceType.TypeVectorPolygon],
                defaultValue='Sections',
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.SECTION_UNIQUE_FIELD,
                self.tr('Champs identifiant les sections'),
                parentLayerParameterName=self.SECTION_LAYER,
                defaultValue='geo_section',
                type=QgsProcessingParameterField.DataType.String
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.PARCELLE_LAYER,
                self.tr('La couche parcelles'),
                [QgsProcessing.SourceType.TypeVectorPolygon],
                defaultValue='Parcelles',
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.PARCELLE_UNIQUE_FIELD,
                self.tr('Champs identifiant les parcelles'),
                parentLayerParameterName=self.PARCELLE_LAYER,
                defaultValue='geo_parcelle',
                type=QgsProcessingParameterField.DataType.String
            )
        )

        self.addOutput(QgsProcessingOutputNumber(self.SUCCESS, self.tr('Succès')))

    def processAlgorithm(self, parameters, context, feedback):
        commune_layer = self.parameterAsVectorLayer(parameters, self.COMMUNE_LAYER, context)
        commune_unique_field = self.parameterAsString(parameters, self.COMMUNE_UNIQUE_FIELD, context)

        section_layer = self.parameterAsVectorLayer(parameters, self.SECTION_LAYER, context)
        section_unique_field = self.parameterAsString(parameters, self.SECTION_UNIQUE_FIELD, context)

        parcelle_layer = self.parameterAsVectorLayer(parameters, self.PARCELLE_LAYER, context)
        parcelle_unique_field = self.parameterAsString(parameters, self.PARCELLE_UNIQUE_FIELD, context)

        variables = context.project().customVariables()

        variables['cadastre_commune_layer_id'] = commune_layer.id()
        variables['cadastre_commune_unique_field'] = commune_unique_field

        variables['cadastre_section_layer_id'] = section_layer.id()
        variables['cadastre_section_unique_field'] = section_unique_field

        variables['cadastre_parcelle_layer_id'] = parcelle_layer.id()
        variables['cadastre_parcelle_unique_field'] = parcelle_unique_field

        context.project().setCustomVariables(variables)
        # Returns empty dict if no outputs
        return {self.SUCCESS: 1}

    def name(self):
        return 'config_project'

    def displayName(self):
        return self.tr('Configuration du projet')

    @staticmethod
    def tags():
        return 'cadastre', 'lizmap'

    def shortHelpString(self):
        return (
            'Ce traitement permet de configurer un projet QGIS pour de la publication sur le web avec '
            '<a href="https://github.com/3liz/lizmap-web-client/">Lizmap Web Client</a> et son '
            '<a href="https://github.com/3liz/lizmap-cadastre-module">module Cadastre</a>.\n'
        )

    def helpUrl(self) -> str:
        return f"{URL_DOCUMENTATION}/processing/#configuration-du-projet"
