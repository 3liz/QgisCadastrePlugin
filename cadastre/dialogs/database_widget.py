__copyright__ = "Copyright 2026, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import os

from db_manager.db_plugins.plugin import BaseError
from db_manager.dlg_db_error import DlgDbError
from qgis.core import QgsProviderRegistry, QgsSettings
from qgis.PyQt.QtCore import QFileInfo, Qt, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QWidget,
)
from qgis.utils import OverrideCursor, spatialite_connect

import cadastre.cadastre_common_base as common_utils

from cadastre.cadastre_database import CadastreDatabase
from cadastre.logger import Logger

POSTGIS = "postgis"
SPATIALITE = "spatialite"
# QGIS provider names
PROVIDERS = {POSTGIS: "postgres", SPATIALITE: "spatialite"}


class DatabaseWidget(QWidget):
    """Choice of the database type, the connection and the schema (PostGIS).

    The current choice is given by database(), and databaseChanged is emitted when it changes.
    """

    # CadastreDatabase, or None if there is no valid connection
    databaseChanged = pyqtSignal(object)
    # Message to display in the log of the dialog
    logMessage = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None, creation_enabled: bool = False):
        """
        :param creation_enabled: Show the tools to create a PostGIS schema or a Spatialite database
        """
        super().__init__(parent)
        self.creation_enabled = creation_enabled
        # Connection to the database, the schema is not set
        self._database: CadastreDatabase | None = None

        self.liDbType = QComboBox(self)
        self.liDbType.addItems(["-- Choisir --", "Postgis", "Spatialite"])
        self.liDbConnection = QComboBox(self)
        self.liDbSchema = QComboBox(self)

        self.inDbCreateSchema = QLineEdit(self)
        self.inDbCreateSchema.setPlaceholderText("Nom du nouveau schéma")
        self.btDbCreateSchema = QPushButton("Créer le schéma", self)
        self.btCreateNewSpatialiteDb = QPushButton("Créer une base Spatialite", self)

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setColumnStretch(1, 1)
        layout.addWidget(QLabel("Type de base", self), 0, 0)
        layout.addWidget(self.liDbType, 0, 1)
        layout.addWidget(QLabel("Connexion", self), 1, 0)
        layout.addWidget(self.liDbConnection, 1, 1)
        layout.addWidget(QLabel("Schéma", self), 2, 0)
        layout.addWidget(self.liDbSchema, 2, 1)
        schema_layout = QHBoxLayout()
        schema_layout.addWidget(self.inDbCreateSchema)
        schema_layout.addWidget(self.btDbCreateSchema)
        layout.addLayout(schema_layout, 3, 1)
        layout.addWidget(self.btCreateNewSpatialiteDb, 4, 1)

        if not common_utils.hasSpatialiteSupport():
            self.liDbType.removeItem(2)

        self.liDbType.currentIndexChanged.connect(self.update_connection_list)
        self.liDbConnection.currentIndexChanged.connect(self.connect_database)
        self.liDbSchema.currentIndexChanged.connect(self._emit_database_changed)
        self.btDbCreateSchema.clicked.connect(self.create_schema)
        self.btCreateNewSpatialiteDb.clicked.connect(self.create_spatialite_database)

        self._update_widgets()

    @property
    def db_type(self) -> str | None:
        """postgis, spatialite or None if no type is chosen"""
        if self.liDbType.currentIndex() <= 0:
            return None
        return self.liDbType.currentText().lower()

    def database(self) -> CadastreDatabase | None:
        """The chosen database and schema, None if there is no valid connection"""
        if not self._database:
            return None
        return self._database.with_schema(self.liDbSchema.currentText())

    def _emit_database_changed(self):
        self.databaseChanged.emit(self.database())

    def _update_widgets(self):
        is_postgis = self.db_type == POSTGIS
        is_connected = self._database is not None
        self.liDbSchema.setEnabled(is_postgis and is_connected)

        self.inDbCreateSchema.setVisible(self.creation_enabled and is_postgis)
        self.btDbCreateSchema.setVisible(self.creation_enabled and is_postgis)
        self.inDbCreateSchema.setEnabled(is_connected)
        self.btDbCreateSchema.setEnabled(is_connected)
        self.btCreateNewSpatialiteDb.setVisible(self.creation_enabled and self.db_type == SPATIALITE)

    def update_connection_list(self):
        """Fill the connection list for the chosen database type"""
        with OverrideCursor(Qt.CursorShape.WaitCursor):
            # Clearing the list will reset the current connection
            self.liDbConnection.clear()
            if self.db_type:
                # Use the QGIS cache: reloading the connections, like db_manager connections() does,
                # deletes the connection objects used by the opened db_manager connectors (crash)
                metadata = QgsProviderRegistry.instance().providerMetadata(PROVIDERS[self.db_type])
                self.liDbConnection.addItems(sorted(metadata.dbConnections().keys()))
        self._update_widgets()

    def connect_database(self):
        """Connect to the chosen connection and fill the schema list"""
        self._database = None
        connection_name = self.liDbConnection.currentText()

        if self.db_type and connection_name:
            try:
                with OverrideCursor(Qt.CursorShape.WaitCursor):
                    self._database = CadastreDatabase.from_connection(self.db_type, connection_name)
            except BaseError as e:
                DlgDbError.showError(e, self)
                self.logMessage.emit(e.msg)
            except Exception as err:
                Logger.log_exception(err)
                self.logMessage.emit(
                    "Impossible de récupérer les schémas de la base. Vérifier les informations de connexion."
                )

        self._fill_schema_list()
        self._update_widgets()
        self._emit_database_changed()

    def _fill_schema_list(self, current: str = ""):
        self.liDbSchema.blockSignals(True)
        self.liDbSchema.clear()
        if self._database and self._database.is_postgis:
            self.liDbSchema.addItems([s.name for s in self._database.db.schemas()])
            if current:
                self.liDbSchema.setCurrentIndex(self.liDbSchema.findText(current))
        self.liDbSchema.blockSignals(False)

    def create_schema(self):
        """Create a schema in the PostGIS database and select it"""
        if self._database is None:
            QMessageBox.warning(
                self,
                QApplication.translate("DBManagerPlugin", "Sorry"),
                QApplication.translate(
                    "DBManagerPlugin", "No database selected or you are not connected to it."
                ),
            )
            return

        schema = self.inDbCreateSchema.text().strip()
        if not schema:
            return

        try:
            with OverrideCursor(Qt.CursorShape.WaitCursor):
                self._database.db.createSchema(schema)
        except BaseError as e:
            DlgDbError.showError(e, self)
            self.logMessage.emit(e.msg)
            return

        self.inDbCreateSchema.clear()
        self._fill_schema_list(schema)
        self._emit_database_changed()

    def create_spatialite_database(self):
        """
        Choose a file path to save
        create the sqlite database with
        spatial tools and create QGIS connection
        """
        # Let the user choose new file path
        ipath, __ = QFileDialog.getSaveFileName(
            self,
            "Choisir l'emplacement du nouveau fichier",
            os.path.expanduser("~"),
            "Sqlite database (*.sqlite)",
        )
        if not ipath:
            self.logMessage.emit("Aucune base de données créée (annulation)")
            return

        # Delete file if exists (question already asked above)
        if os.path.exists(ipath):
            os.remove(ipath)

        # Create the spatialite database
        try:
            # Create a connection (which will create the file automatically)
            con = spatialite_connect(ipath, isolation_level=None)
            cur = con.cursor()
            cur.execute("SELECT InitSpatialMetadata(1)")
            con.close()
            del con
        except Exception as err:
            Logger.log_exception(err)
            self.logMessage.emit("Échec lors de la création du fichier Spatialite !")
            return

        # Create QGIS connexion
        name = os.path.basename(ipath)
        metadata = QgsProviderRegistry.instance().providerMetadata(PROVIDERS[SPATIALITE])
        metadata.saveConnection(metadata.createConnection(QFileInfo(ipath).canonicalFilePath(), {}), name)

        # Update connections combo box and set new db selected
        self.update_connection_list()
        self.liDbConnection.setCurrentIndex(self.liDbConnection.findText(name))

    def load_settings(self):
        """Try to restore the choices which are stored in QGIS settings.

        The function will return as soon as it is missing a value in the QGIS Settings.
        The order is DB Type, connection name and then the schema.
        """
        settings = QgsSettings()
        # Default to PostGIS ticket #302
        db_type = settings.value("cadastre/databaseType", type=str, defaultValue=POSTGIS)
        for combo, key in (
            (self.liDbType, "databaseType"),
            (self.liDbConnection, "connection"),
            (self.liDbSchema, "schema"),
        ):
            # Widgets are ordered by hierarchy, so we quit the loop as soon as a value is not correct
            if key == "schema" and db_type != POSTGIS:
                return

            value = settings.value(f"cadastre/{key}", type=str, defaultValue="")
            if not value:
                return

            index = combo.findText(value, Qt.MatchFlag.MatchFixedString)
            if index < 0:
                return

            combo.setCurrentIndex(index)

    def store_settings(self):
        """Store the choices in QGIS settings"""
        settings = QgsSettings()
        db_type = self.liDbType.currentText().lower()
        settings.setValue("cadastre/databaseType", db_type)
        settings.setValue("cadastre/connection", self.liDbConnection.currentText())
        settings.setValue("cadastre/schema", self.liDbSchema.currentText() if db_type == POSTGIS else "")

    def close_connection(self):
        """Close the connection to the database"""
        if self._database:
            self._database.connector.__del__()
