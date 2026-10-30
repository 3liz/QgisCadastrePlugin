__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import os.path

from functools import partial

from qgis.core import QgsCoordinateReferenceSystem, QgsSettings
from qgis.PyQt import uic
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QMessageBox

from cadastre.cadastre_import import ImportOptions, cadastreImport
from cadastre.definitions import MAXIMUM_YEAR, MINIMUM_YEAR
from cadastre.dialogs.database_widget import DatabaseWidget
from cadastre.dialogs.dialog_feedback import CadastreDialogFeedback, append_log
from cadastre.tools import plugin_path, set_window_title

IMPORT_FORM_CLASS, _ = uic.loadUiType(str(plugin_path("forms", "cadastre_import_form.ui")))


class CadastreImportDialog(QDialog, IMPORT_FORM_CLASS):
    def __init__(self, iface, parent=None):
        self.iface = iface
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(f"{self.windowTitle()} {set_window_title()}")

        # Images
        self.btEdigeoSourceDir.setIcon(QIcon(str(plugin_path("forms", "icons", "open.png"))))
        self.btMajicSourceDir.setIcon(QIcon(str(plugin_path("forms", "icons", "open.png"))))

        # Database, connection and schema
        self.database_widget = DatabaseWidget(self, creation_enabled=True)
        self.databaseLayout.addWidget(self.database_widget)
        self.database_widget.logMessage.connect(lambda msg: append_log(self.txtLog, msg))

        # Signals/Slot Connections
        self.btProcessImport.clicked.connect(self.processImport)
        self.rejected.connect(self.onClose)
        self.buttonBox.rejected.connect(self.onClose)

        # path buttons selectors
        # paths needed to be chosen by user
        self.pathSelectors = {
            "edigeoSourceDir": {"button": self.btEdigeoSourceDir, "input": self.inEdigeoSourceDir},
            "majicSourceDir": {"button": self.btMajicSourceDir, "input": self.inMajicSourceDir},
        }
        for key, item in list(self.pathSelectors.items()):
            control = item["button"]
            slot = partial(self.chooseDataPath, key)
            control.clicked.connect(slot)

        # Set initial values
        self.doMajicImport = False
        self.doEdigeoImport = False
        self.dataVersion = None
        self.dataYear = None
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
            "dataVersion": {"widget": self.inDataVersion, "wType": "spinbox", "property": self.dataVersion},
            "dataYear": {"widget": self.inDataYear, "wType": "spinbox", "property": self.dataYear},
            "majicSourceDir": {
                "widget": self.inMajicSourceDir,
                "wType": "text",
                "property": self.majicSourceDir,
            },
            "edigeoSourceDir": {
                "widget": self.inEdigeoSourceDir,
                "wType": "text",
                "property": self.edigeoSourceDir,
            },
            "edigeoDepartement": {
                "widget": self.inEdigeoDepartement,
                "wType": "text",
                "property": self.edigeoDepartement,
            },
            "edigeoDirection": {
                "widget": self.inEdigeoDirection,
                "wType": "spinbox",
                "property": self.edigeoDirection,
            },
            "edigeoLot": {"widget": self.inEdigeoLot, "wType": "text", "property": self.edigeoLot},
            "edigeoSourceProj": {
                "widget": self.inEdigeoSourceProj,
                "wType": "crs",
                "property": self.edigeoSourceProj,
            },
            "edigeoTargetProj": {
                "widget": self.inEdigeoTargetProj,
                "wType": "crs",
                "property": self.edigeoTargetProj,
            },
        }
        self.getValuesFromSettings()
        self.inDataVersion.setMaximum(MAXIMUM_YEAR)
        self.inDataYear.setMaximum(MAXIMUM_YEAR)
        self.inDataVersion.setValue(MAXIMUM_YEAR)
        self.inDataYear.setValue(MAXIMUM_YEAR)
        self.inDataVersion.setMinimum(MINIMUM_YEAR)
        self.inDataYear.setMinimum(MINIMUM_YEAR)

    def onClose(self):
        """
        Close dialog
        """
        self.database_widget.close_connection()

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
        root_directory = str(self.pathSelectors[key]["input"].text()).strip(" \t")
        if not root_directory:
            root_directory = os.path.expanduser("~")
        ipath = QFileDialog.getExistingDirectory(
            None, "Choisir le répertoire contenant les fichiers", root_directory
        )
        if os.path.exists(str(ipath)):
            self.pathSelectors[key]["input"].setText(str(ipath))

    def getValuesFromSettings(self):
        """
        get values from QGIS settings
        and set input fields appropriately
        """
        s = QgsSettings()
        for k, v in list(self.sList.items()):
            value = s.value("cadastre/%s" % k, "", type=str)
            if value and value != "None" and v["widget"]:
                if v["wType"] == "text":
                    v["widget"].setText(value)
                if v["wType"] == "spinbox":
                    v["widget"].setValue(int(value))
                if v["wType"] == "combobox":
                    listDic = {v["list"][i]: i for i in range(0, len(v["list"]))}
                    v["widget"].setCurrentIndex(listDic[value])
                if v["wType"] == "crs":
                    v["widget"].setCrs(QgsCoordinateReferenceSystem(value))

        # self.sLists does not provide database type, connection name and schema
        self.database_widget.load_settings()

    def checkImportInputData(self):
        """
        Check the user defined inpu data
        """

        self.dataVersion = str(self.inDataVersion.text())
        self.dataYear = str(self.inDataYear.text())
        self.majicSourceDir = str(self.inMajicSourceDir.text()).strip(" \t")
        self.edigeoSourceDir = str(self.inEdigeoSourceDir.text()).strip(" \t")
        self.edigeoDepartement = str(self.inEdigeoDepartement.text()).strip(" \t")
        self.edigeoDirection = str(self.inEdigeoDirection.text()).strip(" \t")
        self.edigeoLot = str(self.inEdigeoLot.text()).strip(" \t")
        self.edigeoSourceProj = self.inEdigeoSourceProj.crs().authid()
        self.edigeoTargetProj = self.inEdigeoTargetProj.crs().authid()

        # defined properties
        self.doMajicImport = os.path.exists(self.majicSourceDir)
        self.doEdigeoImport = os.path.exists(self.edigeoSourceDir)

        if self.cbMakeValid.isChecked():
            self.edigeoMakeValid = True

        msg = ""
        if not self.database_widget.database():
            msg += "Veuillez sélectionner une base de données\n"

        if not self.doMajicImport and not self.doEdigeoImport:
            msg += "Veuillez sélectionner le chemin vers les fichiers à importer !\n"

        if self.edigeoSourceDir and not self.doEdigeoImport:
            msg += "Le chemin spécifié pour les fichiers EDIGEO n'existe pas\n"

        if self.majicSourceDir and not self.doMajicImport:
            msg += "Le chemin spécifié pour les fichiers MAJIC n'existe pas\n"

        if self.doEdigeoImport and not self.edigeoSourceProj:
            msg += "La projection source doit être renseignée !\n"
        if self.doEdigeoImport and not self.edigeoTargetProj:
            msg += "La projection cible doit être renseignée !\n"
        if len(self.edigeoDepartement) != 2:
            msg += "Le département ne doit pas être vide !\n"
        if not self.edigeoDirection:
            msg += "La direction doit être un entier (0 par défaut) !\n"
        if not self.edigeoLot:
            msg += "Merci de renseigner un lot pour cet import (code commune, date d'import, etc.)\n"

        append_log(self.txtLog, msg.replace("\n", "<br/>"))
        return msg

    def processImport(self) -> bool:
        """
        Lancement du processus d'import
        """

        msg = self.checkImportInputData()
        if msg:
            QMessageBox.critical(self, "Cadastre", msg)
            return False

        # Store settings
        self.storeSettings()

        options = ImportOptions(
            database=self.database_widget.database(),
            data_version=self.dataVersion,
            data_year=self.dataYear,
            lot=self.edigeoLot,
            departement=self.edigeoDepartement,
            direction=self.edigeoDirection,
            majic_source_dir=self.majicSourceDir,
            edigeo_source_dir=self.edigeoSourceDir,
            edigeo_source_proj=self.edigeoSourceProj,
            edigeo_target_proj=self.edigeoTargetProj,
            edigeo_make_valid=self.edigeoMakeValid,
        )
        feedback = CadastreDialogFeedback(self.txtLog, self.pbProcess, self.stepLabel, self.subStepLabel)
        qi = cadastreImport(options, feedback, self.confirm)
        success = qi.run()

        # The user may have accepted the departement and direction found in MAJIC files
        if (options.departement, options.direction) != (self.edigeoDepartement, self.edigeoDirection):
            self.inEdigeoDepartement.setText(options.departement)
            self.inEdigeoDirection.setValue(int(options.direction))
            self.checkImportInputData()
            self.storeSettings()

        if os.getenv("CI", "").lower() != "true":
            # We don't want QMessagebox in test
            if success:
                msg = "Import terminé"
            else:
                msg = "Des erreurs ont été rencontrées pendant l'import. Veuillez consulter le log."
            QMessageBox.information(self, "Cadastre", msg)

        return success

    def confirm(self, question: str) -> bool:
        """
        Ask a yes/no question to the user during the import
        """
        answer = QMessageBox.question(
            self,
            "Cadastre",
            question,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes

    def storeSettings(self):
        """
        Store cadastre settings in QGIS
        """
        # store chosen data in QGIS settings
        self.database_widget.store_settings()
        s = QgsSettings()
        s.setValue("cadastre/dataVersion", str(self.dataVersion))
        s.setValue("cadastre/dataYear", int(self.dataYear))
        s.setValue("cadastre/majicSourceDir", self.majicSourceDir)
        s.setValue("cadastre/edigeoSourceDir", self.edigeoSourceDir)
        s.setValue("cadastre/edigeoDepartement", str(self.edigeoDepartement))
        s.setValue("cadastre/edigeoDirection", int(self.edigeoDirection))
        s.setValue("cadastre/edigeoLot", str(self.edigeoLot))
        s.setValue("cadastre/edigeoSourceProj", str(self.edigeoSourceProj))
        s.setValue("cadastre/edigeoTargetProj", str(self.edigeoTargetProj))
