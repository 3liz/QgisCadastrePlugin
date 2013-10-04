# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Qadastre - Export method class
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

import csv, sys
import subprocess
import os.path
import operator
import re
import tempfile
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *


class qadastreExport(QObject):

    def __init__(self, dialog, etype='proprietaire', feat=None):
        self.dialog = dialog

        self.etype = etype
        self.feat = feat

        self.maxLineNumber = 15 # max number of line per main table
        self.numPages = 1
        self.pageHeight = 210
        self.pageWidth = 297
        self.printResolution = 300

        # label for header2
        if self.etype == 'proprietaire':
            self.typeLabel = u'DE PROPRIÉTÉ'
            self.feat = feat[0]
        else:
            self.typeLabel = u'PARCELLAIRE'

        # List of templates
        self.composerTemplates = {
            'header1' : {
                'names': ['annee', 'ccodep', 'ccodir', 'ccocom', 'libcom'],
                'position': [3.5, 2.5, 145, 7.5], 'align': [ 128, 4],
                'keepContent' : True,
                'type': 'sql',
                'filter': 'comptecommunal',
                'and': {
                    'proprietaire': u" AND comptecommunal = '%s'" % self.feat['comptecommunal'],
                    'parcelle': u" AND comptecommunal = '%s'" % self.feat['comptecommunal']
                },
            },
            'header2' : {
                'names': ['type'],
                'position': [153.5, 2.5, 60, 7.5], 'align': [ 128, 4],
                'keepContent' : True,
                'type': 'properties',
                'source': [self.typeLabel]
            },
            'header3' : {
                'names': ['comptecommunal'],
                'position': [218.5, 2.5, 75, 7.5], 'align': [ 128, 2],
                'keepContent' : True,
                'type': 'properties',
                'source': [self.feat['comptecommunal'][6:]]
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
                'position': [3.5, 50, 290, 80], 'align': [ 32, 1],
                'keepContent' : False,
                'type': 'parent',
                'source': 'proprietes_baties_line'
            },
            'proprietes_non_baties' : {
                'names': ['lines'],
                'position': [3.5, 130, 290, 77.5], 'align': [ 32, 1],
                'keepContent' : False,
                'type': 'parent',
                'source': 'proprietes_non_baties_line'
            }
        }
        self.mainTables = {
            'proprietaires_line' : {
                'names': ['proprietaire'],
                'type': 'sql',
                'keepContent': True,
                'filter': 'comptecommunal',
                'and': {
                    'proprietaire': u" AND comptecommunal = '%s'" % self.feat['comptecommunal'],
                    'parcelle': u" AND comptecommunal = '%s'" % self.feat['comptecommunal']
                }
            },
            'proprietes_baties_line' : {
                'names': ['section', 'ndeplan', 'ndevoirie', 'adresse', 'coderivoli', 'bat', 'ent', 'niv', 'ndeporte', 'numeroinvar', 'star', 'meval', 'af', 'natloc', 'cat', 'revenucadastral', 'coll', 'natexo', 'anret', 'andeb', 'fractionrcexo', 'pourcentageexo', 'txom', 'coefreduc'],
                'type': 'sql',
                'filter': 'comptecommunal',
                'and': {
                    'proprietaire': u" AND l10.comptecommunal = '%s'" % self.feat['comptecommunal'],
                    'parcelle': u" AND p.geo_parcelle = '%s'" % self.feat['geo_parcelle']
                }
            },
            'proprietes_non_baties_line' : {
                'names': ['section', 'ndeplan', 'ndevoirie', 'adresse', 'coderivoli', 'nparcprim', 'fpdp', 'star', 'suf', 'grssgr', 'cl', 'natcult', 'contenance', 'revenucadastral', 'coll', 'natexo', 'anret', 'fractionrcexo', 'pourcentageexo', 'tc', 'lff'],
                'type': 'sql',
                'and': {
                    'proprietaire': u" AND p.comptecommunal = '%s'" % self.feat['comptecommunal'],
                    'parcelle': u" AND geo_parcelle = '%s'" % self.feat['geo_parcelle']
                }
            }

        }

        # items for which to count number of lines
        self.lineCount = {
            'proprietes_baties_line': 0,
            'proprietes_non_baties_line': 0
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

        # common qadastre methods
        self.qc = self.dialog.qc


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
            self.qc.plugin_dir,
            "templates/%s.tpl" % key
        )

        # Build replace dict depending on source type
        if item['type'] == 'sql':
            # Load SQL query and get data
            # Get sql file
            sqlFile = tplPath + '.sql'
            fin = open(sqlFile)
            sql = fin.read().decode('utf-8')
            fin.close()
            # Add schema to search_path if postgis
            if self.dialog.dbType == 'postgis':
                sql = self.qc.setSearchPath(sql, self.dialog.schema)
            # Add where clause depending on etype
            sql = sql.replace('$and', item['and'][self.etype] )
            # Limit results if asked
            if page and key in self.mainTables.keys() \
            and key in self.lineCount.keys():
                sql+= " LIMIT %s" % self.maxLineNumber
                offset = int((page- 1) * self.maxLineNumber)
                sql+= " OFFSET %s" % offset

            # Run SQL
            #~ self.qc.updateLog(sql)
            [header, data, rowCount] = self.qc.fetchDataFromSqlQuery(self.dialog.connector, sql)
            # Add data length to lineCount object if appropriate
            if not page:
                if key in self.lineCount.keys():
                    self.lineCount[key] = rowCount

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
            self.qc.updateLog(msg)
            return msg

        finally:
            QApplication.restoreOverrideCursor()


    def createComposition(self):
        '''
        Create a composition
        '''
        c = QgsComposition(QgsMapRenderer())
        c.setPaperSize(self.pageWidth, self.pageHeight)
        c.setPrintResolution(self.printResolution)
        c.setSnapGridOffsetX(3.5)
        c.setSnapGridOffsetY(0)
        c.setSnapGridResolution(2.5)

        # set page number
        self.getPageNumberNeeded()
        c.setNumPages(self.numPages)

        return c


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
            1 + int(self.lineCount['proprietes_baties_line'] / self.maxLineNumber),
            1 + int(self.lineCount['proprietes_non_baties_line'] / self.maxLineNumber)
            ]
        )


    def addPageContent(self, composition, page):
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
            cl = QgsComposerLabel(composition)
            cl.setItemPosition(
                item['position'][0],
                item['position'][1] + (page - 1) * (self.pageHeight + 10),
                item['position'][2],
                item['position'][3]
            )
            cl.setVAlign(item['align'][0])
            cl.setHAlign(item['align'][1])
            content = self.getContentForGivenItem(key, item, page)
            cl.setMargin(0)
            cl.setHtmlState(2)
            cl.setText(content)
            cl.setFrameEnabled(False)
            composition.addItem(cl)


    def exportAsPDF(self):
        '''
        Export as PDF using the template composer
        filled with appropriate data
        '''

        # Load the composer from template
        composition = self.createComposition()

        # Populate composition
        for i in range(self.numPages + 1):
            self.addPageContent(composition, i)

        # Export as pdf
        if composition:
            from time import time
            temp = "releve_%s.%.7f.pdf" % (self.etype, time())
            temppath = os.path.join(tempfile.gettempdir(), temp)
            composition.exportAsPDF(temppath)
            if sys.platform == 'linux2':
                subprocess.call(["xdg-open", temppath])
            else:
                os.startfile(temppath)
