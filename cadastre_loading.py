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

from PyQt4.QtCore import (
    Qt,
    QObject,
    QSettings,
    pyqtSignal
)
from PyQt4.QtGui import (
    QApplication,
    QMessageBox
)

from qgis.core import (
    QGis,
    QgsMapLayerRegistry,
    QgsMessageLog,
    QgsLogger,
    QgsExpression,
    QgsMapLayer,
    QgsVectorLayer,
    QgsFeatureRequest
)
from datetime import datetime

# db_manager scripts
from db_manager.db_plugins.plugin import (
    DBPlugin,
    Schema,
    Table,
    BaseError
)
from db_manager.db_plugins import createDbPlugin
from db_manager.dlg_db_error import DlgDbError


class cadastreLoading(QObject):

    cadastreLoadingFinished = pyqtSignal()

    def __init__(self, dialog):
        QObject.__init__(self)
        self.dialog = dialog

        self.startTime = datetime.now()

        # common cadastre methods
        self.qc = self.dialog.qc
        self.defaultThemeDir = 'classique'
        self.themeDir = None

        # List of database layers to load inQGIS
        self.mainLayers = [
            u'Communes',
            u'Sections',
            u'Parcelles',
            u'Bâti'
        ]
        self.qgisCadastreLayerList = [
            {'label': u'Communes', 'name': 'geo_commune', 'table': 'geo_commune', 'geom': 'geom', 'sql': '', 'active': True, 'group': 'C', 'subset': '"geo_commune" IN (%s)'},
            {'label': u'Tronçons de route', 'name': 'geo_tronroute', 'table': 'geo_tronroute', 'geom': 'geom', 'sql': '', 'active': True, 'group': 'D'},
            {'label': u'Voies, routes et chemins', 'name': 'geo_zoncommuni', 'table': 'geo_zoncommuni', 'geom': 'geom', 'sql': '', 'active': False, 'group': 'D'},
            {'label': u'Noms de voies', 'name': 'geo_label_zoncommuni', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" IN ( \'ZONCOMMUNI_id\') ', 'active': True, 'group': 'E'},
            {'label': u'Secteurs', 'name': 'geo_subdsect', 'table': 'geo_subdsect', 'geom': 'geom', 'sql': '', 'active': True, 'group': 'D'},
            {'label': u'Subdivisions fiscales', 'name': 'geo_subdfisc', 'table': 'geo_subdfisc', 'geom': 'geom', 'sql': '', 'active': True, 'group': 'D'},
            {'label': u'Subdivisions fiscales (étiquette)', 'name': 'geo_label_subdfisc', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'SUBDFISC_id\'', 'active': False, 'group': 'E'},
            {'label': u'Bâti', 'name': 'geo_batiment', 'table': 'geo_batiment', 'geom': 'geom', 'sql': '', 'active': True, 'group': 'D'},
            {'label': u'Parcelles (étiquettes)', 'name': 'geo_label_parcelle', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'PARCELLE_id\'', 'active': True, 'group': 'E'},
            {'label': u'Lieux-dits', 'name': 'geo_lieudit', 'table': 'geo_lieudit', 'geom': 'geom', 'sql': '', 'active': True, 'group': 'D'},
            {'label': u'Lieux-dits  (étiquettes)', 'name': 'geo_label_lieudit', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'LIEUDIT_id\'', 'active': False, 'group': 'E'},
            {'label': u'Sections', 'name': 'geo_section', 'table': 'geo_section', 'geom': 'geom', 'sql': '', 'active': True, 'group': 'C', 'subset': '"geo_commune" IN (%s)'},
            {'label': u'Parcelles', 'name': 'parcelle_info', 'table': 'parcelle_info', 'geom': 'geom', 'sql': '', 'key': 'ogc_fid', 'active': True, 'group': 'C', 'subset': 'substr("geo_parcelle", 1, 10) IN (%s)'},
            {'label': u'Sections (étiquettes)', 'name': 'geo_label_section', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'SECTION_id\'', 'active': False, 'group': 'E'},
            {'label': u'Bornes', 'name': 'geo_borne', 'table': 'geo_borne', 'geom': 'geom', 'sql': '', 'active': False, 'group': 'D'},
            {'label': u'Croix', 'name': 'geo_croix', 'table': 'geo_croix', 'geom': 'geom', 'sql': '', 'active': False, 'group': 'D'},
            {'label': u'Repères géodésiques', 'name': 'geo_ptcanv', 'table': 'geo_ptcanv', 'geom': 'geom', 'sql': '', 'active': False, 'group': 'D'},
            {'label': u'Murs, fossés, clotûres', 'name': 'geo_symblim', 'table': 'geo_symblim', 'geom': 'geom', 'sql': '', 'active': False, 'group': 'D'},
            {'label': u'Cours d\'eau', 'name': 'geo_tronfluv', 'table': 'geo_tronfluv', 'geom': 'geom', 'sql': '', 'active': True, 'group': 'D'},
            {'label': u'Cours d\'eau (étiquettes)', 'name': 'geo_label_tronfluv', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'TRONFLUV_id\'', 'active': True, 'group': 'E'},
            {'label': u'Tronçons de route (étiquettes)', 'name': 'geo_label_tronroute', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'TRONROUTE_id\'', 'active': False, 'group': 'E'},
            {'label': u'Surfaces', 'name': 'geo_tsurf', 'table': 'geo_tsurf', 'geom': 'geom', 'sql': '', 'active': True, 'group': 'D'},
            {'label': u'Surfaces (étiquettes)', 'name': 'geo_label_tsurf', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'TSURF_id\'', 'active': False, 'group': 'E'},
            {'label': u'Objets ponctuels', 'name': 'geo_tpoint', 'table': 'geo_tpoint', 'geom': 'geom', 'sql': '', 'active': False, 'group': 'D'},
            {'label': u'Objets ponctuels (étiquettes)', 'name': 'geo_label_tpoint', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'TPOINT_id\'', 'active': False, 'group': 'E'},
            {'label': u'Objets linéaires', 'name': 'geo_tline', 'table': 'geo_tline', 'geom': 'geom', 'sql': '', 'active': False, 'group': 'D'},
            {'label': u'Objets linéaires (étiquettes)', 'name': 'geo_label_tline', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'TLINE_id\'', 'active': False, 'group': 'E'},
            {'label': u'Numéros de voie', 'name': 'geo_label_num_voie', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'NUMVOIE_id\'', 'active': True, 'group': 'E'},
            {'label': u'Établissements publics', 'name': 'geo_label_voiep', 'table': 'geo_label', 'geom': 'geom', 'sql': '"ogr_obj_lnk_layer" = \'VOIEP_id\'', 'active': True, 'group': 'E'}
            #,
            #{'label': u'Unités foncières', 'name': 'geo_unite_fonciere', 'table': 'geo_unite_fonciere', 'geom':'geom', 'sql': '', 'dbType': 'postgis', 'active': False, 'group': 'D'}
        ]

    def updateTimer(self):
        b = datetime.now()
        diff = b - self.startTime
        self.qc.updateLog(u'%s s' % diff.seconds)

    def getGroupIndex(self, groupName):
        '''
        Get a legend group index by its name
        '''
        relationList = self.dialog.iface.legendInterface().groupLayerRelationship()
        i = 0
        for item in relationList:
            if item[0]:
                if item[0] == groupName:
                    return i
                i = i + 1
        return 0

    def processLoading(self):
        '''
        Load all the layers in QGIS
        and apply corresponding style
        '''
        self.startTime = datetime.now()
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # default style to apply for Cadastre layers
        self.themeDir = unicode(self.dialog.liTheme.currentText())
        if not os.path.exists(os.path.join(
            self.qc.plugin_dir,
            "styles/%s" % self.themeDir
        )):
            self.themeDir = self.defaultThemeDir

        # set Cadastre SVG path if not set
        cadastreSvgPath = os.path.join(
            self.qc.plugin_dir,
            "styles/%s/svg" % self.themeDir
        )
        s = QSettings()
        qgisSvgPaths = s.value("svg/searchPathsForSVG", 10, type=str)
        if not cadastreSvgPath in qgisSvgPaths:
            if qgisSvgPaths:
                qgisSvgPaths = u"%s|%s" % (qgisSvgPaths, cadastreSvgPath)
            else:
                qgisSvgPaths = u"%s" % cadastreSvgPath
            s.setValue("svg/searchPathsForSVG", qgisSvgPaths)
            self.qc.updateLog(u"* Le chemin contenant les SVG du plugin Cadastre a été ajouté dans les options de QGIS")

        # Get selected options
        providerName = self.dialog.dbpluginclass.providerName()
        qgisCadastreLayers = []
        self.dialog.schema = unicode(self.dialog.liDbSchema.currentText())
        self.dialog.totalSteps = len(self.qgisCadastreLayerList)

        # Run the loading
        self.updateTimer()
        self.qc.updateLog(u'Chargement des tables :')

        # Get database list of tables
        if self.dialog.dbType == 'postgis':
            schemaSearch = [s for s in self.dialog.db.schemas() if s.name == self.dialog.schema]
            schemaInst = schemaSearch[0]
            dbTables = self.dialog.db.tables(schemaInst)
        if self.dialog.dbType == 'spatialite':
            dbTables = self.dialog.db.tables()

        # Get commune filter by expression
        communeExpression = self.dialog.communeFilter.text()
        communeFilter = None
        cExp = QgsExpression(communeExpression)
        if not cExp.hasParserError():
            self.qc.updateLog(u'Filtrage à partir des communes : %s' % communeExpression)
            cReq = QgsFeatureRequest(cExp)
            cTableList = [a for a in dbTables if a.name == 'geo_commune']
            cTable = cTableList[0]
            cUniqueCol = 'ogc_fid'
            cSchema = self.dialog.schema
            cGeomCol = 'geom'
            cLayerUri = self.dialog.db.uri()
            cLayerUri.setDataSource(
                cSchema,
                cTable.name,
                cGeomCol,
                '',
                cUniqueCol
            )
            clayer = QgsVectorLayer(cLayerUri.uri(), 'com', providerName)
            cfeatures = clayer.getFeatures( cReq )
            cids = [a['commune'] for a in cfeatures]
            if len(cids):
                communeFilter = cids
        else:
            self.qc.updateLog(u'Filtrage à partir des communes : expression invalide !')


        # Loop throuhg qgisQastreLayerList and load each corresponding table
        for item in self.qgisCadastreLayerList:

            if item['label'] not in self.mainLayers and self.dialog.cbMainLayersOnly.isChecked():
                continue

            if item.has_key('dbType') and item['dbType'] != self.dialog.dbType:
                continue

            # update progress bar
            self.qc.updateLog(u'* %s' % item['label'])
            self.dialog.step+=1
            self.qc.updateProgressBar()

            # Tables - Get db_manager table instance
            tableList = [a for a in dbTables if a.name == item['table']]
            if len(tableList) == 0 and not item.has_key('isView'):
                self.qc.updateLog(u'  - Aucune table trouvée pour %s' % item['label'])
                continue

            if tableList:
                table = tableList[0]
                source = table.name
                uniqueField = table.getValidQGisUniqueFields(True)
                if uniqueField:
                    uniqueCol = uniqueField.name
                else:
                    uniqueCol = 'ogc_fid'

            schema = self.dialog.schema

            # View
            if item.has_key('isView'):
                if self.dialog.dbType == 'spatialite':
                    schemaReplace = ''
                else:
                    schemaReplace = '"%s".' % self.dialog.schema
                source = item['table'].replace('schema.', schemaReplace)
                uniqueCol = item['key']
                schema = None

            sql = item['sql']
            geomCol = item['geom']

            if communeFilter:
                communeFilterText = "'" + "', '".join(communeFilter) + "'"
                nschema = ''
                if self.dialog.dbType == 'postgis':
                    nschema = '"%s".' % schema
                if 'subset' in item:
                    subset = item['subset']
                    sql+= subset % communeFilterText
                else:
                    itemcol = item['table']
                    if item['table'] == 'geo_label':
                        itemcol = 'ogc_fid'
                    subset = itemcol + '''
                         IN (

                            SELECT b.''' + itemcol + '''
                            FROM  ''' + nschema + item['table'] + ''' b
                            JOIN  ''' + nschema + '''geo_commune c
                            ON ST_Within(b.geom, c.geom)
                            WHERE 2>1
                            AND c.geo_commune IN ( %s )

                        )
                    '''
                    if sql:
                        sql+= ' AND '
                    sql+= subset % communeFilterText


            # Create vector layer
            alayerUri = self.dialog.db.uri()
            alayerUri.setDataSource(
                schema,
                source,
                geomCol,
                sql,
                uniqueCol
            )

            vlayer = QgsVectorLayer(alayerUri.uri(), item['label'], providerName)

            # apply style
            qmlPath = os.path.join(
                self.qc.plugin_dir,
                "styles/%s/%s.qml" % (self.themeDir, item['name'])
            )
            if os.path.exists(qmlPath):
                vlayer.loadNamedStyle(qmlPath)

            # append vector layer to the list
            qgisCadastreLayers.append(vlayer)

        self.updateTimer()

        # Get canvas and disable rendering
        from qgis.utils import iface
        canvas = iface.mapCanvas()
        canvas.freeze(True)

        # Add all layers to QGIS registry
        self.qc.updateLog(u'Ajout des couches dans le registre de QGIS')
        QgsMapLayerRegistry.instance().addMapLayers(qgisCadastreLayers)
        self.updateTimer()

        # Create a group "Cadastre" and move all layers into it
        self.qc.updateLog(u'Ajout des couches dans le groupe Cadastre')
        li = self.dialog.iface.legendInterface()
        groups = []
        for group in li.groupLayerRelationship():
            if group[0]:
                groups.append(group[0])
        if u"Cadastre" in groups:
            g1 = self.getGroupIndex(u"Cadastre")
            if not u'Fond' in groups:
                gf = li.addGroup(u'Fond', True, g1)
            else:
                gf = self.getGroupIndex(u'Fond')

            if not u'Étiquettes cadastre' in groups:
                ge = li.addGroup(u'Étiquettes cadastre', True, gf)
            else:
                ge = self.getGroupIndex(u'Étiquettes cadastre')

            if not u'Données cadastre' in groups:
                gd = li.addGroup(u'Données cadastre', True, gf)
            else:
                gd = self.getGroupIndex(u"Données cadastre")
        else:
            g1 = li.addGroup("Cadastre")
            gf = li.addGroup("Fond", True, g1)
            ge = li.addGroup(u'Étiquettes cadastre', True, gf)
            gd = li.addGroup(u'Données cadastre', True, gf)

        for layer in qgisCadastreLayers:
            #~ layer.updateExtents()
            # Get layer options
            qlayer = [ a for a in self.qgisCadastreLayerList if a['label'] == layer.name() ]
            if qlayer:
                qlayer = qlayer[0]

                # Enable/Disable layer
                if not qlayer['active']:
                    li.setLayerVisible(layer, False)

                # Move layer to proper group
                if qlayer['group'] == 'E':
                    li.moveLayer(layer, ge)
                elif qlayer['group'] == 'D':
                    li.moveLayer(layer, gd)
                else:
                    li.moveLayer(layer, g1)
            else:
                # Move layer to Cadastre group
                li.moveLayer(layer, g1)

            # Do not expand layer legend
            li.setLayerExpanded(layer, False)

        # Close Cadastre group
        # li.setGroupExpanded(g1, False)

        self.updateTimer()


        # Zoom to full extent
        self.qc.updateLog(u'Zoom sur les couches')
        canvas.zoomToFullExtent()
        canvas.freeze(False)
        canvas.refresh()
        self.updateTimer()

        # progress bar
        self.dialog.step+=1
        self.qc.updateProgressBar()

        # Emit signal
        self.qc.updateLog(u'Mise à jour des outils cadastre')
        self.cadastreLoadingFinished.emit()
        self.updateTimer()

        # Final message
        QApplication.restoreOverrideCursor()
        QMessageBox.information(
            self.dialog,
            u"Cadastre",
            u"Les données ont bien été chargées dans QGIS"
        )
        self.dialog.pbProcess.setValue(0)


        QApplication.restoreOverrideCursor()

    def loadSqlLayer(self):
        '''
        Load a vector layer from SQL and information given by the user
        '''
        providerName = self.dialog.dbpluginclass.providerName()
        self.dialog.schema = unicode(self.dialog.liDbSchema.currentText())

        sqlText = self.dialog.sqlText.toPlainText()
        if self.dialog.dbType == 'postgis':
            self.dialog.schema = unicode(self.dialog.liDbSchema.currentText())

        geometryColumn = self.dialog.geometryColumn.text()
        if not geometryColumn:
            geometryColumn = None

        layerName = self.dialog.layerName.text()
        if not layerName:
            layerName = 'requete_cadastre_%s' % datetime.now()

        layer = self.dialog.db.toSqlLayer(
            sqlText,
            geometryColumn,
            None,
            layerName,
            QgsMapLayer.VectorLayer,
            False
        )
        if layer.isValid():
            # Add layer to layer tree
            QgsMapLayerRegistry.instance().addMapLayers([layer], True)
        else:
            self.qc.updateLog(u"La couche n'est pas valide et n'a pu être chargée. Pour PostGIS, avez-vous pensé à indiquer le schéma comme préfixe des tables ?" )

