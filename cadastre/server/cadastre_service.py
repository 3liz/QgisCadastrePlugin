__copyright__ = "Copyright 2022, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import json
import re
import traceback

from collections import namedtuple
from pathlib import Path
from typing import Any, Dict, Sequence
from uuid import uuid4

from qgis.core import QgsFeature, QgsFeatureRequest, QgsProject, QgsVectorLayer
from qgis.server import QgsServerRequest, QgsServerResponse, QgsService

import cadastre.cadastre_common_base as cadastre_common

from cadastre.cadastre_export import CadastreExport
from cadastre.export_csv import (
    RechercheSpatiale,
    csv_text,
    locaux_proprietaires_export,
    parcelles_proprietaires_export,
    recherche_spatiale,
)
from cadastre.logger import Logger


# Requests of the service, listed in GetCapabilities so that Lizmap knows those it can use
REQUESTS = ["GetCapabilities", "GetHtml", "CreatePdf", "GetPdf", "GetExport"]

# Types of the request GetExport
EXPORT_TYPES = ("locaux", "proprietaires")


def is_true(params: Dict[str, str], name: str) -> bool:
    """Return True if the parameter is set to t, true or 1"""
    return params.get(name, "f").lower() in ("t", "true", "1")


def sensitive_data(params: Dict[str, str]) -> cadastre_common.SensitiveData:
    """Sensitive data the user can see, given by Lizmap from the rights of the user.

    ADVANCED gives access to all the sensitive data. Otherwise BIRTH, REVENUE and EXONERATION give access
    to the birth data, to the revenues and to the exonerations.
    """
    if is_true(params, "ADVANCED"):
        return cadastre_common.SensitiveData.full()
    return cadastre_common.SensitiveData(
        birth=is_true(params, "BIRTH"),
        revenue=is_true(params, "REVENUE"),
        exoneration=is_true(params, "EXONERATION"),
    )


# Parcelle format for validation
PARCELLE_FORMAT_RE = re.compile("^([A-Z0-9]+)*$")


def write_json_response(
    data: Dict[str, Any], response: QgsServerResponse, request_id: str, code: int = 200
) -> None:
    """Write data as json response"""
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
        """Format error response"""
        body = {
            "status": "fail",
            "message": self.msg,
            "request_id": self.request_id,
        }
        response.clear()
        write_json_response(body, response, self.request_id, self.code)


# Immutable structure for holding resources values
CadastreResources = namedtuple(
    "CadastreResources",
    ("layer", "geo_parcelle", "feature", "type", "layername", "connector", "connectionParams"),
)


