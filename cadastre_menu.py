# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Cadastre - QGIS plugin menu class
                                                                 A QGIS plugin
 This plugins helps users to import the french land registry ('cadastre')
 into a database. It is meant to ease the use of the data in QGIs
 by providing search tools and appropriate layer symbology.
                                                            -------------------
                begin                                : 2013-06-11
                copyright                        : (C) 2013 by 3liz
                email                                : info@3liz.com
 ***************************************************************************/

/***************************************************************************
 *                                                                                                                                                 *
 *     This program is free software; you can redistribute it and/or modify    *
 *     it under the terms of the GNU General Public License as published by    *
 *     the Free Software Foundation; either version 2 of the License, or         *
 *     (at your option) any later version.                                                                     *
 *                                                                                                                                                 *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from cadastre_identify_parcelle import IdentifyParcelle
from cadastre_dialogs import *

# ---------------------------------------------

class cadastre_menu:
    def __init__(self, iface):
        self.iface = iface
        self.mapCanvas = iface.mapCanvas()
        self.cadastre_menu = None

        self.cadastre_search_dialog = None
        self.qc = None

    def cadastre_add_submenu(self, submenu):
        if self.cadastre_menu != None:
            self.cadastre_menu.addMenu(submenu)
        else:
            self.iface.addPluginToMenu("&cadastre", submenu.menuAction())

    def initGui(self):

        # Add Cadastre to QGIS menu
        self.cadastre_menu = QMenu(QCoreApplication.translate("cadastre", "Cadastre"))
        self.iface.mainWindow().menuBar().insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.cadastre_menu)

        # Import Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/database.png")
        self.import_action = QAction(icon, u"Importer des données", self.iface.mainWindow())
        QObject.connect(self.import_action, SIGNAL("triggered()"), self.open_import_dialog)

        # Search Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/search.png")
        self.search_action = QAction(icon, u"Outils de recherche", self.iface.mainWindow())
        QObject.connect(self.search_action, SIGNAL("triggered()"), self.toggle_search_dialog)
        if not self.cadastre_search_dialog:
            dialog = cadastre_search_dialog(self.iface)
            self.cadastre_search_dialog = dialog
            self.qc = cadastre_common(dialog)

        # Load Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/output.png")
        self.load_action = QAction(icon, u"Charger des données", self.iface.mainWindow())
        QObject.connect(self.load_action, SIGNAL("triggered()"), self.open_load_dialog)

        # Options Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/config.png")
        self.option_action = QAction(icon, u"Configurer le plugin", self.iface.mainWindow())
        QObject.connect(self.option_action, SIGNAL("triggered()"), self.open_option_dialog)

        # About Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/about.png")
        self.about_action = QAction(icon, u"À propos", self.iface.mainWindow())
        QObject.connect(self.about_action, SIGNAL("triggered()"), self.open_about_dialog)

        # Help Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/about.png")
        self.help_action = QAction(icon, u"Aide", self.iface.mainWindow())
        QObject.connect(self.help_action, SIGNAL("triggered()"), self.open_help)


        # Add actions to Cadastre menu
        self.cadastre_menu.addAction(self.import_action)
        self.cadastre_menu.addAction(self.load_action)
        self.cadastre_menu.addAction(self.search_action)
        self.cadastre_menu.addAction(self.option_action)
        self.cadastre_menu.addAction(self.about_action)
        self.cadastre_menu.addAction(self.help_action)

        # Add cadastre toolbar
        self.toolbar = self.iface.addToolBar(u'Cadastre');

        # open import dialog
        self.openImportAction = QAction(
            QIcon(os.path.dirname(__file__) +"/icons/database.png"),
            u"Importer des données",
            self.iface.mainWindow()
        )
        self.openImportAction.triggered.connect(self.open_import_dialog)
        self.toolbar.addAction(self.openImportAction)

        # open load dialog
        self.openLoadAction = QAction(
            QIcon(os.path.dirname(__file__) +"/icons/output.png"),
            u"Charger des données",
            self.iface.mainWindow()
        )
        self.openLoadAction.triggered.connect(self.open_load_dialog)
        self.toolbar.addAction(self.openLoadAction)

        # open search dialog
        self.openSearchAction = QAction(
            QIcon(os.path.dirname(__file__) +"/icons/search.png"),
            u"Outils de recherche",
            self.iface.mainWindow()
        )
        self.openSearchAction.triggered.connect(self.toggle_search_dialog)
        #~ self.openSearchAction.setCheckable(True)
        self.toolbar.addAction(self.openSearchAction)

        # open Option dialog
        self.openOptionAction = QAction(
            QIcon(os.path.dirname(__file__) +"/icons/config.png"),
            u"Configurer le plugin",
            self.iface.mainWindow()
        )
        self.openOptionAction.triggered.connect(self.open_option_dialog)
        self.toolbar.addAction(self.openOptionAction)

        # open About dialog
        self.openAboutAction = QAction(
            QIcon(os.path.dirname(__file__) +"/icons/about.png"),
            u"À propos",
            self.iface.mainWindow()
        )
        self.openAboutAction.triggered.connect(self.open_about_dialog)
        self.toolbar.addAction(self.openAboutAction)

        # Create action for "Parcelle information"
        self.identifyParcelleAction = QAction(
            QIcon(os.path.dirname(__file__) +"/icons/toolbar/get-parcelle-info.png"),
            "Infos parcelle",
            self.iface.mainWindow()
        )


        self.identifyParcelleAction.setCheckable(True)
        self.identyParcelleTool = IdentifyParcelle(self.mapCanvas)
        self.identyParcelleTool.geomIdentified.connect(self.getParcelleInfo)
        self.identyParcelleTool.setAction(self.identifyParcelleAction)
        self.identifyParcelleAction.triggered.connect(self.setIndentifyParcelleTool)
        self.toolbar.addAction(self.identifyParcelleAction)

        # Display About window on first use
        s = QSettings()
        firstUse = s.value("cadastre/isFirstUse" , 1, type=int)
        if firstUse == 1:
            s.setValue("cadastre/isFirstUse", 0)
            self.open_about_dialog()


        # refresh identify tool when new data loaded
        from cadastre_loading import cadastreLoading
        self.ql = cadastreLoading(self)
        self.ql.cadastreLoadingFinished.connect(self.refreshIndentifyParcelleTool)


    def open_import_dialog(self):
        '''
        Import dialog
        '''
        dialog = cadastre_import_dialog(self.iface)
        dialog.exec_()

    def open_load_dialog(self):
        '''
        Load dialog
        '''
        dialog = cadastre_load_dialog(
            self.iface,
            self.cadastre_search_dialog
        )
        dialog.exec_()

    def toggle_search_dialog(self):
        '''
        Search dock widget
        '''
        if self.cadastre_search_dialog.isVisible():
            self.cadastre_search_dialog.hide()
        else:
            self.cadastre_search_dialog.show()

    def open_option_dialog(self):
        '''
        Config dialog
        '''
        dialog = cadastre_option_dialog(self.iface)
        dialog.exec_()


    def open_about_dialog(self):
        '''
        About dialog
        '''
        dialog = cadastre_about_dialog(self.iface)
        dialog.exec_()

    def refreshIndentifyParcelleTool(self):
        self.identyParcelleTool = IdentifyParcelle(self.mapCanvas)
        layer = self.qc.getLayerFromLegendByTableProps('geo_parcelle')
        if not layer:
            QMessageBox.critical(
                self.cadastre_search_dialog,
                "Cadastre",
                u"La couche des parcelles n'a pas été trouvée !"
            )
            return
        self.iface.setActiveLayer(layer)

    def setIndentifyParcelleTool(self):
        '''
        Activite the identify tool
        for the layer geo_parcelle
        '''
        # First set Parcelle as active layer
        layer = self.qc.getLayerFromLegendByTableProps('geo_parcelle')
        if not layer:
            QMessageBox.critical(
                self.cadastre_search_dialog,
                "Cadastre",
                u"La couche des parcelles n'a pas été trouvée !"
            )
            return
        self.iface.setActiveLayer(layer)

        # The activate identify tool
        self.mapCanvas.setMapTool(self.identyParcelleTool)

    def getParcelleInfo(self, layer, feature):
        '''
        Return information of the identified
        parcelle
        '''
        # show parcelle form
        parcelleDialog = cadastre_parcelle_dialog(
            self.iface,
            layer,
            feature,
            self.cadastre_search_dialog
        )
        parcelleDialog.show()

    def open_help(self):
        '''Opens the html help file content with default browser'''
        #~ localHelpUrl = "https://github.com/3liz/QgisCadastrePlugin/blob/master/doc/index.rst"
        localHelpUrl = os.path.dirname(__file__) + "/doc/index.html"
        QDesktopServices.openUrl( QUrl(localHelpUrl) )


    def unload(self):
        if self.cadastre_menu != None:
            self.iface.mainWindow().menuBar().removeAction(self.cadastre_menu.menuAction())
            self.cadastre_menu.deleteLater()
            self.iface.mainWindow().removeToolBar(self.toolbar)
        else:
            self.iface.removePluginMenu("&cadastre", self.cadastre_menu.menuAction())
            self.cadastre_menu.deleteLater()

        if self.cadastre_search_dialog:
            self.iface.removeDockWidget(self.cadastre_search_dialog)
