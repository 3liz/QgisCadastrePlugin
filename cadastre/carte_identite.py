"""Carte d'identité de la parcelle: a short PDF summary of a parcel.

It contains the general information of the parcel, its owners, and a summary of its locaux, one line per local,
with its lot and its share in a copropriété, its surface, its category.
The data are those of the fiche parcellaire (cadastre/fiche_parcelle.py, cadastre/fiche_locaux.py), with the same
masks of the sensitive data: birth data, revenues and exonerations.

The PDF is a QGIS layout, like the relevés (cadastre/releve_layout.py): native labels and manual tables only.
The tables are paginated by this module: the height of each row is computed from its wrapped texts, so that
the sections follow each other on the pages and a table continues on the next page with its header.
"""

__copyright__ = "Copyright 2026, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import re

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from uuid import uuid4

from qgis.core import (
    Qgis,
    QgsAbstractDatabaseProviderConnection,
    QgsLayoutExporter,
    QgsLayoutFrame,
    QgsLayoutItemLabel,
    QgsLayoutItemManualTable,
    QgsLayoutMultiFrame,
    QgsLayoutPoint,
    QgsLayoutRenderContext,
    QgsLayoutSize,
    QgsLayoutTable,
    QgsLayoutUtils,
    QgsPrintLayout,
    QgsProject,
    QgsTableCell,
    QgsUnitTypes,
)
from qgis.PyQt.QtCore import QMarginsF, QSizeF, Qt
from qgis.PyQt.QtGui import QColor, QFont, QPageLayout, QPageSize, QPainter, QPdfWriter

from cadastre.cadastre_common_base import SensitiveData
from cadastre.fiche import (
    DATE_MASK,
    DisplayOptions,
    Field,
    Row,
    Section,
    date_fr,
    fetch_rows,
    load_sql,
    percent,
    surface,
)
from cadastre.releve_layout import (
    GRID_COLOR,
    GRID_STROKE,
    LEFT,
    MM,
    add_label,
    text_format,
)

# Resolution of the PDF, for the images and the effects: the texts and the tables are vectors
PDF_DPI = 300

# Page: A4 landscape, with its margins, in mm
PAGE_WIDTH = 297
PAGE_HEIGHT = 210
MARGIN = 10
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN

# Height of the header of each page (title and subtitle), and of the footer (page number), in mm
PAGE_HEADER_HEIGHT = 16
PAGE_FOOTER_HEIGHT = 6

# Sizes of the texts, in points
TITLE_SIZE = 14
SUBTITLE_SIZE = 8
SECTION_SIZE = 10
CONTENT_SIZE = 7

# Height of the title of a section, and space after a table, in mm
SECTION_TITLE_HEIGHT = 7
SECTION_SPACING = 4

# Colors of the titles, like the fiche parcellaire, and of the header of the tables
TITLE_COLOR = QColor("#43718c")
HEADER_BACKGROUND = QColor("#43718c")
HEADER_COLOR = QColor("white")

# Margin of the texts in the cells of the tables, in mm
CELL_MARGIN = 0.8

# Space between the lines of a wrapped text in a cell, as a factor of the height of the font
LINE_SPACING = 0.85

# Width of the first column of a table "list" (the labels), in mm
LIST_LABEL_WIDTH = 60
LIST_VALUE_WIDTH = 120


@dataclass
class Pev:
    """A partie d'évaluation (PEV) of a local, with the rows describing it"""

    # Row of fiche/locaux_pevs.sql
    values: Row
    habitations: list[Row] = field(default_factory=list)
    dependances: list[Row] = field(default_factory=list)
    professionnels: list[Row] = field(default_factory=list)
    exonerations: list[Row] = field(default_factory=list)


