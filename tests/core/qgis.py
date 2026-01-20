import configparser
import importlib
import logging
import sys


from pathlib import Path
from typing import (
    Any,
    Optional,
)

import semver

from qgis.core import Qgis, QgsApplication
from qgis.gui import QgisInterface
from qgis.server import QgsServerInterface

#
# Logger hook
#


def install_logger_hook() -> None:
    """Install message log hook"""
    logging.debug("Installing logger hook")
    from qgis.core import Qgis

    # Add a hook to qgis  message log
    def writelogmessage(message, tag, level):
        arg = f"{tag}: {message}"
        if level == Qgis.Warning:
            logging.warning(arg)
        elif level == Qgis.Critical:
            logging.error(arg)
        else:
            logging.debug(arg)

    messageLog = QgsApplication.messageLog()
    messageLog.messageReceived.connect(writelogmessage)


#
# Plugin loader
#


def load_plugin(
    plugin_path: Path,
    iface: Optional[QgisInterface] = None,
    *,
    processing: bool = False,
) -> Any:
    package = _load_plugin(plugin_path, processing=processing)
    init = package.classFactory(iface)
    if processing:
        init.initProcessing()

    return init


def load_server_plugin(
    plugin_path: Path,
    iface: QgsServerInterface,
    *,
    processing: bool = False,
) -> Any:
    package = _load_plugin(plugin_path, processing=processing)
    init = package.serverClassFactory(iface)
    if processing:
        init.initProcessing()

    return init


def _load_plugin(
    plugin_path: Path,
    *,
    server: bool = False,
    processing: bool = False,
) -> Any:
    logging.info("Loading plugin: %s", plugin_path)
    cp = configparser.ConfigParser()
    with plugin_path.joinpath("metadata.txt").open() as f:
        cp.read_file(f)
        if server:
            assert cp["server"].getboolean("server")
        if processing:
            assert cp["general"].getboolean("hasProcessingProvider")
        assert _check_qgis_version(
            cp["general"].get("qgisMinimumVersion"),
            cp["general"].get("qgisMaximumVersion"),
        )

    sys.path.append(str(plugin_path.parent))

    plugin = plugin_path.name

    package = importlib.import_module(plugin)
    assert plugin in sys.modules

    return package


def _check_qgis_version(minver: Optional[str], maxver: Optional[str]) -> bool:
    version = semver.Version.parse(Qgis.QGIS_VERSION.split("-", maxsplit=1)[0])

    def _version(ver: Optional[str]) -> semver.Version:
        if not ver:
            return version

        # Normalize version
        parts = ver.split(".")
        match len(parts):
            case 1:
                parts.extend(("0", "0"))
            case 2:
                parts.append("0")
        return semver.Version.parse(".".join(parts))

    return _version(minver) <= version <= _version(maxver)
