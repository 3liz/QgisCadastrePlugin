__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import os.path
import tempfile

from pathlib import Path

from qgis.core import QgsSettings
from qgis.PyQt import uic
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QMessageBox

from cadastre.definitions import (
    REGEX_BATI,
    REGEX_FANTOIR,
    REGEX_LOTLOCAL,
    REGEX_NBATI,
    REGEX_PDL,
    REGEX_PROP,
)
from cadastre.tools import set_window_title

OPTION_FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        str(Path(__file__).resolve().parent.parent),
        'forms',
        'cadastre_option_form.ui'
    )
)


class CadastreOptionDialog(QDialog, OPTION_FORM_CLASS):

    """ Let the user configure options. """

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.setupUi(self)
        self.setWindowTitle(f'{self.windowTitle()} {set_window_title()}')

        # Images
        self.plugin_dir = str(Path(__file__).resolve().parent.parent)
        self.btComposerTemplateFile.setIcon(QIcon(os.path.join(self.plugin_dir, 'forms', 'icons', 'open.png')))
        self.btTempDir.setIcon(QIcon(os.path.join(self.plugin_dir, 'forms', 'icons', 'open.png')))

        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        self.buttonBox.rejected.connect(self.onReject)
        self.buttonBox.accepted.connect(self.onAccept)

        # interface change buttons
        self.interfaceSelectors = {
            "Cadastre": {
                "button": self.btInterfaceCadastre
            },
            "QGIS": {
                "button": self.btInterfaceQgis
            }
        }
        from functools import partial
        for key, item in list(self.interfaceSelectors.items()):
            control = item['button']
            slot = partial(self.applyInterface, key)
            control.clicked.connect(slot)

        # path buttons selectors
        # paths needed to be chosen by user
        self.pathSelectors = {
            "tempDir": {
                "button": self.btTempDir,
                "input": self.inTempDir,
                "type": "dir"
            },
            "composerTemplateFile": {
                "button": self.btComposerTemplateFile,
                "input": self.inComposerTemplateFile,
                "type": "file"
            }
        }
        from functools import partial
        for key, item in list(self.pathSelectors.items()):
            control = item['button']
            slot = partial(self.chooseDataPath, key)
            control.clicked.connect(slot)

        # Set initial widget values
        self.getValuesFromSettings()

    def chooseDataPath(self, key):
        """
        Ask the user to select a folder
        and write down the path to appropriate field
        """
        if self.pathSelectors[key]['type'] == 'dir':
            ipath = QFileDialog.getExistingDirectory(
                None,
                "Choisir le répertoire contenant les fichiers",
                str(self.pathSelectors[key]['input'].text().encode('utf-8')).strip(' \t')
            )
        else:
            ipath, __ = QFileDialog.getOpenFileName(
                None,
                "Choisir le modèle de composeur utilisé pour l'export",
                str(self.pathSelectors[key]['input'].text().encode('utf-8')).strip(' \t'),
                "Composeur (*.qpt)"
            )

        if os.path.exists(str(ipath)):
            self.pathSelectors[key]['input'].setText(str(ipath))

    def getValuesFromSettings(self):
        """
        Get majic file names and other options
        from settings and set corresponding inputs
        """
        s = QgsSettings()
        regexBati = s.value("cadastre/regexBati", REGEX_BATI, type=str)
        if regexBati:
            self.inMajicBati.setText(regexBati)
        regexFantoir = s.value("cadastre/regexFantoir", REGEX_FANTOIR, type=str)
        if regexFantoir:
            self.inMajicFantoir.setText(regexFantoir)
        regexLotLocal = s.value("cadastre/regexLotLocal", REGEX_LOTLOCAL, type=str)
        if regexLotLocal:
            self.inMajicLotlocal.setText(regexLotLocal)
        regexNbati = s.value("cadastre/regexNbati", REGEX_NBATI, type=str)
        if regexNbati:
            self.inMajicNbati.setText(regexNbati)
        regexPdl = s.value("cadastre/regexPdl", REGEX_PDL, type=str)
        if regexPdl:
            self.inMajicPdl.setText(regexPdl)
        regexProp = s.value("cadastre/regexProp", REGEX_PROP, type=str)
        if regexProp:
            self.inMajicProp.setText(regexProp)
        tempDir = s.value("cadastre/tempDir", type=str)
        if tempDir and Path(tempDir).exists():
            self.inTempDir.setText(tempDir)
        else:
            self.inTempDir.setText(tempfile.gettempdir())
        maxInsertRows = s.value("cadastre/maxInsertRows", 50000, type=int)
        if maxInsertRows:
            self.inMaxInsertRows.setValue(maxInsertRows)
        spatialiteTempStore = s.value("cadastre/spatialiteTempStore", 'MEMORY', type=str)
        if spatialiteTempStore and hasattr(self, 'inSpatialiteTempStore'):
            if spatialiteTempStore == 'MEMORY':
                self.inSpatialiteTempStore.setCurrentIndex(0)
            else:
                self.inSpatialiteTempStore.setCurrentIndex(1)
        composerTemplateFile = s.value(
            "cadastre/composerTemplateFile",
            '%s/composers/paysage_a4.qpt' % self.plugin_dir,
            type=str
        )
        if composerTemplateFile:
            self.inComposerTemplateFile.setText(composerTemplateFile)

    def applyInterface(self, key):
        """
        Help the user to select
        and apply personalized interface
        """

        # item = self.interfaceSelectors[key]
        iniPath = os.path.join(
            self.plugin_dir,
            'interface/'
        )
        interfaceInfo = '''
        Pour appliquer l'interface <b>{}</b>
        <ul>
            <li>Menu Préférences > Personnalisation</li>
            <li>Bouton <b>Charger depuis le fichier</b> (icône dossier ouvert)</li>
            <li>Sélectionner le fichier <b>{}.ini</b> situé dans le dossier : <b>{}</b></li>
            <li>Appliquer et fermer la fenêtre</li>
            <li>Redémarer QGIS</li>
        </ul>
        '''.format(key, key.lower(), iniPath)
        QMessageBox.information(
            self,
            "Cadastre - Personnalisation",
            interfaceInfo
        )

    def onAccept(self):
        """
        Save options when pressing OK button
        """

        # Save Majic file names
        s = QgsSettings()
        s.setValue("cadastre/regexBati", self.inMajicBati.text().strip(' \t\n\r'))
        s.setValue("cadastre/regexFantoir", self.inMajicFantoir.text().strip(' \t\n\r'))
        s.setValue("cadastre/regexLotLocal", self.inMajicLotlocal.text().strip(' \t\n\r'))
        s.setValue("cadastre/regexNbati", self.inMajicNbati.text().strip(' \t\n\r'))
        s.setValue("cadastre/regexPdl", self.inMajicPdl.text().strip(' \t\n\r'))
        s.setValue("cadastre/regexProp", self.inMajicProp.text().strip(' \t\n\r'))

        # Save temp dir
        s.setValue("cadastre/tempDir", self.inTempDir.text().strip(' \t\n\r'))
        # Save composer template dir
        s.setValue("cadastre/composerTemplateFile", self.inComposerTemplateFile.text().strip(' \t\n\r'))

        # Save performance tuning
        s.setValue("cadastre/maxInsertRows", int(self.inMaxInsertRows.value()))
        s.setValue("cadastre/spatialiteTempStore", self.inSpatialiteTempStore.currentText().upper())

        self.accept()

    def onReject(self):
        """
        Run some actions when
        the user closes the dialog
        """
        self.close()
