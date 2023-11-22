from abc import abstractmethod
from os.path import join
from pathlib import Path

from qgis.core import Qgis, QgsProcessingAlgorithm
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon

__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"


class BaseProcessingAlgorithm(QgsProcessingAlgorithm):

    @abstractmethod
    def shortHelpString(self):
        pass

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return self.__class__()

    def icon(self):
        plugin_dir = str(Path(__file__).resolve().parent.parent.parent)
        return QIcon(join(plugin_dir, 'icon.png'))
