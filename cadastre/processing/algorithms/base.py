from abc import abstractmethod

from qgis.core import QgsProcessingAlgorithm
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon

from cadastre.tools import plugin_path

__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"


class BaseProcessingAlgorithm(QgsProcessingAlgorithm):
    @abstractmethod
    def shortHelpString(self):
        pass

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        return self.__class__()

    def icon(self):
        return QIcon(str(plugin_path("icon.png")))
