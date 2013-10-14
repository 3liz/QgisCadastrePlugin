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
        self.cadastre_load_dialog = None
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
        icon = QIcon(os.path.dirname(__file__) + "/icons/icon.png")
        self.import_action = QAction(icon, u"Importer des données", self.iface.mainWindow())
        QObject.connect(self.import_action, SIGNAL("triggered()"), self.open_import_dialog)
        self.cadastre_menu.addAction(self.import_action)

        # Load Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/icon.png")
        self.load_action = QAction(icon, u"Charger des données", self.iface.mainWindow())
        QObject.connect(self.load_action, SIGNAL("triggered()"), self.toggle_load_dialog)
        self.cadastre_menu.addAction(self.load_action)
        if not self.cadastre_load_dialog:
            dialog = cadastre_load_dialog(self.iface)
            self.cadastre_load_dialog = dialog

        # Search Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/icon.png")
        self.search_action = QAction(icon, u"Outils de recherche", self.iface.mainWindow())
        QObject.connect(self.search_action, SIGNAL("triggered()"), self.toggle_search_dialog)
        self.cadastre_menu.addAction(self.search_action)
        if not self.cadastre_search_dialog:
            dialog = cadastre_search_dialog(self.iface)
            self.cadastre_search_dialog = dialog
            self.qc = cadastre_common(dialog)

        # Options Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/icon.png")
        self.option_action = QAction(icon, u"Configurer le plugin", self.iface.mainWindow())
        QObject.connect(self.option_action, SIGNAL("triggered()"), self.open_option_dialog)
        self.cadastre_menu.addAction(self.option_action)

        # About Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/icon.png")
        self.about_action = QAction(icon, u"À propos", self.iface.mainWindow())
        QObject.connect(self.about_action, SIGNAL("triggered()"), self.open_about_dialog)
        self.cadastre_menu.addAction(self.about_action)

        # Add cadastre toolbar
        self.toolbar = self.iface.addToolBar('Cadastre');

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


    def open_import_dialog(self):
        '''
        Import dialog
        '''
        dialog = cadastre_import_dialog(self.iface)
        dialog.exec_()

    def toggle_load_dialog(self):
        '''
        Load dock widget
        '''
        if self.cadastre_load_dialog.isVisible():
            self.cadastre_load_dialog.hide()
        else:
            self.cadastre_load_dialog.show()

            # hide search dialog if necessary
            self.cadastre_search_dialog.hide()

    def toggle_search_dialog(self):
        '''
        Search dock widget
        '''
        if self.cadastre_search_dialog.isVisible():
            self.cadastre_search_dialog.hide()
        else:
            self.cadastre_search_dialog.show()

            # hide load dialog if necessary
            self.cadastre_load_dialog.hide()

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
        parcelleDialog = cadastre_parcelle_dialog(self.iface, layer, feature, self.cadastre_search_dialog)
        parcelleDialog.show()


    def unload(self):
        if self.cadastre_menu != None:
            self.iface.mainWindow().menuBar().removeAction(self.cadastre_menu.menuAction())
            self.cadastre_menu.deleteLater()
        else:
            self.iface.removePluginMenu("&cadastre", self.cadastre_menu.menuAction())
            self.iface.removeToolBar(self.toolbar)
            self.cadastre_menu.deleteLater()

        if self.cadastre_load_dialog:
            self.iface.removeDockWidget(self.cadastre_load_dialog)
