"""Layout items of the relevés de propriété and parcellaires.

Only native QGIS layout items are used (labels and manual tables), so that the PDF does not depend on
QtWebKit, which is not available in some QGIS builds, nor with Qt 6.
"""

__copyright__ = "Copyright 2026, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from dataclasses import dataclass, field
from pathlib import Path

from qgis.core import (
    Qgis,
    QgsLayout,
    QgsLayoutExporter,
    QgsLayoutFrame,
    QgsLayoutItem,
    QgsLayoutItemLabel,
    QgsLayoutItemManualTable,
    QgsLayoutMultiFrame,
    QgsLayoutPoint,
    QgsLayoutRenderContext,
    QgsLayoutSize,
    QgsLayoutTable,
    QgsPrintLayout,
    QgsTableCell,
    QgsTextFormat,
    QgsUnitTypes,
)
from qgis.PyQt.QtCore import QMarginsF, QSizeF, Qt
from qgis.PyQt.QtGui import QColor, QFont, QPageLayout, QPageSize, QPainter, QPdfWriter

GRID_COLOR = QColor("#323232")
ZEBRA_COLOR = QColor("#E2E2E2")
MM = QgsUnitTypes.LayoutUnit.LayoutMillimeters

# Resolution of the PDF, for the images and the effects: the texts and the tables are vectors
PDF_DPI = 300

CENTER = Qt.AlignmentFlag.AlignHCenter
LEFT = Qt.AlignmentFlag.AlignLeft
RIGHT = Qt.AlignmentFlag.AlignRight

# Cell margin and grid stroke, in mm, added by QGIS to the column widths
CELL_MARGIN = 0.3
GRID_STROKE = 0.2

# Height of the row of the titles of the columns, in mm
HEADER_HEIGHT = 7

# Sizes in points
TITLE_SIZE = 8
HEADER_SIZE = 5
CONTENT_SIZE = 5.5


@dataclass
class Column:
    """A column of a table: title, width in mm, alignment and names of the values from the SQL query"""

    title: str
    width: float
    names: list[str] = field(default_factory=list)
    align: Qt.AlignmentFlag = CENTER

    def value(self, row: dict[str, str]) -> str:
        return " ".join(row.get(name, "") for name in self.names).strip()


@dataclass
class Group:
    """Header above several columns, instead of merged cells"""

    title: str
    columns: int


def text_format(size: float, bold: bool = False, italic: bool = False) -> QgsTextFormat:
    font = QFont("Sans Serif")
    font.setBold(bold)
    font.setItalic(italic)
    text = QgsTextFormat()
    text.setFont(font)
    text.setSize(size)
    text.setSizeUnit(Qgis.RenderUnit.Points)
    text.setColor(QColor("black"))
    return text


def place(item: QgsLayoutItem, x: float, y: float, width: float, height: float):
    item.attemptMove(QgsLayoutPoint(x, y, MM))
    item.attemptResize(QgsLayoutSize(width, height, MM))


def add_label(
    layout: QgsLayout,
    text: str,
    rect: tuple[float, float, float, float],
    size: float = TITLE_SIZE,
    bold: bool = True,
    italic: bool = False,
    align: Qt.AlignmentFlag = CENTER,
) -> QgsLayoutItemLabel:
    label = QgsLayoutItemLabel(layout)
    label.setText(text)
    label.setTextFormat(text_format(size, bold, italic))
    label.setHAlign(align)
    label.setVAlign(Qt.AlignmentFlag.AlignVCenter)
    label.setMargin(0)
    layout.addLayoutItem(label)
    place(label, *rect)
    return label


