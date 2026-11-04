""" Request GetExport of the service CADASTRE, called directly with the project of the test data """

import csv
import io
import json

from pathlib import Path
from urllib.parse import urlencode

import pytest

from qgis.core import QgsProject, QgsVectorLayer
from qgis.server import QgsBufferServerRequest, QgsBufferServerResponse

from cadastre.cadastre_common_base import SensitiveData
from cadastre.export_csv import csv_text, locaux_proprietaires_export, parcelles_proprietaires_export
from cadastre.server.cadastre_service import CadastreService

from .test_export_csv import LOCAUX_COLUMNS, PARCELLE, PARCELLES_COLUMNS, Connection, connection  # noqa: F401
from .test_majic_data import COPROPRIETE, database, fetch, parcelles  # noqa: F401


def raw_request(tmp_path: Path, **params: str) -> QgsBufferServerResponse:
    """Execute a request of the service CADASTRE, return the response"""
    url = "http://localhost/?" + urlencode({"SERVICE": "CADASTRE", **params})
    response = QgsBufferServerResponse()
    CadastreService(tmp_path).executeRequest(QgsBufferServerRequest(url), response, QgsProject.instance())
    response.finish()
    return response


def request(tmp_path: Path, **params: str) -> tuple[int, dict]:
    """Execute a request of the service CADASTRE, return the HTTP code and the JSON response"""
    response = raw_request(tmp_path, **params)
    return response.statusCode(), json.loads(bytes(response.body()).decode())


@pytest.mark.parametrize("name", ["", "GetMap", "getexports"])
def test_unknown_request(tmp_path: Path, name: str):
    """ An unknown request is refused at once, with the list of the requests """
    code, data = request(tmp_path, REQUEST=name)
    assert code == 400
    assert data["status"] == "fail"
    assert "GetExport" in data["message"]


def test_capabilities_requests(tmp_path: Path, parcelles: QgsVectorLayer):  # noqa: F811
    """ Lizmap knows from GetCapabilities that it can use GetExport """
    project = QgsProject.instance()
    project.setCustomVariables({"cadastre_parcelle_layer_id": parcelles.id(), "cadastre_parcelle_unique_field": "x"})
    try:
        code, data = request(tmp_path, REQUEST="GetCapabilities")
    finally:
        project.setCustomVariables({})
    assert code == 200
    assert "GetExport" in data["data"]["requests"]


def export(tmp_path: Path, **params: str) -> tuple[str, list[list[str]]]:
    """Execute a request GetExport, return the CSV file and its lines"""
    response = raw_request(tmp_path, REQUEST="GetExport", LAYER="Parcelles", **params)
    content = bytes(response.body()).decode("utf-8")
    assert response.statusCode() == 200, content
    assert response.headers()["Content-Type"] == "text/csv; charset=utf-8"
    return content, list(csv.reader(io.StringIO(content)))


@pytest.mark.parametrize("export_type", ["locaux", "proprietaires"])
def test_export_csv(tmp_path: Path, connection: Connection, parcelles: QgsVectorLayer, export_type: str):  # noqa: F811
    """ The CSV file is the one of the export, see csv_text """
    content, _lines = export(tmp_path, TYPE=export_type, PARCELLES=f"{COPROPRIETE},{PARCELLE}")
    function = locaux_proprietaires_export if export_type == "locaux" else parcelles_proprietaires_export
    columns, rows = function(*connection, [COPROPRIETE, PARCELLE], SensitiveData())
    assert content == csv_text(columns, rows)


@pytest.mark.parametrize("sensitive, masked", [({}, True), ({"BIRTH": "1"}, False), ({"ADVANCED": "t"}, False)])
def test_export_locaux(tmp_path: Path, parcelles: QgsVectorLayer, sensitive: dict, masked: bool):  # noqa: F811
    _content, lines = export(tmp_path, TYPE="locaux", PARCELLES=f"{COPROPRIETE},{PARCELLE}", **sensitive)
    assert lines[0] == LOCAUX_COLUMNS
    rows = [dict(zip(LOCAUX_COLUMNS, line)) for line in lines[1:]]
    assert {row["parcelle"] for row in rows} == {COPROPRIETE, PARCELLE}
    assert all((row["p_date_naissance"] == "XX/XX/XXXX") is masked for row in rows)


def test_export_proprietaires(tmp_path: Path, parcelles: QgsVectorLayer):  # noqa: F811
    """ The owners, with the codes of the buildings selected near their parcelles """
    bati = QgsProject.instance().mapLayersByName("Bâti")[0]
    objets = [str(fid) for (fid,) in fetch("SELECT ogc_fid FROM cadastre.geo_batiment ORDER BY 1 LIMIT 20")]
    _content, lines = export(
        tmp_path, TYPE="proprietaires", PARCELLES=COPROPRIETE,
        SPATIAL_LAYER=bati.id(), SPATIAL_FIELD="geo_batiment", SPATIAL_OBJECTS=",".join(objets),
        SPATIAL_DISTANCE="1000",
    )
    assert lines[0] == [*PARCELLES_COLUMNS, "code_objet"]
    assert lines[1][-1]


@pytest.mark.parametrize(
    "params",
    [
        {"TYPE": "unknown", "PARCELLES": COPROPRIETE},
        {"TYPE": "locaux", "PARCELLES": ""},
        {"TYPE": "locaux", "PARCELLES": f"{COPROPRIETE}') OR ('1'='1"},
        {"TYPE": "proprietaires", "PARCELLES": COPROPRIETE, "SPATIAL_LAYER": "unknown"},
        {"TYPE": "locaux", "PARCELLES": COPROPRIETE, "LAYER": "unknown"},
    ],
)
def test_export_errors(tmp_path: Path, parcelles: QgsVectorLayer, params: dict):  # noqa: F811
    """ The invalid parameters are refused, with a JSON error """
    code, data = request(tmp_path, **{"REQUEST": "GetExport", "LAYER": "Parcelles", **params})
    assert code in (400, 404)
    assert data["status"] == "fail"


def test_carte_identite(tmp_path: Path, parcelles: QgsVectorLayer):  # noqa: F811
    """ CreatePdf with the type identite: the carte d'identité of the parcel, then GetPdf gives the file """
    code, data = request(tmp_path, REQUEST="CreatePdf", LAYER="Parcelles", PARCELLE=COPROPRIETE, TYPE="identite")
    assert code == 200, data
    tokens = data["data"]["tokens"]
    assert len(tokens) == 1

    response = raw_request(tmp_path, REQUEST="GetPdf", TOKEN=tokens[0])
    assert response.statusCode() == 200
    assert bytes(response.body()).startswith(b"%PDF")
