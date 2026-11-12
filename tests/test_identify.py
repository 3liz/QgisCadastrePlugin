""" Tool "Identifier une parcelle": a click on a parcel emits the parcel (issue #600) """

from qgis.core import QgsDataSourceUri, QgsFeatureRequest, QgsProject, QgsVectorLayer
from qgis.gui import QgsMapCanvas, QgsMapMouseEvent
from qgis.PyQt.QtCore import QEvent, QPoint, Qt

from cadastre.cadastre_database import CadastreDatabase
from cadastre.cadastre_identify_parcelle import IdentifyParcelle, parcelle_layers

from .test_import_data import TEST_SCHEMA
from .test_majic_data import COPROPRIETE, database, fetch, parcelles  # noqa: F401


def click_parcelle(layer: QgsVectorLayer, geo_parcelle: str) -> list[tuple[str, str]]:
    """Click with the identify tool on a point inside a parcel, like a user in the map canvas.

    The tool searches the parcel in the layers of the parcels of the current project.

    :param layer: A layer of the parcels, to find the location of the parcel.
    :param geo_parcelle: The parcel to click on.
    :return: The layer id and the geo_parcelle of the features emitted by the tool, empty if nothing is identified.
    """
    request = QgsFeatureRequest().setFilterExpression(f"\"geo_parcelle\" = '{geo_parcelle}'")
    feature = next(layer.getFeatures(request))

    # A canvas zoomed on the parcel, in the CRS of the layer
    canvas = QgsMapCanvas()
    canvas.resize(800, 600)
    canvas.setDestinationCrs(layer.crs())
    canvas.setExtent(feature.geometry().boundingBox().buffered(20))
    pixel = canvas.getCoordinateTransform().transform(feature.geometry().pointOnSurface().asPoint())

    # Release of the left button on the point, the tool emits the feature under it
    found: list[tuple[str, str]] = []
    tool = IdentifyParcelle(canvas)
    tool.cadastreGeomIdentified.connect(lambda lyr, f: found.append((lyr.id(), f["geo_parcelle"])))
    point = QPoint(round(pixel.x()), round(pixel.y()))
    tool.canvasReleaseEvent(
        QgsMapMouseEvent(canvas, QEvent.Type.MouseButtonRelease, point, Qt.MouseButton.LeftButton)
    )
    return found


def test_identify_postgis(parcelles: QgsVectorLayer):  # noqa: F811
    """ PostgreSQL: the parcel under the click is identified """
    assert click_parcelle(parcelles, COPROPRIETE) == [(parcelles.id(), COPROPRIETE)]


def test_identify_several_layers(database: CadastreDatabase, parcelles: QgsVectorLayer):  # noqa: F811
    """ Several layers of the parcels, and other layers on similar tables (issue #600) """
    project = QgsProject.instance()

    # A view of the user whose name contains parcelle_info, without the field geo_parcelle
    fetch(f"CREATE OR REPLACE VIEW {TEST_SCHEMA}.v_parcelle_info AS SELECT ogc_fid, geom FROM {TEST_SCHEMA}.parcelle_info")
    uri = QgsDataSourceUri(parcelles.source())
    uri.setTable("v_parcelle_info")
    view = QgsVectorLayer(uri.uri(), "Vue", "postgres")
    # Another layer of the parcels, loaded for other communes: the parcel is not in it
    other = QgsVectorLayer(parcelles.source(), "Parcelles autres communes", "postgres")
    other.setSubsetString(f"\"geo_parcelle\" != '{COPROPRIETE}'")
    project.addMapLayers([view, other])
    try:
        assert view.isValid() and other.isValid()
        assert {layer.id() for layer in parcelle_layers(project)} == {parcelles.id(), other.id()}
        # The parcel is found, whatever the order of the layers
        assert click_parcelle(parcelles, COPROPRIETE) == [(parcelles.id(), COPROPRIETE)]
    finally:
        project.removeMapLayers([view.id(), other.id()])
        fetch(f"DROP VIEW {TEST_SCHEMA}.v_parcelle_info")