class CadastreService(QgsService):
    def __init__(self, cache_dir: Path) -> None:
        super().__init__()
        self.cache_dir = cache_dir

    def name(self) -> str:
        """Service name"""
        return "CADASTRE"

    def version(self) -> str:
        """Service version"""
        return "1.0.0"

    def executeRequest(
        self, request: QgsServerRequest, response: QgsServerResponse, project: QgsProject
    ) -> None:
        """Execute a 'cadastre' request"""
        params = request.parameters()
        request_id = request.headers().get("X-Request-Id", "ND")

        # noinspection PyBroadException
        try:
            req_param = params.get("REQUEST", "").lower()
            # Unknown request: stop at once, before reading anything
            if req_param not in {name.lower() for name in REQUESTS}:
                raise CadastreError(
                    400,
                    f"Invalid REQUEST parameter: must be one of {', '.join(REQUESTS)}, found '{req_param}'",
                    request_id,
                )

            if req_param == "getcapabilities":
                self.get_capabilities(response, project, request_id)
            elif req_param == "createpdf":
                self.create_pdf(params, response, project, request_id)
            elif req_param == "getpdf":
                self.get_pdf(params, response, request_id)
            elif req_param == "gethtml":
                self.get_html(params, response, project, request_id)
            elif req_param == "getexport":
                self.get_export(params, response, project, request_id)

        except CadastreError as err:
            err.format_response(response)
        except Exception:
            Logger.critical(f"Unhandled exception, request-ID: {request_id}\n{traceback.format_exc()}")
            error = CadastreError(500, "Internal 'cadastre' service error", request_id)
            error.format_response(response)

    @staticmethod
    def get_capabilities(response: QgsServerResponse, project: QgsProject, request_id: str) -> None:
        """Get cadastral capabilities based on config stored as project custom variables"""
        # get project custom variables
        variables = project.customVariables()

        if "cadastre_parcelle_layer_id" not in variables or "cadastre_parcelle_unique_field" not in variables:
            raise CadastreError(400, "Project has no cadastral capabilities", request_id)

        parcelle_layer_id = variables["cadastre_parcelle_layer_id"]
        parcelle_layer_unique_field = variables["cadastre_parcelle_unique_field"]

        player = project.mapLayer(parcelle_layer_id)
        if not player:
            raise CadastreError(404, "Parcel layer not available", request_id)

        capabilities: Dict[str, Any] = {
            "parcelle": {
                "id": player.id(),
                "name": player.name(),
                "title": player.serverProperties().title(),
                "shortName": player.serverProperties().shortName(),
                "unique_field": parcelle_layer_unique_field,
            }
        }

        if "cadastre_section_layer_id" in variables:
            section_layer_id = variables["cadastre_section_layer_id"]
            slayer = project.mapLayer(section_layer_id)
            if slayer:
                capabilities["section"] = {
                    "id": slayer.id(),
                    "name": slayer.name(),
                    "title": slayer.serverProperties().title(),
                    "shortName": slayer.serverProperties().shortName(),
                }
                if "cadastre_section_unique_field" in variables:
                    capabilities["section"]["unique_field"] = variables["cadastre_section_unique_field"]

        if "cadastre_commune_layer_id" in variables:
            commune_layer_id = variables["cadastre_commune_layer_id"]
            slayer = project.mapLayer(commune_layer_id)
            if slayer:
                capabilities["commune"] = {
                    "id": slayer.id(),
                    "name": slayer.name(),
                    "title": slayer.serverProperties().title(),
                    "shortName": slayer.serverProperties().shortName(),
                }
                if "cadastre_commune_unique_field" in variables:
                    capabilities["commune"]["unique_field"] = variables["cadastre_commune_unique_field"]

        capabilities["requests"] = REQUESTS
        write_json_response(
            {"status": "success", "message": "Capabilities", "data": capabilities}, response, request_id
        )

    def create_pdf(
        self, params: Dict[str, str], response: QgsServerResponse, project: QgsProject, request_id: str
    ) -> None:
        """Create a PDF from cadastral data"""
        # Load ressources based on passed params
        res = self.get_ressources(params, project, request_id)

        # Get compte communal
        compte_communal = cadastre_common.getCompteCommunalFromParcelleId(
            res.geo_parcelle, res.connectionParams, res.connector
        )
        if not compte_communal:
            raise CadastreError(404, "No MAJIC data found for this parcel", request_id)

        # For an owner, all his comptes communaux
        comptes_communaux: str | list[str] = compte_communal
        p_multi = 1
        all_cities = params.get("ALLCITIES", "f").lower() in ("t", "true", "1")
        if res.type == "proprietaire" and p_multi == 1:
            comptes_communaux = cadastre_common.getProprietaireComptesCommunaux(
                compte_communal, res.connectionParams, res.connector, all_cities
            )

        Logger.debug(f"comptecommunal = {comptes_communaux}")

        # Export PDF
        qex = CadastreExport(
            project,
            res.layer,
            res.type,
            comptes_communaux,
            res.geo_parcelle,
            sensitive=sensitive_data(params),
        )
        qex.print_parcelle_page = True
        paths = qex.export_as_pdf()

        if not paths:
            raise CadastreError(424, "An error occurred while generating the PDF", request_id)

        Logger.debug(f"export_as_pdf(), paths: {paths}")

        tokens = []
        for path in map(Path, paths):
            uid = uuid4()

            Logger.debug(f"Item path: {path}")

            new_path = self.cache_dir / f"{uid.hex}.pdf"
            path.rename(new_path)
            tokens.append(uid.hex)

        json_response: Dict[str, Any] = {
            "status": "success",
            "message": "PDF generated",
            "data": {
                "url": {
                    "request": "getPdf",
                    "service": "cadastre",
                },
                "tokens": tokens,
            },
        }
        # The token is added here and not above to pass the bandit security check, code B105
        json_response["data"]["url"]["token"] = None
        write_json_response(json_response, response, request_id)

    def get_html(
        self, params: Dict[str, str], response: QgsServerResponse, project: QgsProject, request_id: str
    ) -> None:
        # Load ressources based on passed params
        res = self.get_ressources(params, project, request_id)
        sensitive = sensitive_data(params)

        def get_item_html(n):
            return cadastre_common.getItemHtml(n, res.feature, res.connectionParams, res.connector, sensitive)

        html = ""
        html += get_item_html("parcelle_majic")
        html += get_item_html("proprietaires")
        html += get_item_html("indivisions")
        html += get_item_html("subdivisions")
        html += get_item_html("locaux")

        write_json_response(
            {"status": "success", "message": "HTML generated", "data": html}, response, request_id
        )

    def get_export(
        self, params: Dict[str, str], response: QgsServerResponse, project: QgsProject, request_id: str
    ) -> None:
        """Export the locaux or the owners of a list of parcelles, for the CSV exports of Lizmap.

        Parameters:

        * LAYER: the name of the layer of the parcelles;
        * TYPE: locaux (one row per local and owner) or proprietaires (one row per owner, for mail merges);
        * PARCELLES: the identifiers of the parcelles, separated by commas. Lizmap gives only the parcelles
          the user can see (filters by login, of the layer and by polygon). The list can be long:
          the request can be sent with POST;
        * ADVANCED, or BIRTH, REVENUE and EXONERATION: the sensitive data the user can see;
        * SPATIAL_LAYER, SPATIAL_FIELD, SPATIAL_OBJECTS and SPATIAL_DISTANCE, optional, only for the type
          proprietaires: the id of a layer, its field, the values of the primary key of the objects selected
          by the spatial search of Lizmap and the distance: the codes of the objects near the parcelles
          of each owner are added.

        The response is the CSV file itself (standard CSV, see export_csv.csv_text): Lizmap sends it
        to the user without reading it all. The errors are in JSON.
        """
        export_type = params.get("TYPE", "")
        if export_type not in EXPORT_TYPES:
            raise CadastreError(
                400, f"Invalid or missing value for 'TYPE': {', '.join(EXPORT_TYPES)}", request_id
            )
        layer = self.parcelles_layer(params, project, request_id)
        parcelles = [p.strip() for p in params.get("PARCELLES", "").split(",") if p.strip()]
        sensitive = sensitive_data(params)
        connection_params = cadastre_common.getConnectionParameterFromDbLayer(layer)
        connector = cadastre_common.getConnectorFromUri(connection_params)

        try:
            if export_type == "locaux":
                columns, rows = locaux_proprietaires_export(
                    connector, connection_params, parcelles, sensitive
                )
            else:
                recherche = self.spatial_search(params, project, layer, request_id)
                columns, rows = parcelles_proprietaires_export(
                    connector, connection_params, parcelles, sensitive, recherche
                )
        except ValueError as e:
            raise CadastreError(400, str(e), request_id) from e

        response.setStatusCode(200)
        response.setHeader("Content-Type", "text/csv; charset=utf-8")
        response.setHeader("X-Request-Id", request_id)
        response.write(csv_text(columns, rows))

    @staticmethod
    def parcelles_layer(params: Dict[str, str], project: QgsProject, request_id: str) -> QgsVectorLayer:
        """Return the layer of the parcelles given by the parameter LAYER, from a database"""
        name = params.get("LAYER")
        if not name:
            raise CadastreError(400, "Missing parameter 'LAYER'", request_id)
        layers = project.mapLayersByName(name)
        if not layers or layers[0].providerType() not in ("postgres", "spatialite"):
            raise CadastreError(404, f"Layer '{name}' not found", request_id)
        return layers[0]

    @staticmethod
    def spatial_search(
        params: Dict[str, str], project: QgsProject, parcelles_layer: QgsVectorLayer, request_id: str
    ) -> RechercheSpatiale | None:
        """Return the spatial search of the export of the owners, None without SPATIAL_LAYER"""
        layer_id = params.get("SPATIAL_LAYER")
        if not layer_id:
            return None
        layer = project.mapLayer(layer_id)
        if not isinstance(layer, QgsVectorLayer):
            raise CadastreError(404, f"Layer '{layer_id}' not found", request_id)
        distance = params.get("SPATIAL_DISTANCE", "0")
        if not distance.isdigit():
            raise CadastreError(400, f"Invalid value for 'SPATIAL_DISTANCE': {distance}", request_id)
        objets = [o.strip() for o in params.get("SPATIAL_OBJECTS", "").split(",") if o.strip()]
        return recherche_spatiale(
            layer, parcelles_layer, params.get("SPATIAL_FIELD", ""), objets, int(distance)
        )

    @staticmethod
    def get_ressources(params: Dict[str, str], project: QgsProject, request_id: str) -> CadastreResources:
        """Find layer and feature corresponding to given parameters"""

        def get_param(name: str, allowed_values: Sequence[str] | None = None) -> str:
            v = params.get(name)
            if not v:
                raise CadastreError(400, f"Missing parameter '{name}'", request_id)

            if allowed_values and v not in allowed_values:
                raise CadastreError(400, f"Invalid or missing value for '{name}'", request_id)
            return v

        # Get layer and expression
        p_layer = get_param("LAYER")
        p_parcelle = get_param("PARCELLE")
        p_type = get_param("TYPE", ("parcelle", "proprietaire", "fiche"))

        # Get feature
        if not PARCELLE_FORMAT_RE.match(p_parcelle):
            raise CadastreError(400, f"Invalid PARCELLE format: {p_parcelle}", request_id)

        # Find layer
        lr = project.mapLayersByName(p_layer)
        if len(lr) <= 0:
            raise CadastreError(404, f"Layer '{p_layer}' not found", request_id)

        layer = lr[0]

        req = QgsFeatureRequest()
        req.setFilterExpression(f" \"geo_parcelle\" = '{p_parcelle}' ")

        it = layer.getFeatures(req)
        feat = QgsFeature()
        if not it.nextFeature(feat):
            raise CadastreError(
                404, f"Feature not found for parcelle '{p_parcelle}' in layer '{p_layer}'", request_id
            )

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
        """Get PDF files previously exported"""
        ptoken = params.get("TOKEN")
        if not ptoken:
            raise CadastreError(400, "Missing parameter: token", request_id)

        path = self.cache_dir / f"{ptoken}.pdf"

        Logger.debug(f"GetPDF = path is {path.as_posix()}")

        if not path.exists():
            raise CadastreError(404, "PDF not found", request_id)

        # Send PDF
        response.setHeader("Content-type", "application/pdf")
        response.setHeader("X-Request-Id", request_id)
        response.setStatusCode(200)
        try:
            response.write(path.read_bytes())
            path.unlink()
        except Exception:
            Logger.critical("Error occurred while reading PDF file, request ID {}".format(request_id))
            raise
