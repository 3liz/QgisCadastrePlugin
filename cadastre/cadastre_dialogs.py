"""
Cadastre - Dialog classes

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
import os.path
import sys
import tempfile

from pathlib import Path

from qgis.core import (
    QgsCoordinateTransform,
    QgsMapSettings,
    QgsProject,
    QgsSettings,
)
from qgis.PyQt.QtCore import QSize, Qt
from qgis.PyQt.QtGui import QIcon, QKeySequence, QPixmap, QTextDocument
from qgis.PyQt.QtPrintSupport import QPrinter, QPrintPreviewDialog
from qgis.PyQt.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QMenu,
    QMessageBox,
    QPushButton,
    QTextEdit,
)

sys.path.append(os.path.join(str(Path(__file__).resolve().parent), 'forms'))


from functools import partial

# db_manager scripts
from qgis.PyQt import uic

from .dialog_common import CadastreCommon

# --------------------------------------------------------
#        Option - Let the user configure options
# --------------------------------------------------------

OPTION_FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        str(Path(__file__).resolve().parent),
        'forms',
        'cadastre_option_form.ui'
    )
)


class CadastreOptionDialog(QDialog, OPTION_FORM_CLASS):
    def __init__(self, iface, parent=None):
        super(CadastreOptionDialog, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)

        # Images
        self.plugin_dir = str(Path(__file__).resolve().parent)
        self.btComposerTemplateFile.setIcon(QIcon(os.path.join(self.plugin_dir, 'forms', 'icons', 'open.png')))
        self.btTempDir.setIcon(QIcon(os.path.join(self.plugin_dir, 'forms', 'icons', 'open.png')))

        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        self.buttonBox.rejected.connect(self.onReject)
        self.buttonBox.accepted.connect(self.onAccept)

        # interface change buttons
        self.interfaceSelectors = {
            "Cadastre": {
                "button": self.btInterfaceCadastre
            },
            "QGIS": {
                "button": self.btInterfaceQgis
            }
        }
        from functools import partial
        for key, item in list(self.interfaceSelectors.items()):
            control = item['button']
            slot = partial(self.applyInterface, key)
            control.clicked.connect(slot)

        # path buttons selectors
        # paths needed to be chosen by user
        self.pathSelectors = {
            "tempDir": {
                "button": self.btTempDir,
                "input": self.inTempDir,
                "type": "dir"
            },
            "composerTemplateFile": {
                "button": self.btComposerTemplateFile,
                "input": self.inComposerTemplateFile,
                "type": "file"
            }
        }
        from functools import partial
        for key, item in list(self.pathSelectors.items()):
            control = item['button']
            slot = partial(self.chooseDataPath, key)
            control.clicked.connect(slot)

        # Set initial widget values
        self.getValuesFromSettings()

    def chooseDataPath(self, key):
        """
        Ask the user to select a folder
        and write down the path to appropriate field
        """
        if self.pathSelectors[key]['type'] == 'dir':
            ipath = QFileDialog.getExistingDirectory(
                None,
                u"Choisir le répertoire contenant les fichiers",
                str(self.pathSelectors[key]['input'].text().encode('utf-8')).strip(' \t')
            )
        else:
            ipath, __ = QFileDialog.getOpenFileName(
                None,
                u"Choisir le modèle de composeur utilisé pour l'export",
                str(self.pathSelectors[key]['input'].text().encode('utf-8')).strip(' \t'),
                u"Composeur (*.qpt)"
            )

        if os.path.exists(str(ipath)):
            self.pathSelectors[key]['input'].setText(str(ipath))

    def getValuesFromSettings(self):
        """
        Get majic file names and other options
        from settings and set corresponding inputs
        """
        s = QgsSettings()
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
        spatialiteTempStore = s.value("cadastre/spatialiteTempStore", 'MEMORY', type=str)
        if spatialiteTempStore and hasattr(self, 'inSpatialiteTempStore'):
            if spatialiteTempStore == 'MEMORY':
                self.inSpatialiteTempStore.setCurrentIndex(0)
            else:
                self.inSpatialiteTempStore.setCurrentIndex(1)
        composerTemplateFile = s.value(
            "cadastre/composerTemplateFile",
            '%s/composers/paysage_a4.qpt' % self.plugin_dir,
            type=str
        )
        if composerTemplateFile:
            self.inComposerTemplateFile.setText(composerTemplateFile)

    def applyInterface(self, key):
        """
        Help the user to select
        and apply personalized interface
        """

        # item = self.interfaceSelectors[key]
        iniPath = os.path.join(
            self.plugin_dir,
            'interface/'
        )
        interfaceInfo = u'''
        Pour appliquer l'interface <b>%s</b>
        <ul>
            <li>Menu Préférences > Personnalisation</li>
            <li>Bouton <b>Charger depuis le fichier</b> (icône dossier ouvert)</li>
            <li>Sélectionner le fichier <b>%s.ini</b> situé dans le dossier : <b>%s</b></li>
            <li>Appliquer et fermer la fenêtre</li>
            <li>Redémarer QGIS</li>
        </ul>
        ''' % (key, key.lower(), iniPath)
        QMessageBox.information(
            self,
            u"Cadastre - Personnalisation",
            interfaceInfo
        )

    def onAccept(self):
        """
        Save options when pressing OK button
        """

        # Save Majic file names
        s = QgsSettings()
        s.setValue("cadastre/batiFileName", self.inMajicBati.text().strip(' \t\n\r'))
        s.setValue("cadastre/fantoirFileName", self.inMajicFantoir.text().strip(' \t\n\r'))
        s.setValue("cadastre/lotlocalFileName", self.inMajicLotlocal.text().strip(' \t\n\r'))
        s.setValue("cadastre/nbatiFileName", self.inMajicNbati.text().strip(' \t\n\r'))
        s.setValue("cadastre/pdlFileName", self.inMajicPdl.text().strip(' \t\n\r'))
        s.setValue("cadastre/propFileName", self.inMajicProp.text().strip(' \t\n\r'))

        # Save temp dir
        s.setValue("cadastre/tempDir", self.inTempDir.text().strip(' \t\n\r'))
        # Save composer template dir
        s.setValue("cadastre/composerTemplateFile", self.inComposerTemplateFile.text().strip(' \t\n\r'))

        # Save performance tuning
        s.setValue("cadastre/maxInsertRows", int(self.inMaxInsertRows.value()))
        s.setValue("cadastre/spatialiteTempStore", self.inSpatialiteTempStore.currentText().upper())

        self.accept()

    def onReject(self):
        """
        Run some actions when
        the user closes the dialog
        """
        self.close()


# --------------------------------------------------------
#        About - Let the user display the about dialog
# --------------------------------------------------------


ABOUT_FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        str(Path(__file__).resolve().parent),
        'forms',
        'cadastre_about_form.ui'
    )
)


class CadastreAboutDialog(QDialog, ABOUT_FORM_CLASS):
    def __init__(self, iface, parent=None):
        super(CadastreAboutDialog, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)

        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        self.buttonBox.rejected.connect(self.onReject)
        self.buttonBox.accepted.connect(self.onAccept)

        # Images
        plugin_dir = str(Path(__file__).resolve().parent)
        self.label_logo_rennes_metropole.setPixmap(QPixmap(os.path.join(plugin_dir, 'forms', 'images', 'logo_rennes_metropole.png')))
        self.label_logo_mtes.setPixmap(QPixmap(os.path.join(plugin_dir, 'forms', 'images', 'logo_mtes.png')))
        self.label_logo_mtes_2.setPixmap(QPixmap(os.path.join(plugin_dir, 'forms', 'images', 'logo_mtes_2.png')))
        self.label_logo_asadefrance.setPixmap(QPixmap(os.path.join(plugin_dir, 'forms', 'images', 'logo_asadefrance.png')))
        self.label_logo_grandnarbonne.setPixmap(QPixmap(os.path.join(plugin_dir, 'forms', 'images', 'logo_grandnarbonne.png')))
        self.label_logo_datagences_bretagne.setPixmap(QPixmap(os.path.join(plugin_dir, 'forms', 'images', 'logo_datagences_bretagne.png')))
        self.label_logo_cd54.setPixmap(QPixmap(os.path.join(plugin_dir, 'forms', 'images', 'logo_cd54.png')))
        self.label_logo_ue.setPixmap(QPixmap(os.path.join(plugin_dir, 'forms', 'images', 'logo_europe.png')))
        self.label_logo_feder.setPixmap(QPixmap(os.path.join(plugin_dir, 'forms', 'images', 'logo_feder.png')))
        self.label_logo_picardie.setPixmap(QPixmap(os.path.join(plugin_dir, 'forms', 'images', 'logo_picardie.png')))
        self.label_logo_aduga.setPixmap(QPixmap(os.path.join(plugin_dir, 'forms', 'images', 'logo_aduga.png')))
        self.label_logo_3liz.setPixmap(QPixmap(os.path.join(plugin_dir, 'forms', 'images', 'logo_3liz.png')))

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
        self.close()


# --------------------------------------------------------
#        Parcelle - Show parcelle information
# --------------------------------------------------------

from .cadastre_export_dialog import cadastreExport

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

        self.butActions = MyPushButtonFunny(self)
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


# --------------------------------------------------------
#        Messages - Displays a message to the user
# --------------------------------------------------------

MESSAGE_FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        str(Path(__file__).resolve().parent),
        'forms',
        'cadastre_message_form.ui'
    )
)


class CadastreMessageDialog(QDialog, MESSAGE_FORM_CLASS):
    def __init__(self, iface, message, parent=None):
        super(CadastreMessageDialog, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)

        self.teMessage.setText(message)

        # Signals/Slot Connections
        self.rejected.connect(self.onReject)
        self.buttonBox.rejected.connect(self.onReject)
        self.buttonBox.accepted.connect(self.onAccept)

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
        self.close()


class MyPushButtonFunny(QPushButton):
    def __init__(self, *args):
        super(MyPushButtonFunny, self).__init__(*args)

    def initPushButton(
            self, sizeWidth, sizeHeight, coordX, coordY, name, text,
            toolTip, isGeom, icon, iconWidth, iconHeight, isStyleSheeted):
        self.setMinimumSize(sizeWidth, sizeHeight)
        self.setMaximumSize(sizeWidth, sizeHeight)
        self.iconWidth = iconWidth
        self.iconHeight = iconHeight
        self.selfFocused = False
        self.subMenuVisble = False

        if isGeom:
            self.setGeometry(coordX, coordY, sizeWidth, sizeHeight)

        if icon != "":
            self.setIcon(QIcon(icon))
            self.setIconSize(QSize(self.iconWidth, self.iconHeight))

        self.setToolTip(toolTip)

        if isStyleSheeted:
            self.setStyleSheet(" QPushButton {border-width: 0px; border-radius: 10px;  border-color: beige;}")

        self.setObjectName(name)

        if text != "":
            self.setText(text)
