__copyright__ = 'Copyright 2022, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'

import json
import re
import traceback

from collections import namedtuple
from pathlib import Path
from typing import Dict, Sequence
from uuid import uuid4

from qgis.core import QgsFeature, QgsFeatureRequest, QgsProject
from qgis.server import QgsServerRequest, QgsServerResponse, QgsService

import cadastre.cadastre_common_base as cadastre_common

from cadastre.cadastre_export import CadastreExport
from cadastre.logger import Logger

# Parcelle format for validation
PARCELLE_FORMAT_RE = re.compile("^([A-Z0-9]+)*$")


def write_json_response(
        data: Dict[str, str], response: QgsServerResponse, request_id: str, code: int = 200) -> None:
    """ Write data as json response
    """
    response.setStatusCode(code)
    response.setHeader("Content-Type", "application/json")
    response.setHeader("X-Request-Id", request_id)
    response.write(json.dumps(data))


class CadastreError(Exception):

    def __init__(self, code: int, msg: str, request_id: str) -> None:
        super().__init__(msg)
        self.msg = msg
        self.code = code
        self.request_id = request_id
        Logger.critical(f"Cadastre request ID {request_id}, error {code}: {msg}")

    def format_response(self, response: QgsServerResponse) -> None:
        """ Format error response
        """
        body = {
            'status': 'fail',
            'message': self.msg,
            'request_id': self.request_id,
        }
        response.clear()
        write_json_response(body, response, self.request_id, self.code)


# Immutable structure for holding resources values
CadastreResources = namedtuple(
    'CadastreResources',
    (
        'layer', 'geo_parcelle', 'feature', 'type', 'layername',
        'connector', 'connectionParams'
    )
)