@dataclass
class LocalIdentite:
    """A local of the parcel, with its owners and its PEV for the carte identité"""

    # First row of fiche/locaux_carte_identite.sql for the local: the values of the local
    values: Row
    # Rows of fiche/locaux_carte_identite.sql: one per owner of the local
    proprietaires: list[Row] = field(default_factory=list)
    pevs: list[Pev] = field(default_factory=list)

    # @property
    # def destinataire(self) -> str:
    #     """Return the names of the owners receiving the tax notice, separated by commas"""
    #     names = [p["nom"] for p in self.proprietaires if p.get("destinataire") == "1" and p.get("nom")]
    #     return ", ".join(names)


def proprietaires(row: Row) -> str:
    """Return the names of the owners of a local, separated by commas"""
    return row.get("proprietaires", "")


def adresse(row: Row) -> str:
    """Return the adresse of the owners of a local, separated by commas"""
    return row.get("adresse", "")


def distinct(values: Sequence[str | None]) -> list[str]:
    """Return the non empty values, stripped, without duplicates, in their order.

    :param values: The values, None for a NULL value.
    :return: The distinct values.
    """
    result: list[str] = []
    for value in values:
        text = (value or "").strip()
        if text and text not in result:
            result.append(text)
    return result


def nom_adresse_invariant_cle(local: LocalIdentite) -> str:
    """Return the text of the first column of a local: its owners, then its invariant and its key.

    :param local: The local, with its owners.
    :return: The name and the address of each owner, one per line, then the invariant and the key.
    """
    lines: list[str] = []
    # Name, then address of each owner
    for owner in local.proprietaires:
        lines.extend(distinct([owner.get("nom"), owner.get("adresse")]))
    # Invariant and key of the local
    invariant = " ".join(distinct([local.values.get("invariant"), local.values.get("cle")]))
    if invariant:
        lines.append(invariant)
    return "\n".join(lines)


def demembrement_nature_occupation(local: LocalIdentite) -> str:
    """Return the text of the second column of a local: démembrement, nature du local and occupation.

    The démembrement and the occupation of the owners are written once, separated by commas.

    :param local: The local, with its owners.
    :return: The 3 values, one per line, "-" when there is no démembrement.
    """
    demembrements = distinct([owner.get("demembrement") for owner in local.proprietaires])
    occupations = distinct([owner.get("occupation") for owner in local.proprietaires])
    return "\n".join(
        [
            ", ".join(demembrements) or "-",
            (local.values.get("nature") or "").strip(),
            ", ".join(occupations),
        ]
    )


def valeur_locative(local: LocalIdentite) -> str:
    """Return the sum of the valeurs locatives of the PEV of a local, empty if it is unknown"""
    total = 0.0
    known = False
    for pev in local.pevs:
        try:
            total += float(pev.values.get("valeur_locative") or "")
            known = True
        except ValueError:
            continue
    return str(total) if known else ""


def categorie(local: LocalIdentite) -> str:
    """Return the categories of the PEV of a local, separated by commas, without duplicates"""
    values = []
    for pev in local.pevs:
        value = (pev.values.get("categorie") or "").strip()
        if value and value not in values:
            values.append(value)
    return ", ".join(values)


def exonerations(local: LocalIdentite) -> str:
    """Return the exonerations of the PEV of a local, like "Commune, Construction nouvelle, 2020-2022, 100 %" """
    texts = []
    for pev in local.pevs:
        for row in pev.exonerations:
            years = "-".join(v for v in (row.get("annee_debut"), row.get("annee_retour")) if v)
            taux = percent(str(row["taux"])) if row.get("taux") else ""
            text = ", ".join(v for v in (row.get("collectivite"), row.get("nature"), years, taux) if v)
            if text and text not in texts:
                texts.append(text)
    return " ; ".join(texts)


# Description of the tables. The general information of the parcel is the table of the fiche parcellaire.

