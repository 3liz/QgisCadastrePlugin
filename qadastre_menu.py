# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Qadastre - QGIS plugin menu class
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

from qadastre_dialogs import *

# ---------------------------------------------

class qadastre_menu:
    def __init__(self, iface):
        self.iface = iface
        self.qadastre_menu = None
        self.qadastre_load_dialog = None
        self.qadastre_search_dialog = None

    def qadastre_add_submenu(self, submenu):
        if self.qadastre_menu != None:
            self.qadastre_menu.addMenu(submenu)
        else:
            self.iface.addPluginToMenu("&qadastre", submenu.menuAction())

    def initGui(self):
        # Uncomment the following two lines to have qadastre accessible from a top-level menu
        self.qadastre_menu = QMenu(QCoreApplication.translate("qadastre", "Qadastre"))
        self.iface.mainWindow().menuBar().insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.qadastre_menu)

        # Import Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/icon.png")
        self.import_action = QAction(icon, u"Importer des données", self.iface.mainWindow())
        QObject.connect(self.import_action, SIGNAL("triggered()"), self.open_import_dialog)
        self.qadastre_menu.addAction(self.import_action)

        # Load Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/icon.png")
        self.load_action = QAction(icon, u"Charger des données", self.iface.mainWindow())
        QObject.connect(self.load_action, SIGNAL("triggered()"), self.toggle_load_dialog)
        self.qadastre_menu.addAction(self.load_action)
        if not self.qadastre_load_dialog:
            dialog = qadastre_load_dialog(self.iface)
            self.qadastre_load_dialog = dialog

        # Search Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/icon.png")
        self.search_action = QAction(icon, u"Outils de recherche", self.iface.mainWindow())
        QObject.connect(self.search_action, SIGNAL("triggered()"), self.toggle_search_dialog)
        self.qadastre_menu.addAction(self.search_action)
        if not self.qadastre_search_dialog:
            dialog = qadastre_search_dialog(self.iface)
            self.qadastre_search_dialog = dialog

        # Interface Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/icon.png")
        self.interface_action = QAction(icon, u"Choisir l'interface", self.iface.mainWindow())
        QObject.connect(self.interface_action, SIGNAL("triggered()"), self.open_interface_dialog)
        self.qadastre_menu.addAction(self.interface_action)


    def open_import_dialog(self):
        '''
        Import dialog
        '''
        dialog = qadastre_import_dialog(self.iface)
        dialog.exec_()

    def toggle_load_dialog(self):
        '''
        Load dock widget
        '''
        if self.qadastre_load_dialog.isVisible():
            self.qadastre_load_dialog.hide()
        else:
            self.qadastre_load_dialog.show()

            # hide search dialog if necessary
            self.qadastre_search_dialog.hide()

    def toggle_search_dialog(self):
        '''
        Search dock widget
        '''
        if self.qadastre_search_dialog.isVisible():
            self.qadastre_search_dialog.hide()
        else:
            self.qadastre_search_dialog.show()

            # hide load dialog if necessary
            self.qadastre_load_dialog.hide()

    def open_interface_dialog(self):
        '''
        Config dock widget
        '''
        dialog = qadastre_interface_dialog(self.iface)
        dialog.exec_()


    def unload(self):
        if self.qadastre_menu != None:
            self.iface.mainWindow().menuBar().removeAction(self.qadastre_menu.menuAction())
            self.qadastre_menu.deleteLater()
        else:
            self.iface.removePluginMenu("&qadastre", self.qadastre_menu.menuAction())
            self.qadastre_menu.deleteLater()

        if self.qadastre_load_dialog:
            self.iface.removeDockWidget(self.qadastre_load_dialog)
