#-----------------------------------------------------------
#
# Plain Geometry Editor is a QGIS plugin to edit geometries
# using plain text editors (WKT, WKB)
#
# Copyright    : (C) 2013 Denis Rouzaud
# Email        : denis.rouzaud@gmail.com
#
#-----------------------------------------------------------
#
# licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this progsram; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#---------------------------------------------------------------------

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QPixmap, QCursor
from qgis.core import QgsVectorLayer, QgsFeature
from qgis.gui import QgsMapToolIdentify

from cadastre_cursor import Cursor


class IdentifyParcelle(QgsMapToolIdentify):
    geomIdentified = pyqtSignal(QgsVectorLayer, QgsFeature)
    geomUnidentified = pyqtSignal()

    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolIdentify.__init__(self, canvas)
        self.setCursor(QCursor(QPixmap(Cursor), 1, 6))

    def canvasReleaseEvent(self, mouseEvent):
        results = self.identify(mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer)
        if len(results) > 0:
            self.geomIdentified.emit(results[0].mLayer, QgsFeature(results[0].mFeature))
        else:
            self.geomUnidentified.emit()
