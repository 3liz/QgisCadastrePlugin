# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Cadastre - QGIS plugin menu class
                                                                 A QGIS plugin
 This plugins helps users to import the french land registry ('cadastre')
 into a database. It is meant to ease the use of the data in QGIs
 by providing search tools and appropriate layer symbology.
                                                            -------------------
                begin                                : 2013-06-11
                copyright                        : (C) 2013 by 3liz
                email                                : info@3liz.com
 ***************************************************************************/

/***************************************************************************
 *                                                                                                                                                 *
 *     This program is free software; you can redistribute it and/or modify    *
 *     it under the terms of the GNU General Public License as published by    *
 *     the Free Software Foundation; either version 2 of the License, or         *
 *     (at your option) any later version.                                                                     *
 *                                                                                                                                                 *
 ***************************************************************************/
"""
try:
    from qgis.server import *
except:
    pass

from qgis.core import QgsMessageLog, QgsLogger

class cadastreServer:
    """Plugin for QGIS server
    this plugin loads Cadastre server tools"""

    def __init__(self, serverIface):
        # Save reference to the QGIS server interface
        self.serverIface = serverIface
        QgsMessageLog.logMessage("SUCCESS - Cadastre init", 'plugin', QgsMessageLog.INFO)
        from filters.cadastreFilter import cadastreFilter
        try:
            serverIface.registerFilter( cadastreFilter(serverIface), 100 )
        except Exception, e:
            QgsLogger.debug("cadastreServer - Error loading filter cadastreServer : %s" % e )
            QgsMessageLog.logMessage("CADASTRE  - Error loading filter cadastreServer: %s" % e, 'plugin', QgsMessageLog.WARNING)
