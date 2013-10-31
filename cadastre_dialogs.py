# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Cadastre - Dialog classes
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

import csv
import os.path
import operator
import re
import tempfile
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import QgsGenericProjectionSelector
import unicodedata

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms")

from db_manager.db_plugins.plugin import DBPlugin, Schema, Table
from db_manager.db_plugins import createDbPlugin
from db_manager.db_plugins.postgis.connector import PostGisDBConnector


from functools import partial

# --------------------------------------------------------
#        import - Import data from EDIGEO and MAJIC files
# --------------------------------------------------------


class cadastre_common():

    def __init__(self, dialog):

        self.dialog = dialog

        # plugin directory path
        self.plugin_dir = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/cadastre"

        # default auth id for layers
        self.defaultAuthId = 'EPSG:2154'

    def hasSpatialiteSupport(self):
        '''
        Check whether or not
        spatialite support is ok
        '''
        try:
            from db_manager.db_plugins.spatialite.connector import SpatiaLiteDBConnector
            return True
        except ImportError:
            return False
            pass

    def updateLog(self, msg):
        '''
        Update the log
        '''
        t = self.dialog.txtLog
        t.ensureCursorVisible()
        t.append(msg)
        c = t.textCursor()
        c.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        t.setTextCursor(c)
        qApp.processEvents()


    def updateProgressBar(self):
        '''
        Update the progress bar
        '''
        if self.dialog.go:
            self.dialog.step+=1
            self.dialog.pbProcess.setValue(int(self.dialog.step * 100/self.dialog.totalSteps))
            qApp.processEvents()


    def updateConnectionList(self):
        '''
        Update the combo box containing the database connection list
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)

        dbType = unicode(self.dialog.liDbType.currentText()).lower()
        self.dialog.liDbConnection.clear()

        if self.dialog.liDbType.currentIndex() != 0:
            self.dialog.dbType = dbType
            # instance of db_manager plugin class
            dbpluginclass = createDbPlugin( dbType )
            self.dialog.dbpluginclass = dbpluginclass

            # fill the connections combobox
            self.dialog.connectionDbList = []
            for c in dbpluginclass.connections():
                self.dialog.liDbConnection.addItem( unicode(c.connectionName()))
                self.dialog.connectionDbList.append(unicode(c.connectionName()))

            # Show/Hide database specific pannel
            if hasattr(self.dialog, 'databaseSpecificOptions'):
                if dbType == 'postgis':
                    self.dialog.databaseSpecificOptions.setCurrentIndex(0)
                else:
                    self.dialog.databaseSpecificOptions.setCurrentIndex(1)
        else:
            if hasattr(self.dialog, "inDbCreateSchema"):
                self.dialog.databaseSpecificOptions.setTabEnabled(0, False)
                self.dialog.databaseSpecificOptions.setTabEnabled(1, False)

        QApplication.restoreOverrideCursor()


    def toggleSchemaList(self, t):
        '''
        Toggle Schema list and inputs
        '''
        self.dialog.liDbSchema.setEnabled(t)

        if hasattr(self.dialog, "inDbCreateSchema"):
            self.dialog.inDbCreateSchema.setEnabled(t)
            self.dialog.btDbCreateSchema.setEnabled(t)
            self.dialog.databaseSpecificOptions.setTabEnabled(0, t)
            self.dialog.databaseSpecificOptions.setTabEnabled(1, not t)
            self.dialog.btCreateNewSpatialiteDb.setEnabled(not t)


    def updateSchemaList(self):
        '''
        Update the combo box containing the schema list if relevant
        '''
        self.dialog.liDbSchema.clear()

        QApplication.setOverrideCursor(Qt.WaitCursor)
        connectionName = unicode(self.dialog.liDbConnection.currentText())
        self.dialog.connectionName = connectionName
        dbType = unicode(self.dialog.liDbType.currentText()).lower()

        # Deactivate schema fields
        self.toggleSchemaList(False)

        connection = None
        if connectionName:
            # Get schema list
            dbpluginclass = createDbPlugin( dbType, connectionName )
            self.dialog.dbpluginclass = dbpluginclass
            try:
                connection = dbpluginclass.connect()
            except BaseError as e:

                DlgDbError.showError(e, self.dialog)
                self.dialog.go = False
                self.updateLog(e.msg)
                return

        if connection:
            self.dialog.connection = connection
            db = dbpluginclass.database()
            if db:
                self.dialog.db = db
                self.dialog.schemaList = []

            if dbType == 'postgis':
                # Activate schema fields
                self.toggleSchemaList(True)
                for s in db.schemas():
                    self.dialog.liDbSchema.addItem( unicode(s.name))
                    self.dialog.schemaList.append(unicode(s.name))
            else:
                self.toggleSchemaList(False)

        QApplication.restoreOverrideCursor()


    def checkDatabaseForExistingStructure(self):
        '''
        Search among a database / schema
        if there are alreaday Cadastre structure tables
        in it
        '''
        hasStructure = False
        hasData = False
        hasMajicData = False

        searchTable = u'geo_commune'
        majicTable = u'proprietaire'
        if self.dialog.db:
            if self.dialog.dbType == 'postgis':
                schemaSearch = [s for s in self.dialog.db.schemas() if s.name == self.dialog.schema]
                schemaInst = schemaSearch[0]
                getSearchTable = [a for a in self.dialog.db.tables(schemaInst) if a.name == searchTable]
            if self.dialog.dbType == 'spatialite':
                getSearchTable = [a for a in self.dialog.db.tables() if a.name == searchTable]
            if getSearchTable:
                hasStructure = True

                # Check for data in it
                sql = 'SELECT * FROM "%s" LIMIT 1' % searchTable
                if self.dialog.dbType == 'postgis':
                    sql = self.setSearchPath(sql, self.dialog.schema)
                [header, data, rowCount] = self.fetchDataFromSqlQuery(self.dialog.db.connector, sql)
                if rowCount >= 1:
                    hasData = True

                # Check for Majic data in it
                sql = 'SELECT * FROM "%s" LIMIT 1' % majicTable
                if self.dialog.dbType == 'postgis':
                    sql = self.setSearchPath(sql, self.dialog.schema)
                [header, data, rowCount] = self.fetchDataFromSqlQuery(self.dialog.db.connector, sql)
                if rowCount >= 1:
                    hasMajicData = True

        # Set global properties
        self.dialog.hasStructure = hasStructure
        self.dialog.hasData = hasData
        self.dialog.hasMajicData = hasMajicData


    def getLayerFromLegendByTableProps(self, tableName, geomCol='geom', sql=''):
        '''
        Get the layer from QGIS legend
        corresponding to a database
        table name (postgis or sqlite)
        '''

        layer = None
        layers = self.dialog.iface.legendInterface().layers()
        for l in layers:
            if not l.type() == QgsMapLayer.VectorLayer:
                pass
            if not l.providerType() in (u'postgres', u'spatialite'):
                pass
            connectionParams = self.getConnectionParameterFromDbLayer(l)
            if connectionParams and \
                connectionParams['table'] == tableName and \
                connectionParams['geocol'] == geomCol and \
                connectionParams['sql'] == sql:
                return l

        return layer

    def getConnectionParameterFromDbLayer(self, layer):
        '''
        Get connection parameters
        from the layer datasource
        '''
        connectionParams = None

        # Get params via regex
        uri = layer.dataProvider().dataSourceUri()
        reg = "dbname='([^ ]+)' (?:host=([^ ]+) )?(?:port=([0-9]+) )?(?:user='([^ ]+)' )?(?:password='([^ ]+)' )?(?:sslmode=([^ ]+) )?(?:key='([^ ]+)' )?(?:estimatedmetadata=([^ ]+) )?(?:srid=([0-9]+) )?(?:type=([a-zA-Z]+) )?(?:table=\"(.+)\" \()?(?:([^ ]+)\) )?(?:sql=(.*))?"
        result = re.findall(r'%s' % reg, uri)
        if not result:
            return None

        res = result[0]
        if not res:
            return None

        dbname = res[0]
        host = res[1]
        port = res[2]
        user = res[3]
        password = res[4]
        sslmode = res[5]
        key = res[6]
        estimatedmetadata = res[7]
        srid = res[8]
        gtype = res[9]
        table = res[10]
        geocol = res[11]
        sql = res[12]

        schema = ''
        if re.search('"\."', table):
            table = '"' + table + '"'
            sp = table.replace('"', '').split('.')
            schema = sp[0]
            table = sp[1]

        if layer.providerType() == u'postgres':
            dbType = 'postgis'
        else:
            dbType = 'spatialite'

        connectionParams = {
            'dbname' : dbname,
            'host' : host,
            'port': port,
            'user' : user,
            'password': password,
            'sslmode' : sslmode,
            'key': key,
            'estimatedmetadata' : estimatedmetadata,
            'srid' : srid,
            'type': gtype,
            'schema': schema,
            'table' : table,
            'geocol' : geocol,
            'sql' : sql,
            'dbType': dbType
        }

        return connectionParams

    def setSearchPath(self, sql, schema):
        '''
        Set the search_path parameters if postgis database
        '''
        prefix = u'SET search_path = "%s", public, pg_catalog;' % schema
        if re.search('^BEGIN;', sql):
            sql = sql.replace('BEGIN;', 'BEGIN;%s' % prefix)
        else:
            sql = prefix + sql

        return sql


    def fetchDataFromSqlQuery(self, connector, sql, schema=None):
        '''
        Execute a SQL query and
        return [header, data, rowCount]
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)

        data = []
        header = []
        rowCount = 0
        c = None


        try:
            c = connector._execute(None,unicode(sql))
            data = []
            header = connector._get_cursor_columns(c)

            if header == None:
                header = []

            if len(header) > 0:
                data = connector._fetchall(c)

            rowCount = c.rowcount
            if rowCount == -1:
                rowCount = len(data)

        except BaseError as e:

            DlgDbError.showError(e, self.dialog)
            self.dialog.go = False
            self.updateLog(e.msg)
            return

        finally:
            QApplication.restoreOverrideCursor()
            if c:
                c.close()
                del c

        return [header, data, rowCount]



    def getConnectorFromUri(self, connectionParams):
        '''
        Set connector property
        for the given database type
        and parameters
        '''
        uri = QgsDataSourceURI()
        if connectionParams['dbType'] == 'postgis':
            uri.setConnection(
                connectionParams['host'],
                connectionParams['port'],
                connectionParams['dbname'],
                connectionParams['user'],
                connectionParams['password']
            )
            connector = PostGisDBConnector(uri)

        if connectionParams['dbType'] == 'spatialite':
            uri.setConnection('', '', connectionParams['dbname'], '', '')
            if self.hasSpatialiteSupport():
                from db_manager.db_plugins.spatialite.connector import SpatiaLiteDBConnector
            connector = SpatiaLiteDBConnector(uri)

        return connector


    def chooseDataPath(self, key):
        '''
        Ask the user to select a folder
        and write down the path to appropriate field
        '''
        ipath = QFileDialog.getExistingDirectory(
            None,
            u"Choisir le répertoire contenant les fichiers",
            str(self.dialog.pathSelectors[key]['input'].text().encode('utf-8')).strip(' \t')
        )
        if os.path.exists(unicode(ipath)):
            self.dialog.pathSelectors[key]['input'].setText(unicode(ipath))



    def unaccent(self, s):
        '''
        Removes all accents from
        the given string and
        replace e dans l'o
        '''
        p = re.compile( '(œ)')
        s = p.sub('oe', s)

        if isinstance(s,str):
            s = unicode(s,"utf8","replace")
        s=unicodedata.normalize('NFD',s)

        return s.encode('ascii','ignore')


    def postgisToSpatialite(self, sql):
        '''
        Convert postgis SQL statement
        into spatialite compatible
        statements
        '''

        # delete some incompatible options
        # replace other by spatialite syntax
        replaceDict = [
            # delete
            {'in': r'with\(oids=.+\)', 'out': ''},
            {'in': r'comment on [^;]+;', 'out': ''},
            {'in': r'alter table [^;]+add primary key[^;]+;', 'out': ''},
            {'in': r'alter table [^;]+drop column[^;]+;', 'out': ''},
            {'in': r'alter table [^;]+drop constraint[^;]+;', 'out': ''},
            {'in': r'^analyse [^;]+;', 'out': ''},
            # replace
            {'in': r'truncate (bati|fanr|lloc|nbat|pdll|prop)',
            'out': r'drop table \1;create table \1 (tmp text)'},
            {'in': r'truncate ', 'out': 'delete from '},
            {'in': r'distinct on *\([a-z, ]+\)', 'out': 'distinct'},
            {'in': r'serial', 'out': 'INTEGER PRIMARY KEY AUTOINCREMENT'},
            {'in': r'current_schema::text, ', 'out': ''},
            {'in': r'substring', 'out': 'SUBSTR'},
            {'in': r"(to_char\()([^']+) *, *'[09]+' *\)", 'out': r"CAST(\2 AS TEXT)"},
            {'in': r"(to_number\()([^']+) *, *'[09]+' *\)", 'out': r"CAST(\2 AS integer)"},
            {'in': r"(to_date\()([^']+) *, *'DDMMYYYY' *\)",
            'out': r"date(substr(\2, 5, 4) || '-' || substr(\2, 3, 2) || '-' || substr(\2, 1, 2))"},
            {'in': r"(to_date\()([^']+) *, *'DD/MM/YYYY' *\)",
            'out': r"date(substr(\2, 7, 4) || '-' || substr(\2, 4, 2) || '-' || substr(\2, 1, 2))"},
            {'in': r"(to_date\()([^']+) *, *'YYYYMMDD' *\)",
            'out': r"date(substr(\2, 1, 4) || '-' || substr(\2, 5, 2) || '-' || substr(\2, 7, 2))"},
            {'in': r"(to_char\()([^']+) *, *'dd/mm/YYYY' *\)",
            'out': r"strftime('%d/%m/%Y', \2)"},
        ]

        for a in replaceDict:
            r = re.compile(a['in'], re.IGNORECASE|re.MULTILINE)
            sql = r.sub(a['out'], sql)

        # index spatiaux
        r = re.compile(r'(create index [^;]+ ON )([^;]+)( USING +)(gist +)?\(([^;]+)\);',  re.IGNORECASE|re.MULTILINE)
        sql = r.sub(r'SELECT createSpatialIndex("\2", "\5");', sql)

        # update from : geo_parcelle -> parcelle
        r = re.compile(r'update parcelle SET geo_parcelle=g.geo_parcelle[^;]+;', re.IGNORECASE|re.MULTILINE)
        res = r.findall(sql)
        replaceBy = ''
        for statement in res:
            replaceBy = '''
            CREATE INDEX idx_geo_parcelle_parcelle ON geo_parcelle (parcelle);
            CREATE INDEX idx_parcelle_parcelle ON parcelle (parcelle);
            CREATE TABLE parcelle_temp AS
            SELECT p.parcelle, p.annee, p.ccodep, p.ccodir, p.ccocom, p.ccopre, p.ccosec, p.dnupla, p.dcntpa, p.dsrpar, p.dnupro, p.comptecommunal, p.jdatat, p.dreflf, p.gpdl, p.cprsecr, p.ccosecr, p.dnuplar, p.dnupdl, p.pdl, p.gurbpa, p.dparpi, p.ccoarp, p.gparnf, p.gparbat, p.parrev, p.gpardp, p.fviti, p.dnvoiri, p.dindic, p.ccovoi, p.ccoriv, p.voie, p.ccocif, p.gpafpd, p.ajoutcoherence, p.cconvo, p.dvoilib, p.ccocomm, p.ccoprem, p.ccosecm, p.dnuplam, p.parcellefiliation, p.type_filiation, gp.geo_parcelle
            FROM parcelle p
            LEFT JOIN geo_parcelle gp ON gp.parcelle = p.parcelle AND gp.annee='?';
            DROP TABLE parcelle;
            ALTER TABLE parcelle_temp RENAME TO parcelle;
            DROP INDEX idx_geo_parcelle_parcelle;
            '''
            replaceBy = replaceBy.replace('?', self.dialog.dataYear)
            sql = sql.replace(statement, replaceBy)

        # replace postgresql "update from" statement
        r = re.compile(r'(update [^;=]+)(=)([^;=]+ FROM [^;]+)(;)', re.IGNORECASE|re.MULTILINE)
        sql = r.sub(r'\1=(SELECT \3);', sql)

        # replace multiple column update for geo_parcelle
        r = re.compile(r'update [^;]+parcelle, voie, comptecommunal[^;]+;',  re.IGNORECASE|re.MULTILINE)
        res = r.findall(sql)
        replaceBy = ''
        for statement in res:
            replaceBy = '''
            ALTER TABLE geo_parcelle ADD COLUMN temp_import text;
            UPDATE geo_parcelle SET temp_import = SUBSTR(geo_parcelle,1,4) || '@' || SUBSTR(geo_parcelle,5,3) || replace(SUBSTR(geo_parcelle,8,5),'0','-') || SUBSTR(geo_parcelle,13,4) ;
            CREATE INDEX idx_parcelle_temp_import ON geo_parcelle ( temp_import);
            DROP TABLE IF EXISTS geo_parcelle_temp;
            CREATE TABLE geo_parcelle_temp AS
            SELECT geo_parcelle.geo_parcelle, geo_parcelle.annee, geo_parcelle.object_rid, geo_parcelle.idu, geo_parcelle.geo_section, geo_parcelle.geo_subdsect, geo_parcelle.supf, geo_parcelle.geo_indp, geo_parcelle.coar, geo_parcelle.tex, geo_parcelle.tex2, geo_parcelle.codm, geo_parcelle.creat_date, geo_parcelle.update_dat, p.parcelle, geo_parcelle.lot, p.comptecommunal, p.voie, geo_parcelle.ogc_fid, geo_parcelle.geom, geo_parcelle.geom_uf
            FROM geo_parcelle
            LEFT JOIN parcelle p ON p.parcelle=geo_parcelle.temp_import AND p.annee='?' AND geo_parcelle.annee='?'
            ;
            DROP TABLE geo_parcelle;
            ALTER TABLE geo_parcelle_temp RENAME TO geo_parcelle;
            '''
            replaceBy = replaceBy.replace('?', self.dialog.dataYear)
            replaceBy = replaceBy.replace('@', '%s%s' % (self.dialog.edigeoDepartement, self.dialog.edigeoDirection))
            sql = sql.replace(statement, replaceBy)

        # majic formatage : replace multiple column update for loca10
        r = re.compile(r'update local10 set[^;]+;',  re.IGNORECASE|re.MULTILINE)
        res = r.findall(sql)
        replaceBy = ''
        for statement in res:
            replaceBy = '''
            CREATE TABLE ll AS
            SELECT l.invar, l.ccopre , l.ccosec, l.dnupla, l.ccoriv, l.ccovoi, l.dnvoiri, l10.annee || l10.invar AS local00, REPLACE(l10.annee||l10.ccodep || l10.ccodir || l10.ccocom || l.ccopre || l.ccosec || l.dnupla,' ', '-') AS parcelle, REPLACE(l10.annee || l10.ccodep ||  l10.ccodir || l10.ccocom || l.ccovoi,' ', '-') AS voie
            FROM local00 l
            INNER JOIN local10 AS l10 ON l.invar = l10.invar AND l.annee = l10.annee
            WHERE l10.annee='?';
            CREATE INDEX  idx_ll_invar ON ll (invar);
            UPDATE local10 SET ccopre = (SELECT ll.ccopre FROM ll WHERE ll.invar = local10.invar)
            WHERE local10.annee = '?';
            UPDATE local10 SET ccosec = (SELECT ll.ccosec FROM ll WHERE ll.invar = local10.invar)
            WHERE local10.annee = '?';
            UPDATE local10 SET dnupla = (SELECT ll.dnupla FROM ll WHERE ll.invar = local10.invar)
            WHERE local10.annee = '?';
            UPDATE local10 SET ccoriv = (SELECT ll.ccoriv FROM ll WHERE ll.invar = local10.invar)
            WHERE local10.annee = '?';
            UPDATE local10 SET ccovoi = (SELECT ll.ccovoi FROM ll WHERE ll.invar = local10.invar)
            WHERE local10.annee = '?';
            UPDATE local10 SET dnvoiri = (SELECT ll.dnvoiri FROM ll WHERE ll.invar = local10.invar)
            WHERE local10.annee = '?';
            UPDATE local10 SET local00 = (SELECT ll.local00 FROM ll WHERE ll.invar = local10.invar)
            WHERE local10.annee = '?';
            UPDATE local10 SET parcelle = (SELECT ll.parcelle FROM ll WHERE ll.invar = local10.invar)
            WHERE local10.annee = '?';
            UPDATE local10 SET voie = (SELECT ll.voie FROM ll WHERE ll.invar = local10.invar)
            WHERE local10.annee = '?';
            DROP TABLE ll;
            '''
            replaceBy = replaceBy.replace('?', self.dialog.dataYear)
            sql = sql.replace(statement, replaceBy)

        #~ self.updateLog(sql)
        return sql


    def createNewSpatialiteDatabase(self):
        '''
        Choose a file path to save
        create the sqlite database with
        spatial tools and create QGIS connection
        '''
        # Let the user choose new file path
        ipath = QFileDialog.getSaveFileName (
            None,
            u"Choisir l'emplacement du nouveau fichier",
            str(os.path.expanduser("~").encode('utf-8')).strip(' \t'),
            "Sqlite database (*.sqlite)"
        )
        if not ipath:
            self.updateLog(u"Aucune base de données créée (annulation)")
            return None

        # Delete file if exists (check already done above)
        if os.path.exists(unicode(ipath)):
            os.remove(unicode(ipath))

        # Create the spatialite database
        try:
            from pyspatialite import dbapi2 as db
            conn=db.connect(unicode(ipath))
            c=conn.cursor()
            sql = "select initspatialmetadata(1)"
            c.execute(sql)
        except:
            self.updateLog(u"Échec lors de la création du fichier Spatialite !")
            return None

        # Create QGIS connexion
        baseKey = "/SpatiaLite/connections/"
        settings = QSettings()
        myName = os.path.basename(ipath);
        baseKey+= myName;
        myFi = QFileInfo(ipath)
        settings.setValue( baseKey + "/sqlitepath", myFi.canonicalFilePath());

        # Update connections combo box and set new db selected
        self.updateConnectionList()
        listDic = { self.dialog.connectionDbList[i]:i for i in range(0, len(self.dialog.connectionDbList)) }
        self.dialog.liDbConnection.setCurrentIndex(listDic[myName])


