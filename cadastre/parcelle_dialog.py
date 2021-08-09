__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import os.path
import sys

from pathlib import Path

from qgis.core import QgsCoordinateTransform, QgsMapSettings, QgsProject
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon, QKeySequence, QTextDocument
from qgis.PyQt.QtPrintSupport import QPrinter, QPrintPreviewDialog
from qgis.PyQt.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QMenu,
    QTextEdit,
)

sys.path.append(os.path.join(str(Path(__file__).resolve().parent), 'forms'))


from functools import partial

# db_manager scripts
from qgis.PyQt import uic

from .cadastre_export_dialog import cadastreExport
from .dialog_common import CadastreCommon

# --------------------------------------------------------
#        Parcelle - Show parcelle information
# --------------------------------------------------------


PARCELLE_FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        str(Path(__file__).resolve().parent),
        'forms',
        'cadastre_parcelle_form.ui'
    )
)


class CadastreParcelleDialog(QDialog, PARCELLE_FORM_CLASS):
    def __init__(self, iface, layer, feature, cadastre_search_dialog, parent=None):
        super(CadastreParcelleDialog, self).__init__(parent)

        plugin_dir = str(Path(__file__).resolve().parent)

        self.iface = iface
        self.feature = feature
        self.layer = layer
        self.mc = iface.mapCanvas()
        self.setupUi(self)
        self.cadastre_search_dialog = cadastre_search_dialog
        self.setWindowIcon(QIcon(
            os.path.join(
                plugin_dir, 'icons', 'toolbar', "get-parcelle-info.png"
            )
        ))
        self.setWindowTitle("Cadastre+, ID parcelle : %s" % self.feature['geo_parcelle'])
        self.setMinimumWidth(450)

        self.txtLog = QTextEdit(self)
        self.txtLog.setEnabled(False)

        from .custom_qpush_button import CustomPushButton
        self.butActions = CustomPushButton(self)
        self.butActions.initPushButton(
            40, 24, 10, 0, "butActions", "", "Actions ...", True,
            QIcon(
                os.path.join(
                    plugin_dir, 'icons', "actions.png"
                )
            ), 40, 24, True
        )
        self.contextMnubutActions(self.butActions)

        # Images
        self.btCentrer.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'centrer.png')))
        self.btZoomer.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'zoom.png')))
        self.btSelectionner.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'select.png')))
        self.btParcellesProprietaire.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'select.png')))
        self.btExportParcelle.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'releve.png')))
        self.btExportProprietaire.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'releve.png')))

        # common cadastre methods
        from .dialog_common import CadastreCommon
        self.qc = CadastreCommon(self)

        # Get connection parameters
        connectionParams = CadastreCommon.getConnectionParameterFromDbLayer(layer)
        if not connectionParams:
            return

        self.connectionParams = connectionParams
        self.dbType = connectionParams['dbType']
        self.schema = connectionParams['schema']
        connector = CadastreCommon.getConnectorFromUri(connectionParams)
        self.connector = connector

        self.buttonBox.button(QDialogButtonBox.Ok).setText(u"Fermer")

        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        self.buttonBox.rejected.connect(self.onReject)
        self.buttonBox.accepted.connect(self.onAccept)
        # Export buttons
        exportButtons = {
            'parcelle': self.btExportParcelle,
            'proprietaire': self.btExportProprietaire
        }
        for key, item in list(exportButtons.items()):
            control = item
            slot = partial(self.exportAsPDF, key)
            control.clicked.connect(slot)

        # Parcelle action button
        self.btCentrer.clicked.connect(self.centerToParcelle)
        self.btZoomer.clicked.connect(self.zoomToParcelle)
        self.btSelectionner.clicked.connect(self.selectParcelle)

        # Select parcelle from proprietaire action
        self.btParcellesProprietaire.clicked.connect(self.selectParcellesProprietaire)
        self.tabWidget.currentChanged.connect(self.updateMenuContext)

        # Check majic content
        self.hasMajicDataProp = False
        self.checkMajicContent()

        # Get CSS
        self.css = None
        self.getCss()

        # Set dialog content
        self.setParcelleContent()
        self.setProprietairesContent()
        self.setSubdivisionsContent()
        self.setLocauxContent()
        self.updateMenuContext()

    def resizeEvent(self, event):
        try:
            self.butActions.setGeometry(
                max(300, self.width() - 60),
                15, 48, 48
            )
            self.txtLog.setGeometry(
                5, self.height() - 32,
                max(200, self.width() - 100),
                20
            )
        except:
            pass

    def setObj(self):
        """
        Action for selected proprietaire(s)
        print/copy in clipboard/save
        """

        index = self.tabWidget.currentIndex()

        if index == 0:
            return self.parcelleInfo
        elif index == 1:
            return self.proprietairesInfo
        elif index == 2:
            return self.subdivisionsInfo
        elif index == 3:
            return self.locauxInfo

        return None

    def printInfosTab(self):
        obj = self.setObj()
        if not obj:
            return
        index = self.tabWidget.currentIndex()

        document = QTextDocument()
        title = self.windowTitle().replace("Cadastre+, ID", "").title()
        document.setHtml(
            "<h1>%s</h1><table width=95%%><tr><td>%s</td></tr></table>" % (
                title, obj.toHtml()
            )
        )

        printer = QPrinter()
        printer.setPageSize(QPrinter.A4)
        if index == 0:
            printer.setOrientation(QPrinter.Portrait)
        else:
            printer.setOrientation(QPrinter.Landscape)
        printer.setPageMargins(5, 10, 5, 10, QPrinter.Millimeter)
        printer.setOutputFormat(QPrinter.NativeFormat)
        dlg = QPrintPreviewDialog(printer)
        dlg.setWindowIcon(QIcon("%s/icons/print.png" % os.path.dirname(__file__)))
        dlg.setWindowTitle("Aperçu")
        dlg.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        dlg.paintRequested.connect(document.print_)
        dlg.exec_()

    def copyInfosTabQc(self):
        obj = self.setObj()
        if not obj:
            return
        if obj != self.proprietairesInfo:
            return
        if not self.feature:
            return

        if self.cadastre_search_dialog:
            self.cadastre_search_dialog.qc.updateLog(obj.toPlainText())

    def copyInfosTab(self):
        obj = self.setObj()
        if not obj:
            return

        title = self.windowTitle().replace("Cadastre+, ID", "").title()
        QApplication.clipboard().setText(
            "<h1>%s</h1><table width=95%%><tr><td>%s</td></tr></table>" % (
                title, obj.toHtml()
            )
        )
        self.txtLog.setText('Texte copié dans le presse papier !')

    def saveInfosTab(self):
        obj = self.setObj()
        if not obj:
            return

        dlgFile = QFileDialog(self, "Enregistrer sous ...")
        dlgFile.setNameFilters(("All (*.htm*)", "HTML (*.html)", "HTM (*.htm)"))
        dlgFile.selectNameFilter("Fichier HTML (*.html)")
        dlgFile.setDefaultSuffix("html")
        dlgFile.setViewMode(QFileDialog.Detail)
        dlgFile.setDirectory(os.path.dirname(__file__))
        dlgFile.setAcceptMode(QFileDialog.AcceptSave)

        if dlgFile.exec_():
            fileName = dlgFile.selectedFiles()[0]
            title = self.windowTitle().replace("Cadastre+, ID", "").title()
            with open(fileName, 'w', encoding="ansi", errors="surrogateescape") as inFile:
                inFile.write(
                    "<h1>%s</h1><table width=95%%><tr><td>%s</td></tr></table>" % (
                        title, obj.toHtml()
                    )
                )
            self.txtLog.setText(u'fichier sauvegarde sous : %s !' % fileName)

    def contextMnubutActions(self, obj):
        actions = {
            "printPage": (
                "print.png",
                "Imprimer la page courante ...",
                "Ctrl+P",
                self.printInfosTab,
                True
            ),
            # "~0": (),
            "copyPage": (
                "copy.png",
                "Copier la page courante dans le presse papier",
                "Ctrl+C",
                self.copyInfosTab,
                True
            ),
            "copyPageQc": (
                "copy.png",
                "Copier les infos propriétaires dans la fenêtre 'Outils de recherche'",
                "",
                self.copyInfosTabQc,
                True
            ),
            # "~1": (),
            "savePage": (
                "save.png",
                "Enregistrer la page courante sous ...",
                "Ctrl+S",
                self.saveInfosTab,
                True
            )
        }
        self.builderContextMenu(obj, actions)

    def updateMenuContext(self):
        try:
            self.copyPageQc.setEnabled(self.tabWidget.currentIndex() == 1)
        except:
            pass

    def builderContextMenu(self, obj, actions):
        contextMnu = QMenu()

        plugin_dir = str(Path(__file__).resolve().parent)
        for key in actions:
            icon = os.path.join(plugin_dir, "icons", actions[key][0])
            if key.startswith("~"):
                contextMnu.addSeparator()
            elif key.startswith("list-"):
                subMenu = QMenu(actions[key][1], self)
                subMenu.setIcon(QIcon(icon))
                i = 0
                for elt in actions[key][3]:
                    urlServer = QAction(QIcon(icon), elt, self)
                    urlServer.setObjectName("urlServer%s" % (i))
                    subMenu.addAction(urlServer)
                    urlServer.triggered.connect(self.shortCut)
                    i += 1
                contextMnu.addMenu(subMenu)
            else:
                action = QAction(QIcon(icon), actions[key][1], self)
                if actions[key][2] != "":
                    action.setShortcut(QKeySequence(actions[key][2]))
                setattr(self, key, action)
                action.setEnabled(actions[key][4])
                contextMnu.addAction(action)
                action.triggered.connect(actions[key][3])

        obj.setMenu(contextMnu)

    def getCss(self):
        """
        Get CSS from CSS file
        """
        css = ''
        plugin_dir = str(Path(__file__).resolve().parent)
        with open(os.path.join(plugin_dir, 'scripts', 'css', 'cadastre.css'), 'r') as f:
            css = f.read()
        self.css = css

    def checkMajicContent(self):
        """
        Check if database contains
        any MAJIC data
        """
        self.hasMajicDataProp = False
        sql = 'SELECT * FROM "proprietaire" LIMIT 1'
        if self.connectionParams['dbType'] == 'postgis':
            sql = 'SELECT * FROM "{}"."proprietaire" LIMIT 1'.format(self.connectionParams['schema'])
        data, rowCount, ok = CadastreCommon.fetchDataFromSqlQuery(self.connector, sql)
        if ok and rowCount >= 1:
            self.hasMajicDataProp = True

    # @timing
    def setParcelleContent(self):
        """
        Get parcelle data
        and set the dialog content
        """
        if self.feature.fieldNameIndex('proprietaire') > 0:
            item = 'parcelle_majic'
        else:
            item = 'parcelle_simple'

        html = CadastreCommon.getItemHtml(item, self.feature, self.connectionParams, self.connector)
        self.parcelleInfo.setStyleSheet(self.css)
        self.parcelleInfo.setHtml('%s' % html)

    # @timing
    def setProprietairesContent(self):
        """
        Get proprietaires data
        and set the dialog content
        """
        if self.feature.fieldNameIndex('proprietaire') == -1:
            html = 'Les données MAJIC n\'ont pas été trouvées dans la base de données'
        else:
            item = 'proprietaires'
            html = CadastreCommon.getItemHtml(item, self.feature, self.connectionParams, self.connector)
            html += CadastreCommon.getItemHtml('indivisions', self.feature, self.connectionParams, self.connector)
        self.proprietairesInfo.setStyleSheet(self.css)
        self.proprietairesInfo.setText('%s' % html)

    # @timing
    def setSubdivisionsContent(self):
        """
        Get subdivision data
        and set the dialog content
        """
        if self.feature.fieldNameIndex('proprietaire') == -1:
            html = 'Les données MAJIC n\'ont pas été trouvées dans la base de données'
        else:
            item = 'subdivisions'
            html = CadastreCommon.getItemHtml(item, self.feature, self.connectionParams, self.connector)
        self.subdivisionsInfo.setStyleSheet(self.css)
        self.subdivisionsInfo.setText('%s' % html)

    # @timing
    def setLocauxContent(self):
        """
        Get locaux data
        and set the dialog content
        """
        if self.feature.fieldNameIndex('proprietaire') == -1:
            html = 'Les données MAJIC n\'ont pas été trouvées dans la base de données'
        else:
            item = 'locaux'
            html = CadastreCommon.getItemHtml(item, self.feature, self.connectionParams, self.connector)
            item = 'locaux_detail'
            html += CadastreCommon.getItemHtml(item, self.feature, self.connectionParams, self.connector)
        self.locauxInfo.setStyleSheet(self.css)
        self.locauxInfo.setText('%s' % html)

    def exportAsPDF(self, key):
        """
        Export the parcelle or proprietaire
        information as a PDF file
        """
        if not self.connectionParams or not self.connector:
            self.updateConnexionParams()

        if not self.connector:
            return

        if not self.hasMajicDataProp:
            self.proprietairesInfo.setText(u'Pas de données de propriétaires dans la base')
            return

        if self.feature:
            comptecommunal = CadastreCommon.getCompteCommunalFromParcelleId(
                self.feature['geo_parcelle'],
                self.connectionParams,
                self.connector
            )
            if comptecommunal:
                if key == 'proprietaire':
                    comptecommunal = CadastreCommon.getProprietaireComptesCommunaux(
                        comptecommunal,
                        self.connectionParams,
                        self.connector,
                        self.cbExportAllCities.isChecked()
                    )
                if self.layer:
                    qe = cadastreExport(
                        self.layer,
                        key,
                        comptecommunal,
                        self.feature['geo_parcelle']
                    )
                    qe.exportAsPDF()

    def centerToParcelle(self):
        """
        Centre to parcelle feature
        """
        if self.feature:
            # first get scale
            scale = self.mc.scale()
            extent = self.feature.geometry().boundingBox()

            # reproject extent if needed
            crsDest = QgsMapSettings().destinationCrs()
            layer = self.layer
            crsSrc = layer.crs()
            if crsSrc.authid() != crsDest.authid():
                xform = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
                extent = xform.transform(extent)

            self.mc.setExtent(extent)

            # the set the scale back
            self.mc.zoomScale(scale)
            self.mc.refresh()

    def zoomToParcelle(self):
        """
        Zoom to parcelle feature
        """
        if self.feature:
            extent = self.feature.geometry().boundingBox()

            # reproject extent if needed
            crsDest = QgsMapSettings().destinationCrs()
            layer = self.layer
            crsSrc = layer.crs()
            if crsSrc.authid() != crsDest.authid():
                xform = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
                extent = xform.transform(extent)

            self.mc.setExtent(extent)
            self.mc.refresh()

    def selectParcelle(self):
        """
        Zoom to parcelle feature
        """
        if self.layer and self.feature:
            self.layer.removeSelection()
            self.layer.select(self.feature.id())

    def selectParcellesProprietaire(self):
        """
        Select all parcelles from this parcelle proprietaire.
        Use search class tools.
        Needs refactoring
        """
        if not self.hasMajicDataProp:
            self.proprietairesInfo.setText(u'Pas de données de propriétaires dans la base')
            return

        qs = self.cadastre_search_dialog
        key = 'proprietaire'

        comptecommunal = CadastreCommon.getCompteCommunalFromParcelleId(self.feature['geo_parcelle'],
                                                                        self.connectionParams, self.connector)
        if not comptecommunal:
            # fix_print_with_import
            self.txtLog.setText("Aucune parcelle trouvée pour ce propriétaire")
        value = comptecommunal
        filterExpression = "comptecommunal IN ('%s')" % value

        # Get data for child parcelle combo and fill it
        ckey = qs.searchComboBoxes[key]['search']['parcelle_child']
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
        """
        Save options when pressing OK button
        """
        self.accept()

    def onReject(self):
        """
        Run some actions when
        the user closes the dialog
        """
        self.connector.__del__()
        self.close()
