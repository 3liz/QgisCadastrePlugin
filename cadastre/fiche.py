"""Description and HTML rendering of the tables of the fiche parcellaire.

The SQL queries only return data. The fields displayed, their labels, their formatting and the masking
of the sensitive data are described here, so that a field can be hidden or shown by an option.
The same HTML is used by the dialog of QGIS Desktop and by the GetHtml request of QGIS Server (Lizmap).

Example of a table with one line per owner::

    section = Section("proprietaires", "Propriétaires", [
        Field("Nom", "nom"),
        Field("Date de naissance", "date_naissance", sensitive="birth", mask=DATE_MASK, format=date_fr),
    ])
    rows = fetch_rows(connector, connection_params, "SELECT ... WHERE parcelle = {parcelle}", parcelle=parcelle)
    html = table_html(section, rows, DisplayOptions(sensitive=SensitiveData(birth=True)))
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

# CSS classes of the tables, used by the style sheets of QGIS and of Lizmap
TABLE_CLASS = 'class="table table-condensed table-striped" border=1 cellspacing=0 cellpadding=3 width="100%"'

# Replace a sensitive value which is not displayed, to show that the value exists
DEFAULT_MASK = "XXX"
DATE_MASK = "XX/XX/XXXX"

# A row of a SQL query: the name of the column and its value
Row = dict[str, str]


@dataclass
class Field:
    """A value displayed in the fiche: a column of a table, or a line of a list"""

    # Label displayed in the header of the column or at the beginning of the line
    label: str
    # Name of the column of the SQL query, it also identifies the field in the options
    name: str
    # Attribute of SensitiveData needed to display the value ("birth", "revenue" or "exoneration"),
    # otherwise an existing value is replaced by the mask
    sensitive: str | None = None
    mask: str = DEFAULT_MASK
    # Hidden by default, it can be shown by an option
    visible: bool = True
    # Not displayed when it is empty for all the rows, like a field of the older MAJIC formats
    optional: bool = False
    # Function converting the value of the column to the displayed text, like date_fr or surface
    format: Callable[[str], str] | None = None
    # Function computing the value from the whole row, instead of reading the column
    value: Callable[[Row], str] | None = None

    def raw(self, row: Row) -> str:
        """Return the value of the field in the row, before formatting and masking.

        :param row: A row of the SQL query.
        :return: The value, or an empty string if it is NULL.
        """
        if self.value:
            return self.value(row)
        value = row.get(self.name)
        return "" if value is None else str(value).strip()


@dataclass
class Section:
    """A table of the fiche, with its title and its fields"""

    # Identifies the section in the options, like "local.proprietaires"
    key: str
    # Title displayed above the table, nothing if it is empty
    title: str
    fields: list[Field] = field(default_factory=list)
    # "table": one line per row and one column per field,
    # "list": one line per field with its label and its value, for a single row
    layout: str = "table"


@dataclass(frozen=True)
class DisplayOptions:
    """Fields to hide or to show, and sensitive data which can be displayed.

    A field is identified by "<section key>.<field name>", like "local.pevs.co_vlbaia",
    and a whole section by its key, like "local.proprietaires".
    """

    sensitive: SensitiveData = field(default_factory=SensitiveData)
    # Fields or sections not displayed
    hidden: frozenset[str] = frozenset()
    # Fields hidden by default which are displayed
    shown: frozenset[str] = frozenset()

    def is_visible(self, section: Section, item: Field | None = None) -> bool:
        """Tell if a section, or a field of a section, is displayed according to the options.

        :param section: The section.
        :param item: A field of the section, or None for the section itself.
        :return: False if the section or the field is hidden by the options, or if the field
            is hidden by default and not shown by the options.
        """
        if section.key in self.hidden:
            return False
        if item is None:
            return True
        key = f"{section.key}.{item.name}"
        if key in self.hidden:
            return False
        return item.visible or key in self.shown

    def fields(self, section: Section, rows: list[Row]) -> list[Field]:
        """Return the fields of the section to display for these rows.

        The optional fields which are empty in all the rows are not displayed.

        :param section: The section.
        :param rows: The rows displayed in the table of the section.
        :return: The visible fields, in the order of the section.
        """
        return [
            f
            for f in section.fields
            if self.is_visible(section, f) and not (f.optional and not any(f.raw(row) for row in rows))
        ]

    def text(self, item: Field, row: Row) -> str:
        """Return the text of a field in a row, ready to be written in the HTML.

        An existing sensitive value which is not allowed is replaced by the mask of the field,
        otherwise the value is formatted, then escaped for HTML.

        :param item: The field.
        :param row: A row of the SQL query.
        :return: The HTML text, empty if the value is NULL.
        """
        value = item.raw(row)
        if value and item.sensitive and not getattr(self.sensitive, item.sensitive):
            return item.mask
        if value and item.format:
            value = item.format(value)
        return html.escape(value)


def table_html(section: Section, rows: list[Row], options: DisplayOptions, title_tag: str = "h4") -> str:
    """Build the HTML of a section: its title, then its table.

    :param section: The description of the table.
    :param rows: The rows of the SQL query. With the "list" layout, only the first one is displayed.
    :param options: The fields to display and the sensitive data allowed.
    :param title_tag: The HTML tag of the title, depending on the level of the section in the fiche.
    :return: The HTML, or an empty string if there is no row, or if the section is hidden.
    """
    if not rows or not options.is_visible(section):
        return ""
    fields = options.fields(section, rows)
    if not fields:
        return ""

    text = f"<{title_tag}>{html.escape(section.title)}</{title_tag}>" if section.title else ""
    text += f"<table {TABLE_CLASS}>"
    if section.layout == "list":
        # One line per field: the label in the first column, the value in the second one
        row = rows[0]
        for f in fields:
            text += f"<tr><th>{html.escape(f.label)}</th><td>{options.text(f, row)}</td></tr>"
    else:
        # A header with the labels, then one line per row
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
    """Execute a query of the fiche, in PostgreSQL or Spatialite, and return its rows.

    The query is written for PostgreSQL, without schema: the schema of the cadastre data is added
    to the search_path, or the query is converted for Spatialite.

    :param connector: The connection to the database.
    :param connection_params: The parameters of the connection: dbType, schema and srid.
    :param sql: The query, with placeholders like {parcelle} for the parameters.
    :param params: The values of the placeholders, they are quoted as SQL strings.
    :return: The rows as dictionaries, an empty list if the query fails, the error is logged.
    """
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


# Formatting of the MAJIC values, used as Field.format


def date_fr(value: str) -> str:
    """Write a date of MAJIC or of the database in the French format.

    :param value: A date like 13082013 (DDMMYYYY, in the MAJIC text fields) or 2013-08-13 (ISO).
    :return: The date like 13/08/2013, or the value itself if it is not a date.
    """
    if re.fullmatch(r"\d{8}", value):
        return f"{value[0:2]}/{value[2:4]}/{value[4:8]}"
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})", value)
    if match:
        return f"{match[3]}/{match[2]}/{match[1]}"
    return value


def number(value: str) -> str:
    """Write a number without the leading zeros of the MAJIC text fields, nor useless decimals.

    :param value: A number like "05", "1.00", "326.18" or "1500000".
    :return: The number like "5", "1", "326.18" or "1500000", or the value itself if it is not a number.
    """
    try:
        result = round(float(value), 2)
    except ValueError:
        return value
    if result.is_integer():
        return str(int(result))
    return f"{result:.2f}".rstrip("0")


def percent(value: str) -> str:
    """Write a percentage, like "50 %" """
    return f"{number(value)} %"


def surface(value: str) -> str:
    """Write a surface in square meters, like "135 m²" """
    return f"{number(value)} m²"


def yes_no(value: str) -> str:
    """Write the MAJIC codes O and N as "oui" and "non" """
    return {"O": "oui", "N": "non"}.get(value, value)


def codes(labels: dict[str, str], undefined: str = "indéterminé") -> Callable[[str], str]:
    """Create a format for a code of several characters, each character being a code of the labels.

    For instance, the materials of the walls are coded on 2 characters: "14" is "pierre, briques".

    :param labels: The labels of the codes of one character, "0" and spaces are ignored.
    :param undefined: The text when there is no code.
    :return: The function to use as Field.format.
    """

    def format_codes(value: str) -> str:
        names = [labels.get(c, c) for c in value if c not in " 0"]
        return ", ".join(names) if names else undefined

    return format_codes


def label(labels: dict[str, str]) -> Callable[[str], str]:
    """Create a format replacing a code by its label, or keeping the code if it is unknown.

    :param labels: The labels of the codes.
    :return: The function to use as Field.format.
    """

    def format_label(value: str) -> str:
        return labels.get(value, value)

    return format_label
