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

import os
import unicodedata

from datetime import datetime

from qgis.core import (
    QgsExpression,
    QgsFeatureRequest,
    QgsLayerTreeLayer,
    QgsMapLayer,
    QgsProject,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QObject, QSettings, Qt, pyqtSignal
from qgis.PyQt.QtWidgets import QApplication, QMessageBox


class CadastreLoading(QObject):
    cadastreLoadingFinished = pyqtSignal()

    def __init__(self, dialog):
        QObject.__init__(self)
        self.dialog = dialog

        self.startTime = datetime.now()

        # Disabled because of an issue in selection with Lizmap Web Client
        # https://github.com/3liz/lizmap-web-client/issues/2985
        self.set_short_names = False

        # common cadastre methods
        self.qc = self.dialog.qc
        self.defaultThemeDir = 'classique'
        self.themeDir = None

        # List of database layers to load in QGIS
        self.mainLayers = [
            'Communes',
            'Sections',
            'Parcelles',
            'Bâti'
        ]
        self.qgisCadastreLayerList = [
            {
                'label': 'Communes',
                'name': 'geo_commune',
                'table': 'geo_commune',
                'geom': 'geom',
                'sql': '',
                'key': 'ogc_fid',
                'active': True,
                'group': 'C',
                'subset': '"geo_commune" IN (%s)',
            },
            {
                'label': 'Tronçons de route',
                'name': 'geo_tronroute',
                'table': 'geo_tronroute',
                'geom': 'geom',
                'sql': '',
                'active': True,
                'group': 'D',
            },
            {
                'label': 'Voies, routes et chemins',
                'name': 'geo_zoncommuni',
                'table': 'geo_zoncommuni',
                'geom': 'geom',
                'sql': '',
                'active': False,
                'group': 'D',
            },
            {
                'label': 'Noms de voies',
                'name': 'geo_label_zoncommuni',
                'table': 'geo_label',
                'geom': 'geom',
                'sql': '"ogr_obj_lnk_layer" IN ( \'ZONCOMMUNI_id\') ',
                'active': True,
                'group': 'E',
            },
            {
                'label': 'Secteurs',
                'name': 'geo_subdsect',
                'table': 'geo_subdsect',
                'geom': 'geom',
                'sql': '',
                'active': True,
                'group': 'D',
            },
            {
                'label': 'Subdivisions fiscales',
                'name': 'geo_subdfisc',
                'table': 'geo_subdfisc',
                'geom': 'geom',
                'sql': '',
                'active': True,
                'group': 'D',
            },
            {
                'label': 'Subdivisions fiscales (étiquette)',
                'name': 'geo_label_subdfisc',
                'table': 'geo_label',
                'geom': 'geom',
                'sql': '"ogr_obj_lnk_layer" = \'SUBDFISC_id\'',
                'active': False,
                'group': 'E',
            },
            {
                'label': 'Bâti',
                'name': 'geo_batiment',
                'table': 'geo_batiment',
                'geom': 'geom',
                'sql': '',
                'active': True,
                'group': 'D',
            },
            {
                'label': 'Parcelles (étiquettes)',
                'name': 'geo_label_parcelle',
                'table': 'geo_label',
                'geom': 'geom',
                'sql': '"ogr_obj_lnk_layer" = \'PARCELLE_id\'',
                'active': True,
                'group': 'E',
            },
            {
                'label': 'Lieux-dits',
                'name': 'geo_lieudit',
                'table': 'geo_lieudit',
                'geom': 'geom',
                'sql': '',
                'active': True,
                'group': 'D',
            },
            {
                'label': 'Lieux-dits  (étiquettes)',
                'name': 'geo_label_lieudit',
                'table': 'geo_label',
                'geom': 'geom',
                'sql': '"ogr_obj_lnk_layer" = \'LIEUDIT_id\'',
                'active': False,
                'group': 'E',
            },
            {
                'label': 'Sections',
                'name': 'geo_section',
                'table': 'geo_section',
                'geom': 'geom',
                'sql': '',
                'key': 'ogc_fid',
                'active': True,
                'group': 'C',
                'subset': '"geo_commune" IN (%s)',
            },
            {
                'label': 'Parcelles',
                'name': 'parcelle_info',
                'table': 'parcelle_info',
                'geom': 'geom',
                'sql': '',
                'key': 'ogc_fid',
                'active': True,
                'group': 'C',
                'subset': 'substr("geo_parcelle", 1, 6) IN (%s)',
            },
            {
                'label': 'Sections (étiquettes)',
                'name': 'geo_label_section',
                'table': 'geo_label',
                'geom': 'geom',
                'sql': '"ogr_obj_lnk_layer" = \'SECTION_id\'',
                'active': False,
                'group': 'E',
            },
            {
                'label': 'Bornes',
                'name': 'geo_borne',
                'table': 'geo_borne',
                'geom': 'geom',
                'sql': '',
                'active': False,
                'group': 'D',
            },
            {
                'label': 'Croix',
                'name': 'geo_croix',
                'table': 'geo_croix',
                'geom': 'geom',
                'sql': '',
                'active': False,
                'group': 'D',
            },
            {
                'label': 'Repères géodésiques',
                'name': 'geo_ptcanv',
                'table': 'geo_ptcanv',
                'geom': 'geom',
                'sql': '',
                'active': False,
                'group': 'D',
            },
            {
                'label': 'Murs, fossés, clotûres',
                'name': 'geo_symblim',
                'table': 'geo_symblim',
                'geom': 'geom',
                'sql': '',
                'active': False,
                'group': 'D',
            },
            {
                'label': 'Cours d\'eau',
                'name': 'geo_tronfluv',
                'table': 'geo_tronfluv',
                'geom': 'geom',
                'sql': '',
                'active': True,
                'group': 'D',
            },
            {
                'label': 'Cours d\'eau (étiquettes)',
                'name': 'geo_label_tronfluv',
                'table': 'geo_label',
                'geom': 'geom',
                'sql': '"ogr_obj_lnk_layer" = \'TRONFLUV_id\'',
                'active': True,
                'group': 'E',
            },
            {
                'label': 'Tronçons de route (étiquettes)',
                'name': 'geo_label_tronroute',
                'table': 'geo_label',
                'geom': 'geom',
                'sql': '"ogr_obj_lnk_layer" = \'TRONROUTE_id\'',
                'active': False,
                'group': 'E',
            },
            {
                'label': 'Surfaces',
                'name': 'geo_tsurf',
                'table': 'geo_tsurf',
                'geom': 'geom',
                'sql': '',
                'active': True,
                'group': 'D'
            },
            {
                'label': 'Surfaces (étiquettes)',
                'name': 'geo_label_tsurf',
                'table': 'geo_label',
                'geom': 'geom',
                'sql': '"ogr_obj_lnk_layer" = \'TSURF_id\'',
                'active': False,
                'group': 'E',
            },
            {
                'label': 'Objets ponctuels',
                'name': 'geo_tpoint',
                'table': 'geo_tpoint',
                'geom': 'geom',
                'sql': '',
                'active': False,
                'group': 'D',
            },
            {
                'label': 'Objets ponctuels (étiquettes)',
                'name': 'geo_label_tpoint',
                'table': 'geo_label',
                'geom': 'geom',
                'sql': '"ogr_obj_lnk_layer" = \'TPOINT_id\'',
                'active': False,
                'group': 'E',
            },
            {
                'label': 'Objets linéaires',
                'name': 'geo_tline',
                'table': 'geo_tline',
                'geom': 'geom',
                'sql': '',
                'active': False,
                'group': 'D',
            },
            {
                'label': 'Objets linéaires (étiquettes)',
                'name': 'geo_label_tline',
                'table': 'geo_label',
                'geom': 'geom',
                'sql': '"ogr_obj_lnk_layer" = \'TLINE_id\'',
                'active': False,
                'group': 'E',
            },
            {
                'label': 'Numéros de voie',
                'name': 'geo_label_num_voie',
                'table': 'geo_label',
                'geom': 'geom',
                'sql': '"ogr_obj_lnk_layer" = \'NUMVOIE_id\'',
                'active': True,
                'group': 'E',
            },
            {
                'label': 'Établissements publics',
                'name': 'geo_label_voiep',
                'table': 'geo_label',
                'geom': 'geom',
                'sql': '"ogr_obj_lnk_layer" = \'VOIEP_id\'',
                'active': True,
                'group': 'E',
            }
            # ,
            # {'label': 'Unités foncières', 'name': 'geo_unite_fonciere', 'table': 'geo_unite_fonciere',
            # 'geom':'geom', 'sql': '', 'dbType': 'postgis', 'active': False, 'group': 'D'}
        ]
        # List of database layers to load in QGIS
        self.variableLayers = {
            'Communes': {'var_key': 'commune', 'unique_field': 'geo_commune'},
            'Sections': {'var_key': 'section', 'unique_field': 'geo_section'},
            'Parcelles': {'var_key': 'parcelle', 'unique_field': 'geo_parcelle'},
        }

    def update_timer(self):
        b = datetime.now()
        diff = b - self.startTime
        self.qc.updateLog(f'{diff.seconds} s')

    def get_group_index(self, group_name):
        """
        Get a legend group index by its name
        """
        relation_list = self.dialog.iface.legendInterface().groupLayerRelationship()
        i = 0
        for item in relation_list:
            if item[0]:
                if item[0] == group_name:
                    return i
                i = i + 1
        return 0

    @staticmethod
    def short_name(name: str) -> str:
        """ Clean layer/group name to build the short name for WMS. """
        nfkd_form = unicodedata.normalize('NFKD', name)
        only_ascii = nfkd_form.encode('ASCII', 'ignore').decode()
        only_ascii = only_ascii.replace('-', '_')
        only_ascii = only_ascii.replace(' ', '_')
        only_ascii = only_ascii.replace("'", '_')
        only_ascii = only_ascii.replace(",", '_')
        only_ascii = only_ascii.replace('(', '')
        only_ascii = only_ascii.replace(')', '')

        only_ascii = only_ascii.strip('_')
        lower_name = only_ascii.lower()
        return lower_name

    def process_loading(self):
        """
        Load all the layers in QGIS
        and apply corresponding style
        """
        self.startTime = datetime.now()
        # noinspection PyUnresolvedReferences
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # default style to apply for Cadastre layers
        self.themeDir = str(self.dialog.liTheme.currentText())
        if not os.path.exists(os.path.join(
                self.qc.plugin_dir,
                f"styles/{self.themeDir}"
        )):
            self.themeDir = self.defaultThemeDir

        # set Cadastre SVG path if not set
        cadastre_svg_path = os.path.join(
            self.qc.plugin_dir,
            f"styles/{self.themeDir}/svg"
        )
        s = QSettings()
        qgis_svg_paths = s.value("svg/searchPathsForSVG", 10, type=str)
        a = list(qgis_svg_paths)
        if cadastre_svg_path not in a:
            a.append(cadastre_svg_path)
            s.setValue("svg/searchPathsForSVG", a)
            self.qc.updateLog("* Le chemin contenant les SVG du plugin Cadastre a été ajouté dans les options de QGIS")

        # Get selected options
        provider_name = self.dialog.dbpluginclass.providerName()
        qgis_cadastre_layers = []
        self.dialog.schema = str(self.dialog.liDbSchema.currentText())
        self.dialog.totalSteps = len(self.qgisCadastreLayerList)

        # Run the loading
        self.update_timer()
        self.qc.updateLog('Chargement des tables :')

        # Get database list of tables
        if self.dialog.dbType == 'postgis':
            schema_search = [s for s in self.dialog.db.schemas() if s.name == self.dialog.schema]
            schema_inst = schema_search[0]
            db_tables = self.dialog.db.tables(schema_inst)
        else:
            db_tables = self.dialog.db.tables()

        # Get commune filter by expression
        commune_expression = self.dialog.communeFilter.text().strip()
        commune_filter = None
        c_exp = QgsExpression(commune_expression)
        if commune_expression != '' and not c_exp.hasParserError():
            self.qc.updateLog(f'Filtrage à partir des communes : {commune_expression}')
            c_req = QgsFeatureRequest(c_exp)
            c_table_list = [a for a in db_tables if a.name == 'geo_commune']
            c_table = c_table_list[0]
            c_unique_col = 'ogc_fid'
            c_schema = self.dialog.schema
            c_geom_col = 'geom'
            c_layer_uri = self.dialog.db.uri()
            c_layer_uri.setDataSource(
                c_schema,
                c_table.name,
                c_geom_col,
                '',
                c_unique_col
            )
            c_layer = QgsVectorLayer(c_layer_uri.uri(), 'com', provider_name)
            c_features = c_layer.getFeatures(c_req)
            c_ids = [a['commune'] for a in c_features]
            if len(c_ids):
                commune_filter = c_ids
        else:
            self.qc.updateLog(f'Filtrage à partir des communes, expression invalide : {c_exp.parserErrorString()}')

        # Loop through qgisCadastreLayerList and load each corresponding table
        for item in self.qgisCadastreLayerList:

            if item['label'] not in self.mainLayers and self.dialog.cbMainLayersOnly.isChecked():
                continue

            if 'dbType' in item and item['dbType'] != self.dialog.dbType:
                continue

            # update progress bar
            self.qc.updateLog(f'* {item["label"]}')
            self.dialog.step += 1
            self.qc.updateProgressBar()

            # Tables - Get db_manager table instance
            table_list = [a for a in db_tables if a.name == item['table']]
            if len(table_list) == 0 and 'isView' not in item:
                self.qc.updateLog(f'  - Aucune table trouvée pour {item["label"]}')
                continue

            source = ''
            unique_col = ''

            if table_list:
                table = table_list[0]
                source = table.name
                # noinspection PyBroadException
                try:
                    unique_field = table.getValidQGisUniqueFields(True)
                    unique_col = unique_field.name
                except Exception:
                    unique_col = 'ogc_fid'

            schema = self.dialog.schema

            # View
            if 'isView' in item:
                if self.dialog.dbType == 'spatialite':
                    schema_replace = ''
                else:
                    schema_replace = f'"{self.dialog.schema}".'
                source = item['table'].replace('schema.', schema_replace)
                unique_col = item['key']
                schema = None

            sql = item['sql']
            geom_col = item['geom']

            if commune_filter:
                commune_filter_text = "'" + "', '".join(commune_filter) + "'"
                ns_schema = ''
                if self.dialog.dbType == 'postgis':
                    ns_schema = f'"{schema}".'
                if 'subset' in item:
                    subset = item['subset']
                    sql += subset % commune_filter_text
                else:
                    item_col = item['table']
                    if item['table'] == 'geo_label':
                        item_col = 'ogc_fid'
                    subset = item_col + '''
                         IN (

                            SELECT b.''' + item_col + '''
                            FROM  ''' + ns_schema + item['table'] + ''' b
                            JOIN  ''' + ns_schema + '''geo_commune c
                            ON ST_Within(b.geom, c.geom)
                            WHERE 2>1
                            AND c.geo_commune IN ( %s )

                        )
                    '''
                    if sql:
                        sql += ' AND '
                    sql += subset % commune_filter_text

            # Create vector layer
            a_layer_uri = self.dialog.db.uri()
            a_layer_uri.setDataSource(
                schema,
                source,
                geom_col,
                sql,
                unique_col
            )

            layer_name = item['label']
            v_layer = QgsVectorLayer(a_layer_uri.uri(), layer_name, provider_name)
            if self.set_short_names:
                v_layer.setShortName(self.short_name(layer_name))

            # apply style
            qml_path = os.path.join(
                self.qc.plugin_dir,
                f"styles/{self.themeDir}/{item['name']}.qml"
            )
            if os.path.exists(qml_path):
                v_layer.loadNamedStyle(qml_path)

            # append vector layer to the list
            qgis_cadastre_layers.append(v_layer)

        self.update_timer()

        # Get canvas and disable rendering
        from qgis.utils import iface
        canvas = iface.mapCanvas()
        canvas.freeze(True)

        # Add all layers to QGIS registry (but not yet to the layer tree)
        self.qc.updateLog('Ajout des couches dans le registre de QGIS')
        QgsProject.instance().addMapLayers(qgis_cadastre_layers, False)
        self.update_timer()

        # Create a group "Cadastre" and move all layers into it
        self.qc.updateLog('Ajout des couches dans le groupe Cadastre')
        root = QgsProject.instance().layerTreeRoot()
        g1 = root.findGroup("Cadastre")
        if g1:
            name = "Fond"
            gf = root.findGroup(name)
            if not gf:
                gf = g1.addGroup(name)
                if self.set_short_names:
                    gf.setCustomProperty("wmsShortName", self.short_name(name))

            name = "Étiquettes cadastre"
            ge = root.findGroup(name)
            if not ge:
                ge = gf.addGroup(name)
                if self.set_short_names:
                    ge.setCustomProperty("wmsShortName", self.short_name(name))

            name = "Données cadastre"
            gd = root.findGroup(name)
            if not gd:
                gd = gf.addGroup(name)
                if self.set_short_names:
                    gd.setCustomProperty("wmsShortName", self.short_name(name))
        else:
            g1 = root.insertGroup(0, "Cadastre")

            name = "Fond"
            gf = g1.addGroup(name)
            if self.set_short_names:
                gf.setCustomProperty("wmsShortName", self.short_name(name))

            name = 'Étiquettes cadastre'
            ge = gf.addGroup(name)
            if self.set_short_names:
                ge.setCustomProperty("wmsShortName", self.short_name(name))

            name = "Données cadastre"
            gd = gf.addGroup(name)
            if self.set_short_names:
                gd.setCustomProperty("wmsShortName", self.short_name(name))

        variables = QgsProject.instance().customVariables()
        for layer in qgis_cadastre_layers:
            # ~ layer.updateExtents()
            # Get layer tree item
            node_layer = QgsLayerTreeLayer(layer)

            # Get layer options
            q_layer = [a for a in self.qgisCadastreLayerList if a['label'] == layer.name()]
            if q_layer:
                q_layer = q_layer[0]

                # Move layer to proper group
                if q_layer['group'] == 'E':
                    ge.insertChildNode(0, node_layer)
                elif q_layer['group'] == 'D':
                    gd.insertChildNode(0, node_layer)
                else:
                    g1.insertChildNode(0, node_layer)

                # Enable/Disable layer
                if not q_layer['active']:
                    # noinspection PyUnresolvedReferences
                    node_layer.setItemVisibilityChecked(Qt.Unchecked)
            else:
                # Move layer to Cadastre group
                g1.insertChildNode(-1, node_layer)

            # Do not expand layer legend
            node_layer.setExpanded(False)

            # set variables
            if layer.name() in self.variableLayers:
                var_layer = self.variableLayers[layer.name()]
                variables['cadastre_' + var_layer['var_key'] + '_layer_id'] = layer.id()
                variables['cadastre_' + var_layer['var_key'] + '_unique_field'] = var_layer['unique_field']

        QgsProject.instance().setCustomVariables(variables)

        self.update_timer()

        # Zoom to full extent
        self.qc.updateLog('Zoom sur les couches')
        canvas.zoomToFullExtent()
        canvas.freeze(False)
        canvas.refresh()
        self.update_timer()

        # progress bar
        self.dialog.step += 1
        self.qc.updateProgressBar()

        # Emit signal
        self.qc.updateLog('Mise à jour des outils cadastre')
        self.cadastreLoadingFinished.emit()
        self.update_timer()

        # Final message
        QApplication.restoreOverrideCursor()
        QMessageBox.information(
            self.dialog,
            "Cadastre",
            "Les données ont bien été chargées dans QGIS"
        )
        self.dialog.pbProcess.setValue(0)

        QApplication.restoreOverrideCursor()

    def load_sql_layer(self):
        """
        Load a vector layer from SQL and information given by the user
        """
        self.dialog.dbpluginclass.providerName()
        self.dialog.schema = str(self.dialog.liDbSchema.currentText())

        sql_text = self.dialog.sqlText.toPlainText()
        if self.dialog.dbType == 'postgis':
            self.dialog.schema = str(self.dialog.liDbSchema.currentText())

        geometry_column = self.dialog.geometryColumn.text()
        if not geometry_column:
            geometry_column = None

        layer_name = self.dialog.layerName.text()
        if not layer_name:
            layer_name = f'requete_cadastre_{datetime.now()}'

        layer = self.dialog.db.toSqlLayer(
            sql_text,
            geometry_column,
            None,
            layer_name,
            QgsMapLayer.VectorLayer,
            # QgsMapLayer.VectorLayer is an equivalent to QgsMapLayerType.VectorLayer since 3.8
            False
        )
        if layer.isValid():
            # Add layer to layer tree
            QgsProject.instance().addMapLayers([layer], True)
            return

        self.qc.updateLog(
            "La couche n'est pas valide et n'a pu être chargée. Pour PostGIS, avez-vous pensé à indiquer le schéma "
            "comme préfixe des tables ?")