from cadastre_import_form import *
from cadastre_import import *

class cadastre_import_dialog(QDialog, Ui_cadastre_import_form):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        self.connectionDbList = []
        # common cadastre methods
        self.qc = cadastre_common(self)

        # first disable database specifi tabs
        self.databaseSpecificOptions.setTabEnabled(0, False)
        self.databaseSpecificOptions.setTabEnabled(1, False)

        # spatialite support
        self.hasSpatialiteSupport = self.qc.hasSpatialiteSupport()
        if not self.hasSpatialiteSupport:
            self.liDbType.removeItem(2)
            self.databaseSpecificOptions.setTabEnabled(1, False)
            self.btCreateNewSpatialiteDb.setEnabled(False)


        # Signals/Slot Connections
        self.liDbType.currentIndexChanged[str].connect(self.qc.updateConnectionList)
        self.liDbConnection.currentIndexChanged[str].connect(self.qc.updateSchemaList)
        self.btDbCreateSchema.clicked.connect(self.createSchema)
        self.btCreateNewSpatialiteDb.clicked.connect(self.qc.createNewSpatialiteDatabase)
        self.btProcessImport.clicked.connect(self.processImport)
        self.rejected.connect(self.onClose)
        self.buttonBox.rejected.connect(self.onClose)

        # path buttons selectors
        # paths needed to be chosen by user
        self.pathSelectors = {
            "edigeoSourceDir" : {
                "button" : self.btEdigeoSourceDir,
                "input" : self.inEdigeoSourceDir
            },
            "majicSourceDir" : {
                "button" : self.btMajicSourceDir,
                "input" : self.inMajicSourceDir
            }
        }
        for key, item in self.pathSelectors.items():
            control = item['button']
            slot = partial(self.qc.chooseDataPath, key)
            control.clicked.connect(slot)

        # projection selector
        self.projSelectors = {
            "edigeoSourceProj" : {
                "button" : self.btEdigeoSourceProj,
                "input" : self.inEdigeoSourceProj,
                "sentence" : "Choisir la projection des fichiers Edigeo"
            },
            "edigeoTargetProj" : {
                "button" : self.btEdigeoTargetProj,
                "input" : self.inEdigeoTargetProj,
                "sentence" : "Choisir la projection de destination"
            }
        }
        for key, item in self.projSelectors.items():
            control = item['button']
            slot = partial(self.chooseProjection, key)
            control.clicked.connect(slot)

        # Set initial values
        self.doMajicImport = False
        self.doEdigeoImport = False
        self.dataVersion = None
        self.dataYear = None
        self.dbType = None
        self.dbpluginclass = None
        self.connectionName = None
        self.connection = None
        self.db = None
        self.schema = None
        self.schemaList = None
        self.hasStructure = None
        self.hasData = None
        self.hasMajicData = None
        self.edigeoSourceProj = None
        self.edigeoTargetProj = None
        self.edigeoDepartement = None
        self.edigeoDirection = None
        self.edigeoLot = None
        self.majicSourceDir = None
        self.edigeoSourceDir = None

        # set input values from settings
        self.sList = {
            'dataVersion': {
                'widget': self.inDataVersion,
                'wType': 'spinbox',
                'property': self.dataVersion
            },
            'dataYear': {
                'widget': self.inDataYear,
                'wType': 'spinbox',
                'property': self.dataYear
            } ,
            'schema': {
                'widget': None
            } ,
            'majicSourceDir': {
                'widget': self.inMajicSourceDir,
                'wType': 'text',
                'property': self.majicSourceDir
            },
            'edigeoSourceDir': {
                'widget': self.inEdigeoSourceDir,
                'wType': 'text',
                'property': self.edigeoSourceDir
            },
            'edigeoDepartement': {
                'widget': self.inEdigeoDepartement,
                'wType': 'text',
                'property': self.edigeoDepartement
            },
            'edigeoDirection': {
                'widget': self.inEdigeoDirection,
                'wType': 'text',
                'property': self.edigeoDirection
            },
            'edigeoLot': {
                'widget': self.inEdigeoLot,
                'wType': 'text',
                'property': self.edigeoLot
            },
            'edigeoSourceProj': {
                'widget': self.inEdigeoSourceProj,
                'wType': 'text',
                'property': self.edigeoSourceProj
            },
            'edigeoTargetProj': {
                'widget': self.inEdigeoTargetProj,
                'wType': 'text',
                'property': self.edigeoTargetProj
            }
        }
        self.getValuesFromSettings()

        self.cadastreImportOptions = {
            'dataVersion' : '2012',
            'dataYear' : '2011',
            'edigeoSourceDir' : None,
            'edigeoSourceProj' : None,
            'edigeoTargetProj' : None,
            'majicSourceDir' : None
        }

        s = QSettings()
        self.majicSourceFileNames = [
            {'key': '[FICHIER_BATI]',
                'value': s.value("cadastre/batiFileName", 'REVBATI.800', type=str),
                'table': 'bati'
            },
            {'key': '[FICHIER_FANTOIR]',
                'value': s.value("cadastre/fantoirFileName", 'TOPFANR.800', type=str),
                'table': 'fanr'
            },
            {'key': '[FICHIER_LOTLOCAL]',
                'value': s.value("cadastre/lotlocalFileName", 'REVD166.800', type=str),
                'table': 'lloc'
            },
            {'key': '[FICHIER_NBATI]',
                'value': s.value("cadastre/nbatiFileName", 'REVNBAT.800', type=str),
                'table': 'nbat'
            },
            {'key': '[FICHIER_PDL]',
                'value': s.value("cadastre/pdlFileName", 'REVFPDL.800', type=str),
                'table': 'pdll'
            },
            {'key': '[FICHIER_PROP]',
                'value': s.value("cadastre/propFileName", 'REVPROP.800', type=str),
                'table': 'prop'
            }
        ]


    def onClose(self):
        '''
        Close dialog
        '''
        self.close()


    def getValuesFromSettings(self):
        '''
        get values from QGIS settings
        and set input fields appropriately
        '''
        s = QSettings()
        for k,v in self.sList.items():
            value = s.value("cadastre/%s" % k, '', type=str)
            if value and value != 'None' and v['widget']:
                if v['wType'] == 'text':
                    v['widget'].setText(str(value.encode('utf-8')))
                if v['wType'] == 'spinbox':
                    v['widget'].setValue(int(value))
                if v['wType'] == 'combobox':
                    listDic = {v['list'][i]:i for i in range(0, len(v['list']))}
                    v['widget'].setCurrentIndex(listDic[value])


    def createSchema(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            if self.db == None:
                QMessageBox.information(
                    self,
                    QApplication.translate("DBManagerPlugin", "Sorry"),
                    QApplication.translate("DBManagerPlugin", "No database selected or you are not connected to it.")
                )
                return
            schema = self.inDbCreateSchema.text()
        finally:
            QApplication.restoreOverrideCursor()

        if schema:
            try:
                self.db.createSchema(schema)

            except BaseError as e:

                DlgDbError.showError(e, self)
                self.qc.updateLog(e.msg)
                return

            finally:
                self.qc.updateSchemaList()
                listDic = { self.schemaList[i]:i for i in range(0, len(self.schemaList)) }
                self.liDbSchema.setCurrentIndex(listDic[schema])
                self.inDbCreateSchema.clear()
                QApplication.restoreOverrideCursor()


    def chooseProjection(self, key):
        '''
        Let the user choose a SCR
        '''
        header = u"Choisir la projection"
        sentence = self.projSelectors[key]['sentence']
        projSelector = QgsGenericProjectionSelector(self)
        projSelector.setMessage( "<h2>%s</h2>%s" % (header.encode('UTF8'), sentence.encode('UTF8')) )
        projSelector.setSelectedAuthId(self.qc.defaultAuthId)
        if projSelector.exec_():
            self.crs = QgsCoordinateReferenceSystem( projSelector.selectedCrsId(), QgsCoordinateReferenceSystem.InternalCrsId )
            if len(projSelector.selectedAuthId()) == 0:
                QMessageBox.information(
                    self,
                    self.tr("Cadastre"),
                    self.tr(u"Aucun système de coordonnée de référence valide n'a été sélectionné")
                )
                return
            else:
                self.projSelectors[key]['input'].clear()
                self.projSelectors[key]['input'].setText(self.crs.authid() + " - " + self.crs.description())
        else:
            return

    def processImport(self):
        '''
        Lancement du processus d'import
        '''
        if not self.db:
            msg = u'Veuillez sélectionner une base de données'
            QMessageBox.critical(self, u"Cadastre", self.tr(msg))
            return None

        self.dataVersion = unicode(self.inDataVersion.text())
        self.dataYear = unicode(self.inDataYear.text())
        self.schema = unicode(self.liDbSchema.currentText())
        self.majicSourceDir = str(self.inMajicSourceDir.text().encode('utf-8')).strip(' \t')
        self.edigeoSourceDir = str(self.inEdigeoSourceDir.text().encode('utf-8')).strip(' \t')
        self.edigeoDepartement = unicode(self.inEdigeoDepartement.text())
        self.edigeoDirection = unicode(self.inEdigeoDirection.text())
        self.edigeoLot = unicode(self.inEdigeoLot.text())
        self.edigeoSourceProj = unicode(self.inEdigeoSourceProj.text().split( " - " )[ 0 ])
        self.edigeoTargetProj = unicode(self.inEdigeoTargetProj.text().split( " - " )[ 0 ])

        # store chosen data in QGIS settings
        s = QSettings()
        s.setValue("cadastre/dataVersion", str(self.dataVersion))
        s.setValue("cadastre/dataYear", int(self.dataYear))
        s.setValue("cadastre/majicSourceDir", str(self.majicSourceDir))
        s.setValue("cadastre/edigeoSourceDir", str(self.edigeoSourceDir))
        s.setValue("cadastre/edigeoDepartement", str(self.edigeoDepartement))
        s.setValue("cadastre/edigeoDirection", str(self.edigeoDirection))
        s.setValue("cadastre/edigeoLot", str(self.edigeoLot))
        s.setValue("cadastre/edigeoSourceProj", str(self.edigeoSourceProj))
        s.setValue("cadastre/edigeoTargetProj", str(self.edigeoTargetProj))


        # cadastreImport instance
        qi = cadastreImport(self)

        # Check if structure already exists in the database/schema
        self.qc.checkDatabaseForExistingStructure()

        #~ # Run Script for creating tables
        if not self.hasStructure:
            qi.installOpencadastreStructure()

        # defined properties
        if os.path.exists(self.majicSourceDir):
            self.doMajicImport = True
        if os.path.exists(self.edigeoSourceDir):
            self.doEdigeoImport = True

        # Run MAJIC import
        if os.path.exists(self.majicSourceDir):
            qi.importMajic()

        # Run Edigeo import
        if os.path.exists(self.edigeoSourceDir):
            qi.importEdigeo()

        qi.endImport()

# --------------------------------------------------------
#        load - Load data from database
# --------------------------------------------------------

from cadastre_load_form import *
from cadastre_loading import *

class cadastre_load_dialog(QDockWidget, Ui_cadastre_load_form):
    def __init__(self, iface, cadastre_search_dialog):
        QDockWidget.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self)
        self.mc = self.iface.mapCanvas()

        self.cadastre_search_dialog = cadastre_search_dialog

        # common cadastre methods
        self.qc = cadastre_common(self)
        self.ql = cadastreLoading(self)

        # spatialite support
        self.hasSpatialiteSupport = self.qc.hasSpatialiteSupport()
        if not self.hasSpatialiteSupport:
            self.liDbType.removeItem(2)

        # Set initial values
        self.go = True
        self.step = 0
        self.totalSteps = 0
        self.dbType = None
        self.dbpluginclass = None
        self.connectionName = None
        self.connection = None
        self.db = None
        self.schema = None
        self.schemaList = None
        self.hasStructure = None

        # Get style list
        self.getStyleList()

        # Signals/Slot Connections
        self.liDbType.currentIndexChanged[str].connect(self.qc.updateConnectionList)
        self.liDbConnection.currentIndexChanged[str].connect(self.qc.updateSchemaList)
        self.btProcessLoading.clicked.connect(self.onProcessLoadingClicked)
        self.ql.cadastreLoadingFinished.connect(self.onLoadingEnd)


    def getStyleList(self):
        '''
        Get the list of style directories
        inside the plugin dir
        and add combobox item
        '''
        spath = os.path.join(self.qc.plugin_dir, "styles/")
        dirs = os.listdir(spath)
        dirs = [a for a in dirs if os.path.isdir(os.path.join(spath, a))]
        dirs.sort()
        cb = self.liTheme
        cb.clear()
        for d in dirs:
            cb.addItem('%s' % d, d)

    def onProcessLoadingClicked(self):
        '''
        Activate the loading of layers
        from database tables
        when user clicked on button
        '''
        if self.connection:
            if self.db:
                self.ql.processLoading()

    def onLoadingEnd(self):
        '''
        Actions to trigger
        when all the layers
        have been loaded
        '''
        self.cadastre_search_dialog.checkMajicContent()
        self.cadastre_search_dialog.setupSearchCombobox('commune', None, 'sql')
        self.cadastre_search_dialog.setupSearchCombobox('section', None, 'sql')



