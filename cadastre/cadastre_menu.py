"""
Cadastre - QGIS plugin menu class

This plugins helps users to import the french land registry ('cadastre')
into a database. It is meant to ease the use of the data in QGIs
by providing search tools and appropriate layer symbology.

begin     : 2013-06-11
copyright : (C) 2013 by 3liz
email     : info@3liz.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

"""

import contextlib
import os
import os.path
import tempfile

from pathlib import Path
from time import time
from typing import Optional

from qgis.core import (
    Qgis,
    QgsApplication,
    QgsLayoutExporter,
    QgsMessageLog,
    QgsPrintLayout,
    QgsProject,
    QgsReadWriteContext,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QSettings, QUrl
from qgis.PyQt.QtGui import QDesktopServices, QIcon, QKeySequence
from qgis.PyQt.QtWidgets import (
    QAction,
    QFileDialog,
    QMenu,
    QMessageBox,
    QToolButton,
)
from qgis.PyQt.QtXml import QDomDocument

import cadastre.cadastre_common_base as common_utils
import cadastre.export_csv as export_csv

from cadastre.cadastre_identify_parcelle import IdentifyParcelle, parcelle_layers
from cadastre.definitions import URL_DOCUMENTATION
from cadastre.dialogs.about_dialog import CadastreAboutDialog
from cadastre.dialogs.cadastre_load_dialog import CadastreLoadDialog
from cadastre.dialogs.import_dialog import CadastreImportDialog
from cadastre.dialogs.message_dialog import CadastreMessageDialog
from cadastre.dialogs.options_dialog import CadastreOptionDialog
from cadastre.dialogs.parcelle_dialog import CadastreParcelleDialog
from cadastre.dialogs.search_dialog import CadastreSearchDialog
from cadastre.logger import Logger
from cadastre.plausible import Plausible
from cadastre.processing.provider import CadastreProvider
from cadastre.tools import metadata_config, plugin_path, version, wait_cursor
from cadastre.upgrade import release_notes, release_versions, upgrade_message, upgrade_versions


class CadastreMenu:
    def __init__(self, iface):
        self.iface = iface
        self.cadastre_search_dialog = None
        self.provider = None
        self.help_action_about_menu = None
        if not self.iface:
            # If QGIS is headless, there isn't iface set, on qgis_process for instance
            return

        self.import_action: Optional[QAction] = None
        self.search_action: Optional[QAction] = None
        self.load_action: Optional[QAction] = None
        self.export_action: Optional[QAction] = None
        # CSV exports of the selected parcelles, with a menu to choose the export
        self.csv_export_action: Optional[QAction] = None
        self.csv_export_menu: Optional[QMenu] = None
        self.option_action: Optional[QAction] = None
        self.about_action: Optional[QAction] = None
        self.help_action: Optional[QAction] = None
        self.version_action: Optional[QAction] = None
        self.menu: Optional[QMenu] = None
        # Menu where the Cadastre menu is added
        self.parent_menu = None
        self.toolbar = None
        self.identifyParcelleAction: Optional[QAction] = None
        self.identyParcelleTool: Optional[IdentifyParcelle] = None
        self.mConfig = None

        self.mapCanvas = iface.mapCanvas()

    # noinspection PyPep8Naming
    def initProcessing(self):
        self.provider = CadastreProvider()
        # noinspection PyArgumentList
        QgsApplication.processingRegistry().addProvider(self.provider)

    # noinspection PyPep8Naming
    def initGui(self):

        self.initProcessing()

        main_icon = QIcon(str(plugin_path("icon.png")))

        # Open the online help
        self.help_action_about_menu = QAction(main_icon, "Cadastre", self.iface.mainWindow())
        self.iface.pluginHelpMenu().addAction(self.help_action_about_menu)
        self.help_action_about_menu.triggered.connect(self.open_help)

        actions = {
            "import_action": ("database.png", "Importer des données", "", self.open_import_dialog, True),
            "search_action": ("search.png", "Outils de recherche", "", self.toggle_search_dialog, True),
            "load_action": ("output.png", "Charger des données", "", self.open_load_dialog, True),
            "export_action": ("mActionSaveAsPDF.png", "Exporter la vue", "", self.export_view, True),
            "option_action": ("config.png", "Configurer le plugin", "", self.open_option_dialog, True),
            "about_action": ("about.png", "À propos", "", self.open_about_dialog, True),
            "help_action": ("about.png", "Aide", "", self.open_help, True),
            "version_action": ("about.png", "Notes de version", "", self.open_message_dialog, True),
        }

        for key in actions:
            icon_path = str(plugin_path("icons", actions[key][0]))
            icon = QIcon(icon_path)
            action = QAction(QIcon(icon), actions[key][1], self.iface.mainWindow())
            if actions[key][2] != "":
                action.setShortcut(QKeySequence(actions[key][2]))
            setattr(self, key, action)
            action.setEnabled(actions[key][4])
            action.setObjectName(key)
            action.triggered.connect(actions[key][3])

        # CSV exports of the selected parcelles: a menu with one action per export
        self.csv_export_menu = QMenu("Exporter un CSV pour publipostage", self.iface.mainWindow())
        for export_type, (label, _filename) in export_csv.CSV_EXPORTS.items():
            export = self.csv_export_menu.addAction(label)
            export.setObjectName(f"csv_export_{export_type}")
            export.triggered.connect(lambda _checked=False, t=export_type: self.export_csv(t))
        self.csv_export_action = QAction(
            QIcon(str(plugin_path("icons", "export_csv.svg"))),
            "Exporter un CSV pour publipostage",
            self.iface.mainWindow(),
        )
        self.csv_export_action.setObjectName("csv_export_action")
        self.csv_export_action.setToolTip(
            "Exporter un CSV pour publipostage, à partir des parcelles sélectionnées"
        )
        self.csv_export_action.setMenu(self.csv_export_menu)

        if not self.cadastre_search_dialog:
            dialog = CadastreSearchDialog(self.iface)
            self.cadastre_search_dialog = dialog

        self.menu = QMenu("&Cadastre")
        self.menu.setObjectName("Cadastre")
        self.menu.setIcon(main_icon)

        # Add Cadastre to Extension menu
        self.menu.addAction(self.import_action)
        self.menu.addAction(self.load_action)
        self.menu.addSeparator()
        self.menu.addAction(self.search_action)
        self.menu.addAction(self.export_action)
        self.menu.addAction(self.csv_export_action)
        self.menu.addSeparator()
        self.menu.addAction(self.option_action)
        self.menu.addAction(self.about_action)
        self.menu.addAction(self.version_action)
        self.menu.addAction(self.help_action)

        menuBar = self.iface.mainWindow().menuBar()
        menu = menuBar
        for child in menuBar.children():
            if child.objectName() == "mPluginMenu":
                menu = child
                break
        menu.addMenu(self.menu)
        self.parent_menu = menu

        # Add cadastre toolbar
        self.toolbar = self.iface.addToolBar("&Cadastre")
        self.toolbar.setObjectName("cadastreToolbar")

        # Create action for "Parcelle information"
        self.identifyParcelleAction = QAction(
            QIcon(str(plugin_path("icons", "toolbar", "get-parcelle-info.png"))),
            "Infos parcelle",
            self.iface.mainWindow(),
        )
        self.identifyParcelleAction.setCheckable(True)
        self.identifyParcelleAction.triggered.connect(self.setIndentifyParcelleTool)

        self.toolbar.addAction(self.import_action)
        self.toolbar.addAction(self.load_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.search_action)
        self.toolbar.addAction(self.identifyParcelleAction)
        self.toolbar.addAction(self.export_action)
        self.toolbar.addAction(self.csv_export_action)
        # A click on the button opens the menu of the exports
        csv_export_button = self.toolbar.widgetForAction(self.csv_export_action)
        if isinstance(csv_export_button, QToolButton):
            csv_export_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.option_action)
        self.toolbar.addAction(self.about_action)

        # Disable some dialogs on CI : about and changelog
        on_ci = os.getenv("CI", "").lower() == "true"

        # Display About window on first use
        s = QSettings()
        firstUse = s.value("cadastre/isFirstUse", 1, type=int)
        if firstUse == 1 and not on_ci:
            s.setValue("cadastre/isFirstUse", 0)
            self.open_about_dialog()

        # Display some messages depending on version number
        self.mConfig = metadata_config()
        if not on_ci:
            self.open_upgrade_dialog(first_use=firstUse == 1)

        # Project load or create : refresh search and identify tool
        self.iface.projectRead.connect(self.onProjectRead)
        self.iface.newProjectCreated.connect(self.on_new_project_created)

        # Delete layers from table when deleted from registry
        # noinspection PyArgumentList
        lr = QgsProject.instance()
        lr.layersRemoved.connect(self.checkIdentifyParcelleTool)

        # The CSV export needs selected parcelles
        self.mapCanvas.selectionChanged.connect(self.update_csv_export_action)
        lr.layersAdded.connect(self.update_csv_export_action)
        lr.layersRemoved.connect(self.update_csv_export_action)
        self.update_csv_export_action()

        self.updateSearchButton()

        self.cadastre_search_dialog.visibilityChanged.connect(self.updateSearchButton)

        # noinspection PyBroadException
        try:
            plausible = Plausible(server=False)
            plausible.request_stat_event()
        except Exception as e:
            QgsMessageLog.logMessage(
                f'Error while calling the stats API : "{e}"', "cadastre", Qgis.MessageLevel.Warning
            )

    def open_import_dialog(self):
        """
        Import dialog
        """
        dialog = CadastreImportDialog(self.iface)
        dialog.exec()

    def open_load_dialog(self):
        """
        Load dialog
        """
        dialog = CadastreLoadDialog(self.iface, self.cadastre_search_dialog)
        dialog.exec()

    def toggle_search_dialog(self):
        """
        Search dock widget
        """
        if self.cadastre_search_dialog.isVisible():
            self.cadastre_search_dialog.hide()
        else:
            self.cadastre_search_dialog.show()
        self.updateSearchButton()

    def updateSearchButton(self):
        """
        Update search button icon
        """
        if not self.search_action or not self.cadastre_search_dialog:
            # The plugin is being unloaded
            return

        if self.cadastre_search_dialog.isVisible():
            icon_file = "nosearch.png"
        else:
            icon_file = "search.png"
        icon_path = str(plugin_path("icons", icon_file))
        self.search_action.setIcon(QIcon(icon_path))

    @wait_cursor
    def export_view(self):
        """
        Export current view to PDF
        """
        # Load template from file
        s = QSettings()
        f = s.value("cadastre/composerTemplateFile", "", type=str)
        if not os.path.exists(f):
            f = str(plugin_path("composers", "paysage_a4.qpt"))
            s.setValue("cadastre/composerTemplateFile", f)

        template_content = None
        with open(f, encoding="utf8") as ff:
            template_content = ff.read()
        if not template_content:
            return
        d = QDomDocument()
        d.setContent(template_content)

        # noinspection PyArgumentList
        c = QgsPrintLayout(QgsProject.instance())
        c.loadFromTemplate(d, QgsReadWriteContext())

        # Set scale and extent
        cm = c.referenceMap()
        canvas = self.iface.mapCanvas()
        extent = canvas.extent()
        scale = canvas.scale()
        if extent:
            cm.zoomToExtent(extent)
        if scale:
            cm.setScale(scale)

        # Export
        tempDir = s.value("cadastre/tempDir", type=str)
        if not tempDir or not Path(tempDir).exists():
            tempDir = tempfile.gettempdir()
        self.targetDir = tempfile.mkdtemp("", "cad_export_", tempDir)
        temp = int(time() * 100)
        temppath = os.path.join(tempDir, "export_cadastre_%s.pdf" % temp)

        exporter = QgsLayoutExporter(c)
        exportersettings = QgsLayoutExporter.PdfExportSettings()
        exportersettings.dpi = 300
        exportersettings.forceVectorOutput = True
        exportersettings.rasterizeWholeImage = False  # rasterizeWholeImage = false
        exporter.exportToPdf(temppath, exportersettings)


        if os.path.exists(temppath):
            common_utils.openFile(temppath)

    def parcelles_layer(self) -> QgsVectorLayer | None:
        """Return the layer of the parcels whose selected parcels are exported in CSV.

        The project may have several layers of the parcels, see parcelle_layers: the active layer
        is used if it is one of them and has a selection, otherwise the first one with a selection.

        :return: The layer, None if no parcel is selected in any layer of the parcels.
        """
        layers = [layer for layer in parcelle_layers(QgsProject.instance()) if layer.selectedFeatureCount()]
        active = self.iface.activeLayer()
        for layer in layers:
            if active is not None and layer.id() == active.id():
                return layer
        return layers[0] if layers else None

    def update_csv_export_action(self, *_args):
        """Enable the CSV export if at least one parcelle is selected"""
        if not self.csv_export_action:
            # The plugin is being unloaded
            return
        layer = self.parcelles_layer()
        self.csv_export_action.setEnabled(bool(layer and layer.selectedFeatureCount()))

    def export_csv(self, export_type: str):
        """Export the selected parcelles in a CSV file, like the CSV exports of Lizmap

        :param export_type: The export: proprietaires or locaux, see export_csv.CSV_EXPORTS.
        """
        layer = self.parcelles_layer()
        if not layer or not layer.selectedFeatureCount():
            self.iface.messageBar().pushWarning("Cadastre", "Aucune parcelle sélectionnée")
            return

        label, filename = export_csv.CSV_EXPORTS[export_type]

        # Many parcelles: QGIS does not respond during the export
        count = layer.selectedFeatureCount()
        if count > export_csv.CSV_EXPORT_CONFIRM_COUNT:
            answer = QMessageBox.question(
                self.iface.mainWindow(),
                "Exporter un CSV pour publipostage",
                f"L'export de {count} parcelles peut prendre du temps, "
                "QGIS ne répondra pas pendant l'export. Continuer ?",
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        s = QSettings()
        directory = s.value("cadastre/csvExportDir", str(Path.home()), type=str)
        path, _filter = QFileDialog.getSaveFileName(
            self.iface.mainWindow(),
            f"Exporter un CSV pour publipostage : {label}",
            str(Path(directory) / filename),
            "CSV (*.csv)",
        )
        if not path:
            return
        csv_path = Path(path)
        if csv_path.suffix.lower() != ".csv":
            csv_path = csv_path.with_name(csv_path.name + ".csv")
        s.setValue("cadastre/csvExportDir", str(csv_path.parent))

        try:
            # The QGIS user reads the database: all the sensitive data are exported, like in the fiche
            count = wait_cursor(export_csv.export_selected_parcelles)(
                layer, export_type, csv_path, common_utils.SensitiveData.full()
            )
        except (ValueError, OSError) as err:
            Logger.log_exception(err)
            self.iface.messageBar().pushCritical("Cadastre", f"Erreur lors de l'export CSV : {err}")
            return

        url = QUrl.fromLocalFile(str(csv_path)).toString()
        self.iface.messageBar().pushSuccess(
            "Cadastre",
            f'{label} : {count} ligne(s) exportée(s) dans <a href="{url}">{csv_path}</a>',
        )

    def open_option_dialog(self):
        """
        Config dialog
        """
        dialog = CadastreOptionDialog(self.iface)
        dialog.exec()

    def open_about_dialog(self):
        """
        About dialog
        """
        dialog = CadastreAboutDialog(self.iface)
        dialog.exec()

    def checkIdentifyParcelleTool(self, layerIds=None):
        """Deactivate the tool "Identifier une parcelle" when the project has no layer of the parcels.

        :param layerIds: The layers removed from the project, when called by layersRemoved.
        """
        if not parcelle_layers(QgsProject.instance()):
            self.identifyParcelleAction.setChecked(False)
            self.iface.actionPan().trigger()

    def setIndentifyParcelleTool(self):
        """Activate the tool "Identifier une parcelle", if the project has a layer of the parcels.

        The layers of the parcels are searched by the tool at each click, see IdentifyParcelle.
        """
        if not parcelle_layers(QgsProject.instance()):
            QMessageBox.warning(
                self.cadastre_search_dialog,
                "Cadastre",
                "La couche de parcelles n'a pas été trouvée dans le projet",
            )
            self.identifyParcelleAction.setChecked(False)
            self.iface.actionPan().trigger()
            return

        self.identyParcelleTool = IdentifyParcelle(self.mapCanvas)
        self.identyParcelleTool.cadastreGeomIdentified.connect(self.getParcelleInfo)
        # The action is unchecked by QGIS when another map tool is activated
        self.identyParcelleTool.setAction(self.identifyParcelleAction)

        # The activate identify tool
        self.mapCanvas.setMapTool(self.identyParcelleTool)

    def getParcelleInfo(self, layer, feature):
        """
        Return information of the identified
        parcelle
        """
        parcelleDialog = CadastreParcelleDialog(self.iface, layer, feature, self.cadastre_search_dialog)
        parcelleDialog.show()

    def onProjectRead(self):
        """
        Refresh search dialog when new data has been loaded
        """
        if self.cadastre_search_dialog:
            self.cadastre_search_dialog.checkMajicContent()
            self.cadastre_search_dialog.clearComboboxes()
            self.cadastre_search_dialog.setupSearchCombobox("commune", None, "sql")
            self.cadastre_search_dialog.setupSearchCombobox("section", None, "sql")
            self.cadastre_search_dialog.setupSearchCombobox("commune_proprietaire", None, "sql")
            self.checkIdentifyParcelleTool()

    def on_new_project_created(self):
        """
        Refresh search dialog when new data has been loaded
        """
        self.checkIdentifyParcelleTool()
        if self.cadastre_search_dialog:
            self.cadastre_search_dialog.checkMajicContent()
            self.cadastre_search_dialog.clearComboboxes()

    @staticmethod
    def open_help():
        """Opens the html help file content with default browser"""
        # noinspection PyArgumentList
        QDesktopServices.openUrl(QUrl(URL_DOCUMENTATION))

    def open_message_dialog(self):
        """Display the release notes: the changelog of the version, if packaged, and the update messages."""
        # The changelog is written in metadata.txt by the packaging only, not in the sources
        changelog = self.mConfig.get("general", "changelog", fallback=None)
        message = release_notes(version(), changelog, f"{URL_DOCUMENTATION}changelog/")
        # The SQL commands of the update messages can be run again, in another database for example
        dialog = CadastreMessageDialog(self.iface, message, release_versions(version()))
        dialog.exec()

    def open_upgrade_dialog(self, first_use: bool):
        """Display the messages of an update of the plugin, once, then record the version.

        The messages are given again by the release notes of the menu, see open_message_dialog.

        :param first_use: True for a first installation of the plugin: there is no message,
            the data imported with this version have the new indexes.
        """
        s = QSettings()
        current = version()
        previous = s.value("cadastre/version", "", type=str)
        if previous == current:
            return
        s.setValue("cadastre/version", current)

        # Without a recorded version, the plugin was used before the recording of the versions
        previous_version = None if first_use else previous
        message = upgrade_message(previous_version, current)
        if message:
            dialog = CadastreMessageDialog(self.iface, message, upgrade_versions(previous_version, current))
            dialog.exec()

    def unload(self):
        if self.iface:
            self.unload_gui()

        # Remove processing provider
        if self.provider:
            # noinspection PyArgumentList
            QgsApplication.processingRegistry().removeProvider(self.provider)
            self.provider = None

    def unload_gui(self):
        """Remove everything added by initGui, so that the plugin can be reloaded"""
        # Signals, otherwise this instance would still be called after a reload
        signals = [
            (self.iface.projectRead, self.onProjectRead),
            (self.iface.newProjectCreated, self.on_new_project_created),
            (QgsProject.instance().layersRemoved, self.checkIdentifyParcelleTool),
            (self.mapCanvas.selectionChanged, self.update_csv_export_action),
            (QgsProject.instance().layersAdded, self.update_csv_export_action),
            (QgsProject.instance().layersRemoved, self.update_csv_export_action),
        ]
        if self.cadastre_search_dialog:
            # Removing the dock widget hides it, after the actions have been deleted
            signals.append((self.cadastre_search_dialog.visibilityChanged, self.updateSearchButton))
        for signal, slot in signals:
            # TypeError if not connected, when initGui has not been fully run
            with contextlib.suppress(TypeError):
                signal.disconnect(slot)

        if self.identyParcelleTool:
            self.mapCanvas.unsetMapTool(self.identyParcelleTool)
            self.identyParcelleTool.deleteLater()
            self.identyParcelleTool = None

        if self.help_action_about_menu:
            self.iface.pluginHelpMenu().removeAction(self.help_action_about_menu)
            self.help_action_about_menu.deleteLater()
            self.help_action_about_menu = None

        if self.menu:
            self.parent_menu.removeAction(self.menu.menuAction())
            self.menu.deleteLater()
            self.menu = None

        if self.toolbar:
            self.iface.mainWindow().removeToolBar(self.toolbar)
            self.toolbar.deleteLater()
            self.toolbar = None

        for name in (
            "import_action",
            "search_action",
            "load_action",
            "export_action",
            "option_action",
            "about_action",
            "help_action",
            "version_action",
            "identifyParcelleAction",
            "csv_export_action",
            "csv_export_menu",
        ):
            action = getattr(self, name)
            if action:
                action.deleteLater()
                setattr(self, name, None)

        if self.cadastre_search_dialog:
            self.iface.removeDockWidget(self.cadastre_search_dialog)
            self.cadastre_search_dialog.deleteLater()
            self.cadastre_search_dialog = None