def add_table(
    layout: QgsLayout,
    rect: tuple[float, float, float, float],
    rows: list[list[str]],
    widths: list[float],
    aligns: list[Qt.AlignmentFlag] | None = None,
    row_height: float | None = None,
    zebra: bool = False,
    grid: bool = True,
    size: float = CONTENT_SIZE,
    bold: bool = False,
    wrap: bool = False,
) -> QgsLayoutItemManualTable:
    """A manual table in a single frame, without header row.

    The widths and the row height are the total sizes of the cells, in mm, including margins and grid.
    Long texts are truncated, unless wrap is True. A row higher than the frame is not drawn.
    """
    table = QgsLayoutItemManualTable.create(layout)
    layout.addMultiFrame(table)
    table.setResizeMode(QgsLayoutMultiFrame.ResizeMode.UseExistingFrames)
    if wrap:
        table.setWrapBehavior(QgsLayoutTable.WrapBehavior.WrapText)
    else:
        table.setWrapBehavior(QgsLayoutTable.WrapBehavior.TruncateText)
    table.setCellMargin(CELL_MARGIN)
    table.setContentTextFormat(text_format(size, bold))
    table.setShowGrid(grid)
    table.setGridColor(GRID_COLOR)
    table.setGridStrokeWidth(GRID_STROKE)
    table.setBackgroundColor(QColor("white"))

    aligns = aligns or [CENTER] * len(widths)

    contents = []
    for i, row in enumerate(rows):
        cells = []
        for value, align in zip(row, aligns):
            cell = QgsTableCell(value)
            cell.setHorizontalAlignment(align)
            cell.setVerticalAlignment(Qt.AlignmentFlag.AlignVCenter)
            if zebra and i % 2 == 0:
                cell.setBackgroundColor(ZEBRA_COLOR)
            cells.append(cell)
        contents.append(cells)
    table.setTableContents(contents)
    # QGIS adds the cell margins and the grid to the width of each column
    table.setColumnWidths([max(w - 2 * CELL_MARGIN - GRID_STROKE, 1) for w in widths])
    if row_height:
        # Same for the height of each row: it is the total height, in mm
        table.setRowHeights([max(row_height - 2 * CELL_MARGIN - GRID_STROKE, 0.5)] * len(rows))

    frame = QgsLayoutFrame(layout, table)
    frame.setFrameEnabled(not grid)
    frame.setFrameStrokeColor(GRID_COLOR)
    table.addFrame(frame)
    # Room for the last grid stroke, and for rounding: a row higher than the frame would not be drawn
    x, y, width, height = rect
    place(frame, x, y, width, height + GRID_STROKE + 0.05)
    return table


def add_columns_table(
    layout: QgsLayout,
    x: float,
    y: float,
    title: str,
    groups: list[Group],
    columns: list[Column],
    rows: list[dict[str, str]],
    lines: int,
    row_height: float,
):
    """Title, header of groups of columns, then a table with one line per row, completed with empty lines"""
    width = sum(c.width for c in columns)
    add_label(layout, title, (x, y, width, 4))
    y += 4

    # Groups of columns, like merged cells
    group_widths = []
    start = 0
    for group in groups:
        group_widths.append(sum(c.width for c in columns[start : start + group.columns]))
        start += group.columns
    add_table(
        layout, (x, y, width, 3.5), [[g.title for g in groups]], group_widths, size=HEADER_SIZE, bold=True
    )
    y += 3.5

    # Titles of the columns, on 2 lines. A row higher than its frame would not be drawn.
    widths = [c.width for c in columns]
    add_table(
        layout,
        (x, y, width, HEADER_HEIGHT),
        [[c.title for c in columns]],
        widths,
        row_height=HEADER_HEIGHT,
        size=HEADER_SIZE,
        bold=True,
        wrap=True,
    )
    y += HEADER_HEIGHT

    values = [[c.value(row) for c in columns] for row in rows]
    values += [[""] * len(columns)] * (lines - len(values))
    add_table(
        layout,
        (x, y, width, lines * row_height),
        values,
        widths,
        aligns=[c.align for c in columns],
        row_height=row_height,
        zebra=True,
    )


def completed(columns: list[Column], width: float, flexible: str) -> list[Column]:
    """Give the remaining width to the flexible column"""
    used = sum(c.width for c in columns if c.title != flexible)
    for column in columns:
        if column.title == flexible:
            column.width = width - used
    return columns


ADRESSE = "ADRESSE"

