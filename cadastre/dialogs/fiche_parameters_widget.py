"""Choice of the sections and fields displayed in the fiche parcellaire, in the options of the plugin."""

__copyright__ = "Copyright 2026, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import sqlite3

from qgis.core import QgsProviderConnectionException
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from cadastre.dialogs.database_widget import DatabaseWidget
from cadastre.fiche_parametres import TABLE, parameters, write_table

# Labels of the attributes of SensitiveData
SENSITIVE_LABELS = {"birth": "naissance", "revenue": "revenus", "exoneration": "exonérations"}

# Role of the tree items storing the key of the section or of the field
KEY_ROLE = Qt.ItemDataRole.UserRole


class FicheParametersWidget(QGroupBox):
    """Tree of the tabs, sections and fields of the fiche parcellaire, with a check box for each one."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__("Fiche parcellaire", parent)
        self.items: dict[str, QTreeWidgetItem] = {}

        label = QLabel(
            "Sections et champs affichés dans la fiche parcellaire. Lors d'un import, ces options sont copiées "
            f"dans la table <b>{TABLE}</b> de la base si elle n'existe pas encore : ensuite, c'est cette table "
            "qui est utilisée, dans QGIS et dans Lizmap. Le bouton « Enregistrer dans une base » remplace "
            "les paramètres d'une base existante. Les données sensibles restent masquées selon les droits.",
            self,
        )
        label.setWordWrap(True)

        self.tree = QTreeWidget(self)
        self.tree.setHeaderLabels(["Section ou champ", "Donnée sensible"])
        self.tree.setMinimumHeight(250)
        self.fill_tree()
        self.tree.itemChanged.connect(self.update_section)

        self.btDefaults = QPushButton("Valeurs par défaut", self)
        self.btDefaults.clicked.connect(self.reset)
        self.btDatabase = QPushButton("Enregistrer dans une base…", self)
        self.btDatabase.clicked.connect(self.save_in_database)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(self.btDefaults)
        buttons.addWidget(self.btDatabase)
        layout = QVBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(self.tree)
        layout.addLayout(buttons)

    def fill_tree(self):
        """Create an item for each tab, then for each section and each field, from the description of the fiche"""
        tabs: dict[str, QTreeWidgetItem] = {}
        section = None
        # The parameters are ordered: each section is followed by its fields
        for p in parameters():
            if p.tab not in tabs:
                tabs[p.tab] = QTreeWidgetItem(self.tree, [p.tab])
            if not p.field:
                # A section, in its tab
                item = section = QTreeWidgetItem(tabs[p.tab], [p.section])
            else:
                # A field, in its section
                item = QTreeWidgetItem(section, [p.field, SENSITIVE_LABELS.get(p.sensitive, "")])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setData(0, KEY_ROLE, p.key)
            item.setCheckState(0, Qt.CheckState.Checked if p.default else Qt.CheckState.Unchecked)
            self.items[p.key] = item
        for tab in tabs.values():
            tab.setExpanded(True)
        self.tree.resizeColumnToContents(0)

    def update_section(self, item: QTreeWidgetItem, column: int):
        """Disable the fields of a section which is not displayed"""
        if column != 0 or item.childCount() == 0 or item.data(0, KEY_ROLE) is None:
            return
        hidden = item.checkState(0) != Qt.CheckState.Checked
        for i in range(item.childCount()):
            item.child(i).setDisabled(hidden)

    def visibility(self) -> dict[str, bool]:
        """Return for each key of section or field, True if it is checked"""
        return {key: item.checkState(0) == Qt.CheckState.Checked for key, item in self.items.items()}

    def set_visibility(self, visibility: dict[str, bool]):
        """Check the sections and fields displayed

        :param visibility: For each key, True if it is displayed, see visibility_from_options.
        """
        for key, visible in visibility.items():
            if key in self.items:
                self.items[key].setCheckState(
                    0, Qt.CheckState.Checked if visible else Qt.CheckState.Unchecked
                )

    def reset(self):
        """Check the sections and fields displayed by default"""
        self.set_visibility({p.key: p.default for p in parameters()})

    def save_in_database(self):
        """Write the checked sections and fields in the table of a database chosen by the user"""
        dialog = SaveFicheParametersDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        database = dialog.database_widget.database()
        if database is None:
            return
        if not database.structure().has_structure:
            QMessageBox.warning(self, "Cadastre", "La base choisie ne contient pas de données cadastrales.")
            return
        try:
            write_table(database, self.visibility())
        except (QgsProviderConnectionException, sqlite3.Error) as e:
            QMessageBox.critical(self, "Cadastre", f"Erreur lors de l'écriture de la table {TABLE} : {e}")
            return
        dialog.database_widget.store_settings()
        QMessageBox.information(
            self, "Cadastre", f"Les paramètres de la fiche ont été enregistrés dans la table {TABLE}."
        )


class SaveFicheParametersDialog(QDialog):
    """Choice of the database and of the schema where the parameters of the fiche are written"""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Cadastre - Enregistrer les paramètres de la fiche")
        label = QLabel(
            f"Les paramètres de la table <b>{TABLE}</b> de cette base seront remplacés par les options cochées.",
            self,
        )
        label.setWordWrap(True)
        self.database_widget = DatabaseWidget(self)
        self.database_widget.load_settings()
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(self.database_widget)
        layout.addWidget(buttons)
