"""
/***************************************************************************
 Cadastre
                                 A QGIS plugin
 This plugins helps users to import the french land registry ('cadastre') into a database.
 It is meant to ease the use of the data in QGIs by providing search tools and appropriate layer symbology.
                             -------------------
        begin                : 2013-06-11
        copyright            : (C) 2013 by 3liz
        email                : info@3liz.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
from __future__ import absolute_import


def classFactory(iface):
    # load Cadastre class from file Cadastre
    from .cadastre_menu import CadastreMenu
    return CadastreMenu(iface)


def serverClassFactory(serverIface):  # pylint: disable=invalid-name
    """Load cadastreServer class from file cadastre.
    :param serverIface: A QGIS Server interface instance.
    :type serverIface: QgsServerInterface
    """
    #
    from .server.cadastre_server import CadastreServer
    return CadastreServer(serverIface)