class CadastreService(QgsService):

    def __init__(self, cache_dir: Path) -> None:
        super().__init__()
        self.cache_dir = cache_dir

    def name(self) -> str:
        """ Service name
        """
        return 'CADASTRE'

    def version(self) -> str:
        """ Service version
        """
        return "1.0.0"

    def executeRequest(
            self, request: QgsServerRequest, response: QgsServerResponse,
            project: QgsProject) -> None:
        """ Execute a 'cadastre' request
        """
        params = request.parameters()
        request_id = request.headers().get('X-Request-Id', 'ND')

        # noinspection PyBroadException
        try:
            req_param = params.get('REQUEST', '').lower()

            if req_param == 'getcapabilities':
                self.get_capabilities(response, project, request_id)
            elif req_param == 'createpdf':
                self.create_pdf(params, response, project, request_id)
            elif req_param == 'getpdf':
                self.get_pdf(params, response, request_id)
            elif req_param == 'gethtml':
                self.get_html(params, response, project, request_id)
            else:
                raise CadastreError(
                    400,
                    (
                        f"Invalid REQUEST parameter: must be one of GetCapabilities, GetHtml, CreatePdf or GetPdf, "
                        f"found '{req_param}'"
                    ),
                    request_id,
                )

        except CadastreError as err:
            err.format_response(response)
        except Exception:
            Logger.critical(f"Unhandled exception, request-ID: {request_id}\n{traceback.format_exc()}")
            err = CadastreError(500, "Internal 'cadastre' service error", request_id)
            err.format_response(response)

    @staticmethod
    def get_capabilities(response: QgsServerResponse, project: QgsProject, request_id: str) -> None:
        """ Get cadastral capabilities based on config stored as project custom variables
        """
        # get project custom variables
        variables = project.customVariables()

        if 'cadastre_parcelle_layer_id' not in variables or \
                'cadastre_parcelle_unique_field' not in variables:
            raise CadastreError(400, "Project has no cadastral capabilities", request_id)

        parcelle_layer_id = variables['cadastre_parcelle_layer_id']
        parcelle_layer_unique_field = variables['cadastre_parcelle_unique_field']

        player = project.mapLayer(parcelle_layer_id)
        if not player:
            raise CadastreError(404, "Parcel layer not available", request_id)

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
        }, response, request_id)

    def create_pdf(
            self, params: Dict[str, str], response: QgsServerResponse, project: QgsProject, request_id: str) -> None:
        """ Create a PDF from cadastral data
        """
        # Load ressources based on passed params
        res = self.get_ressources(params, project, request_id)

        # Get compte communal
        compte_communal = cadastre_common.getCompteCommunalFromParcelleId(
            res.geo_parcelle,
            res.connectionParams,
            res.connector
        )
        p_multi = 1
        all_cities = params.get('ALLCITIES', 'f').lower() in ('t', 'true', '1')
        if res.type == 'proprietaire' and p_multi == 1:
            compte_communal = cadastre_common.getProprietaireComptesCommunaux(
                compte_communal,
                res.connectionParams,
                res.connector,
                all_cities
            )

        Logger.debug(f"comptecommunal = {compte_communal}")

        # Export PDF
        qex = CadastreExport(project, res.layer, res.type, compte_communal, res.geo_parcelle)
        qex.print_parcelle_page = True
        qex.for_third_party = params.get('ADVANCED', 'f').lower() not in ('t', 'true', '1')
        paths = qex.export_as_pdf()

        if not paths:
            raise CadastreError(424, 'An error occurred while generating the PDF', request_id)

        Logger.debug(f"export_as_pdf(), paths: {paths}")

        tokens = []
        for path in map(Path, paths):
            uid = uuid4()

            Logger.debug(f"Item path: {path}")

            new_path = self.cache_dir / f'{uid.hex}.pdf'
            path.rename(new_path)
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
        }, response, request_id)

    def get_html(
            self, params: Dict[str, str], response: QgsServerResponse, project: QgsProject, request_id: str) -> None:
        # Load ressources based on passed params
        res = self.get_ressources(params, project, request_id)
        for_third_party = params.get('ADVANCED', 'f').lower() not in ('t', 'true', '1')

        def get_item_html(n):
            return cadastre_common.getItemHtml(
                n,
                res.feature,
                res.connectionParams,
                res.connector,
                for_third_party
            )

        html = ''
        html += get_item_html('parcelle_majic')
        html += get_item_html('proprietaires')
        html += get_item_html('indivisions')
        html += get_item_html('subdivisions')
        html += get_item_html('locaux')
        html += get_item_html('locaux_detail')

        write_json_response({
            'status': 'success',
            'message': 'HTML generated',
            'data': html
        }, response, request_id)

    @staticmethod
    def get_ressources(params: Dict[str, str], project: QgsProject, request_id: str) -> CadastreResources:
        """ Find layer and feature corresponding to given parameters
        """

        def get_param(name: str, allowed_values: Sequence[str] = None) -> str:
            v = params.get(name)
            if not v:
                raise CadastreError(400, f"Missing parameter '{name}'", request_id)

            if allowed_values and v not in allowed_values:
                raise CadastreError(400, f"Invalid or missing value for '{name}'", request_id)
            return v

        # Get layer and expression
        p_layer = get_param('LAYER')
        p_parcelle = get_param('PARCELLE')
        p_type = get_param('TYPE', ('parcelle', 'proprietaire', 'fiche'))

        # Get feature
        if not PARCELLE_FORMAT_RE.match(p_parcelle):
            raise CadastreError(400, f"Invalid PARCELLE format: {p_parcelle}", request_id)

        # Find layer
        lr = project.mapLayersByName(p_layer)
        if len(lr) <= 0:
            raise CadastreError(404, f"Layer '{p_layer}' not found", request_id)

        layer = lr[0]

        req = QgsFeatureRequest()
        req.setFilterExpression(f' "geo_parcelle" = \'{p_parcelle}\' ')

        it = layer.getFeatures(req)
        feat = QgsFeature()
        if not it.nextFeature(feat):
            raise CadastreError(
                404, f"Feature not found for parcelle '{p_parcelle}' in layer '{p_layer}'", request_id)

        # Get layer connection parameters
        connection_params = cadastre_common.getConnectionParameterFromDbLayer(layer)
        connector = cadastre_common.getConnectorFromUri(connection_params)

        return CadastreResources(
            geo_parcelle=p_parcelle,
            feature=feat,
            type=p_type,
            layer=layer,
            layername=p_layer,
            connector=connector,
            connectionParams=connection_params,
        )

    def get_pdf(self, params: Dict[str, str], response: QgsServerResponse, request_id: str) -> None:
        """ Get PDF files previously exported
        """
        ptoken = params.get('TOKEN')
        if not ptoken:
            raise CadastreError(400, "Missing parameter: token", request_id)

        path = self.cache_dir / f'{ptoken}.pdf'

        Logger.debug(f"GetPDF = path is {path.as_posix()}")

        if not path.exists():
            raise CadastreError(404, "PDF not found", request_id)

        # Send PDF
        response.setHeader('Content-type', 'application/pdf')
        response.setHeader("X-Request-Id", request_id)
        response.setStatusCode(200)
        try:
            response.write(path.read_bytes())
            path.unlink()
        except Exception:
            Logger.critical("Error occurred while reading PDF file, request ID {}".format(request_id))
            raise