BATI_GROUPS = [
    Group("DÉSIGNATION DES PROPRIÉTÉS", 5),
    Group("IDENTIFIANT DU LOCAL", 5),
    Group("ÉVALUATION DU LOCAL", 15),
]
BATI_COLUMNS = completed(
    [
        Column("SECTION", 9, ["section"]),
        Column("N° DE\nPLAN", 9, ["ndeplan"]),
        Column("N° DE\nVOIRIE", 9, ["ndevoirie"]),
        Column(ADRESSE, 0, ["adresse"], LEFT),
        Column("CODE\nRIVOLI", 10, ["coderivoli"]),
        Column("BAT", 6, ["bat"]),
        Column("ENT", 6, ["ent"]),
        Column("NIV", 6, ["niv"]),
        Column("N° DE\nPORTE", 10, ["ndeporte"]),
        Column("NUMÉRO\nINVAR", 18, ["numeroinvar"]),
        Column("S\nTAR", 6, ["star"]),
        Column("M\nEVAL", 7, ["meval"]),
        Column("AF", 6, ["af"]),
        Column("NAT\nLOC", 7, ["natloc"]),
        Column("CAT", 6, ["cat"]),
        Column("REVENU\nCADASTRAL", 15, ["revenucadastral"], RIGHT),
        Column("COLL", 7, ["coll"]),
        Column("NAT\nEXO", 8, ["natexo"]),
        Column("AN\nRET", 8, ["anret"]),
        Column("AN\nDEB", 8, ["andeb"]),
        Column("FRACTION\nRC EXO", 14, ["fractionrcexo"], RIGHT),
        Column("%\nEXO", 9, ["pourcentageexo"]),
        Column("TX\nOM", 8, ["txom"]),
        Column("COEF\nREDUC", 10, ["coefreduc"]),
        Column("RC\nTEOM", 12, ["rcteom"], RIGHT),
    ],
    290,
    ADRESSE,
)

NON_BATI_GROUPS = [
    Group("DÉSIGNATION DES PROPRIÉTÉS", 5),
    Group("IDENTIFIANT", 7),
    Group("ÉVALUATION", 8),
    Group("", 1),
]
NON_BATI_COLUMNS = completed(
    [
        Column("SECTION", 9, ["section"]),
        Column("N° DE\nPLAN", 9, ["ndeplan"]),
        Column("N° DE\nVOIRIE", 9, ["ndevoirie"]),
        Column(ADRESSE, 0, ["adresse"], LEFT),
        Column("CODE\nRIVOLI", 10, ["coderivoli"]),
        Column("N° PARC\nPRIM", 11, ["nparcprim"]),
        Column("FP/DP", 8, ["fpdp"]),
        Column("S\nTAR", 6, ["star"]),
        Column("SUF", 6, ["suf"]),
        Column("GR/\nSSGR", 9, ["grssgr"]),
        Column("CL", 6, ["cl"]),
        Column("NAT\nCULT", 9, ["natcult"]),
        Column("CONTENANCE\nHA A CA", 16, ["ha_contenance", "a_contenance", "ca_contenance"], RIGHT),
        Column("REVENU\nCADASTRAL", 15, ["revenucadastral"], RIGHT),
        Column("COLL", 7, ["coll"]),
        Column("NAT\nEXO", 8, ["natexo"]),
        Column("AN\nRET", 8, ["anret"]),
        Column("FRACTION\nRC EXO", 14, ["fractionrcexo"], RIGHT),
        Column("%\nEXO", 9, ["pourcentageexo"]),
        Column("TC", 6, ["tc"]),
        Column("LIVRE\nFONCIER", 14, ["lff"]),
    ],
    290,
    ADRESSE,
)


def export_layouts(layouts: list[QgsPrintLayout], path: Path | str, title: str) -> bool:
    """Write the layouts of one page each in a single PDF file, one page per layout.

    A layout of many pages is slow to export: the expression context of each of its items reads all
    its pages, and the time of exportToPdf grows like the cube of the number of pages. The relevés and
    the carte d'identité build one layout per page, written here in a single PDF.

    It is what QgsLayoutExporter.exportToPdf does for the pages of a single layout, with the same settings:
    vector output and texts kept as texts, so that they can be selected and searched in the PDF.

    :param layouts: The layouts, of one page each, all of the size of the first one.
    :param path: The PDF file.
    :param title: The title in the metadata of the PDF.
    :return: True if the file is written.
    """
    if not layouts:
        return False
    size = layouts[0].pageCollection().page(0).pageSize()
    writer = QPdfWriter(str(path))
    writer.setTitle(title)
    writer.setCreator("QGIS - Cadastre")
    writer.setResolution(PDF_DPI)
    writer.setPageLayout(
        QPageLayout(
            QPageSize(QSizeF(size.width(), size.height()), QPageSize.Unit.Millimeter),
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
