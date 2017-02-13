# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Cadastre - Export method class
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

# TODO
# * Utiliser une seule requête et non plusieurs requêtes avec des offset -> long si nb parcelle grand


import csv, sys
import subprocess
import os.path
import operator
import tempfile
import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from cadastre_dialogs import cadastre_common

try:
    from qgis.utils import iface
except:
    iface = None
    pass


class cadastreExport(QObject):

    def __init__(self, layer, etype, comptecommunal, geo_parcelle=None):

        self.plugin_dir = os.path.dirname(__file__)
        self.iface = iface

        # Store an instance of QgsComposition
        self.currentComposition = None

        # Get instance needed for QgsComposition
        self.getMapInstance()

        # type of export : proprietaire or parcelle
        self.etype = etype

        # id of the parcelle
        self.geo_parcelle = geo_parcelle

        # memory layer for redlining
        self.redlineLayer = None

        self.ccFilter = None

        if isinstance(comptecommunal, list):
            self.isMulti = True
            if len(comptecommunal) == 1:
                self.isMulti = False
                comptecommunal = comptecommunal[0].strip(" '")
        else:
            self.isMulti = False

        self.comptecommunal = comptecommunal

        self.maxLineNumber = 15 # max number of line per main table
        self.numPages = 1
        self.pageHeight = 210
        self.pageWidth = 297
        self.printResolution = 300
        self.addExperimentalWatershed = False

        # target directory for saving
        s = QSettings()
        tempDir = s.value("cadastre/tempDir", '%s' % tempfile.gettempdir(), type=str)
        self.targetDir = tempfile.mkdtemp('', 'cad_export_', tempDir)

        # label for header2
        if self.etype == 'proprietaire':
            self.typeLabel = u'DE PROPRIÉTÉ'
        else:
            self.typeLabel = u'PARCELLAIRE'

        self.layer = layer
        self.connectionParams = cadastre_common.getConnectionParameterFromDbLayer(self.layer)
        self.connector = cadastre_common.getConnectorFromUri(self.connectionParams)
        self.dbType = self.connectionParams['dbType']


    def getMapInstance(self):
        '''
        Get instance of object needed to instantiate QgsComposition
        QgsMapRenderer or QgsMapSettings
        Different if context is server
        '''

        # Store an instance of QgsMapRenderer or QgsMapSettings
        # to avoid a nasty bug with 2.4 :
        # https://github.com/3liz/QgisCadastrePlugin/issues/36
        if QGis.QGIS_VERSION_INT < 20400:
            if self.iface:
                self.mInstance = self.iface.mapCanvas().mapRenderer()
            else:
                self.mInstance = QgsMapRenderer()
        else:
            if self.iface:
                self.mInstance = self.iface.mapCanvas().mapSettings()
            else:
                self.mInstance = QgsMapSettings()

    def setComposerTemplates(self, comptecommunal):
        '''
        Set parameters for given comptecommunal
        '''

        # List of templates
        comptecommunalAbrev = comptecommunal[9:]
        self.composerTemplates = {
            'header1' : {
                'names': ['annee', 'ccodep', 'ccodir', 'ccocom', 'libcom'],
                'position': [3.5, 2.5, 145, 7.5], 'align': [ 128, 4],
                'keepContent' : True,
                'type': 'sql',
                'filter': 'comptecommunal',
                'and': {
                    'proprietaire': u" AND comptecommunal = '%s'" % comptecommunal,
                    'parcelle': u" AND comptecommunal = '%s'" % comptecommunal
                },
                'sticky': True
            },
            'header2' : {
                'names': ['type'],
                'position': [153.5, 2.5, 60, 7.5], 'align': [ 128, 4],
                'keepContent' : True,
                'type': 'properties',
                'source': [self.typeLabel],
                'sticky': True
            },
            'header3' : {
                'names': ['comptecommunal'],
                'position': [218.5, 2.5, 75, 7.5], 'align': [ 128, 2],
                'keepContent' : True,
                'type': 'properties',
                'source': [comptecommunalAbrev],
                'sticky': True
            },
            'proprietaires' : {
                'names': ['lines'],
                'position': [3.5, 10, 290, 40], 'align': [ 32, 1],
                'keepContent' : False,
                'type': 'parent',
                'source': 'proprietaires_line'
            },
            'proprietes_baties' : {
                'names': ['lines'],
                'position': [3.5, 50, 290, 65], 'align': [ 32, 1],
                'keepContent' : False,
                'type': 'parent',
                'source': 'proprietes_baties_line'
            },
            'proprietes_baties_sum' : {
                'names': ['revenucadastral', 'co_vlbaia', 'co_bipevla', 'gp_vlbaia', 'gp_bipevla', 'de_vlbaia', 'de_bipevla', 're_vlbaia', 're_bipevla'],
                'position': [3.5, 115, 290, 15], 'align': [ 32, 1],
                'type': 'sql',
                'keepContent' : True,
                'filter': 'comptecommunal',
                'and': {
                    'proprietaire': u" AND l10.comptecommunal = '%s'" % comptecommunal,
                    'parcelle': u" AND p.parcelle = '%s'" % self.geo_parcelle
                }
            },
            'proprietes_non_baties' : {
                'names': ['lines'],
                'position': [3.5, 130, 290, 65], 'align': [ 32, 1],
                'keepContent' : False,
                'type': 'parent',
                'source': 'proprietes_non_baties_line'
            },
            'proprietes_non_baties_sum' : {
                'names': ['sum_ha_contenance', 'sum_a_contenance', 'sum_ca_contenance', 'sum_drcsuba'],
                'position': [3.5, 195, 290, 13], 'align': [ 32, 1],
                'type': 'sql',
                'keepContent' : True,
                'filter': 'comptecommunal',
                'and': {
                    'proprietaire': u" AND p.comptecommunal = '%s'" % comptecommunal,
                    'parcelle': u" AND p.parcelle = '%s'" % self.geo_parcelle
                },
                'bgcolor': Qt.transparent
            },
            'footer' : {
                'names': ['foot'],
                'position': [3.5, 208, 288, 4], 'align': [ 128, 4],
                'keepContent' : True,
                'type': 'properties',
                'source': [u"Ce document est donné à titre indicatif - Il n'a pas de valeur légale"],
                'bgcolor' : Qt.white,
                'htmlState' : 0,
                'font': QFont('sans-serif', 4, 1, True),
                'sticky': True
            }
        }
        self.mainTables = {
            'proprietaires_line' : {
                'names': ['mainprop', 'epousede', 'adrprop','nele'],
                'type': 'sql',
                'keepContent': True,
                'filter': 'comptecommunal',
                'and': {
                    'proprietaire': u" AND comptecommunal = '%s'" % comptecommunal,
                    'parcelle': u" AND comptecommunal = '%s'" % comptecommunal
                }
            },
            'proprietes_baties_line' : {
                'names': ['section', 'ndeplan', 'ndevoirie', 'adresse', 'coderivoli', 'bat', 'ent', 'niv', 'ndeporte', 'numeroinvar', 'star', 'meval', 'af', 'natloc', 'cat', 'revenucadastral', 'coll', 'natexo', 'anret', 'andeb', 'fractionrcexo', 'pourcentageexo', 'txom', 'coefreduc'],
                'type': 'sql',
                'filter': 'comptecommunal',
                'and': {
                    'proprietaire': u" AND l10.comptecommunal = '%s'" % comptecommunal,
                    'parcelle': u" AND p.parcelle = '%s'" % self.geo_parcelle
                }
            },
            'proprietes_non_baties_line' : {
                'names': ['section', 'ndeplan', 'ndevoirie', 'adresse', 'coderivoli', 'nparcprim', 'fpdp', 'star', 'suf', 'grssgr', 'cl', 'natcult', 'ha_contenance', 'a_contenance', 'ca_contenance', 'revenucadastral', 'coll', 'natexo', 'anret', 'fractionrcexo', 'pourcentageexo', 'tc', 'lff'],
                'type': 'sql',
                'and': {
                    'proprietaire': u" AND p.comptecommunal = '%s'" % comptecommunal,
                    'parcelle': u" AND p.parcelle = '%s'" % self.geo_parcelle
                }
            }

        }

        # items for which to count number of lines
        self.lineCount = {
            'proprietes_baties_line': {'count' : 0, 'data' : None},
            'proprietes_non_baties_line': {'count' : 0, 'data' : None}
        }

        # items for which not the run a query for each page
        # but only once and keep content for next pages
        self.contentKeeped = {}
        for key, item in self.composerTemplates.items():
            if item.has_key('keepContent') and item['keepContent']:
                self.contentKeeped[key] = ''
        for key, item in self.mainTables.items():
            if item.has_key('keepContent') and item['keepContent']:
                self.contentKeeped[key] = ''

    def getContentForGivenItem(self, key, item, page=None):
        '''
        Take content from template file
        corresponding to the key
        and assign data from item
        '''
        # First check previous stored content
        if item.has_key('keepContent') and item['keepContent'] \
         and self.contentKeeped[key]:
            return self.contentKeeped[key]

        content = ''
        replaceDict = ''
        # Build template file path
        tplPath = os.path.join(
            self.plugin_dir,
            "templates/%s.tpl" % key
        )

        # Build replace dict depending on source type
        if item['type'] == 'sql':
            data = None

            # Load SQL query and get data
            # Get sql file
            sqlFile = tplPath + '.sql'
            fin = open(sqlFile)
            sql = fin.read().decode('utf-8')
            fin.close()

            # Add schema to search_path if postgis
            if self.dbType == 'postgis':
                sql = cadastre_common.setSearchPath(sql, self.connectionParams['schema'])
            # Add where clause depending on etype
            sql = sql.replace('$and', item['and'][self.etype] )

            # Limit results if asked
            if page and key in self.mainTables.keys() \
            and key in self.lineCount.keys():
                offset = int((page- 1) * self.maxLineNumber)
                #~ sql+= " LIMIT %s" % self.maxLineNumber
                #~ sql+= " OFFSET %s" % offset
                # Get data from previous fetched full data
                data = self.lineCount[key]['data'][offset:self.maxLineNumber+offset]

            # Run SQL
            if self.dbType == 'spatialite':
                sql = cadastre_common.postgisToSpatialite(sql)
            # Run SQL only if data has not already been defined
            if data is None:
                #~ print sql
                [header, data, rowCount, ok] = cadastre_common.fetchDataFromSqlQuery(self.connector, sql)


            # Page no defined = means the query is here to
            # get line count and whole data for proprietes_baties & proprietes_non_baties
            if not page:
                if key in self.lineCount.keys():
                    # line count
                    self.lineCount[key]['count'] = rowCount
                    # keep data
                    self.lineCount[key]['data'] = data

            if page:
                # Get content for each line of data
                for line in data:
                    replaceDict = {}
                    for i in range(len(item['names'])):
                        replaceDict['$%s' % item['names'][i] ] = u'%s' % line[i]
                    content+= self.getHtmlFromTemplate(tplPath, replaceDict)

                # fill empty data to have full size table
                if key in self.mainTables.keys() \
                and key not in self.contentKeeped.keys() \
                and len(data) < self.maxLineNumber:
                    for l in range(self.maxLineNumber - len(data)):
                        replaceDict = {}
                        for i in range(len(item['names'])):
                            replaceDict['$%s' % item['names'][i] ] = u'&nbsp;'
                        content+= self.getHtmlFromTemplate(tplPath, replaceDict)

        elif item['type'] == 'properties':
            # build replace dict from properties
            replaceDict = {}
            for i in range(len(item['names'])):
                replaceDict['$' + item['names'][i]] = item['source'][i]
            content = self.getHtmlFromTemplate(tplPath, replaceDict)

        elif item['type'] == 'parent':
            replaceDict = {}
            for i in range(len(item['names'])):
                replaceDict['$' + item['names'][i]] = self.mainTables[ item['source'] ]['content']
            content = self.getHtmlFromTemplate(tplPath, replaceDict)

        # Keep somme content globally
        if item.has_key('keepContent') and item['keepContent']:
            self.contentKeeped[key] = content

        # replace some unwanted content
        content = content.replace('None', '')

        return content


    def getHtmlFromTemplate(self, tplPath, replaceDict):
        '''
        Get the content of a template file
        and replace all variables with given data
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)

        def replfunc(match):
            return replaceDict[match.group(0)]
        regex = re.compile('|'.join(re.escape(x) for x in replaceDict))

        try:
            fin = open(tplPath)
            data = fin.read().decode('utf-8')
            fin.close()
            data = regex.sub(replfunc, data)
            return data

        except IOError, e:
            msg = u"Erreur lors de l'export: %s" % e
            self.go = False
            print "%s" % msg
            return msg

        finally:
            QApplication.restoreOverrideCursor()


    def createComposition(self):
        '''
        Create a composition
        '''
        # Create composition
        c = QgsComposition(self.mInstance)

        # Set main properties
        c.setPaperSize(self.pageWidth, self.pageHeight)
        c.setPrintResolution(self.printResolution)
        c.setSnapGridOffsetX(3.5)
        c.setSnapGridOffsetY(0)
        c.setSnapGridResolution(2.5)

        # Set page number
        self.getPageNumberNeeded()
        c.setNumPages(self.numPages)

        # Set plot style if map added
        if self.etype == 'parcelle':
            c.setPlotStyle(QgsComposition.Print)

        self.currentComposition = c


    def getPageNumberNeeded(self):
        '''
        Calculate the minimum pages
        needed to fit all the data
        '''
        # retrieve total data and get total count
        for key in self.lineCount.keys():
            self.getContentForGivenItem(key, self.mainTables[key])
        self.numPages = max(
            [
            1 + int(self.lineCount['proprietes_baties_line']['count'] / self.maxLineNumber),
            1 + int(self.lineCount['proprietes_non_baties_line']['count'] / self.maxLineNumber)
            ]
        )

        # Add a page for map if etype == parcelle
        if self.etype == 'parcelle' and self.iface:
            self.numPages+=1


    def addPageContent(self, page):
        '''
        Add all needed item for a single page
        '''

        # First get content for parent items
        for key, item in self.mainTables.items():
            self.mainTables[key]['content'] = self.getContentForGivenItem(
                key,
                item,
                page
            )

        # Then get content for displayed items
        for key, item in self.composerTemplates.items():
            self.buildComposerLabel(key,item,page)


        # Add watershed
        if self.addExperimentalWatershed:
            w = QgsComposerPicture(self.currentComposition)
            w.setItemPosition(50, (page - 1) * (self.pageHeight + 10), 150, 100)
            w.setFrameEnabled(False)
            pictureFile = os.path.join(
                self.plugin_dir,
                "templates/experimental.svg"
            )
            w.setPictureFile(pictureFile)
            w.setBackgroundEnabled(False)
            w.setTransparency(60)
            self.currentComposition.addItem(w)


    def buildComposerLabel(self, key, item, page):
        '''
        Add a QgsLabel to composition for an item and page
        '''
        cl = QgsComposerLabel(self.currentComposition)

        # 1st page is a map for parcelle
        dpage = page -1
        if self.etype == 'parcelle' and self.iface:
            dpage = page

        cl.setItemPosition(
            item['position'][0],
            item['position'][1] + (dpage) * (self.pageHeight + 10),
            item['position'][2],
            item['position'][3],
            False,
            -1
        )
        cl.setVAlign(item['align'][0])
        cl.setHAlign(item['align'][1])
        content = self.getContentForGivenItem(
            key,
            item,
            page
        )
        cl.setMargin(0)
        cl.setHtmlState(2)
        cl.setText(content)
        cl.setFrameEnabled(False)
        if 'bgcolor' in item:
            cl.setBackgroundColor(item['bgcolor'])
        if 'htmlState' in item:
            cl.setHtmlState(item['htmlState'])
        if 'font' in item:
            cl.setFont(item['font'])
        self.currentComposition.addItem(cl)

    def addParcelleMap(self):
        '''
        Add content in the first page
        with a map and basic information
        '''
        # First add headers
        for key, item in self.composerTemplates.items():
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
            extent = geom.buffer(buf,5).boundingBox()

        # Add memory layer to highlight parcelle
        if extent:
            if self.redlineLayer:
                QgsMapLayerRegistry.instance().removeMapLayer(self.redlineLayer.id())
            crs = self.layer.crs().authid()
            vl = QgsVectorLayer("Polygon?crs=" + crs, "temporary", "memory")
            pr = vl.dataProvider()
            vl.startEditing()
            pr.addFeatures([f for f in self.layer.getFeatures(request)])
            vl.commitChanges()
            vl.updateExtents()
            props = vl.rendererV2().symbol().symbolLayer(0).properties()
            props['outline_width'] = u'1'
            props['outline_color'] = u'0,85,255,255'
            props['outline_style'] = u'solid'
            props['style'] = u'no'
            vl.rendererV2().setSymbol(QgsFillSymbolV2.createSimple(props))
            QgsMapLayerRegistry.instance().addMapLayer(vl)
            self.redlineLayer = vl

        # Add composer map & to parcelle
        miLayers = self.mInstance.layers()
        miLayers.insert( 0, vl.id() )
        self.mInstance.setLayers( miLayers )
        cm = QgsComposerMap(self.currentComposition, 6, 15, 286, 190)
        if extent:
            cm.zoomToExtent(extent)

        cm.setFrameEnabled(True)
        cm.setBackgroundEnabled(True)
        self.currentComposition.addItem(cm)


    def exportItemAsPdf(self, comptecommunal, suffix=None):
        '''
        Export one PDF file using the template composer
        filled with appropriate data
        for one "compte communal"
        '''
        temppath = None

        #QgsMessageLog.logMessage( "cadastre debug - begin exportItemAsPdf" )

        # Set configuration
        self.setComposerTemplates(comptecommunal)

        # Create the composition
        self.createComposition()

        if self.currentComposition:
            if self.iface:
                QApplication.setOverrideCursor(Qt.WaitCursor)

            # Populate composition for all pages
            for i in range(self.numPages):
                j=i+1
                self.addPageContent(j)

            # Add map in first page if export parcelle
            if self.etype == 'parcelle' and self.iface:
                self.addParcelleMap()

            # Create the pdf output path
            from time import time
            temp = "releve_%s_%s_%s.pdf" % (
                self.etype,
                comptecommunal,
                int(time()*100)
            )
            temppath = os.path.join(self.targetDir, temp)
            temppath = os.path.normpath(temppath)
            temppath = re.sub(r'[\?\*\+<>]', '-', temppath)
            #QgsMessageLog.logMessage( "cadastre debug - temppath = %s " % temppath )

            # Export as pdf
            self.currentComposition.exportAsPDF(temppath)
            #QgsMessageLog.logMessage( "cadastre debug - after currentComposition.exportAsPdf" )

            if self.redlineLayer:
                QgsMapLayerRegistry.instance().removeMapLayer(self.redlineLayer.id())
                miLayers = self.mInstance.layers()
                self.mInstance.setLayers( miLayers.pop(0) )

            if self.iface:
                QApplication.restoreOverrideCursor()

            # Opens PDF in default application
            if not self.isMulti and self.iface:
                cadastre_common.openFile(temppath)

        return temppath


    def openFile(self, filename):
        '''
        Opens a file with default system app
        '''
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener ="open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])


    def exportAsPDF(self):
        '''
        Run the PDF export
        '''
        paths = []
        # Export as many pdf as compte communal
        if self.isMulti:
            if self.iface:
                # Show print progress dialog
                self.setupPrintProgressDialog()
            nb = len(self.comptecommunal)

            # Export PDF for each compte
            for comptecommunal in self.comptecommunal:
                # export as PDF
                comptecommunal = comptecommunal.strip("' ")
                apath = self.exportItemAsPdf(comptecommunal)
                if apath:
                    paths.append(apath)

                # update progress bar
                if self.iface:
                    self.printStep+=1
                    self.printProgress.pbPrint.setValue(int(self.printStep * 100 / nb))
            if self.iface:
                info = u"Les relevés ont été enregistrés dans le répertoire :\n%s\n\nOuvrir le dossier ?" % self.targetDir
                openFolder = QDesktopServices()
                openFolder.openUrl(QUrl('file:///%s' % self.targetDir))

        else:
            apath = self.exportItemAsPdf(self.comptecommunal)
            if apath:
                paths.append(apath)

        return paths


    def setupPrintProgressDialog(self):
        '''
        Opens print progress dialog
        '''
        if not self.iface:
            return
        # Show progress dialog
        self.printProgress = cadastrePrintProgress()
        # Set progress bar
        self.printStep = 0
        self.printProgress.pbPrint.setValue(0)
        # Show dialog
        self.printProgress.show()

if iface:
    from cadastre_print_form import *

    class cadastrePrintProgress(QDialog, Ui_cadastre_print_form):
        def __init__(self):
            QDialog.__init__(self)
            # Set up the user interface
            self.setupUi(self)
