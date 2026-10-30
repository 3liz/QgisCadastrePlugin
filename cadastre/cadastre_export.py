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

import math
import os
import tempfile

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Generator, List
from uuid import uuid4

from qgis.core import (
    Qgis,
    QgsExpression,
    QgsFeatureRequest,
    QgsFillSymbol,
    QgsLayoutExporter,
    QgsLayoutGridSettings,
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
from qgis.PyQt.QtCore import QRectF, QSettings

import cadastre.cadastre_common_base as cadastre_common
import cadastre.releve_layout as releve_layout

from .tools import plugin_path


@contextmanager
def _printProgress(_this, nb: int) -> Generator[Callable[[int], None], None, None]:
    """Define a dummy defaultprint progress"""
    yield (lambda step: None)


# Height of a line of the main tables, in mm: 15 lines are displayed in the zone of each table
ROW_HEIGHT = 3.3


class CadastreExport:
    def __init__(
        self,
        project: QgsProject,
        layer: QgsMapLayer,
        etype: str,
        comptecommunal: str | list[str],
        geo_parcelle: str | None = None,
        target_dir: str | None = None,
        for_third_party: bool = False,
    ) -> None:
        self.print_parcelle_page = False

        if not hasattr(self, "mProgress"):
            self.mProgress = _printProgress

        # Store project from context
        self.mProject = project

        # Store an instance of QgsComposition
        self.currentComposition: QgsPrintLayout | None = None

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

        # Several comptes communaux: one PDF for each
        self.isMulti: bool = False
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
        tempDir = s.value("cadastre/tempDir", type=str)
        if not tempDir or not Path(tempDir).exists():
            tempDir = tempfile.gettempdir()
        if not target_dir or not os.path.exists(target_dir):
            self.targetDir = tempfile.mkdtemp("", "cad_export_", tempDir)
        else:
            self.targetDir = target_dir

        # label for header2
        if self.etype == "proprietaire":
            self.typeLabel = "DE PROPRIÉTÉ"
        else:
            self.typeLabel = "PARCELLAIRE"

        self.layer = layer
        self.connectionParams = cadastre_common.getConnectionParameterFromDbLayer(self.layer)
        self.connector = cadastre_common.getConnectorFromUri(self.connectionParams)
        self.dbType = self.connectionParams["dbType"]

        # Variable created in set_composer_templates
        self.main_tables: dict[str, Any] = {}

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
        compte_communal_abrev = compte_communal[-6:]
        self.composerTemplates = {
            "header1": {
                "names": ["annee", "ccodep", "ccodir", "ccocom", "libcom"],
                "position": [3.5, 2.5, 145, 7.5],
                "keepContent": True,
                "type": "sql",
                "filter": "comptecommunal",
                "and": {
                    "proprietaire": f" AND comptecommunal = '{compte_communal}'",
                    "parcelle": f" AND comptecommunal = '{compte_communal}'",
                },
                "sticky": True,
            },
            "header2": {
                "names": ["type"],
                "position": [153.5, 2.5, 60, 7.5],
                "keepContent": True,
                "type": "properties",
                "source": [self.typeLabel],
                "sticky": True,
            },
            "header3": {
                "names": ["comptecommunal"],
                "position": [218.5, 2.5, 75, 7.5],
                "keepContent": True,
                "type": "properties",
                "source": [compte_communal_abrev],
                "sticky": True,
            },
            "proprietaires": {
                "names": ["lines"],
                "position": [3.5, 10, 290, 40],
                "keepContent": False,
                "type": "parent",
                "source": "proprietaires_line",
            },
            "proprietes_baties": {
                "names": ["lines"],
                "position": [3.5, 50, 290, 65],
                "keepContent": False,
                "type": "parent",
                "source": "proprietes_baties_line",
            },
            "proprietes_baties_sum": {
                "names": [
                    "revenucadastral",
                    "co_vlbaia",
                    "co_bipevla",
                    "gp_vlbaia",
                    "gp_bipevla",
                    "de_vlbaia",
                    "de_bipevla",
                    "re_vlbaia",
                    "re_bipevla",
                ],
                "position": [3.5, 115, 290, 15],
                "type": "sql",
                "keepContent": True,
                "filter": "comptecommunal",
                "and": {
                    "proprietaire": f" AND l10.comptecommunal = '{compte_communal}'",
                    "parcelle": f" AND p.parcelle = '{self.geo_parcelle}'",
                },
            },
            "proprietes_non_baties": {
                "names": ["lines"],
                "position": [3.5, 130, 290, 65],
                "keepContent": False,
                "type": "parent",
                "source": "proprietes_non_baties_line",
            },
            "proprietes_non_baties_sum": {
                "names": ["sum_ha_contenance", "sum_a_contenance", "sum_ca_contenance", "sum_drcsuba"],
                "position": [3.5, 195, 290, 13],
                "type": "sql",
                "keepContent": True,
                "filter": "comptecommunal",
                "and": {
                    "proprietaire": f" AND p.comptecommunal = '{compte_communal}'",
                    "parcelle": f" AND p.parcelle = '{self.geo_parcelle}'",
                },
            },
            "footer": {
                "names": ["foot"],
                "position": [3.5, 208, 288, 4],
                "keepContent": True,
                "type": "properties",
                "source": ["Ce document est donné à titre indicatif - Il n'a pas de valeur légale"],
                "sticky": True,
            },
        }
        self.main_tables = {
            "proprietaires_line": {
                "names": ["mainprop", "epousede", "adrprop", "nele"],
                "type": "sql",
                "keepContent": True,
                "filter": "comptecommunal",
                "and": {
                    "proprietaire": f" AND comptecommunal = '{compte_communal}'",
                    "parcelle": f" AND comptecommunal = '{compte_communal}'",
                },
            },
            "proprietes_baties_line": {
                "names": [
                    "section",
                    "ndeplan",
                    "ndevoirie",
                    "adresse",
                    "coderivoli",
                    "bat",
                    "ent",
                    "niv",
                    "ndeporte",
                    "numeroinvar",
                    "star",
                    "meval",
                    "af",
                    "natloc",
                    "cat",
                    "revenucadastral",
                    "coll",
                    "natexo",
                    "anret",
                    "andeb",
                    "fractionrcexo",
                    "pourcentageexo",
                    "txom",
                    "coefreduc",
                    "rcteom",
                ],
                "type": "sql",
                "filter": "comptecommunal",
                "and": {
                    "proprietaire": f" AND l10.comptecommunal = '{compte_communal}'",
                    "parcelle": f" AND p.parcelle = '{self.geo_parcelle}'",
                },
            },
            "proprietes_non_baties_line": {
                "names": [
                    "section",
                    "ndeplan",
                    "ndevoirie",
                    "adresse",
                    "coderivoli",
                    "nparcprim",
                    "fpdp",
                    "star",
                    "suf",
                    "grssgr",
                    "cl",
                    "natcult",
                    "ha_contenance",
                    "a_contenance",
                    "ca_contenance",
                    "revenucadastral",
                    "coll",
                    "natexo",
                    "anret",
                    "fractionrcexo",
                    "pourcentageexo",
                    "tc",
                    "lff",
                ],
                "type": "sql",
                "and": {
                    "proprietaire": f" AND p.comptecommunal = '{compte_communal}'",
                    "parcelle": f" AND p.parcelle = '{self.geo_parcelle}'",
                },
            },
        }

        # items for which to count number of lines
        self.lineCount = {
            "proprietes_baties_line": {"count": 0, "data": None},
            "proprietes_non_baties_line": {"count": 0, "data": None},
        }

        # Data of the items for which the query is run only once, and kept for next pages
        self.dataKept: dict[str, list[dict[str, str]]] = {}

    def getDataForGivenItem(
        self, key: str, item: dict[str, Any], page: int | None = None
    ) -> list[dict[str, str]]:
        """
        Get the rows of data of an item, from its SQL query, as dictionaries of strings.
        Without page, all the rows are fetched and counted for the main tables.
        With a page, only the rows of this page are returned for the main tables.
        """
        if item.get("keepContent") and key in self.dataKept:
            return self.dataKept[key]

        if page and key in self.lineCount:
            # Rows of the page, from the data fetched to count the lines
            offset = (page - 1) * self.maxLineNumber
            data = self.lineCount[key]["data"][offset : offset + self.maxLineNumber]
        else:
            sql = plugin_path("templates", f"{key}.tpl.sql").read_text()

            # Add schema to search_path if postgis
            if self.dbType == "postgis":
                sql = sql.replace("$schema", '"{}".'.format(self.connectionParams["schema"]))
            else:
                sql = sql.replace("$schema", "")

            # Add the for_third_party values
            # only useful for proprietaire
            # to empty sensitive data (date and location of birth)
            sql = sql.replace("$for_third_party", str(self.for_third_party))

            # Add where clause depending on etype
            sql = sql.replace("$and", item["and"][self.etype])

            # Convert PostgreSQL syntax to SQLite
            if self.dbType == "spatialite":
                sql = cadastre_common.postgisToSpatialite(sql)

            data, row_count, _ok = cadastre_common.fetchDataFromSqlQuery(self.connector, sql)
            if key in self.lineCount:
                self.lineCount[key]["count"] = row_count
                self.lineCount[key]["data"] = data

        rows = [
            {name: "" if value is None else str(value) for name, value in zip(item["names"], line)}
            for line in data
        ]
        if item.get("keepContent"):
            self.dataKept[key] = rows
        return rows

    def createComposition(self):
        """
        Create a print Layout
        """
        c = QgsPrintLayout(self.mProject)
        # We need to set a name to the layout, otherwise, error when exporting
        # more than one time:
        # RuntimeError: wrapped C/C++ object of type QgsPrintLayout has been deleted
        uid = uuid4()
        c.setName(f"cadastre_export_{uid.hex}")
        c.initializeDefaults()
        c.setUnits(QgsUnitTypes.LayoutUnit.LayoutMillimeters)

        g = QgsLayoutGridSettings(c)
        g.setOffset(QgsLayoutPoint(3.5, 0, QgsUnitTypes.LayoutUnit.LayoutMillimeters))
        g.setResolution(QgsLayoutMeasurement(2.5))

        # Set page number
        self.getPageNumberNeeded()
        # Set main properties
        for i in range(1, self.numPages):
            p = QgsLayoutItemPage(c)
            # page.setPageSize('A6')
            p.setPageSize(
                QgsLayoutSize(self.pageWidth, self.pageHeight, QgsUnitTypes.LayoutUnit.LayoutMillimeters)
            )
            c.pageCollection().addPage(p)

        # Set the global currentComposition
        self.currentComposition = c

    def getPageNumberNeeded(self):
        """
        Calculate the minimum pages
        needed to fit all the data
        """
        # retrieve total data and get total count
        for key in self.lineCount:
            self.getDataForGivenItem(key, self.main_tables[key])
        lines = max(self.lineCount[key]["count"] for key in self.lineCount)
        self.numPages = max(1, math.ceil(lines / self.maxLineNumber))

        # Add a page for map if etype == parcelle
        if self.etype == "parcelle" and self.print_parcelle_page:
            self.numPages += 1

    def addPageContent(self, page):
        """
        Add all needed item for a single page
        """
        for key, item in list(self.composerTemplates.items()):
            self.buildComposerLabel(key, item, page)

    def buildComposerLabel(self, key, item, page):
        """
        Add the layout items of a template for a page: labels and tables
        """
        # 1st page is a map for parcelle
        dpage = page - 1
        if self.etype == "parcelle" and self.print_parcelle_page:
            dpage = page

        layout = self.currentComposition
        x, y, width, height = item["position"]
        y += dpage * (self.pageHeight + 10)

        if key == "header1":
            rows = self.getDataForGivenItem(key, item)
            row = rows[0] if rows else {}
            values = [
                "ANNÉE MAJ",
                row.get("annee", ""),
                "DEP/DIR",
                "{}/{}".format(row.get("ccodep", ""), row.get("ccodir", "")),
                "COM",
                "{} {}".format(row.get("ccocom", ""), row.get("libcom", "")).strip(),
            ]
            releve_layout.add_table(layout, (x, y, width, height), [values], [22, 13, 18, 13, 12, 67], size=7)

        elif key == "header2":
            releve_layout.add_label(layout, f"RELEVÉ {item['source'][0]}", (x, y, width, height), size=10)

        elif key == "header3":
            values = ["COMPTE", item["source"][0]]
            releve_layout.add_table(layout, (x, y, width, height), [values], [width / 2, width / 2], size=7)

        elif key == "proprietaires":
            releve_layout.add_label(layout, "PROPRIÉTAIRES", (x, y, width, 4))
            source = item["source"]
            rows = [
                [" ".join("{mainprop} {epousede} {adrprop}".format(**row).split()), row["nele"].strip()]
                for row in self.getDataForGivenItem(source, self.main_tables[source], page)
            ]
            releve_layout.add_table(
                layout,
                (x, y + 4, width, height - 4),
                rows,
                [width * 0.7, width * 0.3],
                aligns=[releve_layout.LEFT, releve_layout.RIGHT],
                row_height=3.5,
                grid=False,
            )

        elif key in ("proprietes_baties", "proprietes_non_baties"):
            source = item["source"]
            if key == "proprietes_baties":
                title, groups, columns = (
                    "PROPRIÉTÉS BATIES",
                    releve_layout.BATI_GROUPS,
                    releve_layout.BATI_COLUMNS,
                )
            else:
                title, groups, columns = (
                    "PROPRIÉTÉS NON BATIES",
                    releve_layout.NON_BATI_GROUPS,
                    releve_layout.NON_BATI_COLUMNS,
                )
            releve_layout.add_columns_table(
                layout,
                x,
                y,
                title,
                groups,
                columns,
                self.getDataForGivenItem(source, self.main_tables[source], page),
                self.maxLineNumber,
                ROW_HEIGHT,
            )

        elif key == "proprietes_baties_sum":
            rows = self.getDataForGivenItem(key, item)
            row = rows[0] if rows else {}
            # Without merged cells, the labels of the 2 lines are on the first one
            first = ["REV IMPOSABLE", row.get("revenucadastral", ""), "COM"]
            second = ["", "", ""]
            for collectivite, prefix in (("COM", "co"), ("GRP COM", "gp"), ("DEP", "de"), ("REG", "re")):
                if collectivite != "COM":
                    first.append(collectivite)
                    second.append("")
                first += ["R EXO", row.get(f"{prefix}_vlbaia", "")]
                second += ["R IMP", row.get(f"{prefix}_bipevla", "")]
            values = [first, second]
            widths = [30, 24, 16, 14, 24, 18, 14, 24, 16, 14, 24, 16, 14, 26]
            widths = [w * width / sum(widths) for w in widths]
            releve_layout.add_table(layout, (x, y + 2, width, height - 2), values, widths, row_height=4)

        elif key == "proprietes_non_baties_sum":
            rows = self.getDataForGivenItem(key, item)
            row = rows[0] if rows else {}
            contenance = "{} {} {}".format(
                row.get("sum_ha_contenance", ""),
                row.get("sum_a_contenance", ""),
                row.get("sum_ca_contenance", ""),
            ).strip()
            values = [["CONTENANCE HA A CA", contenance, "REV IMPOSABLE", row.get("sum_drcsuba", "")]]
            releve_layout.add_table(
                layout, (x, y + 2, width, height - 2), values, [60, 85, 60, 85], row_height=4
            )

        elif key == "footer":
            releve_layout.add_label(
                layout, item["source"][0], (x, y, width, height), size=5, bold=False, italic=True
            )

    def addParcelleMap(self):
        """
        Add content in the first page
        with a map and basic information
        """
        # First add headers
        for key, item in list(self.composerTemplates.items()):
            if "sticky" in item:
                self.buildComposerLabel(key, item, 0)

        # Get feature extent
        exp = QgsExpression("\"geo_parcelle\" = '%s'" % self.geo_parcelle)
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
            pr.addFeatures(list(self.layer.getFeatures(request)))
            vl.commitChanges()
            vl.updateExtents()
            props = vl.renderer().symbol().symbolLayer(0).properties()
            props["outline_width"] = "1"
            props["outline_color"] = "0,85,255,255"
            props["outline_style"] = "solid"
            props["style"] = "no"
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

    def exportItemAsPdf(self, comptecommunal: str, suffix: str | None = None) -> str | None:
        """
        Export one PDF file using the template composer
        filled with appropriate data
        for one "compte communal"
        """
        temppath = None
        # Set configuration
        self.set_composer_templates(comptecommunal)

        # Create the composition
        self.createComposition()

        if self.currentComposition:
            # Populate composition for all pages
            for i in range(self.numPages):
                j = i + 1
                self.addPageContent(j)

            # Add map in first page if export parcelle
            if self.etype == "parcelle" and self.print_parcelle_page:
                self.addParcelleMap()

            # Create the pdf output path
            from time import time

            temp = "releve_{}_{}_{}.pdf".format(
                self.etype,
                comptecommunal.replace("+", "plus").replace("*", "fois"),  # .replace('¤', 'plus'),
                int(time() * 100),
            )
            # Create regexp to remove all non ascii chars
            import re

            r = re.compile(r"[^ -~]")
            temp = r.sub("", temp)
            # print temp
            temppath = os.path.join(self.targetDir, temp)
            temppath = os.path.normpath(temppath)
            QgsMessageLog.logMessage(f"Export PDF vers {temppath}", "cadastre", Qgis.MessageLevel.Info)

            # add layout to layout manager: for tests only
            # lmgr = self.mProject.layoutManager()
            # lmgr.addLayout(self.currentComposition)

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
                # Export PDF for each compte
                for printStep, comptecommunal in enumerate(self.comptecommunal):
                    # export as PDF
                    comptecommunal = comptecommunal.strip("' ")
                    apath = self.exportItemAsPdf(comptecommunal)
                    if apath:
                        paths.append(apath)

                    printProgress(printStep + 1)
        else:
            # A list with one compte communal has been converted to a string in __init__
            compte = self.comptecommunal
            apath = self.exportItemAsPdf(compte[0] if isinstance(compte, list) else compte)
            if apath:
                paths.append(apath)
        return paths
