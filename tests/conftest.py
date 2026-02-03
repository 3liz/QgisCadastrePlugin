import os
import sys
import warnings


from pathlib import Path
from typing import (
    Any,
    Optional,
)

import pytest


from qgis.PyQt import Qt

from qgis.core import Qgis, QgsFontUtils, QgsProject
from qgis.gui import QgisInterface
from qgis.server import (
    QgsBufferServerRequest,
    QgsBufferServerResponse,
    QgsServer,
    QgsServerInterface,
    QgsServerRequest,
)

from .core.qgis import load_plugin, install_logger_hook
from .core.client import Response, Client

PLUGIN_SOURCE = "cadastre"


with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from osgeo import gdal


def pytest_report_header(config):
    return (
        f"QGIS : {Qgis.QGIS_VERSION_INT}\n"
        f"Python GDAL : {gdal.VersionInfo('VERSION_NUM')}\n"
        f"Python : {sys.version}\n"
        f"QT : {Qt.QT_VERSION_STR}"
    )


def pytest_sessionstart(session: pytest.Session):
    """Start qgis application"""
    # NOTE: prevent hanging on QMessageBox
    os.environ["CI"] = "true"
    install_logger_hook()


@pytest.fixture(scope="session")
def rootdir(request: pytest.FixtureRequest) -> Path:
    return request.config.rootpath


@pytest.fixture(scope="session")
def fixtures(rootdir: Path) -> Path:
    return rootdir.joinpath("fixtures")


@pytest.fixture(scope="session")
def output_dir(rootdir: Path) -> Path:
    outdir = rootdir.joinpath("__output__")
    outdir.mkdir(exist_ok=True)
    return outdir


@pytest.fixture(scope="session")
def qgis_server(request: pytest.FixtureRequest) -> QgsServer:
    QgsFontUtils.loadStandardTestFonts(["All"])
    return QgsServer()


@pytest.fixture(scope="session")
def qgis_server_iface(qgis_server: QgsServer) -> QgsServerInterface:
    return qgis_server.serverInterface()


@pytest.fixture(autouse=True, scope="session")
def plugin(rootdir: Path, qgis_iface: QgisInterface, qgis_processing: Any) -> Any:
    plugin_path = rootdir.parent.joinpath(PLUGIN_SOURCE)
    plugin = load_plugin(plugin_path, qgis_iface, processing=True)

    yield plugin


# Requests


@pytest.fixture(scope="session")
def client(data: Path, plugin: Any, qgis_server: QgsServer) -> Client:
    """Return a qgis server instance"""

    class _Client:
        def __init__(self) -> None:
            # Activate debug headers
            os.environ["QGIS_WMTS_CACHE_DEBUG_HEADERS"] = "true"

        @property
        def plugin(self) -> Any:
            """retourne l'instance du plugin"""
            return plugin

        def get_project_path(self, name: str) -> Path:
            return data.joinpath(name)

        def get_project(self, name: str) -> Optional[QgsProject]:
            projectpath = self.get_project_path(name)
            assert projectpath.exists()
            qgsproject = QgsProject(capabilities=Qgis.ProjectCapabilities())
            if qgsproject.read(str(projectpath)):
                return qgsproject

            return None

        def get(
            self,
            query: str,
            project: Optional[str] = None,
            headers: Optional[dict[str, str]] = None,
        ) -> Response:
            """Return server response from query"""
            if headers is None:
                headers = {}

            request = QgsBufferServerRequest(
                query,
                QgsServerRequest.GetMethod,
                headers,
                None,
            )
            response = QgsBufferServerResponse()
            if project is not None:
                qgsproject = self.get_project(project)
                if not qgsproject:
                    raise ValueError(f"Error reading project '{project}':")
            else:
                qgsproject = None
            qgis_server.handleRequest(request, response, project=qgsproject)
            return Response(responser)

    return _Client()
