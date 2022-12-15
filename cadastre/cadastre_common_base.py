"""
Cadastre - Dialog classeas

This plugins helps users to import the french land registry ('cadastre')
into a database. It is meant to ease the use of the data in QGIs
by providing search tools and appropriate layer symbology.

begin     : 2013-06-11
copyright : (C) 2013,2019 by 3liz
email     : info@3liz.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

"""
import os
import re
import sys

from pathlib import Path
from typing import Any, Dict, List, Union

from db_manager.db_plugins.plugin import BaseError, ConnectionError
from db_manager.db_plugins.postgis.connector import (
    DBConnector,
    PostGisDBConnector,
)
from qgis.core import (
    Qgis,
    QgsDataSourceUri,
    QgsMapLayer,
    QgsMessageLog,
    QgsProject,
)
from qgis.PyQt.QtCore import QObject


def hasSpatialiteSupport() -> bool:
    """
    Check whether or not
    spatialite support is ok
    """
    try:
        from db_manager.db_plugins.spatialite.connector import (  # NOQA
            SpatiaLiteDBConnector,
        )
        return True
    except ImportError:
        return False
        pass


def openFile(filename: str) -> None:
    """
    Opens a file with default system app
    """
    import subprocess
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])


def getLayerFromLegendByTableProps(
        project: QgsProject, table_name: str, geom_col: str = 'geom', sql: str = ''
            ) -> Union[None, QgsMapLayer]:
    """
    Get the layer from QGIS legend
    corresponding to a database
    table name (postgis or sqlite)
    """
    _ = sql
    for _, layer in list(project.mapLayers().items()):

        if not hasattr(layer, 'providerType'):
            continue

        if hasattr(layer, 'type') and layer.type() != QgsMapLayer.VectorLayer:
            # Ignore this layer as it's not a vector
            # QgsMapLayer.VectorLayer is an equivalent to QgsMapLayerType.VectorLayer since 3.8
            continue

        if not layer.providerType() in ('postgres', 'spatialite'):
            # Ignore this layer as it's not a postgres or spatialite vector layer
            continue

        connection_params = getConnectionParameterFromDbLayer(layer)

        reg = r'(\.| )?(%s)' % table_name
        if connection_params and \
                ( \
                                connection_params['table'] == table_name or \
                                (re.findall(reg, '%s' % connection_params['table']) and
                                 re.findall(reg, '%s' % connection_params['table'])[0]) \
                        ) and \
                connection_params['geocol'] == geom_col:
            # and connectionParams['sql'] == sql:
            return layer

    return None


def getConnectionParameterFromDbLayer(layer: QgsMapLayer) -> Dict[str, str]:
    """
    Get connection parameters
    from the layer datasource
    """
    connectionParams = None

    if layer.providerType() == 'postgres':
        dbType = 'postgis'
    else:
        dbType = 'spatialite'

    src = layer.source()
    uri = QgsDataSourceUri(src)

    # TODO Use immutable namedtuple
    connectionParams = {
        'service': uri.service(),
        'dbname': uri.database(),
        'host': uri.host(),
        'port': uri.port(),
        'user': uri.username(),
        'password': uri.password(),
        'sslmode': uri.sslMode(),
        'key': uri.keyColumn(),
        'estimatedmetadata': str(uri.useEstimatedMetadata()),
        'checkPrimaryKeyUnicity': '',
        'srid': uri.srid(),
        'type': uri.wkbType(),
        'schema': uri.schema(),
        'table': uri.table(),
        'geocol': uri.geometryColumn(),
        'sql': uri.sql(),
        'dbType': dbType
    }

    return connectionParams


def setSearchPath(sql: str, schema: str) -> str:
    """
    Set the search_path parameters if postgis database
    """
    prefix = 'SET search_path = "%s", public, pg_catalog;' % schema
    if re.search('^BEGIN;', sql):
        sql = sql.replace('BEGIN;', 'BEGIN;%s' % prefix)
    else:
        sql = prefix + sql

    return sql