PROPRIETAIRES = Section(
    "identite.proprietaires",
    "Ayant droits de la parcelle",
    [
        Field("Droit", "droit"),
        Field("Nom", "nom"),
        Field("Date de naissance", "date_naissance", sensitive="birth", mask=DATE_MASK, format=date_fr),
        Field("Lieu de naissance", "lieu_naissance", sensitive="birth"),
        Field("Numéro MAJIC", "code"),
        Field("Adresse", "adresse"),
    ],
)

# Width of the columns of the owners, in mm, in the order of the fields
# Sum must equal 277 mm
PROPRIETAIRES_WIDTHS: list[float] = [35, 90, 22, 35, 18, 77]

LOCAUX = Section(
    "identite.locaux",
    "Locaux",
    [
        Field("Adresse\nNuméro d'invariant + Clé", "nom_adresse_invariant_cle"),
        Field("Démembrement\nNature du local\nOccupation", "demembrement_nature_occupation"),
        Field("Lots", "lots", optional=True),
        Field("Surface", "surface", format=surface),
        # Field("Propriétaires", "proprietaires", value=proprietaires),
        # Field("Valeur locative", "valeur_locative", sensitive="revenue", format=number),
        # Field("Exonérations", "exonerations", sensitive="exoneration"),
        Field("Cat.", "categorie"),
        Field("Bât.", "batiment"),
        Field("Ent.", "entree"),
        Field("Niv.", "niveau"),
        Field("Porte", "porte"),
    ],
)

# Width of the columns of the locaux, in mm, by field name. The last columns share the remaining width.
# Sum must equal 277 mm
LOCAUX_WIDTHS: dict[str, float] = {
    "nom_adresse_invariant_cle": 105,
    "demembrement_nature_occupation": 87,
    "lots": 28,
    # "quote_part": 18,
    # "type": 20,
    # "nature": 24,
    "surface": 15,
    "categorie": 8,
    "batiment": 8,
    "entree": 8,
    "niveau": 8,
    "porte": 10,
}
LOCAUX_FLEXIBLE = ("nom_adresse_invariant_cle", "demembrement_nature_occupation")


@dataclass
class CarteIdentite:
    """Data of the carte d'identité of a parcel"""

    # Identifier of the parcel, like 1320290000A0107
    parcelle: str
    # Row of fiche/parcelle_majic.sql
    values: Row
    # Rows of fiche/proprietaires.sql
    proprietaires: list[Row] = field(default_factory=list)
    # One row per local
    locaux: list[Row] = field(default_factory=list)


def load_locaux(
    connector: QgsAbstractDatabaseProviderConnection, connection_params: dict[str, str], parcelle: str
) -> list[LocalIdentite]:
    """Read the locaux of the parcel, with their owners, their PEV and the descriptions of the PEV.

    Each query returns the rows of one level for the whole parcel, they are attached to their local
    or to their PEV by their identifier (local10 or pev).

    :param connector: The connection to the database.
    :param connection_params: The parameters of the connection, see fetch_rows.
    :param parcelle: The identifier of the parcel, like 1320290000A0107.
    :return: The locaux, in the order of the building, the entrance, the level and the door.
    """

    def fetch(name: str) -> list[Row]:
        return fetch_rows(connector, connection_params, load_sql(f"fiche/{name}"), parcelle=parcelle)

    # The locaux, by their identifier local10: the query returns one row per owner of each local
    locaux: dict[str, LocalIdentite] = {}
    for row in fetch("locaux_carte_identite"):
        local = locaux.setdefault(row["local10"], LocalIdentite(row))
        local.proprietaires.append(row)
    # The owners of each local in the order of their number in the compte communal
    for local in locaux.values():
        local.proprietaires.sort(key=lambda owner: owner.get("numero") or "")

    # The PEV, by their identifier pev, attached to their local
    pevs = {}
    for row in fetch("locaux_pevs"):
        if row["local10"] in locaux:
            pevs[row["pev"]] = Pev(row)
            locaux[row["local10"]].pevs.append(pevs[row["pev"]])
    # The rows describing the PEV, attached to their PEV
    for name, attribute in (
        ("locaux_habitations", "habitations"),
        ("locaux_dependances", "dependances"),
        ("locaux_professionnels", "professionnels"),
        ("locaux_exonerations", "exonerations"),
    ):
        for row in fetch(name):
            if row["pev"] in pevs:
                getattr(pevs[row["pev"]], attribute).append(row)

    return list(locaux.values())


