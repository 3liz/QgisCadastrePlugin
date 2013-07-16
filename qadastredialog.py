# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QadastreDialog
                                 A QGIS plugin
 This plugins helps users to import the french land registry ('cadastre') 
 into a database. It is meant to ease the use of the data in QGIs 
 by providing search tools and appropriate layer symbology.
                             -------------------
        begin                : 2013-06-11
        copyright            : (C) 2013 by 3liz
        email                : info@3liz.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from ui_qadastre import Ui_Qadastre
# create the dialog for zoom to point


class QadastreDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_Qadastre()
        self.ui.setupUi(self)