def fetchDataFromSqlQuery(connector: 'DBConnector',
                          sql: str) -> List[Any]:
    """
    Execute an SQL query and
    return [data, rowCount, ok]
    NB: commit qgis/QGIS@14ab5eb changes QGIS DBmanager behaviour
    """
    data = []
    row_count = 0
    c = None
    ok = True
    try:
        c = connector._execute(None, str(sql))
        data = connector._fetchall(c)
        row_count = len(data)

    except BaseError as e:
        ok = False
        QgsMessageLog.logMessage(
            "Error while fetching data from database : {}".format(str(e.msg)),
            "cadastre",
            Qgis.Critical
        )
        QgsMessageLog.logMessage(sql, "cadastre", Qgis.Info)

    finally:
        if c:
            c.close()
            del c

    return [data, row_count, ok]


def getConnectorFromUri(connectionParams: Dict[str, str]) -> 'DBConnector':
    """
    Set connector property
    for the given database type
    and parameters
    """
    connector = None
    uri = QgsDataSourceUri()
    if connectionParams['dbType'] == 'postgis':
        if connectionParams['host']:
            uri.setConnection(
                connectionParams['host'],
                connectionParams['port'],
                connectionParams['dbname'],
                connectionParams['user'],
                connectionParams['password']
            )
        if connectionParams['service']:
            uri.setConnection(
                connectionParams['service'],
                connectionParams['dbname'],
                connectionParams['user'],
                connectionParams['password']
            )

        if Qgis.QGIS_VERSION_INT >= 31200:
            # we need a fake DBPlugin object
            # with connectionName and providerName methods
            obj = QObject()
            obj.connectionName = lambda: 'fake'
            obj.providerName = lambda: 'postgres'

            connector = PostGisDBConnector(uri, obj)
        else:
            connector = PostGisDBConnector(uri)

    if connectionParams['dbType'] == 'spatialite':
        uri.setConnection('', '', connectionParams['dbname'], '', '')
        if hasSpatialiteSupport():
            from db_manager.db_plugins.spatialite.connector import (
                SpatiaLiteDBConnector,
            )

            # Il y a bug évident ici si il n'y pas le support spatialite, quid de SpatiaLiteDBConnector ?
        try:
            connector = SpatiaLiteDBConnector(uri)
        except ConnectionError as e:
            QgsMessageLog.logMessage(
                "Erreur lors de la récupération du fichier SQLite : {}".format(str(e)),
                'cadastre',
                Qgis.Critical)

    return connector


def postgisToSpatialite(sql: str, targetSrid: str = '2154') -> str:
    """
    Convert postgis SQL statement
    into spatialite compatible
    statements
    """

    # delete some incompatible options
    # replace other by spatialite syntax
    replaceDict = [
        # delete
        {'in': r'with\(oids=.+\)', 'out': ''},
        {'in': r'comment on [^;]+;', 'out': ''},
        {'in': r'alter table ([^;]+) add primary key( )+\(([^;]+)\);',
         'out': r'create index idx_\1_\3 on \1 (\3);'},
        {'in': r'alter table ([^;]+) add constraint [^;]+ primary key( )+\(([^;]+)\);',
         'out': r'create index idx_\1_\3 on \1 (\3);'},
        {'in': r'alter table [^;]+drop column[^;]+;', 'out': ''},
        {'in': r'alter table [^;]+drop constraint[^;]+;', 'out': ''},
        # ~ {'in': r'^analyse [^;]+;', 'out': ''},
        # replace
        {'in': r'truncate (bati|fanr|lloc|nbat|pdll|prop)',
         'out': r'drop table \1;create table \1 (tmp text)'},
        {'in': r'truncate ', 'out': 'delete from '},
        {'in': r'distinct on *\([a-z, ]+\)', 'out': 'distinct'},
        {'in': r'serial', 'out': 'INTEGER PRIMARY KEY AUTOINCREMENT'},
        {'in': r'string_agg', 'out': 'group_concat'},
        {'in': r'current_schema::text, ', 'out': ''},
        {'in': r'substring', 'out': 'SUBSTR'},
        {'in': r"(to_char\()([^']+) *, *'[09]+' *\)", 'out': r"CAST(\2 AS TEXT)"},
        {'in': r"(to_number\()([^']+) *, *'[09]+' *\)", 'out': r"CAST(\2 AS float)"},
        {'in': r"(to_date\()([^']+) *, *'DDMMYYYY' *\)",
         'out': r"date(substr(\2, 5, 4) || '-' || substr(\2, 3, 2) || '-' || substr(\2, 1, 2))"},
        {'in': r"(to_date\()([^']+) *, *'DD/MM/YYYY' *\)",
         'out': r"date(substr(\2, 7, 4) || '-' || substr(\2, 4, 2) || '-' || substr(\2, 1, 2))"},
        {'in': r"(to_date\()([^']+) *, *'YYYYMMDD' *\)",
         'out': r"date(substr(\2, 1, 4) || '-' || substr(\2, 5, 2) || '-' || substr(\2, 7, 2))"},
        {'in': r"(to_char\()([^']+) *, *'dd/mm/YYYY' *\)",
         'out': r"strftime('%d/%m/%Y', \2)"},
        {'in': r"ST_MakeValid\(geom\)",
         'out': r"CASE WHEN ST_IsValid(geom) THEN geom ELSE ST_Buffer(geom,0) END"},
        {'in': r"ST_MakeValid\(p\.geom\)",
         'out': r"CASE WHEN ST_IsValid(p.geom) THEN p.geom ELSE ST_Buffer(p.geom,0) END"},
        {'in': r' ~ ', 'out': ' regexp '}
    ]

    for a in replaceDict:
        r = re.compile(a['in'], re.IGNORECASE | re.MULTILINE)
        sql = r.sub(a['out'], sql)

    # index spatiaux
    r = re.compile(r'(create index [^;]+ ON )([^;]+)( USING +)(gist +)?\(([^;]+)\);', re.IGNORECASE | re.MULTILINE)
    sql = r.sub(r"SELECT createSpatialIndex('\2', '\5');", sql)

    # replace postgresql "update from" statement
    r = re.compile(r'(update [^;=]+)(=)([^;=]+ FROM [^;]+)(;)', re.IGNORECASE | re.MULTILINE)
    sql = r.sub(r'\1=(SELECT \3);', sql)

    return sql


