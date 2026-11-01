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

import re
import sqlite3
import unicodedata

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from qgis.core import (
    Qgis,
    QgsAbstractDatabaseProviderConnection,
    QgsDataSourceUri,
    QgsMapLayer,
    QgsMessageLog,
    QgsProject,
    QgsProviderConnectionException,
    QgsProviderRegistry,
)
from qgis.PyQt.QtCore import QDate, QDateTime, Qt, QTime, QUrl, QVariant
from qgis.PyQt.QtGui import QDesktopServices
from qgis.utils import spatialite_connect

from cadastre.tools import plugin_path


@dataclass(frozen=True)
class SensitiveData:
    """Sensitive data written in the relevés and the fiche parcellaire.

    Without the access, an existing value is replaced by a mask like XX/XX/XXXX or XXX.
    """

    # Date and place of birth of the owners
    birth: bool = False
    # Revenus cadastraux, valeurs locatives and bases d'imposition
    revenue: bool = False
    # Exonérations: nature, collectivité, years, percentage and exonerated revenue
    exoneration: bool = False

    @classmethod
    def full(cls) -> "SensitiveData":
        return cls(birth=True, revenue=True, exoneration=True)


def hasSpatialiteSupport() -> bool:
    """
    Check whether or not
    spatialite support is ok
    """
    return QgsProviderRegistry.instance().providerMetadata("spatialite") is not None


def openFile(filename: str) -> None:
    """
    Opens a file with default system app
    """
    p = Path(filename).expanduser().resolve()
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(p)))


def getLayerFromLegendByTableProps(
    project: QgsProject, table_name: str, geom_col: str = "geom", sql: str = ""
) -> QgsMapLayer | None:
    """
    Get the layer from QGIS legend
    corresponding to a database
    table name (postgis or sqlite)
    """
    _ = sql
    for _, layer in list(project.mapLayers().items()):
        if not hasattr(layer, "providerType"):
            continue

        if hasattr(layer, "type") and layer.type() != QgsMapLayer.LayerType.VectorLayer:
            # Ignore this layer as it's not a vector
            # QgsMapLayer.VectorLayer is an equivalent to QgsMapLayerType.VectorLayer since 3.8
            continue

        if layer.providerType() not in ("postgres", "spatialite"):
            # Ignore this layer as it's not a postgres or spatialite vector layer
            continue

        connection_params = getConnectionParameterFromDbLayer(layer)

        reg = r"(\.| )?(%s)" % table_name
        if (
            connection_params
            and (
                connection_params["table"] == table_name
                or (
                    re.findall(reg, "%s" % connection_params["table"])
                    and re.findall(reg, "%s" % connection_params["table"])[0]
                )
            )
            and connection_params["geocol"] == geom_col
        ):
            # and connectionParams['sql'] == sql:
            return layer

    return None


def getConnectionParameterFromDbLayer(layer: QgsMapLayer) -> dict[str, str]:
    """
    Get connection parameters
    from the layer datasource
    """
    if layer.providerType() == "postgres":
        dbType = "postgis"
    else:
        dbType = "spatialite"

    src = layer.source()
    uri = QgsDataSourceUri(src)

    # TODO Use immutable namedtuple
    return {
        "service": uri.service(),
        "dbname": uri.database(),
        "host": uri.host(),
        "port": uri.port(),
        "user": uri.username(),
        "password": uri.password(),
        "sslmode": uri.sslMode(),
        "authcfg": uri.authConfigId(),
        "key": uri.keyColumn(),
        "estimatedmetadata": str(uri.useEstimatedMetadata()),
        "checkPrimaryKeyUnicity": "",
        "srid": uri.srid(),
        "type": uri.wkbType(),
        "schema": uri.schema(),
        "table": uri.table(),
        "geocol": uri.geometryColumn(),
        "sql": uri.sql(),
        "dbType": dbType,
    }


def setSearchPath(sql: str, schema: str) -> str:
    """
    Set the search_path parameters if postgis database
    """
    prefix = 'SET search_path = "%s", public, pg_catalog;' % schema
    if re.search("^BEGIN;", sql):
        sql = sql.replace("BEGIN;", "BEGIN;%s" % prefix)
    else:
        sql = prefix + sql

    return sql


def quoteString(value: str) -> str:
    """
    Quote a string value for a SQL query (PostgreSQL and SQLite)
    """
    return "'{}'".format(str(value).replace("'", "''"))


