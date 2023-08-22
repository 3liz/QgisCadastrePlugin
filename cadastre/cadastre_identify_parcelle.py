"""
/***************************************************************************
 Cadastre - import main methods
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

from qgis.core import (
    QgsFeature,
    QgsFeatureRequest,
    QgsGeometry,
    QgsMapLayer,
    QgsVectorLayer,
)
from qgis.gui import QgsMapToolIdentify
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QCursor, QPixmap

from cadastre.cadastre_cursor import Cursor


class IdentifyParcelle(QgsMapToolIdentify):
    cadastreGeomIdentified = pyqtSignal(QgsVectorLayer, QgsFeature)

    def __init__(self, canvas, layer):

        super(QgsMapToolIdentify, self).__init__(canvas)
        self.canvas = canvas
        self.layer = layer
        self.cursor = QCursor(QPixmap(Cursor), 1, 6)

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def canvasReleaseEvent(self, mouseEvent):

        layer = self.layer

        if not layer:
            # Ignore if no layer
            return

        if layer.type() != QgsMapLayer.VectorLayer:
            # Ignore this layer as it's not a vector
            # QgsMapLayer.VectorLayer is an equivalent to QgsMapLayerType.VectorLayer since 3.8
            return

        if layer.featureCount() == 0:
            # There are no features - skip
            return

        # ~ layer.removeSelection()

        # Determine the location of the click in real-world coords
        point = self.toLayerCoordinates(layer, mouseEvent.pos())
        pntGeom = QgsGeometry.fromPointXY(point)
        pntBuff = pntGeom.buffer((self.canvas.mapUnitsPerPixel() * 2), 0)
        rect = pntBuff.boundingBox()
        rq = QgsFeatureRequest(rect)
        selectList = []

        # Take first feature
        feature = None
        for feat in layer.getFeatures(rq):
            if feat.geometry().intersects(pntGeom):
                selectList.append(feat.id())
                feature = feat
                break

        # ~ layer.setSelectedFeatures( selectList )

        # Send signal
        if not feature:
            return

        self.cadastreGeomIdentified.emit(layer, feature)
