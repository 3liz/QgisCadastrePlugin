# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Qadastre - operation functions
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

import sys
import time
import os.path
import operator
import tempfile

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

# --------------------------------------------------------
#    Qadastre utility functions
# --------------------------------------------------------


   

# --------------------------------------------------------
#    qadastre_import - Import data from EDIGEO +/- MAJIC
#    into a Sqlite/PostGreSQL database
# --------------------------------------------------------

def qadastre_import(dialog):
    
    
    return None



# --------------------------------------------------------
#    qadastre_load - Load data from database
# --------------------------------------------------------

def qadastre_load(dialog):

    return None


# --------------------------------------------------------
#    qadastre_interface - Change QGIS interface
# --------------------------------------------------------

def qadastre_interface(dialog, onetext):

    QMessageBox.critical(dialog, "Test", "Le texte = %s" % onetext)

    return None