def local_row(local: LocalIdentite) -> Row:
    """Return the row of a local in the carte d'identité: its values and the values computed from its PEV"""
    return {
        **local.values,
        "nom_adresse_invariant_cle": nom_adresse_invariant_cle(local),
        "demembrement_nature_occupation": demembrement_nature_occupation(local),
        "categorie": categorie(local),
    }


def load_carte_identite(
    connector: QgsAbstractDatabaseProviderConnection, connection_params: dict[str, str], parcelle: str
) -> CarteIdentite | None:
    """Read the data of the carte d'identité of a parcel, with the MAJIC data.

    :param connector: The connection to the database.
    :param connection_params: The parameters of the connection, see fetch_rows.
    :param parcelle: The identifier of the parcel, like 1320290000A0107.
    :return: The data, None if the parcel is not found.
    """
    rows = fetch_rows(connector, connection_params, load_sql("fiche/parcelle_majic"), parcelle=parcelle)
    if not rows:
        return None
    owners = fetch_rows(connector, connection_params, load_sql("fiche/proprietaires"), parcelle=parcelle)
    # locaux = fetch_rows(connector, connection_params, load_sql("fiche/locaux_carte_identite"), parcelle=parcelle)
    locaux = [local_row(local) for local in load_locaux(connector, connection_params, parcelle)]
    return CarteIdentite(parcelle, rows[0], owners, locaux)


# Layout


def content_font() -> QFont:
    """Font of the content of the tables"""
    return text_format(CONTENT_SIZE).toQFont()


def colored(label: QgsLayoutItemLabel) -> None:
    """Write a title in the color of the titles of the fiche parcellaire"""
    title_format = label.textFormat()
    title_format.setColor(TITLE_COLOR)
    label.setTextFormat(title_format)


def wrapped_lines(text: str, width: float, font: QFont) -> int:
    """Return the number of lines of a text wrapped in a cell of the given width.

    :param text: The text.
    :param width: The width of the text in the cell, in mm.
    :param font: The font of the text.
    :return: The number of lines, at least 1.
    """
    lines = 0
    for paragraph in (text or "").split("\n"):
        lines += 1
        current = ""
        for word in paragraph.split():
            candidate = f"{current} {word}".strip()
            if current and QgsLayoutUtils.textWidthMM(font, candidate) > width:
                lines += 1
                current = word
            else:
                current = candidate
    return max(lines, 1)


