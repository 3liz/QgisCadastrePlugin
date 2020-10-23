"""
Cadastre - Export method class

This plugins helps users to import the french land registry ('cadastre')
into a database. It is meant to ease the use of the data in QGIs
by providing search tools and appropriate layer symbology.

begin     : 2013-06-11
copyright : (C) 2013, 2019 by 3liz
email     : info@3liz.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

"""
import os.path

from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtWidgets import QApplication
from qgis.PyQt.QtGui import QDesktopServices

from qgis.core import (
    QgsProject,
    QgsMapLayer,
    QgsMapSettings,
)

from .cadastre_export import cadastreExport as cadastreExportBase
import cadastre.cadastre_common_base as cadastre_common

from qgis.PyQt.QtWidgets import QDialog

from pathlib import Path
from qgis.PyQt import uic

PRINT_FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        str(Path(__file__).resolve().parent),
        'forms',
        'cadastre_print_form.ui'
    )
)


class cadastrePrintProgress(QDialog, PRINT_FORM_CLASS):
    def __init__(self, parent=None):
        super(cadastrePrintProgress, self).__init__(parent)
        # Set up the user interface
        self.setupUi(self)


from typing import Generator, Callable
from contextlib import contextmanager


@contextmanager
def printProgress(self, nb: int) -> Generator[Callable[[int], None], None, None]:
    # Show progress dialog
    printProgress = cadastrePrintProgress()
    # Set progress bar
    printProgress.pbPrint.setValue(0)
    # Show dialog
    printProgress.show()

    progress = lambda step: printProgress.pbPrint.setValue(int(step * 100 / nb))
    yield progress


class cadastreExport(cadastreExportBase):

    def __init__(self, layer: QgsMapLayer, etype: str, comptecommunal: str,
                 geo_parcelle: str = None, target_dir: str = None) -> None:

        self.mProgress = printProgress

        super().__init__(QgsProject.instance(),
                         layer, etype, comptecommunal, geo_parcelle, target_dir)

        self.print_parcelle_page = True

    def getMapInstance(self) -> QgsMapSettings:
        """
        Get instance of object needed to instantiate QgsComposition
        QgsMapRenderer or QgsMapSettings
        Different if context is server
        """
        # return self.iface.mapCanvas().mapSettings()
        return super().getMapInstance()

    def getHtmlFromTemplate(self, tplPath, replaceDict):
        """
        Get the content of a template file
        and replace all variables with given data
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            return super().getHtmlFromTemplate(tplPath, replaceDict)
        finally:
            QApplication.restoreOverrideCursor()

    def exportItemAsPdf(self, comptecommunal, suffix=None):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            temppath = super().exportItemAsPdf(comptecommunal, suffix)
            # Opens PDF in default application
            if not self.isMulti:
                cadastre_common.openFile(temppath)
        finally:
            QApplication.restoreOverrideCursor()

        return temppath

    def exportAsPDF(self):

        paths = super().exportAsPDF()

        if self.isMulti:
            # info = u"Les relevés ont été enregistrés dans le répertoire :\n%s\n\nOuvrir le dossier ?" % self.targetDir
            openFolder = QDesktopServices()
            openFolder.openUrl(QUrl('file:///%s' % self.targetDir))

        return paths
