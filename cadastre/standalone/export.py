#!/usr/bin/env python

__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import os
import sys

"""
Script used by Lizmap Web Client to make a asynchrone call from PHP.
"""

qgisPrefixPath = "/usr"
os.environ["DISPLAY"] = ":99"
os.environ["HOME"] = "/srv/qgis"
sys.path.append(os.path.join(qgisPrefixPath, "share/qgis/python/"))
sys.path.append(os.path.join(qgisPrefixPath, "share/qgis/python/plugins/"))
sys.path.append('/srv/qgis/plugins')

import argparse

from qgis.core import QgsApplication, QgsFeatureRequest, QgsProject
from qgis.gui import QgsLayerTreeMapCanvasBridge, QgsMapCanvas

from cadastre.cadastre_export import CadastreExport
from cadastre.dialogs.dialog_common import CadastreCommon

# Variables
parser = argparse.ArgumentParser()
parser.add_argument(
    '-P',
    metavar='\"Project file\"',
    help='Usage: Override QGS project file'
)
parser.add_argument(
    '-L',
    metavar='\"Parcelle layer name\"',
    help='Usage: Override Parcelle layer name'
)
parser.add_argument(
    '-I',
    metavar='\"Parcelle ID\"',
    help='Usage: Override Parcelle ID'
)
parser.add_argument(
    '-T',
    metavar='\"Export type\"',
    help='Usage: Override Export type'
)
parser.add_argument(
    '-O',
    metavar='\"Output log file\"',
    help='Usage: Override Output log file'
)

####      Hardcode variables here      ####
#### Or use flags to override defaults ####
# -P = Project file
project_path = 'c:your\\project\\location.qgs'
# -L = Parcelle Layer Name ("Parcelles")
parcelle_layer = 'Parcelles'
# -I = Parcelle ID ("-1")
parcelle_id = '2018300189000EY0670'
# -T = Export type ("proprietaire")
export_type = 'parcelle'
# -D = Target directory for PDF ("/tmp/")
target_dir = '/tmp/'
# -O = Output log file ("/tmp/export_cadastre.log")
output_log = '/tmp/export_cadastre.log'

#### Setting variables using flags ####
if "-P" in sys.argv:
    project_path = sys.argv[sys.argv.index("-P") + 1]
if "-L" in sys.argv:
    parcelle_layer = sys.argv[sys.argv.index("-L") + 1]
if "-I" in sys.argv:
    parcelle_id = sys.argv[sys.argv.index("-I") + 1]
if "-T" in sys.argv:
    export_type = sys.argv[sys.argv.index("-T") + 1]
if "-D" in sys.argv:
    target_dir = sys.argv[sys.argv.index("-D") + 1]
if "-O" in sys.argv:
    output_log = sys.argv[sys.argv.index("-O") + 1]

# Instantiate QGIS
QgsApplication.setPrefixPath(qgisPrefixPath, True)
qgs = QgsApplication([], True)
QgsApplication.initQgis()

# Open the project
p = QgsProject()
p.read(project_path)
canvas = QgsMapCanvas()
bridge = QgsLayerTreeMapCanvasBridge(
    p.layerTreeRoot(),
    canvas
)
bridge.setCanvasLayers()

# Get the layers in the project
layerList = p.mapLayersByName(parcelle_layer)
if not layerList:
    layers = p.mapLayers()
    for lname, layer in layers.items():
        print(lname + ' ' + layer.name() + ' ' + parcelle_layer)
    layerList = [layer for lname, layer in layers.items() if layer.name() == parcelle_layer]
layer = layerList[0]

# Get Feature
req = QgsFeatureRequest()
req.setFilterExpression(' "geo_parcelle" = \'%s\' ' % parcelle_id)
it = layer.getFeatures(req)
feat = None
for f in it:
    feat = f
    break

# Get connection params
connectionParams = CadastreCommon.getConnectionParameterFromDbLayer(layer)
connector = CadastreCommon.getConnectorFromUri(connectionParams)

# Get compte communal
comptecommunal = CadastreCommon.getCompteCommunalFromParcelleId(
    feat['geo_parcelle'],
    connectionParams,
    connector
)

pmulti = 1
if export_type == 'proprietaire' and pmulti == 1:
    comptecommunal = CadastreCommon.getProprietaireComptesCommunaux(
        comptecommunal,
        connectionParams,
        connector
    )

# Export PDF
print(target_dir)
qex = CadastreExport(
    p,
    layer,
    export_type,
    comptecommunal,
    feat['geo_parcelle'],
    target_dir
)
paths = qex.exportAsPDF()
print(paths)

# Add path into file
with open(output_log, 'w') as f:
    for path in paths:
        f.write(path)

# Exit
QgsApplication.exitQgis()
