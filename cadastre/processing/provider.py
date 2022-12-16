"""
/***************************************************************************
 Cadastre - Processing provider
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
from os.path import join
from pathlib import Path

from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon

from cadastre.processing.algorithms.config import ConfigProjectAlgorithm
from cadastre.processing.algorithms.edigeo_downloader import EdigeoDownloader


class CadastreProvider(QgsProcessingProvider):

    def loadAlgorithms(self):
        self.addAlgorithm(ConfigProjectAlgorithm())
        self.addAlgorithm(EdigeoDownloader())

    def id(self):  # NOQA
        return 'cadastre'

    def name(self):
        return 'Cadastre'

    def longName(self):
        return 'Outils d\'exploitation des données cadastrale français'

    def icon(self):
        plugin_dir = str(Path(__file__).resolve().parent.parent)
        return QIcon(join(plugin_dir, 'icon.png'))