# ---------------------------------------------------------
#        search - search for data among database ans export
# ---------------------------------------------------------

from cadastre_search_form import *
from cadastre_export import *

class cadastre_search_dialog(QDockWidget, Ui_cadastre_search_form):
    def __init__(self, iface):
        QDockWidget.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self)

        # common cadastre methods
        self.qc = cadastre_common(self)

        # database properties
        self.connector = None
        self.dbType = None
        self.schema = None

        self.mc = self.iface.mapCanvas()
        self.communeLayer = None
        self.communeFeatures = None
        self.communeRequest = None
        self.selectedCommuneFeature = None
        self.sectionLayer = None
        self.sectionFeatures = None
        self.sectionRequest = None
        self.sectionCommuneFeature = None

        # signals/slots
        self.searchComboBoxes = {
            'commune': {
                'widget': self.liCommune,
                'labelAttribute': 'tex2',
                'table': 'geo_commune', 'geomCol': 'geom', 'sql': '',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid','tex2','idu','geo_commune','geom'],
                'orderBy': ['tex2'],
                'features': None,
                'chosenFeature': None,
                'resetWidget': self.btResetCommune,
                'child': {
                    'key': 'section',
                    'fkey': 'geo_commune',
                    'getIfNoFeature': True
                }
            },
            'section': {
                'widget': self.liSection,
                'labelAttribute': 'idu',
                'table': 'geo_section', 'geomCol': 'geom', 'sql': '',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid','tex','idu','geo_commune','geo_section','geom'],
                'orderBy': ['tex'],
                'features': None,
                'chosenFeature': None,
                'resetWidget': self.btResetSection,
                'child': {
                    'key': 'parcelle',
                    'fkey': 'geo_section',
                    'getIfNoFeature': False
                }
            },
            'parcelle': {
                'widget': self.liParcelle,
                'labelAttribute': 'idu',
                'table': 'geo_parcelle', 'geomCol': 'geom', 'sql': '',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid','tex','idu','geo_section','geom', 'comptecommunal', 'geo_parcelle'],
                'orderBy': ['geo_parcelle'],
                'features': None,
                'chosenFeature': None,
                'connector': None,
                'resetWidget': self.btResetParcelle
            },
            'proprietaire': {
                'widget': self.liProprietaire,
                'labelAttribute': 'idu',
                'table': 'geo_parcelle',
                'layer': None,
                'request': None,
                'attributes': ['comptecommunal','idu','dnupro','geom'],
                'orderBy': ['ddenom'],
                'features': None,
                'chosenFeature': None,
                'connector': None,
                'search': {
                    'button' : self.btSearchProprietaire,
                    'child': 'parcelle_proprietaire',
                    'minlen': 3
                }
            },
            'parcelle_proprietaire': {
                'widget': self.liParcelleProprietaire,
                'labelAttribute': 'idu',
                'table': 'geo_parcelle', 'geomCol': 'geom', 'sql': '',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid','tex','idu','comptecommunal','geom', 'geo_parcelle'],
                'orderBy': ['geo_parcelle'],
                'features': None,
                'chosenFeature': None,
                'connector': None,
                'resetWidget': self.btResetParcelleProprietaire
            },
            'adresse': {
                'widget': self.liAdresse,
                'labelAttribute': 'voie',
                'table': 'geo_parcelle',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid','voie','idu','geom'],
                'orderBy': ['voie'],
                'features': None,
                'chosenFeature': None,
                'connector': None,
                'search': {
                    'button' : self.btSearchAdresse,
                    'child': 'parcelle_adresse',
                    'minlen': 3
                }
            },
            'parcelle_adresse': {
                'widget': self.liParcelleAdresse,
                'labelAttribute': 'idu',
                'table': 'geo_parcelle', 'geomCol': 'geom', 'sql': '',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid','tex','idu','voie','geom', 'comptecommunal', 'geo_parcelle'],
                'orderBy': ['geo_parcelle'],
                'features': None,
                'chosenFeature': None,
                'connector': None,
                'resetWidget': self.btResetParcelleAdresse
            }
        }

        # Detect that the user has hidden/showed the dock
        self.visibilityChanged.connect(self.onVisibilityChange)

        # center/zoom/selection buttons
        self.zoomButtons = {
            'lieu':{
                'buttons':{
                    'centre': self.btCentrerLieu,
                    'zoom': self.btZoomerLieu,
                    'select': self.btSelectionnerLieu
                },
                'comboboxes': ['commune', 'section', 'parcelle']
            },
            'adresse':{
                'buttons':{
                    'centre': self.btCentrerAdresse,
                    'zoom': self.btZoomerAdresse,
                    'select': self.btSelectionnerAdresse
                },
                'comboboxes': ['adresse', 'parcelle_adresse']
            },
            'proprietaire':{
                'buttons':{
                    'centre': self.btCentrerProprietaire,
                    'zoom': self.btZoomerProprietaire,
                    'select': self.btSelectionnerProprietaire
                },
                'comboboxes': ['proprietaire', 'parcelle_proprietaire']
            }

        }
        zoomButtonsFunctions = {
            'centre': self.setCenterToChosenItem,
            'zoom': self.setZoomToChosenItem,
            'select': self.setSelectionToChosenItem
        }
        for key, item in self.zoomButtons.items():
            for k, button in item['buttons'].items():
                control = button
                slot = partial(zoomButtonsFunctions[k], key)
                control.clicked.connect(slot)

        # Manuel search button and combo (proprietaire, adresse)
        for key, item in self.searchComboBoxes.items():
            # manual search widgets
            if item.has_key('search'):
                # search button
                control = item['search']['button']
                slot = partial(self.searchItem, key)
                control.clicked.connect(slot)
                # connect Enter key pressed event
                item['widget'].lineEdit().returnPressed.connect(slot)

                # when a search result is chosen in combobox
                control = item['widget']
                slot = partial(self.onSearchItemChoose, key)
                control.currentIndexChanged[str].connect(slot)
            else:
                control = item['widget']
                # when the user edits the combobox content
                slot = partial(self.onNonSearchItemEdit, key)
                control.editTextChanged[str].connect(slot)
                # when the user chooses in the list
                slot = partial(self.onNonSearchItemChoose, key)
                control.currentIndexChanged[str].connect(slot)
                # when the user reset the entered value
                control = item['resetWidget']
                slot = partial(self.onNonSearchItemReset, key)
                control.clicked.connect(slot)


        # export buttons
        self.btExportProprietaire.clicked.connect(self.exportProprietaire)
        self.exportParcelleButtons = {
            'parcelle': self.btExportParcelle,
            'parcelle_adresse': self.btExportParcelleAdresse,
            'parcelle_proprietaire': self.btExportParcelleProprietaire
        }
        for key, item in self.exportParcelleButtons.items():
            control = item
            slot = partial(self.exportParcelle, key)
            control.clicked.connect(slot)

        # setup some gui items
        self.setupSearchCombobox('commune', None, 'sql')
        self.setupSearchCombobox('section', None, 'sql')

        # Check majic content
        self.hasMajicData = False
        self.checkMajicContent()


    def checkMajicContent(self):
        '''
        Check if database contains
        any MAJIC data
        '''
        # Get geo_commune layer
        layer = self.qc.getLayerFromLegendByTableProps('geo_commune')
        if layer:
            # Get Connection params
            connectionParams = self.qc.getConnectionParameterFromDbLayer(layer)
            connector = self.qc.getConnectorFromUri(connectionParams)
            self.connector = connector

            if connector:
                # Get data from table proprietaire
                sql = 'SELECT * FROM "proprietaire" LIMIT 1'
                if connectionParams['dbType'] == 'postgis':
                    sql = self.qc.setSearchPath(sql, connectionParams['schema'])
                [header, data, rowCount] = self.qc.fetchDataFromSqlQuery(self.connector, sql)

                if rowCount >= 1:
                    self.hasMajicData = True

        self.grpAdresse.setEnabled(self.hasMajicData)
        self.grpProprietaire.setEnabled(self.hasMajicData)
        self.btExportParcelle.setEnabled(self.hasMajicData)


    def setupSearchCombobox(self, combo, filterExpression=None, queryMode='qgis'):
        '''
        Fil given combobox with data
        from sql query or QGIS layer query
        And add autocompletion
        '''
        layer = None
        features = None

        # Get widget
        searchCombo = self.searchComboBoxes[combo]
        cb = searchCombo['widget']
        cb.clear()

        # Get corresponding QGIS layer
        itemList = []
        layer = self.qc.getLayerFromLegendByTableProps(
            searchCombo['table'],
            searchCombo['geomCol'],
            searchCombo['sql']
        )
        self.searchComboBoxes[combo]['layer'] = layer
        if layer:

            # Get all features
            keepattributes = self.searchComboBoxes[combo]['attributes']
            request = QgsFeatureRequest().setSubsetOfAttributes(
                keepattributes,
                layer.pendingFields()
            )

            self.searchComboBoxes[combo]['request'] = request
            labelAttribute = self.searchComboBoxes[combo]['labelAttribute']

            # Get features
            if queryMode == 'sql':
                features = self.getFeaturesFromSqlQuery(
                    layer,
                    filterExpression,
                    keepattributes,
                    self.searchComboBoxes[combo]['orderBy']
                )
            else:
                features = layer.getFeatures(request)
            self.searchComboBoxes[combo]['features'] = features

            # Loop through features
            # optionnaly filter by QgsExpression
            qe = None
            if filterExpression and queryMode == 'qgis':
                qe = QgsExpression(filterExpression)
            if queryMode == 'sql':
                emptyLabel = u'%s item(s)' % len(features)
            else:
                emptyLabel = ''
            cb.addItem('%s' % emptyLabel, '')
            for feat in features:
                keep = True
                if qe:
                    if not qe.evaluate(feat):
                        keep = False
                if keep:
                    itemList.append(feat[labelAttribute])
                    cb.addItem(feat[labelAttribute], feat)

            # Activate autocompletion
            completer = QCompleter(itemList, self)
            completer.setCompletionMode(QCompleter.PopupCompletion)
            completer.setMaxVisibleItems(30)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            #~ completer.popup().setStyleSheet("background-color: lightblue")
            cb.setEditable(True)
            cb.setCompleter(completer)

        else:
            #~ self.qc.updateLog(u'Veuillez charger des données cadastrales dans QGIS pour pouvoir effectuer une recherche')
            self.searchComboBoxes[combo]['layer'] = None
            self.searchComboBoxes[combo]['request'] = None
            self.searchComboBoxes[combo]['features'] = None
            self.searchComboBoxes[combo]['chosenFeature'] = None

        return [layer, features]


    def getFeaturesFromSqlQuery(self, layer, filterExpression=None, attributes='*', orderBy=None):
        '''
        Get data from a db table,
        optionnally filtered by given expression
        and get corresponding QgsFeature objects
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Get connection parameters
        connectionParams = self.qc.getConnectionParameterFromDbLayer(layer)
        if not connectionParams:
            QApplication.restoreOverrideCursor()
            return None

        # set properties
        self.dbType = connectionParams['dbType']
        self.schema = connectionParams['schema']

        # Use db_manager tool to run the query
        connector = self.qc.getConnectorFromUri(connectionParams)
        self.connector = connector

        # SQL
        sql = ' SELECT %s' % ', '.join(attributes)
        sql+= ' FROM "%s"' % connectionParams['table']
        sql+= " WHERE 2>1"
        if filterExpression:
            sql+= " AND %s" % filterExpression
        if orderBy:
            sql+= ' ORDER BY %s' % ', '.join(orderBy)

        if self.dbType == 'postgis':
            sql = self.qc.setSearchPath(sql, connectionParams['schema'])
        # Get data
        #~ self.qc.updateLog(sql)
        [header, data, rowCount] = self.qc.fetchDataFromSqlQuery(connector, sql)

        # Get features
        features = []
        for line in data:
            request = QgsFeatureRequest().setSubsetOfAttributes(attributes, layer.pendingFields()).setFilterFid(int(line[0]))
            for feat in layer.getFeatures(request):
                features.append(feat)

        QApplication.restoreOverrideCursor()
        return features


    def getFeatureFromComboboxValue(self, combo):
        '''
        Get the feature corresponding to
        the chosen combobox value
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Get widget
        searchCombo = self.searchComboBoxes[combo]
        cb = searchCombo['widget']

        # Reinit
        self.searchComboBoxes[combo]['chosenFeature'] = None
        feature = cb.itemData(cb.currentIndex())
        if feature:
            self.searchComboBoxes[combo]['chosenFeature'] = feature

        QApplication.restoreOverrideCursor()


    def searchItem(self, key):
        '''
        Query database to get item (adresse, proprietaire)
        corresponding to given name
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Get value
        combo = self.searchComboBoxes[key]['widget']
        searchValue = unicode(combo.currentText())

        # Abort if searchValue length too small
        minlen = self.searchComboBoxes[key]['search']['minlen']
        if len(searchValue) < minlen:
            self.qc.updateLog(u"%s caractères minimum requis pour la recherche !" % minlen)
            QApplication.restoreOverrideCursor()
            return None

        # Get database connection parameters from a qgis layer
        dbtable = self.searchComboBoxes[key]['table']
        layer = self.qc.getLayerFromLegendByTableProps(dbtable)
        if not layer:
            QApplication.restoreOverrideCursor()
            return None
        connectionParams = self.qc.getConnectionParameterFromDbLayer(layer)
        if not connectionParams:
            QApplication.restoreOverrideCursor()
            return None

        # Use db_manager tool to run the query
        connector = self.qc.getConnectorFromUri(connectionParams)
        self.connector = connector

        # Format searchValue
        # get rid of contextual info
        sp = searchValue.split('|')
        if len(sp) > 1:
            searchValue = sp[1]

        # get rid of double spaces
        r = re.compile(r'[ ,]+', re.IGNORECASE)
        searchValue = r.sub(' ', searchValue)

        if key == 'adresse':
            # get rid of stopwords
            stopwords = ['allee', 'aqueduc', 'arceaux', 'avenue', 'avenues', 'boulevard', 'carrefour', 'carrer', 'chemin', 'chemins', 'chemin rural', 'clos', 'cour', 'cours', 'descente', 'enclos', 'escalier', 'espace', 'esplanade', 'grand rue', 'impasse', 'mail', 'montee', 'parvis', 'passage', 'passerelle', 'place', 'plan', 'pont', 'quai', 'rond-point', 'route', 'rue', 'ruisseau', 'sente', 'sentier', 'square', 'terrasse', 'traboule', 'traverse', 'traversee', 'traversier', 'tunnel', 'voie', 'voie communale', 'viaduc', 'zone',
            'ach', 'all', 'angl', 'art', 'av', 'ave', 'bd', 'bv', 'camp', 'car', 'cc', 'cd', 'ch', 'che', 'chem', 'chs ', 'chv', 'cite', 'clos', 'cote', 'cour', 'cpg', 'cr', 'crs', 'crx', 'd', 'dig', 'dom', 'ecl', 'esc', 'esp', 'fg', 'fos', 'frm', 'gare', 'gpl', 'gr', 'ham', 'hle', 'hlm ', 'imp', 'jte ', 'lot', 'mail', 'mais', 'n', 'parc', 'pas', 'pch', 'pl', 'ple ', 'pont', 'port', 'prom', 'prv', 'pta', 'pte', 'ptr', 'ptte', 'qua', 'quai', 'rem', 'res', 'rive', 'rle', 'roc', 'rpe ', 'rpt ', 'rte ', 'rue', 'rult', 'sen', 'sq', 'tour', 'tsse', 'val', 'vc', 'ven', 'vla', 'voie', 'voir', 'voy', 'zone'
            ]
            sp = searchValue.split(' ')
            if len(sp)>0 and self.qc.unaccent(sp[0]).lower() in stopwords:
                searchValue = ' '.join(sp[1:])

        sqlSearchValue = self.qc.unaccent(searchValue.strip(' \t\n')).upper()

        # Build SQL query
        if key == 'adresse':
            sql = ' SELECT DISTINCT v.voie, c.libcom, v.natvoi, v.libvoi'
            sql+= ' FROM voie v'
            sql+= ' INNER JOIN commune c ON c.ccodep = v.ccodep AND c.ccocom = v.ccocom'
            sql+= " WHERE libvoi LIKE '%%%s%%'" % sqlSearchValue
            sql+= ' ORDER BY c.libcom, v.natvoi, v.libvoi'

        if key == 'proprietaire':
            sql = " SELECT trim(ddenom) AS k, MyStringAgg(comptecommunal, ',') AS cc, dnuper, c.ccocom"
            sql+= ' FROM proprietaire p'
            sql+= ' INNER JOIN commune c ON c.ccocom = p.ccocom'
            sql+= " WHERE ddenom LIKE '%s%%'" % sqlSearchValue
            sql+= ' GROUP BY dnuper, ddenom, dlign4, c.ccocom'
            sql+= ' ORDER BY ddenom, c.ccocom'
        self.dbType = connectionParams['dbType']
        if self.dbType == 'postgis':
            sql = self.qc.setSearchPath(sql, connectionParams['schema'])
            sql = sql.replace('MyStringAgg', 'string_agg')
        else:
            sql = sql.replace('MyStringAgg', 'group_concat')
        #~ self.qc.updateLog(sql)
        [header, data, rowCount] = self.qc.fetchDataFromSqlQuery(connector,sql)

        # Fill  combobox
        self.qc.updateLog(u"%s résultats correpondent à '%s'" % (rowCount, searchValue))
        cb = self.searchComboBoxes[key]['widget']
        cb.clear()
        cb.addItem(u'%s item(s)' % rowCount , '')
        itemList = []

        for line in data:
            if key == 'adresse':
                label = '%s | %s %s' % (
                    line[1].strip(),
                    line[2].strip(),
                    line[3].strip()
                )
                val = {'voie' : line[0]}

            if key == 'proprietaire':
                label = '%s - %s | %s' % (line[3], line[2], line[0].strip())
                val = {
                    'cc' : ["'%s'" % a for a in line[1].split(',')],
                    'dnuper' : line[2]
                }

            cb.addItem(label, val)

        # Restore cursor
        QApplication.restoreOverrideCursor()


    def onSearchItemChoose(self, key):
        '''
        Select parcelles corresponding
        to chosen item in combo box
        (adresse, proprietaire)
        '''
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Get value
        combo = self.searchComboBoxes[key]['widget']
        value = combo.itemData(combo.currentIndex())

        if not value:
            QApplication.restoreOverrideCursor()
            return None

        # Set filter expression
        if key == 'adresse':
            filterExpression = "voie = '%s'" % value['voie']

        if key == 'proprietaire':
            filterExpression = "comptecommunal IN (%s)" % ', '.join(value['cc'])

        # Get data for child and fill combobox
        ckey = self.searchComboBoxes[key]['search']['child']
        [layer, features] = self.setupSearchCombobox(
            ckey,
            filterExpression,
            'sql'
        )

        # Set properties
        self.searchComboBoxes[key]['layer'] = layer
        self.searchComboBoxes[key]['features'] = features
        self.searchComboBoxes[key]['chosenFeature'] = features

        self.qc.updateLog(
            u"%s parcelle(s) trouvée(s) pour '%s'" % (
                len(features),
                combo.currentText()
            )
        )

        QApplication.restoreOverrideCursor()


    def onNonSearchItemChoose(self, key):
        '''
        Get feature from chosen item in combobox
        and optionnaly fill its child combobox
        '''
        # get feature from the chosen value
        self.getFeatureFromComboboxValue(key)

        # optionnaly also update child combobox
        item = self.searchComboBoxes[key]
        if item.has_key('child'):
            feature = item['chosenFeature']
            ckey = item['child']['key']
            fkey = item['child']['fkey']
            if feature:
                filterExpression = "%s = '%s'" % (fkey, feature[fkey])
                self.setupSearchCombobox(ckey, filterExpression, 'sql')
            else:
                if item['child']['getIfNoFeature']:
                    self.setupSearchCombobox(ckey, None, 'sql')


    def onNonSearchItemEdit(self, key):
        '''
        Empty previous stored feature
        for the combobox every time
        the user edit its content
        '''
        self.searchComboBoxes[key]['chosenFeature'] = None


    def onNonSearchItemReset(self, key):
        '''
        Unchoose item in combobox
        which also trigger onNonSearchItemChoose above
        '''
        self.searchComboBoxes[key]['widget'].setCurrentIndex(0)



    def setZoomToChosenSearchCombobox(self, combo):
        '''
        Zoom to the feature(s)
        selected in the give combobox
        '''
        # Get widget
        searchCombo = self.searchComboBoxes[combo]
        cb = searchCombo['widget']

        # Zoom
        if searchCombo['chosenFeature']:
            if isinstance(searchCombo['chosenFeature'], list):
                # buid virtual geom
                f = searchCombo['chosenFeature'][0]
                extent = f.geometry().boundingBox()
                for feat in searchCombo['chosenFeature']:
                    extent.combineExtentWith(feat.geometry().boundingBox())
            else:
                extent = searchCombo['chosenFeature'].geometry().boundingBox()

            # reproject extent if needed
            if self.mc.hasCrsTransformEnabled():
                crsDest = self.mc.mapRenderer().destinationCrs()
                layer = searchCombo['layer']
                crsSrc = layer.crs()
                xform = QgsCoordinateTransform(crsSrc, crsDest)
                extent = xform.transform(extent)

            self.mc.setExtent(extent)
            self.mc.refresh()


    def setCenterToChosenSearchCombobox(self, combo):
        '''
        Center to the feature(s)
        chosen in the corresponding combobox
        '''
        # Get widget
        searchCombo = self.searchComboBoxes[combo]
        cb = searchCombo['widget']

        # Center
        if searchCombo['chosenFeature']:
            # first get scale
            scale = self.mc.scale()

            # then zoom to geometry extent
            if isinstance(searchCombo['chosenFeature'], list):
                # buid virtual geom
                f = searchCombo['chosenFeature'][0]
                extent = f.geometry().boundingBox()
                for feat in searchCombo['chosenFeature']:
                    extent.combineExtentWith(feat.geometry().boundingBox())
            else:
                extent = searchCombo['chosenFeature'].geometry().boundingBox()

            # reproject extent if needed
            if self.mc.hasCrsTransformEnabled():
                crsDest = self.mc.mapRenderer().destinationCrs()
                layer = searchCombo['layer']
                crsSrc = layer.crs()
                xform = QgsCoordinateTransform(crsSrc, crsDest)
                extent = xform.transform(extent)

            self.mc.setExtent(extent)

            # the set the scale back
            self.mc.zoomScale(scale)
            self.mc.refresh()


    def setSelectionToChosenSearchCombobox(self, combo):
        '''
        Select the feature(s)
        corresponding to the chosen item
        '''
        # Get widget
        searchCombo = self.searchComboBoxes[combo]
        cb = searchCombo['widget']

        # Select
        if searchCombo['chosenFeature'] and searchCombo['layer']:
            searchCombo['layer'].removeSelection()
            if isinstance(searchCombo['chosenFeature'], list):
                i = [feat.id() for feat in searchCombo['chosenFeature']]
            else:
                i = searchCombo['chosenFeature'].id()
            searchCombo['layer'].select(i)


    def setCenterToChosenItem(self, key):
        '''
        Set map center corresponding
        to the chosen feature(s) for the
        last not null item in the list
        '''
        w = None
        for item in self.zoomButtons[key]['comboboxes']:
            if self.searchComboBoxes[item]['chosenFeature'] \
            and self.searchComboBoxes[item]['layer']:
                w = item
        if w:
            self.setCenterToChosenSearchCombobox(w)

    def setZoomToChosenItem(self, key):
        '''
        Zoom to the chosen feature(s) for the
        last not null item in the list
        '''
        w = None
        for item in self.zoomButtons[key]['comboboxes']:
            if self.searchComboBoxes[item]['chosenFeature'] \
            and self.searchComboBoxes[item]['layer']:
                w = item
        if w:
            self.setZoomToChosenSearchCombobox(w)

    def setSelectionToChosenItem(self, key):
        '''
        Select the feature(s) for the
        last non null item in the list
        '''
        w = None
        for item in self.zoomButtons[key]['comboboxes']:
            if self.searchComboBoxes[item]['chosenFeature'] \
            and self.searchComboBoxes[item]['layer']:
                w = item
        if w:
            self.setSelectionToChosenSearchCombobox(w)

    def exportProprietaire(self):
        '''
        Export the selected proprietaire
        as PDF using the template composer
        filled with appropriate data
        '''
        feat = self.searchComboBoxes['proprietaire']['chosenFeature']
        if feat and self.connector:
            qe = cadastreExport(self, 'proprietaire', feat)
            qe.exportAsPDF()
        else:
            self.qc.updateLog(u'Aucun propriétaire sélectionné !')


    def exportParcelle(self, key):
        '''
        Export the selected parcelle
        as PDF using the template composer
        filled with appropriate data
        '''
        feat = self.searchComboBoxes[key]['chosenFeature']
        if feat and self.connector:
            qe = cadastreExport(self, 'parcelle', feat)
            qe.exportAsPDF()
        else:
            self.qc.updateLog(u'Aucune parcelle sélectionnée !')


    def onVisibilityChange(self, visible):
        '''
        Fill commune combobox when the dock
        becomes visible
        '''
        if visible:
            print "visible"
            #~ self.setupSearchCombobox('commune', None, 'sql')
        else:
            self.txtLog.clear()



# --------------------------------------------------------
#        Option - Let the user configure options
# --------------------------------------------------------

from cadastre_option_form import *

class cadastre_option_dialog(QDialog, Ui_cadastre_option_form):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        # common cadastre methods
        self.qc = cadastre_common(self)

        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        self.buttonBox.rejected.connect(self.onReject)
        self.buttonBox.accepted.connect(self.onAccept)

        # path buttons selectors
        # paths needed to be chosen by user
        self.pathSelectors = {
            "tempDir" : {
                "button" : self.btTempDir,
                "input" : self.inTempDir
            }
        }
        from functools import partial
        for key, item in self.pathSelectors.items():
            control = item['button']
            slot = partial(self.qc.chooseDataPath, key)
            control.clicked.connect(slot)

        # Set initial widget values
        self.getValuesFromSettings()



    def getValuesFromSettings(self):
        '''
        Get majic file names and other options
        from settings and set corresponding inputs
        '''
        s = QSettings()
        batiFileName = s.value("cadastre/batiFileName", 'REVBATI.800', type=str)
        if batiFileName:
            self.inMajicBati.setText(batiFileName)
        fantoirFileName = s.value("cadastre/fantoirFileName", 'TOPFANR.800', type=str)
        if fantoirFileName:
            self.inMajicFantoir.setText(fantoirFileName)
        lotlocalFileName = s.value("cadastre/lotlocalFileName", 'REVD166.800', type=str)
        if lotlocalFileName:
            self.inMajicLotlocal.setText(lotlocalFileName)
        nbatiFileName = s.value("cadastre/nbatiFileName", 'REVNBAT.800', type=str)
        if nbatiFileName:
            self.inMajicNbati.setText(nbatiFileName)
        pdlFileName = s.value("cadastre/pdlFileName", 'REVFPDL.800', type=str)
        if pdlFileName:
            self.inMajicPdl.setText(pdlFileName)
        propFileName = s.value("cadastre/propFileName", 'REVPROP.800', type=str)
        if propFileName:
            self.inMajicProp.setText(propFileName)
        tempDir = s.value("cadastre/tempDir", '%s' % tempfile.gettempdir(), type=str)
        if tempDir:
            self.inTempDir.setText(tempDir)
        maxInsertRows = s.value("cadastre/maxInsertRows", 100000, type=int)
        if maxInsertRows:
            self.inMaxInsertRows.setValue(maxInsertRows)


    def onAccept(self):
        '''
        Save options when pressing OK button
        '''

        # Save Majic file names
        s = QSettings()
        s.setValue("cadastre/batiFileName", self.inMajicBati.text().strip(' \t\n\r'))
        s.setValue("cadastre/fantoirFileName", self.inMajicFantoir.text().strip(' \t\n\r'))
        s.setValue("cadastre/lotlocalFileName", self.inMajicLotlocal.text().strip(' \t\n\r'))
        s.setValue("cadastre/nbatiFileName", self.inMajicNbati.text().strip(' \t\n\r'))
        s.setValue("cadastre/pdlFileName", self.inMajicPdl.text().strip(' \t\n\r'))
        s.setValue("cadastre/propFileName", self.inMajicProp.text().strip(' \t\n\r'))

        # Save temp dir
        s.setValue("cadastre/tempDir", self.inTempDir.text().strip(' \t\n\r'))

        # Save maxInsertRows
        s.setValue("cadastre/maxInsertRows", int(self.inMaxInsertRows.value()))

        self.accept()

    def onReject(self):
        '''
        Run some actions when
        the user closes the dialog
        '''
        string = "cadastre option dialog closed"
        self.close()



# --------------------------------------------------------
#        About - Let the user display the about dialog
# --------------------------------------------------------

from cadastre_about_form import *

class cadastre_about_dialog(QDialog, Ui_cadastre_about_form):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        # common cadastre methods
        self.qc = cadastre_common(self)

        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        self.buttonBox.rejected.connect(self.onReject)
        self.buttonBox.accepted.connect(self.onAccept)

    def onAccept(self):
        '''
        Save options when pressing OK button
        '''
        self.accept()

    def onReject(self):
        '''
        Run some actions when
        the user closes the dialog
        '''
        self.close()


# --------------------------------------------------------
#        Parcelle - Show parcelle information
# --------------------------------------------------------

from cadastre_parcelle_form import *
from cadastre_export import *

class cadastre_parcelle_dialog(QDialog, Ui_cadastre_parcelle_form):
    def __init__(self, iface, layer, feature, cadastre_search_dialog):
        QDialog.__init__(self)
        self.iface = iface
        self.feature = feature
        self.layer = layer
        self.mc = iface.mapCanvas()
        self.setupUi(self)
        self.cadastre_search_dialog = cadastre_search_dialog

        # common cadastre methods
        self.qc = cadastre_common(self)

        # Get connection parameters
        connectionParams = self.qc.getConnectionParameterFromDbLayer(layer)
        if not connectionParams:
            return
        self.connectionParams = connectionParams
        self.dbType = connectionParams['dbType']
        self.schema = connectionParams['schema']
        connector = self.qc.getConnectorFromUri(connectionParams)
        self.connector = connector


        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        self.buttonBox.rejected.connect(self.onReject)
        self.buttonBox.accepted.connect(self.onAccept)
        # Export buttons
        exportButtons = {
            'parcelle' : self.btExportParcelle,
            'proprietaire': self.btExportProprietaire
        }
        for key, item in exportButtons.items():
            control = item
            slot = partial(self.exportAsPDF, key)
            control.clicked.connect(slot)

        # Parcelle action button
        self.btCentrer.clicked.connect(self.centerToParcelle)
        self.btZoomer.clicked.connect(self.zoomToParcelle)
        self.btSelectionner.clicked.connect(self.selectParcelle)

        # Select parcelle from proprietaire action
        self.btParcellesProprietaire.clicked.connect(self.selectParcellesProprietaire)


        # Check majic content
        self.hasMajicData = False
        self.checkMajicContent()

        # Set dialog content
        self.setParcelleContent()
        self.setProprietairesContent()


    def checkMajicContent(self):
        '''
        Check if database contains
        any MAJIC data
        '''

        sql = 'SELECT * FROM "proprietaire" LIMIT 1'
        if self.connectionParams['dbType'] == 'postgis':
            sql = self.qc.setSearchPath(sql, self.connectionParams['schema'])
        [header, data, rowCount] = self.qc.fetchDataFromSqlQuery(self.connector, sql)
        if rowCount >= 1:
            self.hasMajicData = True

    def setParcelleContent(self):
        '''
        Get data for the selected
        parcelle and set the dialog
        text content
        '''

        if self.hasMajicData:
            # Get parcelle info
            sql = '''
            SELECT
            c.libcom AS nomcommune, c.ccocom AS codecommune, p.dcntpa AS contenance,
            trim(p.dnvoiri || ' ' || trim(v.natvoi) || ' ' || v.libvoi) AS adresse,
            CASE
                    WHEN p.gurbpa = 'U' THEN 'Oui'
                    ELSE 'Non'
            END  AS urbain,
            ccosec || dnupla
            FROM parcelle p
            INNER JOIN commune c ON p.ccocom = c.ccocom
            INNER JOIN voie v ON v.voie = p.voie
            WHERE 2>1
            AND geo_parcelle = '%s'
            LIMIT 1
            ''' % self.feature['geo_parcelle']
        else:
            self.parcelleInfo.setText(u'<i>Les données MAJIC n\'ont pas été trouvées dans la base de données</i>')

            sql ='''
            SELECT c.tex2 AS nomcommune, c.idu AS codecommune, '' AS contenance,
            '' AS adresse,
            '' AS urbain,
            p.idu
            FROM geo_parcelle p INNER JOIN geo_commune c
            ON ST_Intersects(p.geom, c.geom)
            WHERE geo_parcelle = '%s'
            ''' % self.feature['geo_parcelle']

        if self.connectionParams['dbType'] == 'postgis':
            sql = self.qc.setSearchPath(sql, self.connectionParams['schema'])

        [header, data, rowCount] = self.qc.fetchDataFromSqlQuery(self.connector, sql)
        html = ''
        for line in data:
            html+= u'<h3>%s</h3>' % line[5]
            html+= u'<b>Commune :</b> %s (%s)<br/>' % (line[0], line[1])
            html+= u'<b>Surface géographique :</b> %s m²<br/>' % int(self.feature.geometry().area())
            html+= u'<b>Contenance :</b> %s m²<br/>' % line[2]
            html+= u'<b>Adresse :</b> %s<br/>' % line[3]
            html+= u'<b>Urbaine :</b> %s<br/>' % line[4]

        self.parcelleInfo.setText('%s' % html)


    def setProprietairesContent(self):
        '''
        Get proprietaires data
        and set the dialog content
        '''
        # Check for MAJIC DATA
        if not self.hasMajicData:
            self.proprietairesInfo.setText(u'Les données MAJIC n\'ont pas été trouvées dans la base de données')
            return

        # Get proprietaire info
        sql = u'''
        SELECT coalesce(ccodro_lib, '') || ' - ' || p.dnuper || ' - ' || trim(coalesce(p.dqualp, '')) || ' ' || trim(coalesce(p.ddenom, '')) || ' - ' ||trim(coalesce(p.dlign3, '')) || ' / ' || trim(coalesce(p.dlign4, '')) || trim(coalesce(p.dlign5, '')) || ' ' || trim(coalesce(p.dlign6, '')) ||
        CASE
          WHEN jdatnss IS NOT NULL
          THEN ' - Né(e) le ' || coalesce(to_char(jdatnss, 'dd/mm/YYYY'), '') || ' à ' || coalesce(p.dldnss, '')
          ELSE ''
        END
        FROM proprietaire p
        LEFT JOIN ccodro ON ccodro.ccodro = p.ccodro
        WHERE 2>1
        AND comptecommunal = '%s'
        ''' % self.feature['comptecommunal']
        if self.connectionParams['dbType'] == 'postgis':
            sql = self.qc.setSearchPath(sql, self.connectionParams['schema'])
        if self.connectionParams['dbType'] == 'spatialite':
            sql = self.qc.postgisToSpatialite(sql)

        [header, data, rowCount] = self.qc.fetchDataFromSqlQuery(self.connector, sql)
        html = ''
        for line in data:
            html+= u'%s<br>' % line[0]

        self.proprietairesInfo.setText('%s' % html)


    def exportAsPDF(self, key):
        '''
        Export the parcelle or proprietaire
        information as a PDF file
        '''
        if not self.hasMajicData:
            self.proprietairesInfo.setText(u'Pas de données de propriétaires dans la base')
            return

        if self.feature and self.connector:
            qe = cadastreExport(self, key, self.feature)
            qe.exportAsPDF()

    def centerToParcelle(self):
        '''
        Centre to parcelle feature
        '''
        if self.feature:
            # first get scale
            scale = self.mc.scale()
            extent = self.feature.geometry().boundingBox()

            # reproject extent if needed
            if self.mc.hasCrsTransformEnabled():
                crsDest = self.mc.mapRenderer().destinationCrs()
                layer = self.layer
                crsSrc = layer.crs()
                xform = QgsCoordinateTransform(crsSrc, crsDest)
                extent = xform.transform(extent)

            self.mc.setExtent(extent)

            # the set the scale back
            self.mc.zoomScale(scale)
            self.mc.refresh()

    def zoomToParcelle(self):
        '''
        Zoom to parcelle feature
        '''
        if self.feature:
            extent = self.feature.geometry().boundingBox()

            # reproject extent if needed
            if self.mc.hasCrsTransformEnabled():
                crsDest = self.mc.mapRenderer().destinationCrs()
                layer = self.layer
                crsSrc = layer.crs()
                xform = QgsCoordinateTransform(crsSrc, crsDest)
                extent = xform.transform(extent)

            self.mc.setExtent(extent)
            self.mc.refresh()

    def selectParcelle(self):
        '''
        Zoom to parcelle feature
        '''
        if self.layer and self.feature:
            self.layer.removeSelection()
            self.layer.select(self.feature.id())

    def selectParcellesProprietaire(self):
        '''
        Select all parcelles from this parcelle proprietaire.
        Use search class tools.
        Needs refactoring
        '''
        if not self.hasMajicData:
            self.proprietairesInfo.setText(u'Pas de données de propriétaires dans la base')
            return

        #~ qs = cadastre_search_dialog(self.iface)
        qs = self.cadastre_search_dialog
        key = 'proprietaire'
        value = self.feature['comptecommunal']
        filterExpression = "comptecommunal IN ('%s')" % value

        # Get data for child and fill combobox
        ckey = qs.searchComboBoxes[key]['search']['child']
        [layer, features] = qs.setupSearchCombobox(
            ckey,
            filterExpression,
            'sql'
        )

        # Set properties
        qs.searchComboBoxes[key]['layer'] = layer
        qs.searchComboBoxes[key]['features'] = features
        qs.searchComboBoxes[key]['chosenFeature'] = features

        # Select all parcelles from proprietaire
        qs.setSelectionToChosenSearchCombobox('proprietaire')


    def onAccept(self):
        '''
        Save options when pressing OK button
        '''
        self.accept()

    def onReject(self):
        '''
        Run some actions when
        the user closes the dialog
        '''
        self.close()

