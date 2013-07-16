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
        QObject.connect(self.load_action, SIGNAL("triggered()"), self.open_load_dialog)
        self.qadastre_menu.addAction(self.load_action)

        # Interface Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/icon.png")
        self.interface_action = QAction(icon, u"Choisir l'interface", self.iface.mainWindow())
        QObject.connect(self.interface_action, SIGNAL("triggered()"), self.open_interface_dialog)
        self.qadastre_menu.addAction(self.interface_action)


    def unload(self):
        if self.qadastre_menu != None:
            self.iface.mainWindow().menuBar().removeAction(self.qadastre_menu.menuAction())
        else:
            self.iface.removePluginMenu("&qadastre", self.qadastre_menu.menuAction())
            
    def open_import_dialog(self):
        dialog = qadastre_import_dialog(self.iface)
        dialog.exec_()

            
    def open_load_dialog(self):
        dialog = qadastre_load_dialog(self.iface)
        dialog.exec_()

            
    def open_interface_dialog(self):
        dialog = qadastre_interface_dialog(self.iface)
        dialog.exec_()


