__copyright__ = 'Copyright 2022, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'

import os
import tempfile

from pathlib import Path

from qgis.server import QgsServerInterface

from cadastre.logger import Logger
from cadastre.server.cadastre_service import CadastreService
from cadastre.server.tools import version


class CadastreServer:
    """ Plugin for QGIS server

        This plugin loads Cadastre server service
    """

    def __init__(self, server_iface: QgsServerInterface) -> None:

        Logger.info(f'Init server version "{version()}"')

        cache_dir_str = os.getenv('QGIS_CADASTRE_CACHE_DIR')
        if not cache_dir_str:
            # Create cache in /tmp/org.qgis.cadastre
            cache_dir_str = os.path.join(tempfile.gettempdir(), 'org.qgis.cadastre')

        self.cache_dir = Path(cache_dir_str)
        self.cache_dir.mkdir(mode=0o750, parents=True, exist_ok=True)

        Logger.info(f'Cache directory set to {cache_dir_str}')

        reg = server_iface.serviceRegistry()
        reg.registerService(CadastreService(cache_dir=self.cache_dir))

    def createService(self, debug: bool = False) -> CadastreService:
        """ Create  a new service instance

            Used for testing
        """
        _ = debug
        return CadastreService(self.cache_dir)
