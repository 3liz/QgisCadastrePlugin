# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Cadastre - loading main methods
                                 A QGIS plugin
 This plugins helps users to import the french land registry ('cadastre')
 into a database. It is meant to ease the use of the data in QGIs
 by providing search tools and appropriate layer symbology.
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
"""

import sys, os, glob
import re
import time
import tempfile
import shutil
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

# db_manager scripts
from db_manager.db_plugins.plugin import DBPlugin, Schema, Table, BaseError
from db_manager.db_plugins import createDbPlugin
from db_manager.dlg_db_error import DlgDbError


class cadastreLoading(QObject):

    cadastreLoadingFinished = pyqtSignal()

    def __init__(self, dialog):
        QObject.__init__(self)
        self.dialog = dialog

        # common cadastre methods
        self.qc = self.dialog.qc

        # List of database layers to load inQGIS
        self.qgisCadastreLayerList = [
            {'name': 'geo_commune', 'table': 'geo_commune', 'geom': 'geom', 'sql': ''},
            {'name': 'geo_zoncommuni', 'table': 'geo_zoncommuni', 'geom': 'geom', 'sql': ''},
            {'name': 'geo_label_zoncommuni', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'ZONCOMMUNI_id\''},
            {'name': 'geo_subdsect', 'table': 'geo_subdsect', 'geom': 'geom', 'sql': ''},
            {'name': 'geo_subdfisc', 'table': 'geo_subdfisc', 'geom': 'geom', 'sql': ''},
            {'name': 'geo_label_subdfisc', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'SUBDFISC_id\''},
            {'name': 'geo_batiment', 'table': 'geo_batiment', 'geom': 'geom', 'sql': ''},
            {'name': 'geo_parcelle', 'table': 'geo_parcelle', 'geom': 'geom', 'sql': ''},
            {'name': 'geo_label_parcelle', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'PARCELLE_id\''},
            {'name': 'geo_lieudit', 'table': 'geo_lieudit', 'geom': 'geom', 'sql': ''},
            {'name': 'geo_label_lieudit', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'LIEUDIT_id\''},
            {'name': 'geo_section', 'table': 'geo_section', 'geom': 'geom', 'sql': ''},
            {'name': 'geo_label_section', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'SECTION_id\''},
            {'name': 'geo_borne', 'table': 'geo_borne', 'geom': 'geom', 'sql': ''},
            {'name': 'geo_croix', 'table': 'geo_croix', 'geom': 'geom', 'sql': ''},
            {'name': 'geo_ptcanv', 'table': 'geo_ptcanv', 'geom': 'geom', 'sql': ''},
            {'name': 'geo_symblim', 'table': 'geo_symblim', 'geom': 'geom', 'sql': ''},
            {'name': 'geo_tronfluv', 'table': 'geo_tronfluv', 'geom': 'geom', 'sql': ''},
            {'name': 'geo_label_tronfluv', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'TRONFLUV_id\''},
            {'name': 'geo_tsurf', 'table': 'geo_tsurf', 'geom': 'geom', 'sql': ''},
            {'name': 'geo_label_tsurf', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'TSURF_id\''},
            {'name': 'geo_tpoint', 'table': 'geo_tpoint', 'geom': 'geom', 'sql': ''},
            {'name': 'geo_label_tpoint', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'TPOINT_id\''},
            {'name': 'geo_tline', 'table': 'geo_tline', 'geom': 'geom', 'sql': ''},
            {'name': 'geo_label_tline', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'TLINE_id\''},
            {'name': 'geo_label_num_voie', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'NUMVOIE_id\''},
            {'name': 'geo_label_voiep', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'VOIEP_id\''},
            {'name': 'geo_parcelle_uf', 'table': 'geo_parcelle', 'geom':'geom_uf', 'sql': ''},
            {'name': 'geo_label_parcelle_uf', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'PARCELLE_id\''}
        ]


    def processLoading(self):
        '''
        Load all the layers in QGIS
        and apply corresponding style
        '''

        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Get selected options
        providerName = self.dialog.dbpluginclass.providerName()
        qgisCadastreLayers = []
        communeLayer = None
        self.dialog.schema = unicode(self.dialog.liDbSchema.currentText())
        self.dialog.totalSteps = len(self.qgisCadastreLayerList)

        # Run the loading
        self.qc.updateLog(u'Chargement des tables :')

        # Get database list of tables
        layerUri = self.dialog.db.uri()
        if self.dialog.dbType == 'postgis':
            schemaSearch = [s for s in self.dialog.db.schemas() if s.name == self.dialog.schema]
            schemaInst = schemaSearch[0]
            dbTables = self.dialog.db.tables(schemaInst)
        if self.dialog.dbType == 'spatialite':
            dbTables = self.dialog.db.tables()


        # Get status of override combobox
        override = unicode(self.dialog.liOverrideLayer.currentText())

        # Loop throuhg qgisQastreLayerList and load each corresponding table
        for item in self.qgisCadastreLayerList:

            # update progress bar
            self.qc.updateLog(u'* Table %s' % item['name'])
            self.dialog.step+=1
            self.qc.updateProgressBar()

            # Get db_manager table instance
            table = [a for a in dbTables if a.name == item['table']][0]
            sql = ""
            if item.has_key('sql'):
                sql = item['sql']
            geomCol = ""
            if item.has_key('geom'):
                geomCol = item['geom']

            # Check if the layer is already in QGIS
            load = True
            cLayer = self.qc.getLayerFromLegendByTableProps(
                item['table'],
                geomCol,
                sql
            )
            if cLayer:
                if override == 'Remplacer':
                    self.qc.updateLog(u'  - Remplacement de la couche %s' % item['name'])
                    QgsMapLayerRegistry.instance().removeMapLayer(cLayer.id())
                else:
                    self.qc.updateLog(u'  - La couche %s a été conservée' % item['name'])
                    load = False

            # Create vector layer
            if table and load:
                tableName = table.name
                uniqueCol = table.getValidQGisUniqueFields(True) if table.isView else None
                layerUri.setDataSource(
                    self.dialog.schema,
                    tableName,
                    geomCol,
                    sql,
                    uniqueCol.name if uniqueCol else ""
                )
                vlayer = QgsVectorLayer(layerUri.uri(), item['name'], providerName)

                # apply style
                qmlPath = os.path.join(
                    self.qc.plugin_dir,
                    "styles/%s/%s.qml" % (self.dialog.themeDir, item['name'])
                )
                if os.path.exists(qmlPath):
                    vlayer.loadNamedStyle(qmlPath)

                # append vector layer to the list
                qgisCadastreLayers.append(vlayer)

                # keep commune layer to later zoom to extent
                if item['name'] == 'geo_commune':
                    communeLayer = vlayer


        # Add all layers to QGIS registry
        QgsMapLayerRegistry.instance().addMapLayers(qgisCadastreLayers)

        # Create a group "Cadastre" and move all layers into it
        li = self.dialog.iface.legendInterface()
        g1 = li.addGroup("Cadastre")
        for layer in qgisCadastreLayers:
            li.moveLayer(layer, g1)

        # Zoom to layer commune
        if communeLayer:
            self.dialog.iface.setActiveLayer(communeLayer)
            activeLayer = self.dialog.iface.activeLayer()
            if activeLayer:
                self.dialog.iface.zoomToActiveLayer()


        # progress bar
        self.qc.updateLog(u'Chargement des couches dans QGIS')
        self.dialog.step+=1
        self.qc.updateProgressBar()

        # Emit signal
        self.cadastreLoadingFinished.emit()

        # Final message
        QApplication.restoreOverrideCursor()
        QMessageBox.information(
            self.dialog,
            u"Cadastre",
            u"Les données ont bien été chargées dans QGIS"
        )
        self.dialog.pbProcess.setValue(0)

        QApplication.restoreOverrideCursor()
