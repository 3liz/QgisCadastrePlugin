"""
Cadastre - QGIS plugin menu class

This plugins helps users to import the french land registry ('cadastre')
into a database. It is meant to ease the use of the data in QGIs
by providing search tools and appropriate layer symbology.

begin    : 2013-06-11
copyright: (C) 2013 by 3liz
email    : info@3liz.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

"""

import os
import tempfile

from qgis.core import Qgis, QgsMessageLog
from qgis.server import QgsServerInterface
from pathlib import Path

from .cadastre_service import CadastreService

class CadastreServer:
    """ Plugin for QGIS server

        This plugin loads Cadastre server service
    """
    def __init__(self, serverIface: 'QgsServerInterface') -> None:
        # Save reference to the QGIS server interface
        self.serverIface = serverIface

        cachedirstr = os.getenv('QGIS_CADASTRE_CACHE_DIR')
        if not cachedirstr:
            # Create cache in /tmp/org.qgis.cadastre
            cachedirstr = os.path.join(tempfile.gettempdir(),'org.qgis.cadastre')

        self.cachedir = Path(cachedirstr)
        self.cachedir.mkdir(mode=0o750, parents=True, exist_ok=True)

        QgsMessageLog.logMessage('Cache directory set to %s' % cachedirstr,'cadastre',Qgis.Info)

        debug = os.getenv('QGIS_CADASTRE_DEBUG', '').lower() in ('1','yes','y','true')

        reg = serverIface.serviceRegistry()
        reg.registerService(CadastreService(cachedir=self.cachedir, debug=debug))

    def createService(self, debug: bool=False) -> CadastreService:
        """ Create  a new service instance

            Used for testing
        """
        return CadastreService(self.cachedir, debug=debug)

