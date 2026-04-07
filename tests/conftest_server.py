import sys

from pathlib import Path
from typing import Any

import pytest

from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QT_VERSION_STR

from .qgis_testing import QGIS_VERSION_INT, install_logger_hook, load_server_plugin

# with warnings.catch_warnings():
#    warnings.filterwarnings("ignore", category=DeprecationWarning)
#    from osgeo import gdal

PLUGIN_SOURCE = "cadastre"


def pytest_report_header(config):
    from osgeo import gdal

    return (
        f"QGIS : {QGIS_VERSION_INT}\n"
        f"Python GDAL : {gdal.VersionInfo('VERSION_NUM')}\n"
        f"Python : {sys.version}\n"
        f"QT : {QT_VERSION_STR}"
    )


#
# Fixtures
#


def pytest_sessionstart(session: pytest.Session):
    """Start qgis application"""
    install_logger_hook()


@pytest.fixture(scope="session")
def rootdir(request: pytest.FixtureRequest) -> Path:
    return request.config.rootpath


@pytest.fixture(scope="session")
def data(rootdir: Path) -> Path:
    return rootdir.joinpath("data")


@pytest.fixture(scope="session")
def fixtures(rootdir: Path) -> Path:
    return rootdir.joinpath("fixtures")


@pytest.fixture(scope="session")
def output_dir(rootdir: Path) -> Path:
    outdir = rootdir.joinpath("__output__")
    outdir.mkdir(exist_ok=True)
    return outdir


@pytest.fixture(autouse=True, scope="session")
def plugin(rootdir: Path, qgis_processing: Any) -> Any:
    plugin_path = rootdir.parent.joinpath(PLUGIN_SOURCE)
    plugin = load_server_plugin(plugin_path, qgis_iface, processing=True)

    yield plugin


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