def postgisToSpatialiteLocal10(sql: str, dataYear: str) -> str:
    # majic formatage : replace multiple column update for loca10
    r = re.compile(r'update local10 set[^;]+;', re.IGNORECASE | re.MULTILINE)
    res = r.findall(sql)
    replaceBy = ''
    for statement in res:
        replaceBy = '''
        DROP TABLE IF EXISTS ll;
        CREATE TABLE ll AS
        SELECT DISTINCT l.invar, l.ccopre , l.ccosec, l.dnupla, l.ccoriv, l.ccovoi, l.dnvoiri,
        l10.ccodep || l10.ccodir || l10.invar AS local00,
        REPLACE(l10.ccodep || l10.ccodir || l10.ccocom || l.ccopre || l.ccosec || l.dnupla,' ', '0') AS parcelle,
        REPLACE(l10.ccodep || l10.ccodir || l10.ccocom || l.ccovoi,' ', '0') AS voie
        FROM local00 l
        INNER JOIN local10 AS l10 ON l.invar = l10.invar AND l.annee = l10.annee
        WHERE l10.annee='?';
        CREATE INDEX  idx_ll_invar ON ll (invar);
        UPDATE local10 SET ccopre = (SELECT DISTINCT ll.ccopre FROM ll WHERE ll.invar = local10.invar)
        WHERE local10.annee = '?';
        UPDATE local10 SET ccosec = (SELECT DISTINCT ll.ccosec FROM ll WHERE ll.invar = local10.invar)
        WHERE local10.annee = '?';
        UPDATE local10 SET dnupla = (SELECT DISTINCT ll.dnupla FROM ll WHERE ll.invar = local10.invar)
        WHERE local10.annee = '?';
        UPDATE local10 SET ccoriv = (SELECT DISTINCT ll.ccoriv FROM ll WHERE ll.invar = local10.invar)
        WHERE local10.annee = '?';
        UPDATE local10 SET ccovoi = (SELECT DISTINCT ll.ccovoi FROM ll WHERE ll.invar = local10.invar)
        WHERE local10.annee = '?';
        UPDATE local10 SET dnvoiri = (SELECT DISTINCT ll.dnvoiri FROM ll WHERE ll.invar = local10.invar)
        WHERE local10.annee = '?';
        UPDATE local10 SET local00 = (SELECT DISTINCT ll.local00 FROM ll WHERE ll.invar = local10.invar)
        WHERE local10.annee = '?';
        UPDATE local10 SET parcelle = (SELECT DISTINCT ll.parcelle FROM ll WHERE ll.invar = local10.invar)
        WHERE local10.annee = '?';
        UPDATE local10 SET voie = (SELECT DISTINCT ll.voie FROM ll WHERE ll.invar = local10.invar)
        WHERE local10.annee = '?';
        DROP TABLE ll;
        '''
        replaceBy = replaceBy.replace('?', dataYear)
        sql = sql.replace(statement, replaceBy)

    return sql


