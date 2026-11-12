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
    QgsDataSourceUri,
    QgsFeature,
    QgsFeatureRequest,
    QgsGeometry,
    QgsMapLayer,
    QgsProject,
    QgsVectorLayer,
)
from qgis.gui import QgsMapCanvas, QgsMapMouseEvent, QgsMapToolIdentify
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtGui import QCursor, QPixmap

from cadastre.cadastre_cursor import Cursor

# Table and geometry column of the layer of the parcels loaded by the plugin
PARCELLE_TABLE = "parcelle_info"
PARCELLE_GEOMETRY = "geom"


def parcelle_layers(project: QgsProject) -> list[QgsVectorLayer]:
    """Return the layers of the parcels of the project, which the fiche parcellaire can display.

    A layer of the parcels is a PostgreSQL or Spatialite layer on the table parcelle_info, with the
    field geo_parcelle. The name of the table is compared exactly: a view or a table of the user
    whose name only contains parcelle_info is not a layer of the parcels.

    :param project: The QGIS project.
    :return: The layers of the parcels, several when data have been loaded several times.
    """
    layers = []
    for layer in project.mapLayers().values():
        # Database vector layers only
        if layer.type() != QgsMapLayer.LayerType.VectorLayer:
            continue
        if layer.providerType() not in ("postgres", "spatialite"):
            continue

        # The table parcelle_info, with its geometry and the identifier of the parcel
        uri = QgsDataSourceUri(layer.source())
        if uri.table() != PARCELLE_TABLE or uri.geometryColumn() != PARCELLE_GEOMETRY:
            continue
        if layer.fields().indexOf("geo_parcelle") < 0:
            continue
        layers.append(layer)
    return layers


class IdentifyParcelle(QgsMapToolIdentify):
    """Map tool opening the fiche of the parcel under the click.

    The layers of the parcels are searched at each click, not when the tool is activated, so that
    layers loaded or removed afterwards are taken into account (issue #600).
    """

    cadastreGeomIdentified = pyqtSignal(QgsVectorLayer, QgsFeature)

    def __init__(self, canvas: QgsMapCanvas, project: QgsProject | None = None):
        """
        :param canvas: The map canvas.
        :param project: The project of the layers of the parcels, the current project by default.
        """
        super(QgsMapToolIdentify, self).__init__(canvas)
        self.canvas = canvas
        self.project = project
        self.cursor = QCursor(QPixmap(Cursor), 1, 6)

    def activate(self):
        """Set the cursor of the tool on the map canvas."""
        self.canvas.setCursor(self.cursor)

    def candidate_layers(self) -> list[QgsVectorLayer]:
        """Return the layers of the parcels to search, the visible ones first.

        :return: The layers of the parcels displayed in the map canvas, or all the layers of the
            parcels of the project if none is displayed.
        """
        layers = parcelle_layers(self.project or QgsProject.instance())
        displayed = {layer.id() for layer in self.canvas.layers()}
        visible = [layer for layer in layers if layer.id() in displayed]
        return visible or layers

    def canvasReleaseEvent(self, mouseEvent: QgsMapMouseEvent):
        """Emit cadastreGeomIdentified with the first parcel under the click, nothing if there is none.

        :param mouseEvent: The release of the mouse button on the map canvas.
        """
        for layer in self.candidate_layers():
            # The location of the click in the coordinates of the layer, with a tolerance of 2 pixels
            point = self.toLayerCoordinates(layer, mouseEvent.pos())
            point_geometry = QgsGeometry.fromPointXY(point)
            tolerance = self.canvas.mapUnitsPerPixel() * 2
            rect = point_geometry.buffer(tolerance, 0).boundingBox()

            # The first parcel containing the point
            for feature in layer.getFeatures(QgsFeatureRequest(rect)):
                if feature.geometry().intersects(point_geometry):
                    self.cadastreGeomIdentified.emit(layer, feature)
                    return
