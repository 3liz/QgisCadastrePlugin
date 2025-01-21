__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import os.path

from functools import partial
from pathlib import Path

from db_manager.db_plugins.plugin import BaseError
from db_manager.dlg_db_error import DlgDbError
from qgis.core import QgsCoordinateReferenceSystem, QgsSettings
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox

from cadastre.cadastre_import import cadastreImport
from cadastre.dialogs.dialog_common import CadastreCommon
from cadastre.tools import set_window_title

IMPORT_FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        str(Path(__file__).resolve().parent.parent),
        'forms',
        'cadastre_import_form.ui'
    )
)


class CadastreImportDialog(QDialog, IMPORT_FORM_CLASS):
    def __init__(self, iface, parent=None):
        self.iface = iface
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(f'{self.windowTitle()} {set_window_title()}')

        # Images
        plugin_dir = str(Path(__file__).resolve().parent.parent)
        self.btEdigeoSourceDir.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'open.png')))
        self.btMajicSourceDir.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'open.png')))

        self.connectionDbList = []
        # common cadastre methods
        self.qc = CadastreCommon(self)

        # first disable database specific tabs
        self.databaseSpecificOptions.setTabEnabled(0, False)
        self.databaseSpecificOptions.setTabEnabled(1, False)

        # spatialite support
        self.hasSpatialiteSupport = CadastreCommon.hasSpatialiteSupport()
        if not self.hasSpatialiteSupport:
            self.liDbType.removeItem(2)
            self.databaseSpecificOptions.setTabEnabled(1, False)
            self.btCreateNewSpatialiteDb.setEnabled(False)

        # Signals/Slot Connections
        self.liDbType.currentIndexChanged[str].connect(self.qc.updateConnectionList)
        self.liDbConnection.currentIndexChanged[str].connect(self.qc.updateSchemaList)
        self.btDbCreateSchema.clicked.connect(self.createSchema)
        self.btCreateNewSpatialiteDb.clicked.connect(self.qc.createNewSpatialiteDatabase)
        self.btProcessImport.clicked.connect(self.processImport)
        self.rejected.connect(self.onClose)
        self.buttonBox.rejected.connect(self.onClose)

        # path buttons selectors
        # paths needed to be chosen by user
        self.pathSelectors = {
            "edigeoSourceDir": {
                "button": self.btEdigeoSourceDir,
                "input": self.inEdigeoSourceDir
            },
            "majicSourceDir": {
                "button": self.btMajicSourceDir,
                "input": self.inMajicSourceDir
            }
        }
        for key, item in list(self.pathSelectors.items()):
            control = item['button']
            slot = partial(self.chooseDataPath, key)
            control.clicked.connect(slot)

        # Set initial values
        self.doMajicImport = False
        self.doEdigeoImport = False
        self.dataVersion = None
        self.dataYear = None
        self.dbType = None
        self.dbpluginclass = None
        self.connectionName = None
        self.connection = None
        self.db = None
        self.schema = None
        self.schemaList = None
        self.hasStructure = None
        self.hasData = None
        self.hasMajicData = None
        self.hasMajicDataParcelle = None
        self.hasMajicDataVoie = None
        self.hasMajicDataProp = None
        self.edigeoSourceProj = None
        self.edigeoTargetProj = None
        self.edigeoDepartement = None
        self.edigeoDirection = None
        self.edigeoLot = None
        self.majicSourceDir = None
        self.edigeoSourceDir = None
        self.edigeoMakeValid = False

        # set input values from settings
        self.sList = {
            'dataVersion': {
                'widget': self.inDataVersion,
                'wType': 'spinbox',
                'property': self.dataVersion
            },
            'dataYear': {
                'widget': self.inDataYear,
                'wType': 'spinbox',
                'property': self.dataYear
            },
            'schema': {
                'widget': None
            },
            'majicSourceDir': {
                'widget': self.inMajicSourceDir,
                'wType': 'text',
                'property': self.majicSourceDir
            },
            'edigeoSourceDir': {
                'widget': self.inEdigeoSourceDir,
                'wType': 'text',
                'property': self.edigeoSourceDir
            },
            'edigeoDepartement': {
                'widget': self.inEdigeoDepartement,
                'wType': 'text',
                'property': self.edigeoDepartement
            },
            'edigeoDirection': {
                'widget': self.inEdigeoDirection,
                'wType': 'spinbox',
                'property': self.edigeoDirection
            },
            'edigeoLot': {
                'widget': self.inEdigeoLot,
                'wType': 'text',
                'property': self.edigeoLot
            },
            'edigeoSourceProj': {
                'widget': self.inEdigeoSourceProj,
                'wType': 'crs',
                'property': self.edigeoSourceProj
            },
            'edigeoTargetProj': {
                'widget': self.inEdigeoTargetProj,
                'wType': 'crs',
                'property': self.edigeoTargetProj
            }
        }
        self.getValuesFromSettings()

    def onClose(self):
        """
        Close dialog
        """
        if self.db:
            self.db.connector.__del__()

        # Store settings
        msg = self.checkImportInputData()
        if not msg:
            self.storeSettings()

        self.close()

    def chooseDataPath(self, key):
        """
        Ask the user to select a folder
        and write down the path to appropriate field
        """
        root_directory = str(self.pathSelectors[key]['input'].text()).strip(' \t')
        if not root_directory:
            root_directory = os.path.expanduser("~")
        ipath = QFileDialog.getExistingDirectory(
            None,
            "Choisir le répertoire contenant les fichiers",
            root_directory
        )
        if os.path.exists(str(ipath)):
            self.pathSelectors[key]['input'].setText(str(ipath))

    def getValuesFromSettings(self):
        """
        get values from QGIS settings
        and set input fields appropriately
        """
        s = QgsSettings()
        for k, v in list(self.sList.items()):
            value = s.value("cadastre/%s" % k, '', type=str)
            if value and value != 'None' and v['widget']:
                if v['wType'] == 'text':
                    v['widget'].setText(value)
                if v['wType'] == 'spinbox':
                    v['widget'].setValue(int(value))
                if v['wType'] == 'combobox':
                    listDic = {v['list'][i]: i for i in range(0, len(v['list']))}
                    v['widget'].setCurrentIndex(listDic[value])
                if v['wType'] == 'crs':
                    v['widget'].setCrs(QgsCoordinateReferenceSystem(value))

        # self.sLists does not provide database type, connection name
        # load_default_values will do
        self.qc.load_default_values()

    def createSchema(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            if self.db is None:
                QMessageBox.warning(
                    self,
                    QApplication.translate("DBManagerPlugin", "Sorry"),
                    QApplication.translate("DBManagerPlugin", "No database selected or you are not connected to it.")
                )
                return
            schema = self.inDbCreateSchema.text()
        finally:
            QApplication.restoreOverrideCursor()

        if schema:
            try:
                self.db.createSchema(schema)

            except BaseError as e:

                DlgDbError.showError(e, self)
                self.qc.updateLog(e.msg)
                return

            finally:
                self.qc.updateSchemaList()
                listDic = {self.schemaList[i]: i for i in range(0, len(self.schemaList))}
                self.liDbSchema.setCurrentIndex(listDic[schema])
                self.inDbCreateSchema.clear()
                QApplication.restoreOverrideCursor()

    def checkImportInputData(self):
        """
        Check the user defined inpu data
        """

        self.dataVersion = str(self.inDataVersion.text())
        self.dataYear = str(self.inDataYear.text())
        self.schema = str(self.liDbSchema.currentText())
        self.majicSourceDir = str(self.inMajicSourceDir.text()).strip(' \t')
        self.edigeoSourceDir = str(self.inEdigeoSourceDir.text()).strip(' \t')
        self.edigeoDepartement = str(self.inEdigeoDepartement.text()).strip(' \t')
        self.edigeoDirection = str(self.inEdigeoDirection.text()).strip(' \t')
        self.edigeoLot = str(self.inEdigeoLot.text()).strip(' \t')
        self.edigeoSourceProj = self.inEdigeoSourceProj.crs().authid()
        self.edigeoTargetProj = self.inEdigeoTargetProj.crs().authid()

        # defined properties
        self.doMajicImport = os.path.exists(self.majicSourceDir)
        self.doEdigeoImport = os.path.exists(self.edigeoSourceDir)

        if self.cbMakeValid.isChecked():
            self.edigeoMakeValid = True

        msg = ''
        if not self.db:
            msg += 'Veuillez sélectionner une base de données\n'

        if not self.doMajicImport and not self.doEdigeoImport:
            msg += 'Veuillez sélectionner le chemin vers les fichiers à importer !\n'

        if self.edigeoSourceDir and not self.doEdigeoImport:
            msg += "Le chemin spécifié pour les fichiers EDIGEO n'existe pas\n"

        if self.majicSourceDir and not self.doMajicImport:
            msg += "Le chemin spécifié pour les fichiers MAJIC n'existe pas\n"

        if self.doEdigeoImport and not self.edigeoSourceProj:
            msg += 'La projection source doit être renseignée !\n'
        if self.doEdigeoImport and not self.edigeoTargetProj:
            msg += 'La projection cible doit être renseignée !\n'
        if len(self.edigeoDepartement) != 2:
            msg += 'Le département ne doit pas être vide !\n'
        if not self.edigeoDirection:
            msg += 'La direction doit être un entier (0 par défaut) !\n'
        if not self.edigeoLot:
            msg += 'Merci de renseigner un lot pour cet import (code commune, date d\'import, etc.)\n'

        self.qc.updateLog(msg.replace('\n', '<br/>'))
        return msg

    def processImport(self) -> bool:
        """
        Lancement du processus d'import
        """

        msg = self.checkImportInputData()
        if msg:
            QMessageBox.critical(self, "Cadastre", msg)
            return

        # Store settings
        self.storeSettings()

        # cadastreImport instance
        qi = cadastreImport(self)

        # Check if structure already exists in the database/schema
        self.qc.check_database_for_existing_structure()

        # Run Script for creating tables
        if not self.hasStructure:
            qi.installCadastreStructure()
        else:
            # Run update script which add some missing tables when needed
            qi.updateCadastreStructure()

        # Run MAJIC import
        if self.doMajicImport:
            qi.importMajic()

        # Run Edigeo import
        if self.doEdigeoImport:
            qi.importEdigeo()

        qi.endImport()
        return qi.go

    def storeSettings(self):
        """
        Store cadastre settings in QGIS
        """
        # store chosen data in QGIS settings
        s = QgsSettings()
        database_type = self.liDbType.currentText().lower()
        s.setValue("cadastre/databaseType", database_type)
        s.setValue("cadastre/connection", self.liDbConnection.currentText())
        if database_type == "postgis":
            schema = self.liDbSchema.currentText()
        else:
            schema = ''
        s.setValue("cadastre/schema", schema)
        s.setValue("cadastre/dataVersion", str(self.dataVersion))
        s.setValue("cadastre/dataYear", int(self.dataYear))
        s.setValue("cadastre/majicSourceDir", self.majicSourceDir)
        s.setValue("cadastre/edigeoSourceDir", self.edigeoSourceDir)
        s.setValue("cadastre/edigeoDepartement", str(self.edigeoDepartement))
        s.setValue("cadastre/edigeoDirection", int(self.edigeoDirection))
        s.setValue("cadastre/edigeoLot", str(self.edigeoLot))
        s.setValue("cadastre/edigeoSourceProj", str(self.edigeoSourceProj))
        s.setValue("cadastre/edigeoTargetProj", str(self.edigeoTargetProj))
