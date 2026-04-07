import os
import sys

from pathlib import Path
from typing import Any

import pytest

from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QT_VERSION_STR

from .qgis_testing import QGIS_VERSION_INT, install_logger_hook, load_plugin

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
    os.environ["CI"] = "true"
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
def plugin(rootdir: Path, qgis_iface: QgisInterface, qgis_processing: Any) -> Any:
    plugin_path = rootdir.parent.joinpath(PLUGIN_SOURCE)
    plugin = load_plugin(plugin_path, qgis_iface, processing=True)

    yield plugin