def rowsFromQgis(rows: list[list[Any]], as_string: bool) -> list[list[Any]]:
    """
    Convert the values returned by QgsAbstractDatabaseProviderConnection.executeSql:
    NULL becomes None, and when as_string is True (PostgreSQL), values are converted to strings
    like the db_manager plugin was doing.
    """
    result = []
    for row in rows:
        values = []
        for value in row:
            if value is None or (isinstance(value, QVariant) and value.isNull()):
                value = None
            elif isinstance(value, (QDateTime, QDate, QTime)):
                value = value.toString(Qt.DateFormat.ISODate)
            elif as_string:
                value = str(value)
            values.append(value)
        result.append(values)
    return result


def sqliteRegexp(pattern: str, item: str | None) -> bool:
    """REGEXP function for SQLite, used by the SQL queries and scripts"""
    try:
        return re.search(pattern, item or "", re.IGNORECASE) is not None
    except re.error as err:
        QgsMessageLog.logMessage(
            f"Invalid regular expression {pattern} : {err!s}", "cadastre", Qgis.MessageLevel.Critical
        )
        return False


def executeSql(
    connector: QgsAbstractDatabaseProviderConnection, sql: str
) -> tuple[list[str], list[list[Any]]]:
    """Execute an SQL query and return its columns and its rows.

    With Spatialite, the query is run with a Python sqlite3 connection, like CadastreDatabase does:
    the QGIS connection drops the integer primary key columns (ogc_fid, rowid) from the results,
    because they become the feature ids (issue #598).

    :param connector: The QGIS connection to the database.
    :param sql: The query.
    :return: The names of the columns and the rows.
    :raises QgsProviderConnectionException: If the query fails.
    """
    if connector.providerKey() != "spatialite":
        result = connector.execSql(sql)
        return result.columns(), result.rows()

    connection = spatialite_connect(QgsDataSourceUri(connector.uri()).database())
    try:
        connection.create_function("regexp", 2, sqliteRegexp)
        cursor = connection.execute(sql)
        columns = [description[0] for description in cursor.description or []]
        return columns, [list(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        raise QgsProviderConnectionException(str(e)) from e
    finally:
        connection.close()


def fetchDataFromSqlQuery(connector: QgsAbstractDatabaseProviderConnection, sql: str) -> list[Any]:
    """
    Execute an SQL query and
    return [data, rowCount, ok]
    """
    data = []
    row_count = 0
    ok = True
    try:
        _columns, rows = executeSql(connector, str(sql))
        data = rowsFromQgis(rows, connector.providerKey() == "postgres")
        row_count = len(data)

    except QgsProviderConnectionException as e:
        ok = False
        QgsMessageLog.logMessage(
            f"Error while fetching data from database : {e!s}", "cadastre", Qgis.MessageLevel.Critical
        )
        QgsMessageLog.logMessage(sql, "cadastre", Qgis.MessageLevel.Info)

    return [data, row_count, ok]


def getConnectorFromUri(connectionParams: dict[str, str]) -> QgsAbstractDatabaseProviderConnection | None:
    """
    Get a QGIS database connection
    for the given database type
    and parameters
    """
    uri = QgsDataSourceUri()
    if connectionParams["dbType"] == "postgis":
        provider = "postgres"
        if connectionParams["service"]:
            uri.setConnection(
                connectionParams["service"],
                connectionParams["dbname"],
                connectionParams["user"],
                connectionParams["password"],
                connectionParams["sslmode"],
                connectionParams.get("authcfg", ""),
            )
        else:
            uri.setConnection(
                connectionParams["host"],
                connectionParams["port"],
                connectionParams["dbname"],
                connectionParams["user"],
                connectionParams["password"],
                connectionParams["sslmode"],
                connectionParams.get("authcfg", ""),
            )
    else:
        provider = "spatialite"
        uri.setDatabase(connectionParams["dbname"])

    try:
        return QgsProviderRegistry.instance().providerMetadata(provider).createConnection(uri.uri(False), {})
    except QgsProviderConnectionException as e:
        QgsMessageLog.logMessage(
            f"Erreur lors de la connexion à la base de données : {e!s}",
            "cadastre",
            Qgis.MessageLevel.Critical,
        )
        return None


def normalizeString(s: str) -> str:
    """
    Removes all accents from
    the given string and
    replace e dans l'o
    """
    p = re.compile("(œ)")
    s = p.sub("oe", s)

    s = unicodedata.normalize("NFD", s)
    b = s.encode("ascii", "ignore")
    s = b.decode().upper().strip(" \t\n")
    r = re.compile(r"[^ -~]")
    s = r.sub(" ", s)
    return s.replace("'", " ")


def postgisToSpatialite(sql: str, targetSrid: str = "2154") -> str:
    """
    Convert postgis SQL statement
    into spatialite compatible
    statements
    """

    # delete some incompatible options
    # replace other by spatialite syntax
    replaceDict = [
        # delete
        {"in": r"with\(oids=.+\)", "out": ""},
        {"in": r"comment on [^;]+;", "out": ""},
        {
            "in": r"alter table ([^;]+) add primary key( )+\(([^;]+)\);",
            "out": r"create index idx_\1_\3 on \1 (\3);",
        },
        {
            "in": r"alter table ([^;]+) add constraint [^;]+ primary key( )+\(([^;]+)\);",
            "out": r"create index idx_\1_\3 on \1 (\3);",
        },
        {"in": r"alter table [^;]+drop column[^;]+;", "out": ""},
        {"in": r"alter table [^;]+drop constraint[^;]+;", "out": ""},
        # ~ {'in': r'^analyse [^;]+;', 'out': ''},
        # replace
        {
            "in": r"truncate (bati|lloc|nbat|pdll|prop)",
            "out": r"drop table if exists \1;create table \1 (tmp text)",
        },
        {"in": r"truncate topo", "out": r"delete from topo"},
        {"in": r"truncate ", "out": "delete from "},
        {"in": r"distinct on *\([a-z, ]+\)", "out": "distinct"},
        {"in": r"serial", "out": "INTEGER PRIMARY KEY AUTOINCREMENT"},
        {"in": r"string_agg", "out": "group_concat"},
        {"in": r"current_schema::text, ", "out": ""},
        {"in": r"add column if not exists", "out": "add column"},
        {"in": r"substring", "out": "SUBSTR"},
        {"in": r"(to_char\()([^']+) *, *'[09]+' *\)", "out": r"CAST(\2 AS TEXT)"},
        {"in": r"(to_number\()([^']+) *, *'[09]+' *\)", "out": r"CAST(\2 AS float)"},
        {
            "in": r"(to_date\()([^']+) *, *'DDMMYYYY' *\)",
            "out": r"date(substr(\2, 5, 4) || '-' || substr(\2, 3, 2) || '-' || substr(\2, 1, 2))",
        },
        {
            "in": r"(to_date\()([^']+) *, *'DD/MM/YYYY' *\)",
            "out": r"date(substr(\2, 7, 4) || '-' || substr(\2, 4, 2) || '-' || substr(\2, 1, 2))",
        },
        {"in": r"(to_char\()(.+), 'DDD'\)", "out": r"strftime('%j', \2)"},
        {
            "in": r"(to_date\()([^']+) *, *'YYYYMMDD' *\)",
            "out": r"date(substr(\2, 1, 4) || '-' || substr(\2, 5, 2) || '-' || substr(\2, 7, 2))",
        },
        {"in": r"(to_char\()([^']+) *, *'dd/mm/YYYY' *\)", "out": r"strftime('%d/%m/%Y', \2)"},
        {
            "in": r"ST_MakeValid\(geom\)",
            "out": r"CASE WHEN ST_IsValid(geom) THEN geom ELSE ST_Buffer(geom,0) END",
        },
        {
            "in": r"ST_MakeValid\(p\.geom\)",
            "out": r"CASE WHEN ST_IsValid(p.geom) THEN p.geom ELSE ST_Buffer(p.geom,0) END",
        },
        {"in": r" ~ ", "out": " regexp "},
    ]

    for a in replaceDict:
        r = re.compile(a["in"], re.IGNORECASE | re.MULTILINE)
        sql = r.sub(a["out"], sql)

    # index spatiaux
    r = re.compile(
        r"(create index [^;]+ ON )([^;]+)( USING +)(gist +)?\(([^;]+)\);", re.IGNORECASE | re.MULTILINE
    )
    sql = r.sub(r"SELECT createSpatialIndex('\2', '\5');", sql)

    # replace postgresql "update from" statement
    r = re.compile(r"(update [^;=]+)(=)([^;=]+ FROM [^;]+)(;)", re.IGNORECASE | re.MULTILINE)
    sql = r.sub(r"\1=(SELECT \3);", sql)

    return sql  # noqa: RET504


def postgisToSpatialiteLocal10(sql: str, dataYear: str) -> str:
    # majic formatage : replace multiple column update for loca10
    r = re.compile(r"update local10 set[^;]+;", re.IGNORECASE | re.MULTILINE)
    res = r.findall(sql)
    replaceBy = ""
    for statement in res:
        replaceBy = """
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
        """
        replaceBy = replaceBy.replace("?", dataYear)
        sql = sql.replace(statement, replaceBy)

    return sql


def getCompteCommunalFromParcelleId(
    parcelleId: str, connectionParams: dict[str, str], connector: QgsAbstractDatabaseProviderConnection
) -> str | None:
    comptecommunal = None

    sql = "SELECT comptecommunal FROM parcelle WHERE parcelle = '%s'" % parcelleId
    if connectionParams["dbType"] == "postgis":
        sql = setSearchPath(sql, connectionParams["schema"])
    data, _, ok = fetchDataFromSqlQuery(connector, sql)
    if ok:
        for line in data:
            comptecommunal = line[0]
            break
    return comptecommunal


def getProprietaireComptesCommunaux(
    comptecommunal: str,
    connectionParams: dict[str, str],
    connector: QgsAbstractDatabaseProviderConnection,
    allCities: bool = True,
) -> list[str]:
    """
    Get the list of "comptecommunal" for all cities
    for a owner given one single comptecommunal
    """

    sql = " SELECT trim(ddenom) AS k, MyStringAgg(comptecommunal, ',') AS cc, dnuper"
    sql += " FROM proprietaire p"
    sql += " WHERE 2>1"
    sql += (
        " AND trim(p.ddenom) IN (SELECT trim(ddenom) FROM proprietaire WHERE comptecommunal = '%s')"
        % comptecommunal
    )
    if not allCities:
        sql += " AND substr(comptecommunal, 1, 6) = substr('%s', 1, 6)" % comptecommunal
    sql += " GROUP BY dnuper, ddenom, dlign4"
    sql += " ORDER BY ddenom"

    if connectionParams["dbType"] == "postgis":
        sql = setSearchPath(sql, connectionParams["schema"])
        sql = sql.replace("MyStringAgg", "string_agg")
    if connectionParams["dbType"] == "spatialite":
        sql = sql.replace("MyStringAgg", "group_concat")

    data, _, ok = fetchDataFromSqlQuery(connector, sql)
    ccs: list[str] = []
    if ok:
        for line in data:
            ccs = ccs + line[1].split(",")
    # deduplicate
    return list(set(ccs))


def getItemHtml(
    item: str,
    feature: dict,
    connectionParams: dict[str, str],
    connector: QgsAbstractDatabaseProviderConnection,
    sensitive: SensitiveData | None = None,
) -> str:
    """
    Build Html for a item (parcelle, proprietaires, etc.)
    based on SQL query
    """
    sensitive = sensitive or SensitiveData()
    html = ""

    if item == "locaux":
        # The tables are described in Python, not in the SQL query
        from cadastre.fiche import DisplayOptions
        from cadastre.fiche_locaux import load_locaux, locaux_html

        locaux = load_locaux(connector, connectionParams, feature["geo_parcelle"])
        return locaux_html(locaux, DisplayOptions(sensitive=sensitive))

    infos = {
        "parcelle_majic": {"label": "Parcelle"},
        "parcelle_simple": {"label": "Parcelle"},
        "proprietaires": {"label": "Propriétaires"},
        "indivisions": {"label": "Détails"},
        "subdivisions": {"label": "Subdivisions fiscales"},
        "subdivisions_exoneration": {"label": "Exonérations"},
    }
    info = infos[item]

    sqlfile = "templates/parcelle_info_%s.sql" % item
    with open(plugin_path(sqlfile), encoding="utf8") as sqltemplate:
        if item in ("proprietaires", "indivisions", "subdivisions"):
            sql = sqltemplate.read().format(
                parcelle_id=feature["geo_parcelle"],
                birth=sensitive.birth,
                revenue=sensitive.revenue,
                exoneration=sensitive.exoneration,
            )
        else:
            sql = sqltemplate.read() % feature["geo_parcelle"]
    if not sql:
        html += "Impossible de lire le SQL dans le fichier %s" % sqlfile
        return html

    if connectionParams["dbType"] == "postgis":
        sql = setSearchPath(sql, connectionParams["schema"])
    if connectionParams["dbType"] == "spatialite":
        sql = postgisToSpatialite(sql, connectionParams["srid"])
    data, _, ok = fetchDataFromSqlQuery(connector, sql)
    # print sql

    if ok:
        if item == "indivisions":
            html += "<h3>" + info["label"] + "</h3>"
        else:
            html += "<h2>" + info["label"] + "</h2>"
        for line in data:
            # print info['label']
            # print line
            if line and len(line) > 0 and line[0]:
                if item == "indivisions":
                    html += "<br>"
                html += f"""
                    {line[0].replace("100p", "100%")}
                """

    return html
