"""
Cadastre - Export method class

This plugins helps users to import the french land registry ('cadastre')
into a database. It is meant to ease the use of the data in QGIs
by providing search tools and appropriate layer symbology.

begin     : 2013-06-11
copyright : (C) 2013, 2019 by 3liz
email     : info@3liz.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

"""
import os
import re
import tempfile

from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Generator, List

from qgis.core import (
    Qgis,
    QgsExpression,
    QgsFeatureRequest,
    QgsFillSymbol,
    QgsLayoutExporter,
    QgsLayoutGridSettings,
    QgsLayoutItemLabel,
    QgsLayoutItemMap,
    QgsLayoutItemPage,
    QgsLayoutMeasurement,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsMapLayer,
    QgsMapSettings,
    QgsMessageLog,
    QgsPrintLayout,
    QgsProject,
    QgsUnitTypes,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QRectF, QSettings, Qt
from qgis.PyQt.QtGui import QFont

import cadastre.cadastre_common_base as cadastre_common


@contextmanager
def _printProgress(self, nb: int) -> Generator[Callable[[int], None], None, None]:
    """ Define a dummy defaultprint progress
    """
    yield (lambda step: None)


class CadastreExport:

    def __init__(self, project: QgsProject, layer: QgsMapLayer, etype: str, comptecommunal: str,
                 geo_parcelle: str = None, target_dir: str = None, for_third_party: bool = False) -> None:

        self.plugin_dir = str(Path(__file__).resolve().parent)

        self.print_parcelle_page = False

        if not hasattr(self, 'mProgress'):
            self.mProgress = _printProgress

        # Store project from context
        self.mProject = project

        # Store an instance of QgsComposition
        self.currentComposition = None

        # Get instance needed for QgsComposition
        self.mInstance = self.getMapInstance()

        # type of export : proprietaire or parcelle
        self.etype = etype

        # third party export
        # If true, remove some sensitive fields
        # For example date and location of birth
        self.for_third_party = for_third_party

        # id of the parcelle
        self.geo_parcelle = geo_parcelle

        # memory layer for redlining
        self.redlineLayer = None

        self.ccFilter = None

        if isinstance(comptecommunal, list):
            self.isMulti = True
            comptecommunal = list(set(comptecommunal))
            if len(comptecommunal) == 1:
                self.isMulti = False
                comptecommunal = comptecommunal[0].strip(" '")
        else:
            self.isMulti = False

        self.comptecommunal = comptecommunal

        self.maxLineNumber = 15  # max number of line per main table
        self.numPages = 1
        self.pageHeight = 210
        self.pageWidth = 297
        self.printResolution = 300

        # target directory for saving
        s = QSettings()
        tempDir = s.value("cadastre/tempDir", '%s' % tempfile.gettempdir(), type=str)
        if not tempDir or not os.path.exists(tempDir):
            tempDir = tempfile.gettempdir()
        if not target_dir or not os.path.exists(target_dir):
            self.targetDir = tempfile.mkdtemp('', 'cad_export_', tempDir)
        else:
            self.targetDir = target_dir

        # label for header2
        if self.etype == 'proprietaire':
            self.typeLabel = u'DE PROPRIÉTÉ'
        else:
            self.typeLabel = u'PARCELLAIRE'

        self.layer = layer
        self.connectionParams = cadastre_common.getConnectionParameterFromDbLayer(self.layer)
        self.connector = cadastre_common.getConnectorFromUri(self.connectionParams)
        self.dbType = self.connectionParams['dbType']

        # Variable created in set_composer_templates
        self.main_tables = {}

    def getMapInstance(self) -> QgsMapSettings:
        """
        Get instance of object needed to instantiate QgsComposition
        QgsMapRenderer or QgsMapSettings
        Different if context is server
        """
        return QgsMapSettings()

    def set_composer_templates(self, compte_communal):
        """
        Set parameters for given comptecommunal
        """
        # List of templates
        compte_communal_abrev = compte_communal[9:]
        self.composerTemplates = {
            'header1': {
                'names': ['annee', 'ccodep', 'ccodir', 'ccocom', 'libcom'],
                'position': [3.5, 2.5, 145, 7.5], 'align': [128, 4],
                'keepContent': True,
                'type': 'sql',
                'filter': 'comptecommunal',
                'and': {
                    'proprietaire': " AND comptecommunal = '{}'".format(compte_communal),
                    'parcelle': " AND comptecommunal = '{}'".format(compte_communal),
                },
                'sticky': True
            },
            'header2': {
                'names': ['type'],
                'position': [153.5, 2.5, 60, 7.5], 'align': [128, 4],
                'keepContent': True,
                'type': 'properties',
                'source': [self.typeLabel],
                'sticky': True
            },
            'header3': {
                'names': ['comptecommunal'],
                'position': [218.5, 2.5, 75, 7.5], 'align': [128, 2],
                'keepContent': True,
                'type': 'properties',
                'source': [compte_communal_abrev],
                'sticky': True
            },
            'proprietaires': {
                'names': ['lines'],
                'position': [3.5, 10, 290, 40], 'align': [32, 1],
                'keepContent': False,
                'type': 'parent',
                'source': 'proprietaires_line'
            },
            'proprietes_baties': {
                'names': ['lines'],
                'position': [3.5, 50, 290, 65], 'align': [32, 1],
                'keepContent': False,
                'type': 'parent',
                'source': 'proprietes_baties_line'
            },
            'proprietes_baties_sum': {
                'names': ['revenucadastral', 'co_vlbaia', 'co_bipevla', 'gp_vlbaia', 'gp_bipevla', 'de_vlbaia',
                          'de_bipevla', 're_vlbaia', 're_bipevla'],
                'position': [3.5, 115, 290, 15], 'align': [32, 1],
                'type': 'sql',
                'keepContent': True,
                'filter': 'comptecommunal',
                'and': {
                    'proprietaire': " AND l10.comptecommunal = '{}'".format(compte_communal),
                    'parcelle': " AND p.parcelle = '{}'".format(self.geo_parcelle)
                }
            },
            'proprietes_non_baties': {
                'names': ['lines'],
                'position': [3.5, 130, 290, 65], 'align': [32, 1],
                'keepContent': False,
                'type': 'parent',
                'source': 'proprietes_non_baties_line'
            },
            'proprietes_non_baties_sum': {
                'names': ['sum_ha_contenance', 'sum_a_contenance', 'sum_ca_contenance', 'sum_drcsuba'],
                'position': [3.5, 195, 290, 13], 'align': [32, 1],
                'type': 'sql',
                'keepContent': True,
                'filter': 'comptecommunal',
                'and': {
                    'proprietaire': " AND p.comptecommunal = '{}'".format(compte_communal),
                    'parcelle': " AND p.parcelle = '{}'".format(self.geo_parcelle)
                },
                'bgcolor': Qt.transparent
            },
            'footer': {
                'names': ['foot'],
                'position': [3.5, 208, 288, 4], 'align': [128, 4],
                'keepContent': True,
                'type': 'properties',
                'source': ["Ce document est donné à titre indicatif - Il n'a pas de valeur légale"],
                'bgcolor': Qt.white,
                'htmlState': 0,
                'font': QFont('sans-serif', 4, 1, True),
                'sticky': True
            }
        }
        self.main_tables = {
            'proprietaires_line': {
                'names': ['mainprop', 'epousede', 'adrprop', 'nele'],
                'type': 'sql',
                'keepContent': True,
                'filter': 'comptecommunal',
                'and': {
                    'proprietaire': " AND comptecommunal = '{}'".format(compte_communal),
                    'parcelle': " AND comptecommunal = '{}'".format(compte_communal)
                }
            },
            'proprietes_baties_line': {
                'names': ['section', 'ndeplan', 'ndevoirie', 'adresse', 'coderivoli', 'bat', 'ent', 'niv', 'ndeporte',
                          'numeroinvar', 'star', 'meval', 'af', 'natloc', 'cat', 'revenucadastral', 'coll', 'natexo',
                          'anret', 'andeb', 'fractionrcexo', 'pourcentageexo', 'txom', 'coefreduc'],
                'type': 'sql',
                'filter': 'comptecommunal',
                'and': {
                    'proprietaire': " AND l10.comptecommunal = '{}'".format(compte_communal),
                    'parcelle': " AND p.parcelle = '{}'".format(self.geo_parcelle)
                }
            },
            'proprietes_non_baties_line': {
                'names': ['section', 'ndeplan', 'ndevoirie', 'adresse', 'coderivoli', 'nparcprim', 'fpdp', 'star',
                          'suf', 'grssgr', 'cl', 'natcult', 'ha_contenance', 'a_contenance', 'ca_contenance',
                          'revenucadastral', 'coll', 'natexo', 'anret', 'fractionrcexo', 'pourcentageexo', 'tc', 'lff'],
                'type': 'sql',
                'and': {
                    'proprietaire': " AND p.comptecommunal = '{}'".format(compte_communal),
                    'parcelle': " AND p.parcelle = '{}'".format(self.geo_parcelle)
                }
            }

        }

        # items for which to count number of lines
        self.lineCount = {
            'proprietes_baties_line': {'count': 0, 'data': None},
            'proprietes_non_baties_line': {'count': 0, 'data': None}
        }

        # items for which not the run a query for each page
        # but only once and keep content for next pages
        self.contentKeeped = {}
        for key, item in list(self.composerTemplates.items()):
            if 'keepContent' in item and item['keepContent']:
                self.contentKeeped[key] = ''
        for key, item in list(self.main_tables.items()):
            if 'keepContent' in item and item['keepContent']:
                self.contentKeeped[key] = ''

    def getContentForGivenItem(self, key, item, page=None):
        """
        Take content from template file
        corresponding to the key
        and assign data from item
        """
        # First check previous stored content
        if 'keepContent' in item and item['keepContent'] \
                and self.contentKeeped[key]:
            return self.contentKeeped[key]

        content = ''
        replaceDict = ''

        # Build template file path
        tplPath = os.path.join(
            self.plugin_dir,
            "templates",
            "%s.tpl" % key
        )

        # Build replace dict depending on source type
        if item['type'] == 'sql':
            data = None

            # Load SQL query and get data
            # Get sql file
            sqlFile = tplPath + '.sql'
            fin = open(sqlFile, 'rt', encoding='utf8')
            sql = fin.read()
            fin.close()

            # Add schema to search_path if postgis
            if self.dbType == 'postgis':
                sql = sql.replace('$schema', '"{}".'.format(self.connectionParams['schema']))
            else:
                sql = sql.replace('$schema', '')

            # Add the for_third_party values
            # only useful for proprietaire
            # to empty sensitive data (date and location of birth)
            sql = sql.replace('$for_third_party', str(self.for_third_party))

            # Add where clause depending on etype
            sql = sql.replace('$and', item['and'][self.etype])

            # Limit results if asked
            if page and key in self.main_tables.keys() and key in self.lineCount.keys():
                offset = int((page - 1) * self.maxLineNumber)
                # ~ sql+= " LIMIT %s" % self.maxLineNumber
                # ~ sql+= " OFFSET %s" % offset
                # Get data from previous fetched full data
                data = self.lineCount[key]['data'][offset:self.maxLineNumber + offset]

            # Convert PostgreSQL syntax to SQLite
            if self.dbType == 'spatialite':
                sql = cadastre_common.postgisToSpatialite(sql)

            # Run SQL only if data has not already been defined
            if data is None:
                # print(sql)
                data, rowCount, ok = cadastre_common.fetchDataFromSqlQuery(self.connector, sql)

            # Page no defined = means the query is here to
            # get line count and whole data for proprietes_baties & proprietes_non_baties
            if not page:
                if key in list(self.lineCount.keys()):
                    # line count
                    self.lineCount[key]['count'] = rowCount
                    # keep data
                    self.lineCount[key]['data'] = data
            if page:
                # Get content for each line of data
                for line in data:
                    replaceDict = {}
                    for i in range(len(item['names'])):
                        replaceDict['$%s' % item['names'][i]] = u'%s' % line[i]
                    content += self.getHtmlFromTemplate(tplPath, replaceDict)

                # fill empty data to have full size table
                if key in self.main_tables.keys() and key not in self.contentKeeped.keys() \
                        and len(data) < self.maxLineNumber:
                    for _ in range(self.maxLineNumber - len(data)):
                        replaceDict = {}
                        for i in range(len(item['names'])):
                            replaceDict['$%s' % item['names'][i]] = u'&nbsp;'
                        content += self.getHtmlFromTemplate(tplPath, replaceDict)

        elif item['type'] == 'properties':
            # build replace dict from properties
            replaceDict = {}
            for i in range(len(item['names'])):
                replaceDict['$' + item['names'][i]] = item['source'][i]
            content = self.getHtmlFromTemplate(tplPath, replaceDict)

        elif item['type'] == 'parent':
            replaceDict = {}
            for i in range(len(item['names'])):
                replaceDict['$' + item['names'][i]] = self.main_tables[item['source']]['content']
            content = self.getHtmlFromTemplate(tplPath, replaceDict)

        # Keep somme content globally
        if 'keepContent' in item and item['keepContent']:
            self.contentKeeped[key] = content

        # replace some unwanted content
        content = content.replace('None', '')
        return content

    def getHtmlFromTemplate(self, tplPath, replaceDict):
        """
        Get the content of a template file
        and replace all variables with given data
        """

        def replfunc(match):
            return replaceDict[match.group(0)]

        regex = re.compile('|'.join(re.escape(x) for x in replaceDict))

        try:
            with open(tplPath, 'rt', encoding='utf8') as fin:
                data = fin.read()
            data = regex.sub(replfunc, data)
            return data

        except IOError as e:
            msg = u"Erreur lors de l'export: %s" % e
            self.go = False
            # fix_print_with_import
            print("%s" % msg)
            return msg

    def createComposition(self):
        """
        Create a print Layout
        """
        c = QgsPrintLayout(self.mProject)
        c.initializeDefaults()
        c.setUnits(QgsUnitTypes.LayoutMillimeters)

        g = QgsLayoutGridSettings(c)
        g.setOffset(QgsLayoutPoint(3.5, 0, QgsUnitTypes.LayoutMillimeters))
        g.setResolution(QgsLayoutMeasurement(2.5))

        # Set page number
        self.getPageNumberNeeded()
        # Set main properties
        for i in range(1, self.numPages):
            p = QgsLayoutItemPage(c)
            # page.setPageSize('A6')
            p.setPageSize(QgsLayoutSize(self.pageWidth, self.pageHeight, QgsUnitTypes.LayoutMillimeters))
            c.pageCollection().addPage(p)

        # Set the global currentComposition
        self.currentComposition = c

    def getPageNumberNeeded(self):
        """
        Calculate the minimum pages
        needed to fit all the data
        """
        # retrieve total data and get total count
        for key in list(self.lineCount.keys()):
            self.getContentForGivenItem(key, self.main_tables[key])
        self.numPages = max(
            [
                1 + int(self.lineCount['proprietes_baties_line']['count'] / self.maxLineNumber),
                1 + int(self.lineCount['proprietes_non_baties_line']['count'] / self.maxLineNumber)
            ]
        )

        # Add a page for map if etype == parcelle
        if self.etype == 'parcelle' and self.print_parcelle_page:
            self.numPages += 1

    def addPageContent(self, page):
        """
        Add all needed item for a single page
        """

        # First get content for parent items
        for key, item in list(self.main_tables.items()):
            self.main_tables[key]['content'] = self.getContentForGivenItem(
                key,
                item,
                page
            )

        # Then get content for displayed items
        for key, item in list(self.composerTemplates.items()):
            self.buildComposerLabel(key, item, page)

    def buildComposerLabel(self, key, item, page):
        """
        Add a label to the print layout for an item and page
        """
        cl = QgsLayoutItemLabel(self.currentComposition)

        # 1st page is a map for parcelle
        dpage = page - 1
        if self.etype == 'parcelle' and self.print_parcelle_page:
            dpage = page

        cl.attemptMove(
            QgsLayoutPoint(
                item['position'][0],
                item['position'][1] + (dpage) * (self.pageHeight + 10),
                QgsUnitTypes.LayoutMillimeters
            )
        )
        cl.setFixedSize(
            QgsLayoutSize(
                item['position'][2],
                item['position'][3],
                QgsUnitTypes.LayoutMillimeters
            )
        )

        cl.setVAlign(item['align'][0])
        cl.setHAlign(item['align'][1])
        content = self.getContentForGivenItem(
            key,
            item,
            page
        )

        cl.setMargin(0)
        cl.setMode(1)
        cl.setText(content)
        cl.setFrameEnabled(False)
        if 'bgcolor' in item:
            cl.setBackgroundColor(item['bgcolor'])
        if 'htmlState' in item:
            cl.setMode(item['htmlState'])
        if 'font' in item:
            cl.setFont(item['font'])

        self.currentComposition.addLayoutItem(cl)

    def addParcelleMap(self):
        """
        Add content in the first page
        with a map and basic information
        """
        # First add headers
        for key, item in list(self.composerTemplates.items()):
            if 'sticky' in item:
                self.buildComposerLabel(key, item, 0)

        # Get feature extent
        exp = QgsExpression('"geo_parcelle" = \'%s\'' % self.geo_parcelle)
        request = QgsFeatureRequest(exp)
        extent = None
        features = self.layer.getFeatures(request)
        for feature in features:
            geom = feature.geometry()
            peri = geom.length()
            buf = peri / 20
            extent = geom.buffer(buf, 5).boundingBox()

        # Add memory layer to highlight parcelle
        if extent:
            if self.redlineLayer:
                self.mProject.removeMapLayer(self.redlineLayer.id())
            crs = self.layer.crs().authid()
            vl = QgsVectorLayer("Polygon?crs=" + crs, "temporary", "memory")
            pr = vl.dataProvider()
            vl.startEditing()
            pr.addFeatures([f for f in self.layer.getFeatures(request)])
            vl.commitChanges()
            vl.updateExtents()
            props = vl.renderer().symbol().symbolLayer(0).properties()
            props['outline_width'] = u'1'
            props['outline_color'] = u'0,85,255,255'
            props['outline_style'] = u'solid'
            props['style'] = u'no'
            vl.renderer().setSymbol(QgsFillSymbol.createSimple(props))
            self.mProject.addMapLayer(vl)
            self.redlineLayer = vl

        # Add composer map & to parcelle
        miLayers = self.mInstance.layers()
        miLayers.insert(0, vl)
        cm = QgsLayoutItemMap(self.currentComposition)
        cm.updateBoundingRect()
        cm.setRect(QRectF(0, 0, 286, 190))
        cm.setPos(6, 15)
        cm.setLayers(self.mProject.mapThemeCollection().masterVisibleLayers())

        if extent:
            cm.zoomToExtent(extent)

        cm.setFrameEnabled(True)
        cm.setBackgroundEnabled(True)
        self.currentComposition.addItem(cm)

    def exportItemAsPdf(self, comptecommunal, suffix=None) -> str:
        """
        Export one PDF file using the template composer
        filled with appropriate data
        for one "compte communal"
        """
        temppath = None
        # print("export pour le cc %s" % comptecommunal)
        # Set configuration
        self.set_composer_templates(comptecommunal)

        # Create the composition
        self.createComposition()

        if self.currentComposition:
            # Populate composition for all pages
            # print("numpage %s" % self.numPages)
            for i in range(self.numPages):
                j = i + 1
                self.addPageContent(j)

            # Add map in first page if export parcelle
            if self.etype == 'parcelle' and self.print_parcelle_page:
                self.addParcelleMap()

            # Create the pdf output path
            from time import time
            temp = "releve_%s_%s_%s.pdf" % (
                self.etype,
                comptecommunal.replace('+', 'plus').replace('*', 'fois'),  # .replace('¤', 'plus'),
                int(time() * 100)
            )
            # Create regexp to remove all non ascii chars
            import re
            r = re.compile(r"[^ -~]")
            temp = r.sub('', temp)
            # print temp
            temppath = os.path.join(self.targetDir, temp)
            temppath = os.path.normpath(temppath)
            QgsMessageLog.logMessage('Export PDF vers {}'.format(temppath), 'cadastre', Qgis.Info)
            # print("export temppath %s" % temppath)

            # Export as pdf
            exportersettings = QgsLayoutExporter.PdfExportSettings()
            exportersettings.dpi = 300
            exportersettings.forceVectorOutput = True
            exportersettings.rasterizeWholeImage = False
            exporter = QgsLayoutExporter(self.currentComposition)
            exporter.exportToPdf(temppath, exportersettings)

            # Remove redline layer
            if self.redlineLayer:
                self.mProject.removeMapLayer(self.redlineLayer.id())

        return temppath

    def export_as_pdf(self) -> List:
        """
        Run the PDF export
        """
        paths = []
        # Export as many pdf as compte communal
        if self.isMulti:
            nb = len(self.comptecommunal)
            with self.mProgress(self, nb=nb) as printProgress:
                printStep = 0
                # Export PDF for each compte
                for comptecommunal in self.comptecommunal:
                    # export as PDF
                    comptecommunal = comptecommunal.strip("' ")
                    apath = self.exportItemAsPdf(comptecommunal)
                    if apath:
                        paths.append(apath)

                    printStep += 1
                    printProgress(printStep)
        else:
            apath = self.exportItemAsPdf(self.comptecommunal)
            if apath:
                paths.append(apath)
        return paths