class PageWriter:
    """Write the sections of the carte d'identité one after the other, adding the pages when needed.

    Each page is a layout of one page: the expression context of each item of a layout reads all its
    pages, and the export of a layout of many pages took minutes, its time growing like the cube of
    the number of pages. See export_layouts to write them in a single PDF.
    """

    def __init__(self, project: QgsProject, title: str, subtitle: str) -> None:
        """
        :param project: The project of the layouts.
        :param title: The title written at the top of each page.
        :param subtitle: The subtitle written below the title.
        """
        self.project = project
        self.title = title
        self.subtitle = subtitle
        self.font = content_font()
        self.line_height = QgsLayoutUtils.fontHeightMM(self.font) * LINE_SPACING
        # The pages, the last one is the current page
        self.layouts: list[QgsPrintLayout] = []
        self.y = 0.0
        self.new_page()

    @property
    def layout(self) -> QgsPrintLayout:
        """The layout of the current page"""
        return self.layouts[-1]

    @property
    def bottom(self) -> float:
        """Bottom of the content of a page, in mm from its top"""
        return PAGE_HEIGHT - MARGIN - PAGE_FOOTER_HEIGHT

    def new_page(self) -> None:
        """Add a page, with the header: title and subtitle"""
        layout = QgsPrintLayout(self.project)
        layout.setName(f"cadastre_carte_identite_{uuid4().hex}")
        layout.initializeDefaults()
        layout.setUnits(QgsUnitTypes.LayoutUnit.LayoutMillimeters)
        layout.pageCollection().page(0).setPageSize(QgsLayoutSize(PAGE_WIDTH, PAGE_HEIGHT, MM))
        self.layouts.append(layout)

        colored(add_label(layout, self.title, (MARGIN, MARGIN, CONTENT_WIDTH, 8), size=TITLE_SIZE, align=LEFT))
        add_label(
            layout, self.subtitle, (MARGIN, MARGIN + 8, CONTENT_WIDTH, 5), size=SUBTITLE_SIZE, bold=False,
            italic=True, align=LEFT,
        )
        self.y = MARGIN + PAGE_HEADER_HEIGHT

    def ensure(self, height: float) -> None:
        """Start a new page if the height does not fit in the current one"""
        if self.y + height > self.bottom:
            self.new_page()

    def section_title(self, text: str, next_height: float) -> None:
        """Write the title of a section, on a new page if it would be alone at the bottom of the page.

        :param text: The title.
        :param next_height: The height of the beginning of the section, kept with its title.
        """
        self.ensure(SECTION_TITLE_HEIGHT + next_height)
        colored(
            add_label(
                self.layout, text, (MARGIN, self.y, CONTENT_WIDTH, SECTION_TITLE_HEIGHT), size=SECTION_SIZE, align=LEFT
            )
        )
        self.y += SECTION_TITLE_HEIGHT

    def row_height(self, values: list[str], widths: Sequence[float]) -> float:
        """Return the height of the content of a row, in mm, without the margins of the cells"""
        lines = max(
            wrapped_lines(value, width - 2 * CELL_MARGIN - GRID_STROKE, self.font)
            for value, width in zip(values, widths)
        )
        return lines * self.line_height

    def add_rows(
        self, rows: list[list[str]], widths: Sequence[float], heights: list[float], header: bool = False
    ) -> None:
        """Add a manual table with these rows at the current position, the rows must fit in the page.

        :param rows: The texts of the cells.
        :param widths: The total widths of the columns, in mm.
        :param heights: The heights of the content of the rows, in mm, see row_height.
        :param header: True for the header of a table: bold texts on a grey background.
        """
        table = QgsLayoutItemManualTable.create(self.layout)
        self.layout.addMultiFrame(table)
        table.setResizeMode(QgsLayoutMultiFrame.ResizeMode.UseExistingFrames)
        table.setWrapBehavior(QgsLayoutTable.WrapBehavior.WrapText)
        table.setCellMargin(CELL_MARGIN)
        table.setContentTextFormat(text_format(CONTENT_SIZE, bold=header))
        table.setShowGrid(True)
        table.setGridColor(GRID_COLOR)
        table.setGridStrokeWidth(GRID_STROKE)
        table.setBackgroundColor(QColor("white"))
        contents = []
        for values in rows:
            cells = []
            for idx, value in enumerate(values):
                cell = QgsTableCell(value)
                cell.setVerticalAlignment(Qt.AlignmentFlag.AlignVCenter)
                cell.setHorizontalAlignment(Qt.AlignmentFlag.AlignHCenter)
                if idx < 2:
                    cell.setHorizontalAlignment(Qt.AlignmentFlag.AlignLeft)
                if header:
                    cell.setBackgroundColor(HEADER_BACKGROUND)
                    cell.setForegroundColor(HEADER_COLOR)
                    cell.setForegroundColor(HEADER_COLOR)
                cells.append(cell)
            contents.append(cells)
        table.setTableContents(contents)
        # QGIS adds the cell margins and the grid to the width of each column and to the height of each row
        table.setColumnWidths([max(w - 2 * CELL_MARGIN - GRID_STROKE, 1) for w in widths])
        table.setRowHeights(heights)

        frame = QgsLayoutFrame(self.layout, table)
        frame.setFrameEnabled(False)
        table.addFrame(frame)
        height = sum(h + 2 * CELL_MARGIN + GRID_STROKE for h in heights) + GRID_STROKE
        # Room for rounding: a row higher than the frame would not be drawn
        frame.attemptMove(QgsLayoutPoint(MARGIN, self.y, MM))
        frame.attemptResize(QgsLayoutSize(sum(widths), height + 0.05, MM))
        self.y += height

    def table(self, header: list[str], rows: list[list[str]], widths: Sequence[float]) -> None:
        """Write a table: its header, then its rows, continued on the next pages with the header.

        :param header: The titles of the columns, None for a table without header.
        :param rows: The texts of the cells.
        :param widths: The total widths of the columns, in mm.
        """
        header_height = self.row_height(header, widths) if header else 0.0
        heights = [self.row_height(values, widths) for values in rows]

        def total(content_height: float) -> float:
            return content_height + 2 * CELL_MARGIN + GRID_STROKE

        start = 0
        while start < len(rows):
            # The header and at least one row on the page
            needed = (total(header_height) if header else 0) + total(heights[start])
            self.ensure(needed)
            if header:
                self.add_rows([header], widths, [header_height], header=True)
            available = self.bottom - self.y
            end = start
            used = 0.0
            while end < len(rows) and (end == start or used + total(heights[end]) <= available):
                used += total(heights[end])
                end += 1
            self.add_rows(rows[start:end], widths, heights[start:end])
            start = end
        self.y += SECTION_SPACING

    def footer(self) -> None:
        """Write the page numbers, once all the pages exist"""
        count = len(self.layouts)
        for i, layout in enumerate(self.layouts):
            add_label(
                layout,
                f"Page {i + 1} / {count}",
                (MARGIN, PAGE_HEIGHT - MARGIN - 4, CONTENT_WIDTH, 4),
                size=SUBTITLE_SIZE,
                bold=False,
                align=Qt.AlignmentFlag.AlignRight,
            )


