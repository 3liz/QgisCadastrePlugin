# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Cadastre - QGIS plugin menu class
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

from PyQt4.QtCore import (
    Qt,
    pyqtSignal,
    SIGNAL,
    QObject,
    QSettings,
    QUrl
)
from PyQt4.QtGui import (
    QIcon,
    QApplication,
    QAction,
    QActionGroup,
    QWidgetAction,
    QMessageBox,
    QDesktopServices
)
from PyQt4.QtXml import QDomDocument

from qgis.core import (
    QgsMapLayerRegistry,
    QgsMessageLog,
    QgsLogger,
    QgsMapLayer,
    QgsComposition
)

from cadastre_identify_parcelle import IdentifyParcelle
from cadastre_dialogs import cadastre_common, cadastre_search_dialog, cadastre_import_dialog, cadastre_load_dialog, cadastre_option_dialog, cadastre_about_dialog, cadastre_parcelle_dialog, cadastre_message_dialog
import ConfigParser
import os.path
import tempfile
from time import time

# ---------------------------------------------

class cadastre_menu:
    def __init__(self, iface):
        self.iface = iface
        self.mapCanvas = iface.mapCanvas()
        self.cadastre_search_dialog = None

    def cadastre_add_submenu(self, submenu):
        self.iface.addPluginToMenu("&Cadastre", submenu.menuAction())

    def initGui(self):


        # Import Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/database.png")
        self.import_action = QAction(icon, u"Importer des données", self.iface.mainWindow())
        QObject.connect(self.import_action, SIGNAL("triggered()"), self.open_import_dialog)

        # Search Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/search.png")
        self.search_action = QAction(icon, u"Outils de recherche", self.iface.mainWindow())
        QObject.connect(self.search_action, SIGNAL("triggered()"), self.toggle_search_dialog)
        if not self.cadastre_search_dialog:
            dialog = cadastre_search_dialog(self.iface)
            self.cadastre_search_dialog = dialog

        # Load Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/output.png")
        self.load_action = QAction(icon, u"Charger des données", self.iface.mainWindow())
        QObject.connect(self.load_action, SIGNAL("triggered()"), self.open_load_dialog)

        # Composer Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/mActionSaveAsPDF.png")
        self.export_action = QAction(icon, u"Exporter la vue", self.iface.mainWindow())
        QObject.connect(self.export_action, SIGNAL("triggered()"), self.export_view)

        # Options Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/config.png")
        self.option_action = QAction(icon, u"Configurer le plugin", self.iface.mainWindow())
        QObject.connect(self.option_action, SIGNAL("triggered()"), self.open_option_dialog)

        # About Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/about.png")
        self.about_action = QAction(icon, u"À propos", self.iface.mainWindow())
        QObject.connect(self.about_action, SIGNAL("triggered()"), self.open_about_dialog)

        # Help Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/about.png")
        self.help_action = QAction(icon, u"Aide", self.iface.mainWindow())
        QObject.connect(self.help_action, SIGNAL("triggered()"), self.open_help)

        # version Submenu
        icon = QIcon(os.path.dirname(__file__) + "/icons/about.png")
        self.version_action = QAction(icon, u"Notes de version", self.iface.mainWindow())
        QObject.connect(self.version_action, SIGNAL("triggered()"), self.open_message_dialog)

        # Add Cadastre to Extension menu
        self.iface.addPluginToMenu(u"&Cadastre", self.import_action)
        self.iface.addPluginToMenu(u"&Cadastre", self.load_action)
        self.iface.addPluginToMenu(u"&Cadastre", self.search_action)
        self.iface.addPluginToMenu(u"&Cadastre", self.export_action)
        self.iface.addPluginToMenu(u"&Cadastre", self.option_action)
        self.iface.addPluginToMenu(u"&Cadastre", self.about_action)
        self.iface.addPluginToMenu(u"&Cadastre", self.version_action)
        self.iface.addPluginToMenu(u"&Cadastre", self.help_action)


        # Add cadastre toolbar
        self.toolbar = self.iface.addToolBar(u'&Cadastre');

        # open import dialog
        self.openImportAction = QAction(
            QIcon(os.path.dirname(__file__) +"/icons/database.png"),
            u"Importer des données",
            self.iface.mainWindow()
        )
        self.openImportAction.triggered.connect(self.open_import_dialog)
        self.toolbar.addAction(self.openImportAction)
        self.toolbar.setObjectName("cadastreToolbar");

        # open load dialog
        self.openLoadAction = QAction(
            QIcon(os.path.dirname(__file__) +"/icons/output.png"),
            u"Charger des données",
            self.iface.mainWindow()
        )
        self.openLoadAction.triggered.connect(self.open_load_dialog)
        self.toolbar.addAction(self.openLoadAction)

        # open search dialog
        self.openSearchAction = QAction(
            QIcon(os.path.dirname(__file__) +"/icons/search.png"),
            u"Outils de recherche",
            self.iface.mainWindow()
        )
        self.openSearchAction.triggered.connect(self.toggle_search_dialog)
        #~ self.openSearchAction.setCheckable(True)
        self.toolbar.addAction(self.openSearchAction)

        # export composer
        self.runExportAction = QAction(
            QIcon(os.path.dirname(__file__) +"/icons/mActionSaveAsPDF.png"),
            u"Exporter la vue",
            self.iface.mainWindow()
        )
        self.runExportAction.triggered.connect(self.export_view)
        self.toolbar.addAction(self.runExportAction)

        # open Option dialog
        self.openOptionAction = QAction(
            QIcon(os.path.dirname(__file__) +"/icons/config.png"),
            u"Configurer le plugin",
            self.iface.mainWindow()
        )
        self.openOptionAction.triggered.connect(self.open_option_dialog)
        self.toolbar.addAction(self.openOptionAction)

        # open About dialog
        self.openAboutAction = QAction(
            QIcon(os.path.dirname(__file__) +"/icons/about.png"),
            u"À propos",
            self.iface.mainWindow()
        )
        self.openAboutAction.triggered.connect(self.open_about_dialog)
        self.toolbar.addAction(self.openAboutAction)

        # Create action for "Parcelle information"
        self.identifyParcelleAction = QAction(
            QIcon(os.path.dirname(__file__) +"/icons/toolbar/get-parcelle-info.png"),
            "Infos parcelle",
            self.iface.mainWindow()
        )
        self.identifyParcelleAction.setCheckable(True)
        self.identifyParcelleAction.triggered.connect( self.setIndentifyParcelleTool )
        self.toolbar.addAction( self.identifyParcelleAction )

        self.setActionsExclusive()

        # Display About window on first use
        s = QSettings()
        firstUse = s.value("cadastre/isFirstUse" , 1, type=int)
        if firstUse == 1:
            s.setValue("cadastre/isFirstUse", 0)
            self.open_about_dialog()

        # Display some messages depending on version number
        mConfig = ConfigParser.ConfigParser()
        metadataFile = os.path.dirname(__file__) + "/metadata.txt"
        mConfig.read( metadataFile )
        self.mConfig = mConfig
        myVersion = mConfig.get('general', 'version').replace('.', '_')
        myVersionMsg = s.value("cadastre/version_%s" % myVersion , 1, type=int)
        if myVersionMsg == 1:
            s.setValue("cadastre/version_%s" % myVersion , 0)
            self.open_message_dialog()

        # Project load or create : refresh search and identify tool
        self.iface.projectRead.connect(self.onProjectRead)
        self.iface.newProjectCreated.connect(self.onNewProjectCreated)

        # Delete layers from table when deleted from registry
        lr = QgsMapLayerRegistry.instance()
        lr.layersRemoved.connect( self.checkIdentifyParcelleTool )


    def open_import_dialog(self):
        '''
        Import dialog
        '''
        dialog = cadastre_import_dialog(self.iface)
        dialog.exec_()

    def open_load_dialog(self):
        '''
        Load dialog
        '''
        dialog = cadastre_load_dialog(
            self.iface,
            self.cadastre_search_dialog
        )
        dialog.exec_()

    def toggle_search_dialog(self):
        '''
        Search dock widget
        '''
        if self.cadastre_search_dialog.isVisible():
            self.cadastre_search_dialog.hide()
        else:
            self.cadastre_search_dialog.show()

    def export_view(self):
        '''
        Export current view to PDF
        '''
        # Load template from file
        s = QSettings()
        f = s.value("cadastre/composerTemplateFile", '', type=str)
        if not os.path.exists(f):
            f = '%s/composers/paysage_a4.qpt' % os.path.dirname(__file__)
            s.setValue("cadastre/composerTemplateFile", f)

        QApplication.setOverrideCursor(Qt.WaitCursor)
        tf = file(f, 'rt')
        tc= tf.read()
        tf.close()
        d= QDomDocument()
        d.setContent(tc)

        # Create composition
        ms = self.iface.mapCanvas().mapSettings()
        c = QgsComposition(ms)
        c.loadFromTemplate(d)

        c.setPlotStyle(QgsComposition.Print)
        #c.setPrintResolution(300)

        # Set map
        canvas = self.iface.mapCanvas()
        cm = c.getComposerMapById(0)
        extent = canvas.extent()
        scale = canvas.scale()
        cm.setMapCanvas(canvas)
        if extent:
            cm.zoomToExtent(extent)
        if scale:
            cm.setNewScale(scale)

        # Export
        tempDir = s.value("cadastre/tempDir", '%s' % tempfile.gettempdir(), type=str)
        self.targetDir = tempfile.mkdtemp('', 'cad_export_', tempDir)
        temp = int(time()*100)
        temppath = os.path.join(tempDir, 'export_cadastre_%s.pdf' % temp)
        c.exportAsPDF(temppath)

        QApplication.restoreOverrideCursor()

        if os.path.exists(temppath):
            cadastre_common.openFile(temppath)

    def open_option_dialog(self):
        '''
        Config dialog
        '''
        dialog = cadastre_option_dialog(self.iface)
        dialog.exec_()


    def open_about_dialog(self):
        '''
        About dialog
        '''
        dialog = cadastre_about_dialog(self.iface)
        dialog.exec_()


    def setActionsExclusive(self):

        # Build an action list from QGIS navigation toolbar
        actionList = self.iface.mapNavToolToolBar().actions()

        # Add actions from QGIS attributes toolbar (handling QWidgetActions)
        tmpActionList = self.iface.attributesToolBar().actions()
        for action in tmpActionList:
            if isinstance(action, QWidgetAction):
                actionList.extend( action.defaultWidget().actions() )
            else:
                actionList.append( action )
        # ... add other toolbars' action lists...

        # Build a group with actions from actionList and add your own action
        group = QActionGroup( self.iface.mainWindow() )
        group.setExclusive(True)
        for action in actionList:
            group.addAction( action )
        group.addAction( self.identifyParcelleAction )

    def checkIdentifyParcelleTool(self, layerIds=None):
        '''
        When layers are removed from the project
        Check if the layer Parcelle remains
        If not deactivate Identify parcelle tool
        '''
        # Find parcelle layer
        parcelleLayer = None
        try:
            from cadastre_dialogs import cadastre_common
            parcelleLayer = cadastre_common.getLayerFromLegendByTableProps('parcelle_info')
        except:
            parcelleLayer = None

        if not parcelleLayer:
            self.identifyParcelleAction.setChecked(False)
            self.iface.actionPan().trigger()
            return

    def setIndentifyParcelleTool(self):
        '''
        Activite the identify tool
        for the layer geo_parcelle
        '''

        # Find parcelle layer
        parcelleLayer = cadastre_common.getLayerFromLegendByTableProps('parcelle_info')
        if not parcelleLayer:
            QMessageBox.warning(
                self.cadastre_search_dialog,
                u"Cadastre",
                u"La couche de parcelles n'a pas été trouvée dans le projet"
            )
            self.identifyParcelleAction.setChecked(False)
            self.iface.actionPan().trigger()
            return

        self.identyParcelleTool = IdentifyParcelle( self.mapCanvas, parcelleLayer )
        self.identyParcelleTool.cadastreGeomIdentified.connect(self.getParcelleInfo)

        # The activate identify tool
        self.mapCanvas.setMapTool(self.identyParcelleTool)

    def getParcelleInfo(self, layer, feature):
        '''
        Return information of the identified
        parcelle
        '''
        parcelleDialog = cadastre_parcelle_dialog(
            self.iface,
            layer,
            feature,
            self.cadastre_search_dialog
        )
        parcelleDialog.show()

    def onProjectRead(self):
        '''
        Refresh search dialog when new data has been loaded
        '''
        if self.cadastre_search_dialog:
            self.cadastre_search_dialog.checkMajicContent()
            self.cadastre_search_dialog.clearComboboxes()
            self.cadastre_search_dialog.setupSearchCombobox('commune', None, 'sql')
            self.cadastre_search_dialog.setupSearchCombobox('section', None, 'sql')
            self.checkIdentifyParcelleTool()

    def onNewProjectCreated(self):
        '''
        Refresh search dialog when new data has been loaded
        '''
        self.checkIdentifyParcelleTool()
        if self.cadastre_search_dialog:
            self.cadastre_search_dialog.checkMajicContent()
            self.cadastre_search_dialog.clearComboboxes()


    def open_help(self):
        '''Opens the html help file content with default browser'''
        #~ localHelpUrl = "https://github.com/3liz/QgisCadastrePlugin/blob/master/doc/index.rst"
        localHelpUrl = os.path.dirname(__file__) + "/doc/index.html"
        QDesktopServices.openUrl( QUrl(localHelpUrl) )

    def open_message_dialog(self):
        '''
        Display a message to the user
        '''
        versionMessages = {
            '1.1.0': [
                [
                    u'Compatibilité avec QGIS 2.6',
                    u'La compatibilité n\'est pas assurée à 100 % avec la dernière version 2.6 de QGIS, notamment pour la création d\'une base Spatialite vide. Vous pouvez utiliser les outils de QGIS pour le faire.'
                ] ,
                [
                    u'Lien entre les parcelles EDIGEO et MAJIC',
                    u'Pour cette nouvelle version du plugin, la structure de la base de données a été légèrement modifiée. Pour pouvoir utiliser les fonctions du plugin Cadastre, vous devez donc impérativement <b>réimporter les données dans une base vide</b>'
                ] ,
                [
                    u'Validation des géométries',
                    u'Certaines données EDIGEO contiennent des géométries invalides (polygones croisés dit "papillons", polygones non fermés, etc.). Cette version utilise une fonction de PostGIS qui tente de corriger ces invalidités. Il faut impérativement <b>utiliser une version récente de PostGIS</b> : 2.0.4 minimum pour la version 2, ou les version ultérieures (2.1 par exemple)'
                ]
            ]
            ,
            '1.4.0': [
                [
                    u'Modification de la structure',
                    u'Pour cette nouvelle version 1.4.0 du plugin, la structure de la base de données a été légèrement modifiée par rapport à la 1.4.0. Pour pouvoir utiliser les fonctions du plugin Cadastre, vous devez donc impérativement <b>réimporter les données dans une base vide</b>. Les changements concernent les identifiants des tables parcelle, geo_parcelle, commune, local00, local10, pev, pevexoneration, pevtaxation, pevprincipale, pevprofessionnelle, pevdependances, ainsi que la création d\'une table parcelle_info pour consolider EDIGEO et MAJIC.'
                ]
            ]
        }
        mConfig = self.mConfig
        version = mConfig.get('general', 'version')
        changelog = mConfig.get('general', 'changelog')

        message = '<h2>Version %s - notes concernant cette version</h2>' % version
        if version in versionMessages:
            message+='<ul>'
            for item in versionMessages[version]:
                message+='<li><b>%s</b> - %s</li>' % (item[0], item[1])
            message+='</ul>'

        message+= '<h3>Changelog</h3>'
        message+= '<p>'
        i = 0
        for item in changelog.split('*'):
            if i == 0:
                message+= '<b>%s</b><ul>' % item.decode('utf-8')
            else:
                message+= '<li>%s</li>' % item.decode('utf-8')
            i+=1
        message+='</ul>'
        message+= '</p>'

        dialog = cadastre_message_dialog(self.iface, message)
        dialog.exec_()



    def unload(self):

        self.iface.removePluginMenu(u"&Cadastre", self.import_action)
        self.iface.removePluginMenu(u"&Cadastre", self.load_action)
        self.iface.removePluginMenu(u"&Cadastre", self.search_action)
        self.iface.removePluginMenu(u"&Cadastre", self.export_action)
        self.iface.removePluginMenu(u"&Cadastre", self.option_action)
        self.iface.removePluginMenu(u"&Cadastre", self.about_action)
        self.iface.removePluginMenu(u"&Cadastre", self.version_action)
        self.iface.removePluginMenu(u"&Cadastre", self.help_action)

        self.iface.mainWindow().removeToolBar(self.toolbar)

        if self.cadastre_search_dialog:
            self.iface.removeDockWidget(self.cadastre_search_dialog)

