"""
 Cadastre - Export method class

A QGIS service plugin

This plugins helps users to import the french land registry ('cadastre')
into a database. It is meant to ease the use of the data in QGIs
by providing search tools and appropriate layer symbology.

begin                                : 2013-06-11
copyright                            : (C) 2013,2019 by 3liz
email                                : info@3liz.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import json
import re
import traceback

from collections import namedtuple
from pathlib import Path
from typing import Dict, Sequence
from uuid import uuid4

from qgis.core import (
    Qgis,
    QgsFeature,
    QgsFeatureRequest,
    QgsMessageLog,
    QgsProject,
)
from qgis.server import QgsServerRequest, QgsServerResponse, QgsService

import cadastre.cadastre_common_base as cadastre_common

from cadastre.cadastre_export import CadastreExport

# Parcelle format for validation
PARCELLE_FORMAT_RE = re.compile("^([A-Z0-9]+)*$")


def write_json_response(data: Dict[str, str], response: QgsServerResponse, code: int = 200) -> None:
    """ Write data as json response
    """
    response.setStatusCode(code)
    response.setHeader("Content-Type", "application/json")
    response.write(json.dumps(data))


class CadastreError(Exception):

    def __init__(self, code: int, msg: str) -> None:
        super().__init__(msg)
        self.msg = msg
        self.code = code
        QgsMessageLog.logMessage("Cadastre request error %s: %s" % (code, msg), "cadastre", Qgis.Critical)

    def formatResponse(self, response: QgsServerResponse) -> None:
        """ Format error response
        """
        body = {'status': 'fail', 'message': self.msg}
        response.clear()
        write_json_response(body, response, self.code)


# Immutable structure for holding resources values
CadastreResources = namedtuple('CadastreResources',
                               ('layer', 'geo_parcelle', 'feature', 'type', 'layername',
                                'connector', 'connectionParams'))


class CadastreService(QgsService):

    def __init__(self, cachedir: Path, debug: bool = False) -> None:
        super().__init__()

        self.debugMode = debug
        self.cachedir = cachedir

    # QgsService inherited

    def name(self) -> str:
        """ Service name
        """
        return 'CADASTRE'

    def version(self) -> str:
        """ Service version
        """
        return "1.0.0"

    def allowMethod(self, method: QgsServerRequest.Method) -> bool:
        """ Check supported HTTP methods
        """
        return method in (QgsServerRequest.GetMethod,
                          QgsServerRequest.PostMethod)

    def executeRequest(self, request: QgsServerRequest, response: QgsServerResponse,
                       project: QgsProject) -> None:
        """ Execute a 'cadastre' request
        """
        params = request.parameters()

        try:
            reqparam = params.get('REQUEST', '').lower()

            if reqparam == 'getcapabilities':
                self.get_capabilities(params, response, project)
            elif reqparam == 'createpdf':
                self.create_pdf(params, response, project)
            elif reqparam == 'getpdf':
                self.get_pdf(params, response)
            elif reqparam == 'gethtml':
                self.get_html(params, response, project)
            else:
                raise CadastreError(400, ("Invalid REQUEST parameter: "
                                          "must be one of GetCapabilities, GetHtml, CreatePdf or GetPdf,"
                                          "found '%s'") % reqparam)

        except CadastreError as err:
            err.formatResponse(response)
        except Exception:
            QgsMessageLog.logMessage("Unhandled exception:\n%s" % traceback.format_exc(), "cadastre", Qgis.Critical)
            err = CadastreError(500, "Internal 'cadastre' service error")
            err.formatResponse(response)

    def get_capabilities(self, params: Dict[str, str], response: QgsServerResponse, project: QgsProject) -> None:
        """ Get cadastral capabilities based on config stored as project custom variables
        """
        # get project custom variables
        variables = project.customVariables()

        if 'cadastre_parcelle_layer_id' not in variables or \
                'cadastre_parcelle_unique_field' not in variables:
            raise CadastreError(400, "Project has no cadastral capabilities")

        parcelle_layer_id = variables['cadastre_parcelle_layer_id']
        parcelle_layer_unique_field = variables['cadastre_parcelle_unique_field']

        player = project.mapLayer(parcelle_layer_id)
        if not player:
            raise CadastreError(404, "Parcel layer not available")

        capabilities = {
            'parcelle': {
                'id': player.id(),
                'name': player.name(),
                'title': player.title(),
                'shortName': player.shortName(),
                'unique_field': parcelle_layer_unique_field
            }
        }

        if 'cadastre_section_layer_id' in variables:
            section_layer_id = variables['cadastre_section_layer_id']
            slayer = project.mapLayer(section_layer_id)
            if slayer:
                capabilities['section'] = {
                    'id': slayer.id(),
                    'name': slayer.name(),
                    'title': slayer.title(),
                    'shortName': slayer.shortName()
                }
                if 'cadastre_section_unique_field' in variables:
                    capabilities['section']['unique_field'] = variables['cadastre_section_unique_field']

        if 'cadastre_commune_layer_id' in variables:
            commune_layer_id = variables['cadastre_commune_layer_id']
            slayer = project.mapLayer(commune_layer_id)
            if slayer:
                capabilities['commune'] = {
                    'id': slayer.id(),
                    'name': slayer.name(),
                    'title': slayer.title(),
                    'shortName': slayer.shortName()
                }
                if 'cadastre_commune_unique_field' in variables:
                    capabilities['commune']['unique_field'] = variables['cadastre_commune_unique_field']

        write_json_response({
            'status': 'success',
            'message': 'Capabilities',
            'data': capabilities
        }, response)

    def create_pdf(self, params: Dict[str, str], response: QgsServerResponse, project: QgsProject) -> None:
        """ Create a PDF from cadastral data
        """
        # Load ressources based on passed params
        res = self.get_ressources(params, project)

        # Get compte communal
        comptecommunal = cadastre_common.getCompteCommunalFromParcelleId(
            res.geo_parcelle,
            res.connectionParams,
            res.connector
        )
        pmulti = 1
        all_cities = params.get('ALLCITIES', 'f').lower() in ['t', 'true', '1']
        if res.type == 'proprietaire' and pmulti == 1:
            comptecommunal = cadastre_common.getProprietaireComptesCommunaux(
                comptecommunal,
                res.connectionParams,
                res.connector,
                all_cities
            )

        if self.debugMode:
            QgsMessageLog.logMessage("Comptecommunal = %s" % comptecommunal, 'cadastre', Qgis.Debug)

        # Export PDF
        qex = CadastreExport(project, res.layer, res.type, comptecommunal, res.geo_parcelle)

        paths = qex.export_as_pdf()

        if not paths:
            raise CadastreError(424, 'An error occured while generating the PDF')

        if self.debugMode:
            QgsMessageLog.logMessage("export_as_pdf(), paths: %s" % paths, 'cadastre', Qgis.Debug)

        tokens = []
        for path in map(Path, paths):
            uid = uuid4()

            if self.debugMode:
                QgsMessageLog.logMessage("Item path: %s" % path)

            newpath = self.cachedir / ('%s.pdf' % uid.hex)
            path.rename(newpath)
            tokens.append(uid.hex)

        write_json_response({
            'status': 'success',
            'message': 'PDF generated',
            'data': {
                'url': {
                    'request': 'getPdf',
                    'service': 'cadastre',
                    'token': None
                },
                'tokens': tokens
            }
        }, response)

    def get_html(self, params: Dict[str, str], response: QgsServerResponse, project: QgsProject) -> None:
        # Load ressources based on passed params
        res = self.get_ressources(params, project)

        getItemHtml = lambda n: cadastre_common.getItemHtml(n, res.feature,
                                                            res.connectionParams,
                                                            res.connector)
        html = ''
        html += getItemHtml('parcelle_majic')
        html += getItemHtml('proprietaires')
        html += getItemHtml('subdivisions')
        html += getItemHtml('locaux')
        html += getItemHtml('locaux_detail')

        write_json_response({
            'status': 'success',
            'message': 'HTML generated',
            'data': html
        }, response)

    def get_ressources(self, params: Dict[str, str], project: QgsProject) -> CadastreResources:
        """ Find layer and feature corresponding to given parameters
        """

        def get_param(name: str, allowed_values: Sequence[str] = None) -> str:
            v = params.get(name)
            if not v:
                raise CadastreError(400, "Missing parameter '%s'" % name)
            v = v
            if allowed_values and v not in allowed_values:
                raise CadastreError(400, "Invalid or missing value for '%s'" % name)
            return v

        # Get layer and expression
        player = get_param('LAYER')
        pparcelle = get_param('PARCELLE')
        ptype = get_param('TYPE', ('parcelle', 'proprietaire', 'fiche'))

        # Get feature
        if not PARCELLE_FORMAT_RE.match(pparcelle):
            raise CadastreError(400, "Invalid PARCELLE format: %s" % pparcelle)

        # Find layer
        layer = None
        lr = project.mapLayersByName(player)
        if len(lr) > 0:
            layer = lr[0]
        else:
            raise CadastreError(404, "Layer '%s' not found" % player)

        req = QgsFeatureRequest()
        req.setFilterExpression(' "geo_parcelle" = \'%s\' ' % pparcelle)

        it = layer.getFeatures(req)
        feat = QgsFeature()
        if not it.nextFeature(feat):
            raise CadastreError(404, "Feature not found for parcelle '%s' in layer '%s'" % (pparcelle, player))

        # Get layer connection parameters
        connectionParams = cadastre_common.getConnectionParameterFromDbLayer(layer)
        connector = cadastre_common.getConnectorFromUri(connectionParams)

        return CadastreResources(geo_parcelle=pparcelle,
                                 feature=feat,
                                 type=ptype,
                                 layer=layer,
                                 layername=player,
                                 connector=connector,
                                 connectionParams=connectionParams)

    def get_pdf(self, params: Dict[str, str], response: QgsServerResponse) -> None:
        """ Get PDF files previously exported
        """
        ptoken = params.get('TOKEN')
        if not ptoken:
            raise CadastreError(400, "Missing parameter: token")

        path = self.cachedir / ('%s.pdf' % ptoken)

        if self.debugMode:
            QgsMessageLog.logMessage("GetPDF = path is %s" % path.as_posix(), 'cadastre', Qgis.Debug)

        if not path.exists():
            raise CadastreError(404, "PDF not found")

        # Send PDF
        response.setHeader('Content-type', 'application/pdf')
        response.setStatusCode(200)
        try:
            response.write(path.read_bytes())
            path.unlink()
        except:
            QgsMessageLog.logMessage("Error occured while reading PDF file", 'cadastre', Qgis.Critical)
            raise
