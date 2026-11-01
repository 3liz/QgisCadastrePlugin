"""Description and HTML rendering of the tables of the fiche parcellaire.

The SQL queries only return data. The fields displayed, their labels, their formatting and the masking
of the sensitive data are described here, so that a field can be hidden or shown by an option.
The same HTML is used by the dialog of QGIS Desktop and by the GetHtml request of QGIS Server (Lizmap).
"""

__copyright__ = "Copyright 2026, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import html
import re

from dataclasses import dataclass, field
from typing import Callable

from qgis.core import QgsAbstractDatabaseProviderConnection, QgsProviderConnectionException

from cadastre.cadastre_common_base import (
    SensitiveData,
    postgisToSpatialite,
    quoteString,
    rowsFromQgis,
    setSearchPath,
)
from cadastre.logger import Logger

TABLE_CLASS = 'class="table table-condensed table-striped" border=1 cellspacing=0 cellpadding=3 width="100%"'

DEFAULT_MASK = "XXX"
DATE_MASK = "XX/XX/XXXX"

Row = dict[str, str]


@dataclass
class Field:
    """A value displayed in the fiche"""

    label: str
    # Name of the column of the SQL query
    name: str
    # Attribute of SensitiveData needed to display the value, otherwise it is replaced by the mask
    sensitive: str | None = None
    mask: str = DEFAULT_MASK
    # Hidden by default, it can be shown by an option
    visible: bool = True
    # Not displayed when it is empty for all the rows, like a field of the older MAJIC formats
    optional: bool = False
    format: Callable[[str], str] | None = None
    # Function computing the value from the row, instead of reading the column
    value: Callable[[Row], str] | None = None

    def raw(self, row: Row) -> str:
        if self.value:
            return self.value(row)
        value = row.get(self.name)
        return "" if value is None else str(value).strip()


@dataclass
class Section:
    """A table of the fiche: one line per row, or label and value for a single row"""

    key: str
    title: str
    fields: list[Field] = field(default_factory=list)
    # "table": one line per row, "list": one line per field, for a single row
    layout: str = "table"


@dataclass(frozen=True)
class DisplayOptions:
    """Fields to hide or to show, and sensitive data which can be displayed.

    A field is identified by "<section key>.<field name>", a whole section by its key.
    """

    sensitive: SensitiveData = field(default_factory=SensitiveData)
    hidden: frozenset[str] = frozenset()
    shown: frozenset[str] = frozenset()

    def is_visible(self, section: Section, item: Field | None = None) -> bool:
        if section.key in self.hidden:
            return False
        if item is None:
            return True
        key = f"{section.key}.{item.name}"
        if key in self.hidden:
            return False
        return item.visible or key in self.shown

    def fields(self, section: Section, rows: list[Row]) -> list[Field]:
        return [
            f
            for f in section.fields
            if self.is_visible(section, f) and not (f.optional and not any(f.raw(row) for row in rows))
        ]

    def text(self, item: Field, row: Row) -> str:
        """The formatted value, masked if it is sensitive, as HTML"""
        value = item.raw(row)
        if value and item.sensitive and not getattr(self.sensitive, item.sensitive):
            return item.mask
        if value and item.format:
            value = item.format(value)
        return html.escape(value)


def table_html(section: Section, rows: list[Row], options: DisplayOptions, title_tag: str = "h4") -> str:
    """The title of the section and its table, nothing if the section is hidden or empty"""
    if not rows or not options.is_visible(section):
        return ""
    fields = options.fields(section, rows)
    if not fields:
        return ""

    text = f"<{title_tag}>{html.escape(section.title)}</{title_tag}>" if section.title else ""
    text += f"<table {TABLE_CLASS}>"
    if section.layout == "list":
        row = rows[0]
        for f in fields:
            text += f"<tr><th>{html.escape(f.label)}</th><td>{options.text(f, row)}</td></tr>"
    else:
        text += "<tr>" + "".join(f"<th>{html.escape(f.label)}</th>" for f in fields) + "</tr>"
        for row in rows:
            text += "<tr>" + "".join(f"<td>{options.text(f, row)}</td>" for f in fields) + "</tr>"
    return text + "</table>"


def fetch_rows(
    connector: QgsAbstractDatabaseProviderConnection,
    connection_params: dict[str, str],
    sql: str,
    **params: str,
) -> list[Row]:
    """Rows of a query as dictionaries, the parameters are quoted in the SQL"""
    sql = sql.format(**{name: quoteString(value) for name, value in params.items()})
    if connection_params["dbType"] == "postgis":
        sql = setSearchPath(sql, connection_params["schema"])
    else:
        sql = postgisToSpatialite(sql, connection_params.get("srid", "2154"))
    try:
        result = connector.execSql(sql)
        columns = result.columns()
        rows = rowsFromQgis(result.rows(), False)
    except QgsProviderConnectionException as e:
        Logger.critical(f"Error while fetching data from database : {e!s}")
        Logger.info(sql)
        return []
    return [dict(zip(columns, row)) for row in rows]


# Formatting of the MAJIC values


def date_fr(value: str) -> str:
    """DDMMYYYY or YYYY-MM-DD to DD/MM/YYYY"""
    if re.fullmatch(r"\d{8}", value):
        return f"{value[0:2]}/{value[2:4]}/{value[4:8]}"
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})", value)
    if match:
        return f"{match[3]}/{match[2]}/{match[1]}"
    return value


def number(value: str) -> str:
    """Without the leading zeros of the MAJIC text fields"""
    try:
        return f"{float(value):g}"
    except ValueError:
        return value


def percent(value: str) -> str:
    return f"{number(value)} %"


def surface(value: str) -> str:
    return f"{number(value)} m²"


def yes_no(value: str) -> str:
    return {"O": "oui", "N": "non"}.get(value, value)


def codes(labels: dict[str, str], undefined: str = "indéterminé") -> Callable[[str], str]:
    """A code of several characters, each one is a code of the labels, like the materials of the walls"""

    def format_codes(value: str) -> str:
        names = [labels.get(c, c) for c in value if c not in " 0"]
        return ", ".join(names) if names else undefined

    return format_codes


def label(labels: dict[str, str]) -> Callable[[str], str]:
    def format_label(value: str) -> str:
        return labels.get(value, value)

    return format_label