def section_values(section: Section, rows: list[Row], options: DisplayOptions) -> tuple[list[Field], list[list[str]]]:
    """Return the visible fields of a section and the texts of the rows, with the masks of the sensitive data"""
    fields = options.fields(section, rows)
    return fields, [[options.plain_text(f, row) for f in fields] for row in rows]


def build_layouts(project: QgsProject, carte: CarteIdentite, sensitive: SensitiveData) -> list[QgsPrintLayout]:
    """Build the pages of the carte d'identité of a parcel, one layout per page, see PageWriter.

    :param project: The project of the layouts.
    :param carte: The data of the parcel.
    :param sensitive: The sensitive data written, the others are masked like in the fiche parcellaire.
    :return: The layouts of the pages, as many as needed.
    """
    options = DisplayOptions(sensitive=sensitive)

    values = carte.values
    title = f"Carte d'identité de la parcelle {(values.get('code') or carte.parcelle).strip()}"
    if values.get("commune"):
        title += f" - {values['commune']}"
    subtitle = f"Parcelle {carte.parcelle}"
    if values.get("annee"):
        subtitle += f" - Données MAJIC {values['annee']}"
    subtitle += f" - Édité le {date.today().strftime('%d/%m/%Y')}"
    subtitle += f"\nAdresse : {values['adresse']} - Contenance : {values['contenance']} m² - Bâti : {values['pourcentage_bati']} %"
    writer = PageWriter(project, title, subtitle)

    # Owners
    fields, rows = section_values(PROPRIETAIRES, carte.proprietaires, options)
    widths = [PROPRIETAIRES_WIDTHS[PROPRIETAIRES.fields.index(f)] for f in fields]
    if rows:
        writer.section_title(PROPRIETAIRES.title, 3 * writer.line_height)
        writer.table([f.label for f in fields], rows, widths)

    # Locaux
    count = len(carte.locaux)
    if not count:
        writer.section_title("Locaux", writer.line_height)
        writer.table([], [["La parcelle ne contient aucun local"]], [CONTENT_WIDTH])
    else:
        fields, rows = section_values(LOCAUX, carte.locaux, options)
        fixed = sum(LOCAUX_WIDTHS.get(f.name, 0) for f in fields)
        flexible = [f for f in fields if f.name in LOCAUX_FLEXIBLE]
        share = (CONTENT_WIDTH - fixed) / len(flexible) if flexible else 0
        widths = [LOCAUX_WIDTHS.get(f.name, share) for f in fields]
        writer.section_title(f"Locaux ({count})", 3 * writer.line_height)
        writer.table([f.label for f in fields], rows, widths)

    writer.footer()
    return writer.layouts


