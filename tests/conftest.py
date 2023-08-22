import configparser
import glob
import json
import logging
import os
import sys
import traceback

import pytest

logging.basicConfig( stream=sys.stderr )
logging.disable(logging.NOTSET)

LOGGER = logging.getLogger('cadastre')
LOGGER.setLevel(logging.DEBUG)

from typing import Any, Dict, Generator, List, Union

#
from qgis.core import Qgis, QgsApplication, QgsProject
from qgis.server import (
    QgsBufferServerRequest,
    QgsBufferServerResponse,
    QgsServer,
    QgsServerInterface,
    QgsServerRequest,
)

plugin_path = None

def pytest_addoption(parser):
    parser.addoption("--qgis-plugins", metavar="PATH", help="Plugin path", default=None)


def pytest_configure(config):
    global plugin_path
    plugin_path = config.getoption('qgis_plugins')


qgis_application = None


def pytest_sessionstart(session):
    """ Start qgis application
    """
    global qgis_application
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'

    # Define this in global environment
    os.environ['QGIS_DISABLE_MESSAGE_HOOKS'] = '1'
    os.environ['QGIS_NO_OVERRIDE_IMPORT'] = '1'

    qgis_pluginpath = os.environ.get('QGIS_PLUGINPATH','/usr/share/qgis/python/plugins/')
    sys.path.append(qgis_pluginpath)

    qgis_application = QgsApplication([], False)

    # Install logger hook
    install_logger_hook()


def pytest_sessionfinish(session, exitstatus):
    """ End qgis session
    """
    global qgis_application
    qgis_application.exitQgis()
    del qgis_application


# Define a *very* loosy jsonon type
JsonType = Union[List[Any],Dict[str,Any]]


class _Response:
    """ QgsBufferServerResponse wrapper
    """
    def __init__(self, resp: QgsBufferServerResponse) -> None:
        self._resp = resp
        self._json = None

    def json(self) -> JsonType:
        if self._json is None and self._resp.headers().get('Content-Type','').find('application/json')==0:
            self._json = json.loads(self.content.decode('utf-8'))
        return self._json

    @property
    def content(self) -> bytes:
        return bytes(self._resp.body())

    @property
    def status_code(self) -> int:
        return self._resp.statusCode()

    @property
    def headers(self) -> Dict[str,str]:
        return self._resp.headers()


@pytest.fixture(scope='session')
def client(request):
    """ Return a qgis server instance
    """
    class _Client:

        def __init__(self) -> None:

            self.cachedir = request.config.rootdir.join('__cadastre___')
            self.datapath = request.config.rootdir.join('data')

            os.environ['QGIS_CADASTRE_CACHE_DIR'] = self.cachedir.strpath

            self.server = QgsServer()

            # Load plugins
            load_plugins(self.server.serverInterface())

        def getplugin(self, name) -> Any:
            """ retourne l'instance du plugin
            """
            return server_plugins.get(name)

        def getprojectpath(self, name: str) -> str:
            return self.datapath.join(name)

        def get(self, query: str, project: str=None) -> _Response:
            """ Return server response from query
            """
            request  = QgsBufferServerRequest(query, QgsServerRequest.GetMethod, {}, None)
            response = QgsBufferServerResponse()
            if project is not None and not os.path.isabs(project):
                projectpath = self.datapath.join(project)
                qgsproject  = QgsProject()
                if not qgsproject.read(projectpath.strpath):
                    raise ValueError("Error reading project '%s':" % projectpath.strpath)
            else:
                qgsproject = None
            self.server.handleRequest(request, response, project=qgsproject)
            return _Response(response)

    return _Client()


##
## Plugins
##

def checkQgisVersion(minver: str, maxver: str) -> bool:

    def to_int(ver):
        major, *ver = ver.split('.')
        major = int(major)
        minor = int(ver[0]) if len(ver) > 0 else 0
        rev   = int(ver[1]) if len(ver) > 1 else 0
        if minor >= 99:
            minor = rev = 0
            major += 1
        if rev > 99:
            rev = 99
        return int(f"{major:d}{minor:02d}{rev:02d}")


    version = to_int(Qgis.QGIS_VERSION.split('-')[0])
    minver  = to_int(minver) if minver else version
    maxver  = to_int(maxver) if maxver else version
    return minver <= version <= maxver

def find_plugins(pluginpath: str) -> Generator[str,None,None]:
    """ Load plugins
    """
    for plugin in glob.glob(os.path.join(plugin_path + "/*")):
        if not os.path.exists(os.path.join(plugin, '__init__.py')):
            continue

        metadatafile = os.path.join(plugin, 'metadata.txt')
        if not os.path.exists(metadatafile):
            continue

        cp = configparser.ConfigParser()
        try:
            with open(metadatafile) as f:
                cp.read_file(f)
            if not cp['general'].getboolean('server'):
                logging.critical("%s is not a server plugin", plugin)
                continue

            minver = cp['general'].get('qgisMinimumVersion')
            maxver = cp['general'].get('qgisMaximumVersion')
        except Exception as exc:
            LOGGER.critical("Error reading plugin metadata '%s': %s",metadatafile,exc)
            continue

        if not checkQgisVersion(minver,maxver):
            LOGGER.critical(("Unsupported version for %s:"
                "\n MinimumVersion: %s"
                "\n MaximumVersion: %s"
                "\n Qgis version: %s"
                "\n Discarding") % (plugin,minver,maxver,
                    Qgis.QGIS_VERSION.split('-')[0]))
            continue

        yield os.path.basename(plugin)


server_plugins = {}


def load_plugins(serverIface: 'QgsServerInterface') -> None:
    """ Start all plugins
    """
    if not plugin_path:
        return

    LOGGER.info("Initializing plugins from %s", plugin_path)
    sys.path.append(plugin_path)

    for plugin in find_plugins(plugin_path):
        try:
            __import__(plugin)

            package = sys.modules[plugin]

            # Initialize the plugin
            server_plugins[plugin] = package.serverClassFactory(serverIface)
            LOGGER.info("Loaded plugin %s",plugin)
        except:
            LOGGER.critical("Error loading plugin %s\n%s",plugin, traceback.format_exc())


#
# Logger hook
#

def install_logger_hook( verbose: bool=False ) -> None:
    """ Install message log hook
    """
    from qgis.core import Qgis, QgsApplication

    # Add a hook to qgis  message log
    def writelogmessage(message, tag, level):
        arg = f'{tag}: {message}'
        if level == Qgis.Warning:
            LOGGER.warning(arg)
        elif level == Qgis.Critical:
            LOGGER.error(arg)
        elif verbose:
            # Qgis is somehow very noisy
            # log only if verbose is set
            LOGGER.info(arg)

    messageLog = QgsApplication.messageLog()
    messageLog.messageReceived.connect( writelogmessage )
