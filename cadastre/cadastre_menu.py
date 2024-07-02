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
)
from qgis.PyQt.QtCore import QSettings, Qt, QUrl
from qgis.PyQt.QtGui import QDesktopServices, QIcon, QKeySequence
from qgis.PyQt.QtWidgets import (
    QAction,
    QActionGroup,
    QApplication,
    QMenu,
    QMessageBox,
    QWidgetAction,
)
from qgis.PyQt.QtXml import QDomDocument

from cadastre.cadastre_identify_parcelle import IdentifyParcelle
from cadastre.definitions import URL_DOCUMENTATION
from cadastre.dialogs.about_dialog import CadastreAboutDialog
from cadastre.dialogs.cadastre_load_dialog import CadastreLoadDialog
from cadastre.dialogs.dialog_common import CadastreCommon
from cadastre.dialogs.import_dialog import CadastreImportDialog
from cadastre.dialogs.message_dialog import CadastreMessageDialog
from cadastre.dialogs.options_dialog import CadastreOptionDialog
from cadastre.dialogs.parcelle_dialog import CadastreParcelleDialog
from cadastre.dialogs.search_dialog import CadastreSearchDialog
from cadastre.plausible import Plausible
from cadastre.processing.provider import CadastreProvider
from cadastre.tools import metadata_config


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
        self.option_action: Optional[QAction] = None
        self.about_action: Optional[QAction] = None
        self.help_action: Optional[QAction] = None
        self.version_action: Optional[QAction] = None
        self.menu: Optional[QMenu] = None
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

        plugin_dir = str(Path(__file__).resolve().parent)
        main_icon = QIcon(os.path.join(plugin_dir, "icon.png"))

        # Open the online help
        self.help_action_about_menu = QAction(main_icon, 'Cadastre', self.iface.mainWindow())
        self.iface.pluginHelpMenu().addAction(self.help_action_about_menu)
        self.help_action_about_menu.triggered.connect(self.open_help)

        actions = {
            "import_action": (
                "database.png",
                "Importer des données",
                "",
                self.open_import_dialog,
                True
            ),
            "search_action": (
                "search.png",
                "Outils de recherche",
                "",
                self.toggle_search_dialog,
                True
            ),
            "load_action": (
                "output.png",
                "Charger des données",
                "",
                self.open_load_dialog,
                True
            ),
            "export_action": (
                "mActionSaveAsPDF.png",
                "Exporter la vue",
                "",
                self.export_view,
                True
            ),
            "option_action": (
                "config.png",
                "Configurer le plugin",
                "",
                self.open_option_dialog,
                True
            ),
            "about_action": (
                "about.png",
                "À propos",
                "",
                self.open_about_dialog,
                True
            ),
            "help_action": (
                "about.png",
                "Aide",
                "",
                self.open_help,
                True
            ),
            "version_action": (
                "about.png",
                "Notes de version",
                "",
                self.open_message_dialog,
                True
            )
        }

        for key in actions:
            icon_path = os.path.join(plugin_dir, 'icons', actions[key][0])
            icon = QIcon(icon_path)
            action = QAction(QIcon(icon), actions[key][1], self.iface.mainWindow())
            if actions[key][2] != "":
                action.setShortcut(QKeySequence(actions[key][2]))
            setattr(self, key, action)
            action.setEnabled(actions[key][4])
            action.setObjectName(key)
            action.triggered.connect(actions[key][3])

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

        # Add cadastre toolbar
        self.toolbar = self.iface.addToolBar('&Cadastre')
        self.toolbar.setObjectName("cadastreToolbar")

        # Create action for "Parcelle information"
        self.identifyParcelleAction = QAction(
            QIcon(os.path.join(
                plugin_dir,
                "icons",
                "toolbar",
                "get-parcelle-info.png"
            )),
            "Infos parcelle",
            self.iface.mainWindow()
        )
        self.identifyParcelleAction.setCheckable(True)
        self.identifyParcelleAction.triggered.connect(self.setIndentifyParcelleTool)

        self.toolbar.addAction(self.import_action)
        self.toolbar.addAction(self.load_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.search_action)
        self.toolbar.addAction(self.identifyParcelleAction)
        self.toolbar.addAction(self.export_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.option_action)
        self.toolbar.addAction(self.about_action)

        self.setActionsExclusive()

        # Disable some dialogs on CI : about and changelog
        on_ci = os.getenv("CI", "").lower() == 'true'

        # Display About window on first use
        s = QSettings()
        firstUse = s.value("cadastre/isFirstUse", 1, type=int)
        if firstUse == 1 and not on_ci:
            s.setValue("cadastre/isFirstUse", 0)
            self.open_about_dialog()

        # Display some messages depending on version number
        self.mConfig = metadata_config()

        # Project load or create : refresh search and identify tool
        self.iface.projectRead.connect(self.onProjectRead)
        self.iface.newProjectCreated.connect(self.on_new_project_created)

        # Delete layers from table when deleted from registry
        # noinspection PyArgumentList
        lr = QgsProject.instance()
        lr.layersRemoved.connect(self.checkIdentifyParcelleTool)

        self.updateSearchButton()

        self.cadastre_search_dialog.visibilityChanged.connect(self.updateSearchButton)

        # noinspection PyBroadException
        try:
            plausible = Plausible(server=False)
            plausible.request_stat_event()
        except Exception as e:
            QgsMessageLog.logMessage(f"Error while calling the stats API : \"{e}\"", 'cadastre', Qgis.Warning)

    def open_import_dialog(self):
        """
        Import dialog
        """
        dialog = CadastreImportDialog(self.iface)
        dialog.exec_()

    def open_load_dialog(self):
        """
        Load dialog
        """
        dialog = CadastreLoadDialog(
            self.iface,
            self.cadastre_search_dialog
        )
        dialog.exec_()

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
        plugin_dir = str(Path(__file__).resolve().parent)
        if self.cadastre_search_dialog.isVisible():
            icon_file = "nosearch.png"
        else:
            icon_file = "search.png"
        icon_path = os.path.join(plugin_dir, 'icons', icon_file)
        self.search_action.setIcon(QIcon(icon_path))

    def export_view(self):
        """
        Export current view to PDF
        """
        # Load template from file
        s = QSettings()
        f = s.value("cadastre/composerTemplateFile", '', type=str)
        if not os.path.exists(f):
            f = os.path.join(str(Path(__file__).resolve().parent), 'composers', 'paysage_a4.qpt')
            s.setValue("cadastre/composerTemplateFile", f)

        QApplication.setOverrideCursor(Qt.WaitCursor)
        template_content = None
        with open(f, encoding='utf8') as ff:
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
        self.targetDir = tempfile.mkdtemp('', 'cad_export_', tempDir)
        temp = int(time() * 100)
        temppath = os.path.join(tempDir, 'export_cadastre_%s.pdf' % temp)

        exporter = QgsLayoutExporter(c)
        exportersettings = QgsLayoutExporter.PdfExportSettings()
        exportersettings.dpi = 300
        exportersettings.forceVectorOutput = True
        exportersettings.rasterizeWholeImage = False  # rasterizeWholeImage = false
        exporter.exportToPdf(temppath, exportersettings)

        QApplication.restoreOverrideCursor()

        if os.path.exists(temppath):
            CadastreCommon.openFile(temppath)

    def open_option_dialog(self):
        """
        Config dialog
        """
        dialog = CadastreOptionDialog(self.iface)
        dialog.exec_()

    def open_about_dialog(self):
        """
        About dialog
        """
        dialog = CadastreAboutDialog(self.iface)
        dialog.exec_()

    def setActionsExclusive(self):

        # Build an action list from QGIS navigation toolbar
        actionList = self.iface.mapNavToolToolBar().actions()

        # Add actions from QGIS attributes toolbar (handling QWidgetActions)
        tmpActionList = self.iface.attributesToolBar().actions()
        for action in tmpActionList:
            if isinstance(action, QWidgetAction):
                actionList.extend(action.defaultWidget().actions())
            else:
                actionList.append(action)
        # ... add other toolbars' action lists...

        # Build a group with actions from actionList and add your own action
        group = QActionGroup(self.iface.mainWindow())
        group.setExclusive(True)
        for action in actionList:
            group.addAction(action)
        group.addAction(self.identifyParcelleAction)

    def checkIdentifyParcelleTool(self, layerIds=None):
        """
        When layers are removed from the project
        Check if the layer Parcelle remains
        If not deactivate Identify parcelle tool
        """
        # Find parcelle layer
        parcelleLayer = None
        try:
            from cadastre.dialogs.dialog_common import CadastreCommon
            parcelleLayer = CadastreCommon.getLayerFromLegendByTableProps('parcelle_info')
        except:
            parcelleLayer = None

        if not parcelleLayer:
            self.identifyParcelleAction.setChecked(False)
            self.iface.actionPan().trigger()
            return

    def setIndentifyParcelleTool(self):
        """
        Activite the identify tool
        for the layer geo_parcelle
        """

        # Find parcelle layer
        parcelleLayer = CadastreCommon.getLayerFromLegendByTableProps('parcelle_info')
        if not parcelleLayer:
            QMessageBox.warning(
                self.cadastre_search_dialog,
                "Cadastre",
                "La couche de parcelles n'a pas été trouvée dans le projet"
            )
            self.identifyParcelleAction.setChecked(False)
            self.iface.actionPan().trigger()
            return

        self.identyParcelleTool = IdentifyParcelle(self.mapCanvas, parcelleLayer)
        self.identyParcelleTool.cadastreGeomIdentified.connect(self.getParcelleInfo)

        # The activate identify tool
        self.mapCanvas.setMapTool(self.identyParcelleTool)

    def getParcelleInfo(self, layer, feature):
        """
        Return information of the identified
        parcelle
        """
        parcelleDialog = CadastreParcelleDialog(
            self.iface,
            layer,
            feature,
            self.cadastre_search_dialog
        )
        parcelleDialog.show()

    def onProjectRead(self):
        """
        Refresh search dialog when new data has been loaded
        """
        if self.cadastre_search_dialog:
            self.cadastre_search_dialog.checkMajicContent()
            self.cadastre_search_dialog.clearComboboxes()
            self.cadastre_search_dialog.setupSearchCombobox('commune', None, 'sql')
            self.cadastre_search_dialog.setupSearchCombobox('section', None, 'sql')
            self.cadastre_search_dialog.setupSearchCombobox('commune_proprietaire', None, 'sql')
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
        """
        Display a message to the user
        """
        changelog = self.mConfig.get('general', 'changelog')
        message = '<h3>Changelog</h3>'
        message += '<p>'
        i = 0
        for item in changelog.split('*'):
            if i == 0:
                message += '<b>%s</b><ul>' % item
            else:
                message += '<li>%s</li>' % item
            i += 1
        message += '</ul>'
        message += '</p>'

        dialog = CadastreMessageDialog(self.iface, message)
        dialog.exec_()

    def unload(self):
        if self.help_action_about_menu:
            self.iface.pluginHelpMenu().removeAction(self.help_action_about_menu)
            del self.help_action_about_menu

        self.iface.removePluginMenu("&Cadastre", self.import_action)
        self.iface.removePluginMenu("&Cadastre", self.load_action)
        self.iface.removePluginMenu("&Cadastre", self.search_action)
        self.iface.removePluginMenu("&Cadastre", self.export_action)
        self.iface.removePluginMenu("&Cadastre", self.option_action)
        self.iface.removePluginMenu("&Cadastre", self.about_action)
        self.iface.removePluginMenu("&Cadastre", self.version_action)
        self.iface.removePluginMenu("&Cadastre", self.help_action)

        self.iface.mainWindow().removeToolBar(self.toolbar)

        if self.cadastre_search_dialog:
            self.iface.removeDockWidget(self.cadastre_search_dialog)

        # Remove processing provider
        # noinspection PyArgumentList
        QgsApplication.processingRegistry().removeProvider(self.provider)

    @staticmethod
    def run_tests(pattern='test_*.py', package=None):
        """Run the test inside QGIS."""
        from pathlib import Path
        try:
            from cadastre.tests.runner import test_package
            if package is None:
                package = f'{Path(__file__).parent.name}.__init__'
            test_package(package, pattern)
        except (AttributeError, ModuleNotFoundError):
            message = 'Could not load tests. Are you using a production package?'
            print(message)  # NOQA