def export_carte_identite(
    project: QgsProject,
    connector: QgsAbstractDatabaseProviderConnection,
    connection_params: dict[str, str],
    parcelle: str,
    directory: Path,
    sensitive: SensitiveData,
) -> Path | None:
    """Write the PDF of the carte d'identité of a parcel.

    :param project: The project of the layout.
    :param connector: The connection to the database, with the MAJIC data.
    :param connection_params: The parameters of the connection, see fetch_rows.
    :param parcelle: The identifier of the parcel.
    :param directory: The directory of the PDF file.
    :param sensitive: The sensitive data written, the others are masked.
    :return: The path of the PDF file, None if the parcel is not found or if the export failed.
    """
    carte = load_carte_identite(connector, connection_params, parcelle)
    if carte is None:
        return None
    layouts = build_layouts(project, carte, sensitive)
    name = re.sub(r"[^0-9A-Za-z_-]", "", f"carte_identite_{parcelle}_{uuid4().hex[:8]}")
    path = directory / f"{name}.pdf"
    if not export_layouts(layouts, path, f"Carte d'identité de la parcelle {parcelle}"):
        return None
    return path


def export_layouts(layouts: list[QgsPrintLayout], path: Path, title: str) -> bool:
    """Write the layouts of one page each in a single PDF file, one page per layout.

    It is what QgsLayoutExporter.exportToPdf does for the pages of a single layout, with the same settings:
    vector output and texts kept as texts, so that they can be selected and searched in the PDF.

    :param layouts: The layouts, of one page of PAGE_WIDTH x PAGE_HEIGHT each.
    :param path: The PDF file.
    :param title: The title in the metadata of the PDF.
    :return: True if the file is written.
    """
    writer = QPdfWriter(str(path))
    writer.setTitle(title)
    writer.setCreator("QGIS - Cadastre")
    writer.setResolution(PDF_DPI)
    writer.setPageLayout(
        QPageLayout(
            QPageSize(QSizeF(PAGE_WIDTH, PAGE_HEIGHT), QPageSize.Unit.Millimeter),
            QPageLayout.Orientation.Portrait,
            QMarginsF(0, 0, 0, 0),
        )
    )
    painter = QPainter()
    if not painter.begin(writer):
        return False
    try:
        for i, layout in enumerate(layouts):
            # The settings of exportToPdf
            context = layout.renderContext()
            context.setDpi(PDF_DPI)
            context.setFlag(QgsLayoutRenderContext.Flag.FlagForceVectorOutput, True)
            context.setTextRenderFormat(Qgis.TextRenderFormat.AlwaysText)
            if i > 0:
                writer.newPage()
            QgsLayoutExporter(layout).renderPage(painter, 0)
    finally:
        painter.end()
    return True