def getCompteCommunalFromParcelleId(parcelleId: str, connectionParams: Dict[str, str],
                                    connector: 'DBConnector') -> Union[str, None]:
    comptecommunal = None

    sql = "SELECT comptecommunal FROM parcelle WHERE parcelle = '%s'" % parcelleId
    if connectionParams['dbType'] == 'postgis':
        sql = setSearchPath(sql, connectionParams['schema'])
    data, _, ok = fetchDataFromSqlQuery(connector, sql)
    if ok:
        for line in data:
            comptecommunal = line[0]
            break
    return comptecommunal


def getProprietaireComptesCommunaux(comptecommunal: str, connectionParams: Dict[str, str],
                                    connector: 'DBConnector', allCities: bool = True) -> List[str]:
    """
    Get the list of "comptecommunal" for all cities
    for a owner given one single comptecommunal
    """

    sql = " SELECT trim(ddenom) AS k, MyStringAgg(comptecommunal, ',') AS cc, dnuper"
    sql += " FROM proprietaire p"
    sql += " WHERE 2>1"
    sql += " AND trim(p.ddenom) IN (SELECT trim(ddenom) FROM proprietaire WHERE comptecommunal = '%s')" % comptecommunal
    if not allCities:
        sql += " AND substr(comptecommunal, 1, 6) = substr('%s', 1, 6)" % comptecommunal
    sql += " GROUP BY dnuper, ddenom, dlign4"
    sql += " ORDER BY ddenom"

    if connectionParams['dbType'] == 'postgis':
        sql = setSearchPath(sql, connectionParams['schema'])
        sql = sql.replace('MyStringAgg', 'string_agg')
    if connectionParams['dbType'] == 'spatialite':
        sql = sql.replace('MyStringAgg', 'group_concat')

    data, _, ok = fetchDataFromSqlQuery(connector, sql)
    ccs = []
    if ok:
        for line in data:
            ccs = ccs + line[1].split(',')
    # deduplicate
    ret = list(set(ccs))
    return ret


def getItemHtml(item: str, feature, connectionParams: Dict[str, str],
                connector: 'DBConnector', for_third_party: bool = False) -> str:
    """
    Build Html for a item (parcelle, proprietaires, etc.)
    based on SQL query
    """
    html = ''
    plugin_dir = str(Path(__file__).resolve().parent)

    infos = {
        'parcelle_majic': {
            'label': 'Parcelle'
        },
        'parcelle_simple': {
            'label': 'Parcelle'
        },
        'proprietaires': {
            'label': 'Propriétaires'
        },
        'indivisions': {
            'label': 'Détails'
        },
        'subdivisions': {
            'label': 'Subdivisions fiscales'
        },
        'subdivisions_exoneration': {
            'label': 'Exonérations'
        },
        'locaux': {
            'label': 'Locaux'
        },
        'locaux_detail': {
            'label': 'Locaux : informations détaillées'
        }
    }
    info = infos[item]

    sqlfile = 'templates/parcelle_info_%s.sql' % item
    with open(os.path.join(plugin_dir, sqlfile), encoding='utf8') as sqltemplate:
        if item == 'proprietaires' or item == 'locaux_detail':
            sql = sqltemplate.read().format(parcelle_id=feature['geo_parcelle'], not_for_third_part=(not for_third_party))
        else:
            sql = sqltemplate.read() % feature['geo_parcelle']
    if not sql:
        html += 'Impossible de lire le SQL dans le fichier %s' % sqlfile
        return html

    if connectionParams['dbType'] == 'postgis':
        sql = setSearchPath(sql, connectionParams['schema'])
    if connectionParams['dbType'] == 'spatialite':
        sql = postgisToSpatialite(sql, connectionParams['srid'])
    data, _, ok = fetchDataFromSqlQuery(connector, sql)
    # print sql

    if ok:
        html += '<h2>' + info['label'] + '</h2>'
        for line in data:
            # print info['label']
            # print line
            if line and len(line) > 0 and line[0]:
                if item == "indivisions":
                    html += '<br>'
                html += '%s' % line[0].replace('100p', '100%')

    return html
