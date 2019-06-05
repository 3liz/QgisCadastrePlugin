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

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterField,
                       QgsProcessingOutputNumber)

class ConfigProjectAlgorithm(QgsProcessingAlgorithm):
    """
    Algorithm to set project varaibles for cadastre use
    """

    TOWN_LAYER = 'TOWN_LAYER'
    TOWN_UNIQUE_FIELD = 'TOWN_UNIQUE_FIELD'
    SECTION_LAYER = 'SECTION_LAYER'
    SECTION_UNIQUE_FIELD = 'SECTION_UNIQUE_FIELD'
    PARCEL_LAYER = 'PARCEL_LAYER'
    PARCEL_UNIQUE_FIELD = 'PARCEL_UNIQUE_FIELD'

    SUCCESS = 'SUCCESS'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.TOWN_LAYER,
                self.tr('La couche communes'),
                [QgsProcessing.TypeVectorPolygon],
                defaultValue='Communes'
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.TOWN_UNIQUE_FIELD,
                self.tr('Champs identifiant les communes'),
                parentLayerParameterName=self.TOWN_LAYER,
                defaultValue='geo_commune',
                type=QgsProcessingParameterField.String
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.SECTION_LAYER,
                self.tr('La couche sections'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.SECTION_UNIQUE_FIELD,
                self.tr('Champs identifiant les sections'),
                parentLayerParameterName=self.SECTION_LAYER,
                defaultValue='geo_section',
                type=QgsProcessingParameterField.String
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.PARCEL_LAYER,
                self.tr('La couche parcelles'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.PARCEL_UNIQUE_FIELD,
                self.tr('Champs identifiant les parcelles'),
                parentLayerParameterName=self.PARCEL_LAYER,
                defaultValue='geo_parcelle',
                type=QgsProcessingParameterField.String
            )
        )

        self.addOutput(QgsProcessingOutputNumber(self.SUCCESS, self.tr('Succès')))

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        town_layer = self.parameterAsVectorLayer(parameters, self.TOWN_LAYER, context)
        town_unique_field = self.parameterAsString(parameters, self.TOWN_UNIQUE_FIELD, context)

        section_layer = self.parameterAsVectorLayer(parameters, self.SECTION_LAYER, context)
        section_unique_field = self.parameterAsString(parameters, self.SECTION_UNIQUE_FIELD, context)

        parcel_layer = self.parameterAsVectorLayer(parameters, self.PARCEL_LAYER, context)
        parcel_unique_field = self.parameterAsString(parameters, self.PARCEL_UNIQUE_FIELD, context)

        variables = context.project().customVariables()

        variables['cadastre_commune_layer_id'] = town_layer.id()
        variables['cadastre_commune_unique_col'] = town_unique_field

        variables['cadastre_section_layer_id'] = section_layer.id()
        variables['cadastre_section_unique_col'] = section_unique_field

        variables['cadastre_parcelle_layer_id'] = parcel_layer.id()
        variables['cadastre_parcelle_unique_col'] = parcel_unique_field

        context.project().setCustomVariables(variables)
        # Returns empty dict if no outputs
        return {self.SUCCESS: 1}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'config_project'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Configuration du projet')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Outils')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'tools'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return self.__class__()
