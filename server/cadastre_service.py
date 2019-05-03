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

import os
import traceback
import tempfile
import json
import re

from collections import namedtuple
from uuid import uuid4
from pathlib import Path

from typing import Dict, Sequence

from qgis.core import (Qgis,
                       QgsMessageLog,
                       QgsProject,
                       QgsFeatureRequest,
                       QgsFeature)

from qgis.server import (QgsService,
                         QgsServerRequest,
                         QgsServerResponse)

import cadastre.cadastre_common_base as cadastre_common
from cadastre.cadastre_export import cadastreExport


# Parcelle format for validation
PARCELLE_FORMAT_RE = re.compile("^([A-Z0-9]+)*$")


def write_json_response( data: Dict[str,str], response: QgsServerResponse, code: int=200) -> None:
    """ Write data as json response
    """
    response.setStatusCode(code)
    response.setHeader("Content-Type", "application/json")
    response.write(json.dumps(data))



class CadastreError(Exception):

    def __init__(self, code: int, msg: str) -> None:
        super().__init__(msg)
        self.msg  = msg
        self.code = code
        QgsMessageLog.logMessage("Cadastre request error %s: %s" % (code,msg),"cadastre",Qgis.Critical)

    def formatResponse(self, response: QgsServerResponse) -> None:
        """ Format error response
        """
        body = { 'status': 'fail', 'message': self.msg }
        response.clear()
        write_json_response(body, response, self.code)


# Immutable structure for holding resources values
CadastreResources = namedtuple('CadastreResources',
        ('layer','geo_parcelle','feature','type','layername',
         'connector','connectionParams'))


class CadastreService(QgsService):

    def __init__(self, cachedir :Path, debug: bool=False) -> None:
        super().__init__()

        self.debugMode = debug
        self.cachedir  = cachedir

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
            reqparam  = params.get('REQUEST','').lower()

            if reqparam == 'createpdf':
                self.create_pdf(params, response, project)
            elif reqparam == 'getpdf':
                self.get_pdf()
            elif reqparam == 'gethtml':
                self.get_html(params, response, project)
            else:
                raise CadastreError(400, ("Invalid REQUEST parameter: "
                                          "must be one of GetHtml, CreatePdf or GetPdf,"
                                          "found '%s'") % reqparam)

        except CadastreError as err:
            err.formatResponse(response)
        except Exception as exc:
            QgsMessageLog.logMessage("Unhandled exception:\n%s" % traceback.format_exc(),"cadastre",Qgis.Critical)
            err = CadastreError(500,"Internal 'cadastre' service error")
            err.formatResponse(response)


    def create_pdf(self, params:Dict[str,str], response: QgsServerResponse, project: QgsProject) -> None:
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
        if self.type == 'proprietaire' and pmulti == 1:
            comptecommunal = cadastre_common.getProprietaireComptesCommunaux(
                comptecommunal,
                res.connectionParams,
                res.connector
            )

        if self.debugMode:
            QgsMessageLog.logMessage( "Comptecommunal = %s" % comptecommunal,'cadastre',Qgis.Debug )

        # Export PDF
        qex = cadastreExport(res.layer,res.type,comptecommunal,res.geo_parcelle)

        paths = qex.exportAsPDF()

        if not paths:
            raise CadastreError(424,'An error occured while generating the PDF')

        if self.debugMode:
            QgsMessageLog.logMessage( "exportAsPDF(), paths: %s" % paths,'cadastre', Qgis.Debug )

        tokens = []
        for path in map(Path,paths):
            uid = uuid4()

            if self.debugMode:
                QgsMessageLog.logMessage( "Item path: %s" % path )

            newpath = self.cachedir / ('%s.pdf' % uid.hex)
            path.rename(newpath)
            tokens.append( uid.hex )

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
        },response)

    def get_html(self, params:Dict[str,str], response: QgsServerResponse, project: QgsProject) -> None:
        # Load ressources based on passed params
        res = self.get_ressources(params, project)

        getItemHtml = lambda n: cadastre_common.getItemHtml(n,res.feature,
                                                              res.connectionParams,
                                                              res.connector)
        html = ''
        html+= getItemHtml('parcelle_majic')
        html+= getItemHtml('proprietaires')
        html+= getItemHtml('subdivisions')
        html+= getItemHtml('locaux')
        html+= getItemHtml('locaux_detail')

        write_json_response({
            'status': 'success',
            'message': 'HTML generated',
            'data': html
        },response)

    def get_ressources(self, params: Dict[str,str], project: QgsProject) -> CadastreResources:
        """ Find layer and feature corresponding to given parameters
        """

        def get_param(name: str, allowed_values: Sequence[str]=None) -> str:
            v = params.get(name)
            if not v:
                raise CadastreError(400,"Missing parameter '%s'" % name)
            v = v
            if allowed_values and not v in allowed_values:
                raise CadastreError(400,"Invalid or missing value for '%s'" % name)
            return v

        # Get layer and expression
        player    = get_param('LAYER')
        pparcelle = get_param('PARCELLE')
        ptype     = get_param('TYPE',('parcelle', 'proprietaire', 'fiche'))

        # Get feature
        if not PARCELLE_FORMAT_RE.match(pparcelle):
            raise CadastreError(400, "Invalid PARCELLE format: %s" % pparcelle)

        # Find layer
        lr = project.mapLayersByName(lname)
        if len(lr) > 0:
            layer = lr[0]
        else:
            raise CadastreError(404,"Layer '%s' not found" % lname)

        req = QgsFeatureRequest()
        req.setFilterExpression(' "geo_parcelle" = \'%s\' ' % pparcelle)

        it = layer.getFeatures(req)
        feat = QgsFeature()
        if not it.nextFeature(feat):
            raise CadastreError(404,"Feature not found for parcelle '%s' in layer '%s'" % (pparcelle,player))

        # Get layer connection parameters
        connectionParams = cadastre_common.getConnectionParameterFromDbLayer(layer)
        connector = cadastre_common.getConnectorFromUri( self.connectionParams )

        return CadastreResources(geo_parcelle = pparcelle,
                                 feature = feat,
                                 type = ptype,
                                 layer = layer,
                                 layername = player,
                                 connector = connector,
                                 connectionParams = connectionParams)

    def get_pdf(self, params: Dict[str,str], response: QgsServerResponse ) -> None:
        """ Get PDF files previously exported
        """
        ptoken = params.get('TOKEN')
        if not ptoken:
            raise CadastreError(400,"Missing parameter: token")

        path = self.cachedir / ('%s.pdf' % ptoken)

        if self.debugMode:
            QgsMessageLog.logMessage("GetPDF = path is %s" % path.as_posix(),'cadastre', Qgis.Debug)

        if not path.exists():
            raise CadastreError(404,"PDF not found")

        # Send PDF
        response.setHeader('Content-type', 'application/pdf')
        response.request.setStatusCode(200)
        try:
            response.write(path.read_bytes())
            path.unlink()
        except:
            QgsMessageLog.logMessage("Error occured while reading PDF file",'cadastre',QGis.Critical)
            raise
