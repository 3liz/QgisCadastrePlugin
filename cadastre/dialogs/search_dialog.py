__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import os.path
import re

from functools import partial
from pathlib import Path

from qgis.core import (
    QgsCoordinateTransform,
    QgsExpression,
    QgsFeatureRequest,
    QgsMapSettings,
    QgsProject,
)
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon, QTextDocument
from qgis.PyQt.QtPrintSupport import QPrinter, QPrintPreviewDialog
from qgis.PyQt.QtWidgets import (
    QApplication,
    QCompleter,
    QDockWidget,
    QFileDialog,
)
from qgis.utils import OverrideCursor

from cadastre.cadastre_export import CadastreExport
from cadastre.dialogs.custom_qcompleter import CustomQCompleter
from cadastre.dialogs.dialog_common import CadastreCommon
from cadastre.dialogs.parcelle_dialog import CadastreParcelleDialog

SEARCH_FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        str(Path(__file__).resolve().parent.parent),
        'forms',
        'cadastre_search_form.ui'
    )
)


class CadastreSearchDialog(QDockWidget, SEARCH_FORM_CLASS):

    """ Search for data among database ans export. """

    def __init__(self, iface, parent=None):
        # QDockWidget.__init__(self)
        super(CadastreSearchDialog, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self)

        # Images
        plugin_dir = str(Path(__file__).resolve().parent.parent)
        self.btExportParcelle.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'releve.png')))
        self.btResetCommune.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'delete.png')))
        self.btResetParcelle.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'delete.png')))
        self.btResetSection.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'delete.png')))
        self.btResetAdresse.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'delete.png')))
        self.btCentrerLieu.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'centrer.png')))
        self.btZoomerLieu.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'zoom.png')))
        self.btSelectionnerLieu.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'select.png')))
        self.btExportProprietaire.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'releve.png')))
        self.btExportParcelleProprietaire.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'releve.png')))
        self.btResetProprietaire.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'delete.png')))
        self.btResetParcelleProprietaire.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'delete.png')))
        self.btIdentifierProprietaire.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'identify.png')))
        self.btCentrerProprietaire.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'centrer.png')))
        self.btZoomerProprietaire.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'zoom.png')))
        self.btSelectionnerProprietaire.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'select.png')))
        self.btResetCommuneProprietaire.setIcon(QIcon(os.path.join(plugin_dir, 'forms', 'icons', 'delete.png')))

        # common cadastre methods
        from cadastre.dialogs.dialog_common import CadastreCommon
        self.qc = CadastreCommon(self)

        # database properties
        self.connectionParams = None
        self.connector = None
        self.dbType = None
        self.schema = None

        self.mc = self.iface.mapCanvas()
        self.communeLayer = None
        self.communeFeatures = None
        self.communeRequest = None
        self.selectedCommuneFeature = None
        self.sectionLayer = None
        self.sectionFeatures = None
        self.sectionRequest = None
        self.sectionCommuneFeature = None

        aLayer = CadastreCommon.getLayerFromLegendByTableProps('geo_commune')
        if aLayer:
            self.connectionParams = CadastreCommon.getConnectionParameterFromDbLayer(aLayer)
            self.connector = CadastreCommon.getConnectorFromUri(self.connectionParams)

        # signals/slots
        self.searchComboBoxes = {
            'commune': {
                'widget': self.liCommune,
                'labelAttribute': 'tex2',
                'table': 'geo_commune',
                'geomCol': 'geom',
                'sql': '',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid', 'tex2', 'idu', 'geo_commune', 'geom', 'lot'],
                'orderBy': ['tex2'],
                'features': None,
                'chosenFeature': None,
                'resetWidget': self.btResetCommune,
                'children': [
                    {
                        'key': 'section',
                        'fkey': 'geo_commune',
                        'getIfNoFeature': True
                    }
                ]
            },
            'section': {
                'widget': self.liSection,
                'labelAttribute': 'idu',
                'table': 'geo_section',
                'geomCol': 'geom',
                'sql': '',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid', 'tex', 'idu', 'geo_commune', 'geo_section', 'geom', 'lot'],
                'orderBy': ['geo_section'],
                'features': None,
                'chosenFeature': None,
                'resetWidget': self.btResetSection,
                'children': [
                    {
                        'key': 'parcelle',
                        'fkey': 'geo_section',
                        'getIfNoFeature': False
                    }
                ]
            },
            'adresse': {
                'widget': self.liAdresse,
                'labelAttribute': 'voie',
                'table': 'parcelle_info',
                'layer': None,
                'geomCol': None,
                'sql': '',
                'request': None,
                'attributes': ['ogc_fid', 'voie', 'idu', 'geom'],
                'orderBy': ['voie'],
                'features': None,
                'chosenFeature': None,
                'resetWidget': self.btResetAdresse,
                'connector': None,
                'search': {
                    'parcelle_child': 'parcelle',
                    'minlen': 3
                },
                'children': [
                    {
                        'key': 'parcelle',
                        'fkey': 'voie',
                        'getIfNoFeature': False
                    }
                ]
            },
            'parcelle': {
                'widget': self.liParcelle,
                'labelAttribute': 'idu',
                'table': 'parcelle_info',
                'geomCol': 'geom',
                'sql': '',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid', 'tex', 'idu', 'geo_section', 'geom', 'comptecommunal', 'geo_parcelle'],
                'orderBy': ['geo_parcelle'],
                'features': None,
                'chosenFeature': None,
                'connector': None,
                'resetWidget': self.btResetParcelle
            },
            'proprietaire': {
                'widget': self.liProprietaire,
                'labelAttribute': 'idu',
                'table': 'parcelle_info',
                'layer': None,
                'request': None,
                'attributes': ['comptecommunal', 'idu', 'dnupro', 'geom'],
                'orderBy': ['ddenom'],
                'features': None,
                'id': None,
                'chosenFeature': None,
                'connector': None,
                'search': {
                    'parcelle_child': 'parcelle_proprietaire',
                    'minlen': 3
                },
                'resetWidget': self.btResetProprietaire,
            },
            'parcelle_proprietaire': {
                'widget': self.liParcelleProprietaire,
                'labelAttribute': 'idu',
                'table': 'parcelle_info',
                'geomCol': 'geom',
                'sql': '',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid', 'tex', 'idu', 'comptecommunal', 'geom', 'geo_parcelle'],
                'orderBy': ['geo_parcelle'],
                'features': None,
                'chosenFeature': None,
                'connector': None,
                'resetWidget': self.btResetParcelleProprietaire
            },
            'commune_proprietaire': {
                'widget': self.liCommuneProprietaire,
                'labelAttribute': 'tex2',
                'table': 'geo_commune',
                'geomCol': 'geom',
                'sql': '',
                'layer': None,
                'request': None,
                'attributes': ['ogc_fid', 'tex2', 'idu', 'geo_commune', 'geom', 'lot'],
                'orderBy': ['tex2'],
                'features': None,
                'chosenFeature': None,
                'resetWidget': self.btResetCommuneProprietaire,
                'children': [
                    {
                        'key': 'section',
                        'fkey': 'geo_commune',
                        'getIfNoFeature': True
                    }
                ]
            }
        }

        # Detect that the user has hidden/showed the dock
        self.visibilityChanged.connect(self.onVisibilityChange)

        # identifier/center/zoom/selection buttons
        self.zoomButtons = {
            'lieu': {
                'buttons': {
                    'identifier': self.btIdentifierProprietaire,
                    'centre': self.btCentrerLieu,
                    'zoom': self.btZoomerLieu,
                    'select': self.btSelectionnerLieu
                },
                'comboboxes': ['commune', 'section', 'adresse', 'parcelle']
            },
            'proprietaire': {
                'buttons': {
                    'centre': self.btCentrerProprietaire,
                    'zoom': self.btZoomerProprietaire,
                    'select': self.btSelectionnerProprietaire
                },
                'comboboxes': ['proprietaire', 'parcelle_proprietaire']
            }

        }
        zoomButtonsFunctions = {
            'identifier': self.setIdentifierToChosenItem,
            'centre': self.setCenterToChosenItem,
            'zoom': self.setZoomToChosenItem,
            'select': self.setSelectionToChosenItem
        }
        for key, item in list(self.zoomButtons.items()):
            for k, button in list(item['buttons'].items()):
                control = button
                slot = partial(zoomButtonsFunctions[k], key)
                control.clicked.connect(slot)

        # Manuel search button and combo (proprietaire, adresse)
        for key, item in list(self.searchComboBoxes.items()):
            # Combobox not prefilled (too much data proprietaires & adresse
            if 'search' in item:

                # when the user add some text : autocomplete
                # the search comboboxes are not filled in with item
                # only autocompletion popup is filled while typing
                # Activate autocompletion
                completer = CustomQCompleter([], self)
                # completer.setCompletionMode(QCompleter.PopupCompletion) # does not work with regex custom completer
                completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
                completer.setMaxVisibleItems(20)
                completer.setCaseSensitivity(Qt.CaseInsensitive)
                # completer.popup().setStyleSheet("background-color: lightblue")
                completer.activated.connect(partial(self.onCompleterActivated, key))
                control = item['widget']
                li = control.lineEdit()
                li.setCompleter(completer)
                li.textEdited.connect(partial(self.refreshAutocomplete, key))

                # when the user resets the entered value
                control = item['resetWidget']
                slot = partial(self.onSearchItemReset, key)
                control.clicked.connect(slot)

            else:
                control = item['widget']
                # when the user edits the combobox content
                slot = partial(self.onNonSearchItemEdit, key)
                control.editTextChanged[str].connect(slot)

                # when the user chooses in the list
                slot = partial(self.onNonSearchItemChoose, key)
                control.currentIndexChanged[str].connect(slot)

                # when the user reset the entered value
                control = item['resetWidget']
                slot = partial(self.onNonSearchItemReset, key)
                control.clicked.connect(slot)

        # export buttons
        self.btExportProprietaire.clicked.connect(self.export_proprietaire)
        self.exportParcelleButtons = {
            'parcelle': self.btExportParcelle,
            'parcelle_proprietaire': self.btExportParcelleProprietaire
        }
        for key, item in list(self.exportParcelleButtons.items()):
            control = item
            slot = partial(self.exportParcelle, key)
            control.clicked.connect(slot)

        # setup some gui items
        self.setupSearchCombobox('commune', None, 'sql')
        self.setupSearchCombobox('commune_proprietaire', None, 'sql')
        # self.setupSearchCombobox('section', None, 'sql')

        # Check majic content
        self.hasMajicDataProp = False
        self.hasMajicDataVoie = False
        self.hasMajicDataParcelle = False
        self.checkMajicContent()

        # signals

    def clearComboboxes(self):
        """
        Clear comboboxes content
        """
        self.txtLog.clear()
        for key, item in list(self.searchComboBoxes.items()):
            # manual search widgets
            if 'widget' in item:
                item['widget'].clear()

    def checkMajicContent(self):
        """
        Check if database contains
        any MAJIC data
        """
        self.hasMajicDataProp = False
        self.hasMajicDataVoie = False
        self.hasMajicDataParcelle = False

        from cadastre.dialogs.dialog_common import CadastreCommon
        aLayer = CadastreCommon.getLayerFromLegendByTableProps('geo_commune')
        if aLayer:
            self.connectionParams = CadastreCommon.getConnectionParameterFromDbLayer(aLayer)

        # Get connection parameters
        if self.connectionParams:

            # Get Connection params
            connector = CadastreCommon.getConnectorFromUri(self.connectionParams)
            if connector:
                # Tables to check
                majicTableParcelle = 'parcelle'
                majicTableProp = 'proprietaire'
                majicTableVoie = 'voie'

                # dbType
                is_postgis = (self.connectionParams['dbType'] == 'postgis')

                # Get data from table proprietaire
                sql = 'SELECT * FROM "{}" LIMIT 1'.format(majicTableProp)
                if is_postgis:
                    sql = 'SELECT * FROM "{}"."{}" LIMIT 1'.format(self.connectionParams['schema'], majicTableProp)
                data, rowCount, ok = CadastreCommon.fetchDataFromSqlQuery(connector, sql)
                if ok and rowCount >= 1:
                    self.hasMajicDataProp = True

                # Get data from table voie
                sql = 'SELECT * FROM "{}" LIMIT 1'.format(majicTableVoie)
                if is_postgis:
                    sql = 'SELECT * FROM "{}"."{}" LIMIT 1'.format(self.connectionParams['schema'], majicTableVoie)
                data, rowCount, ok = CadastreCommon.fetchDataFromSqlQuery(connector, sql)
                if ok and rowCount >= 1:
                    self.hasMajicDataVoie = True

                # Get data from table parcelle
                sql = 'SELECT * FROM "{}" LIMIT 1'.format(majicTableParcelle)
                if is_postgis:
                    sql = 'SELECT * FROM "{}"."{}" LIMIT 1'.format(self.connectionParams['schema'], majicTableParcelle)
                data, rowCount, ok = CadastreCommon.fetchDataFromSqlQuery(connector, sql)
                if ok and rowCount >= 1:
                    self.hasMajicDataParcelle = True

                connector.__del__()

        self.liAdresse.setEnabled(self.hasMajicDataVoie and self.hasMajicDataParcelle)
        self.grpProprietaire.setEnabled(self.hasMajicDataProp)
        self.btExportParcelle.setEnabled(self.hasMajicDataProp)

        if not self.hasMajicDataParcelle or not self.hasMajicDataVoie:
            self.qc.updateLog(
                u"<b>Pas de données MAJIC non bâties et/ou fantoir</b> -> désactivation de la recherche d'adresse")
        if not self.hasMajicDataProp:
            self.qc.updateLog(
                u"<b>Pas de données MAJIC propriétaires</b> -> désactivation de la recherche de propriétaires")

    def setupSearchCombobox(self, combo, filterExpression=None, queryMode='qgis'):
        """
        Fil given combobox with data
        from sql query or QGIS layer query
        And add autocompletion
        """
        layer = None
        features = None

        # Get widget
        searchCombo = self.searchComboBoxes[combo]
        cb = searchCombo['widget']
        cb.clear()

        # Get corresponding QGIS layer
        itemList = []
        table = searchCombo['table']
        layer = CadastreCommon.getLayerFromLegendByTableProps(
            table,
            searchCombo['geomCol'],
            searchCombo['sql']
        )

        self.searchComboBoxes[combo]['layer'] = layer
        if layer:

            # Get all features
            keepattributes = self.searchComboBoxes[combo]['attributes']
            request = QgsFeatureRequest().setSubsetOfAttributes(
                keepattributes,
                layer.fields()
            )

            self.searchComboBoxes[combo]['request'] = request
            labelAttribute = self.searchComboBoxes[combo]['labelAttribute']

            # Get features
            if queryMode == 'sql':
                features = self.getFeaturesFromSqlQuery(
                    layer,
                    filterExpression,
                    keepattributes,
                    self.searchComboBoxes[combo]['orderBy']
                )
            else:
                features = layer.getFeatures(request)

            self.searchComboBoxes[combo]['features'] = features

            # Loop through features
            # optionnaly filter by QgsExpression
            qe = None
            if filterExpression and queryMode == 'qgis':
                qe = QgsExpression(filterExpression)
            if queryMode == 'sql':
                emptyLabel = u'%s item(s)' % len(features)
            else:
                emptyLabel = ''
            cb.addItem('%s' % emptyLabel, '')

            for feat in features:
                keep = True
                if qe:
                    if not qe.evaluate(feat):
                        keep = False
                if keep:
                    if feat and feat[labelAttribute]:
                        itemList.append(feat[labelAttribute])
                        cb.addItem(feat[labelAttribute], feat)

            # style cb to adjust list width to max length content
            pView = cb.view()
            pView.setMinimumWidth(pView.sizeHintForColumn(0))

            # Activate autocompletion ( based on combobox content, match only first letters)
            completer = QCompleter(itemList, self)
            completer.setCompletionMode(QCompleter.PopupCompletion)
            completer.setMaxVisibleItems(30)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            # ~ completer.popup().setStyleSheet("background-color: lightblue")
            cb.setEditable(True)
            cb.setCompleter(completer)

        else:
            # ~ self.qc.updateLog(u'Veuillez charger des données cadastrales dans QGIS pour pouvoir effectuer une recherche')
            self.searchComboBoxes[combo]['layer'] = None
            self.searchComboBoxes[combo]['request'] = None
            self.searchComboBoxes[combo]['features'] = None
            self.searchComboBoxes[combo]['chosenFeature'] = None

        return [layer, features]

    def refreshAutocomplete(self, key):
        """
        Refresh autocompletion while the users add more chars in line edit
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Get value
        combo = self.searchComboBoxes[key]['widget']
        searchValue = str(combo.currentText())

        # Abort if searchValue length too small
        minlen = self.searchComboBoxes[key]['search']['minlen']
        if len(self.qc.normalizeString(searchValue)) < minlen:
            # self.qc.updateLog(u"%s caractères minimum requis pour la recherche !" % minlen)
            QApplication.restoreOverrideCursor()
            return None

        # Get database connection parameters from a qgis layer
        dbtable = self.searchComboBoxes[key]['table']
        layer = CadastreCommon.getLayerFromLegendByTableProps(dbtable.replace('v_', ''))
        if not layer:
            QApplication.restoreOverrideCursor()
            return None
        connectionParams = CadastreCommon.getConnectionParameterFromDbLayer(layer)
        if not connectionParams:
            QApplication.restoreOverrideCursor()
            return None

        # Use db_manager tool to run the query
        connector = CadastreCommon.getConnectorFromUri(connectionParams)
        self.connector = connector

        # Format searchValue
        # get rid of contextual info
        sp = searchValue.split('|')
        if len(sp) > 1:
            searchValue = sp[1]

        # get rid of double spaces
        r = re.compile(r'[ ,]+', re.IGNORECASE)
        searchValue = r.sub(' ', searchValue).strip(' \t\n')

        if key == 'adresse':
            # get rid of stopwords
            stopwords = ['ALLEE', 'AQUEDUC', 'ARCEAUX', 'AVENUE', 'AVENUES', 'BOULEVARD', 'CARREFOUR', 'CARRER',
                         'CHEMIN', 'CHEMINS', 'CHEMIN RURAL', 'CLOS', 'COUR', 'COURS', 'DESCENTE', 'ENCLOS', 'ESCALIER',
                         'ESPACE', 'ESPLANADE', 'GRAND RUE', 'IMPASSE', 'MAIL', 'MONTEE', 'PARVIS', 'PASSAGE',
                         'PASSERELLE', 'PLACE', 'PLAN', 'PONT', 'QUAI', 'ROND-POINT', 'ROUTE', 'RUE', 'RUISSEAU',
                         'SENTE', 'SENTIER', 'SQUARE', 'TERRASSE', 'TRABOULE', 'TRAVERSE', 'TRAVERSEE', 'TRAVERSIER',
                         'TUNNEL', 'VOIE', 'VOIE COMMUNALE', 'VIADUC', 'ZONE',
                         'ACH', 'ALL', 'ANGL', 'ART', 'AV', 'AVE', 'BD', 'BV', 'CAMP', 'CAR', 'CC', 'CD', 'CH', 'CHE',
                         'CHEM', 'CHS ', 'CHV', 'CITE', 'CLOS', 'COTE', 'COUR', 'CPG', 'CR', 'CRS', 'CRX', 'D', 'DIG',
                         'DOM', 'ECL', 'ESC', 'ESP', 'FG', 'FOS', 'FRM', 'GARE', 'GPL', 'GR', 'HAM', 'HLE', 'HLM ',
                         'IMP', 'JTE ', 'LOT', 'MAIL', 'MAIS', 'N', 'PARC', 'PAS', 'PCH', 'PL', 'PLE ', 'PONT', 'PORT',
                         'PROM', 'PRV', 'PTA', 'PTE', 'PTR', 'PTTE', 'QUA', 'QUAI', 'REM', 'RES', 'RIVE', 'RLE', 'ROC',
                         'RPE ', 'RPT ', 'RTE ', 'RUE', 'RULT', 'SEN', 'SQ', 'TOUR', 'TSSE', 'VAL', 'VC', 'VEN', 'VLA',
                         'VOIE', 'VOIR', 'VOY', 'ZONE'
                         ]
            sp = searchValue.split(' ')
            if len(sp) > 0 and self.qc.normalizeString(sp[0]) in stopwords:
                searchValue = ' '.join(sp[1:])
                if len(self.qc.normalizeString(searchValue)) < minlen:
                    self.qc.updateLog(u"%s caractères minimum requis pour la recherche !" % minlen)
                    QApplication.restoreOverrideCursor()
                    return None

        sqlSearchValue = self.qc.normalizeString(searchValue)
        searchValues = sqlSearchValue.split(' ')

        # Build SQL query
        hasCommuneFilter = None
        if key == 'adresse':
            sql = ' SELECT DISTINCT v.voie, c.tex2 AS libcom, v.natvoi, v.libvoi'
            if self.dbType == 'postgis':
                sql += ' FROM "{}"."voie" v'.format(connectionParams['schema'])
            else:
                sql += ' FROM voie v'
            # filter among commune existing in geo_commune
            if self.dbType == 'postgis':
                sql += ' INNER JOIN "{}"."geo_commune" c ON c.commune = v.commune'.format(connectionParams['schema'])
            else:
                sql += ' INNER JOIN geo_commune c ON c.commune = v.commune'
            sql += " WHERE 2>1"
            for sv in searchValues:
                sql += " AND libvoi LIKE %s" % self.connector.quoteString('%' + sv + '%')

            # filter on the chosen commune in the combobox, if any
            communeCb = self.searchComboBoxes['commune']
            searchCom = str(self.liCommune.currentText())
            if communeCb and communeCb['chosenFeature'] and not isinstance(communeCb['chosenFeature'],
                                                                           list) and 'item(s)' not in searchCom:
                geo_commune = communeCb['chosenFeature']['geo_commune']
                sql += ' AND trim(c.geo_commune) = %s' % self.connector.quoteString(geo_commune)
                hasCommuneFilter = True

            # order
            sql += ' ORDER BY c.tex2, v.natvoi, v.libvoi'

        if key == 'proprietaire':

            # determines if search by usage name or birth name
            searchByBirthName = self.cbSearchNameBirth.isChecked()

            # get commune code from combo
            communeProprioCb = self.searchComboBoxes['commune_proprietaire']
            cityJoin = ''
            selectedCity = None
            if 'chosenFeature' in communeProprioCb and communeProprioCb['chosenFeature'] is not None:
                selectedCity = communeProprioCb['chosenFeature']['geo_commune']

            if self.dbType == "postgis":
                PGschema = connectionParams["schema"]
                sqlFrom = "  FROM " + PGschema + ".proprietaire\r\n"
                cityJoin = ' INNER JOIN "{}"."commune" commune ON commune.ccocom = proprio.ccocom\r\n'.format(connectionParams['schema'])
            else:
                sqlFrom = "  FROM proprietaire\r\n"
                cityJoin = " INNER JOIN commune ON commune.ccocom = proprio.ccocom\r\n"

            selectedCity = '' if selectedCity is None else selectedCity

            if searchByBirthName is False:
                # search by usage name
                sql = "/* search by usage name*/\r\n"
                sql += "WITH proprio AS (\r\n"
                sql += "  SELECT\r\n"
                sql += "    ccocom, comptecommunal, dnuper, dnomus, dprnus,\r\n"
                sql += "    CASE\r\n"
                sql += "        WHEN gtoper = '1' THEN COALESCE(rtrim(dqualp),'')||' '||COALESCE(rtrim(dnomus),'')||' '||COALESCE(rtrim(dprnus),'')\r\n"
                sql += "        WHEN gtoper = '2' THEN trim(ddenom)\r\n"
                sql += "    END AS nom_usage\r\n"
                sql += sqlFrom
                sql += ")\r\n"
                sql += "SELECT nom_usage, comptecommunal, dnuper, geo_commune\r\n"
                sql += "FROM proprio\r\n"
                sql += cityJoin
                sql += "WHERE 2>1\r\n"

                for sv in searchValues:
                    sql += "AND nom_usage LIKE %s" % self.connector.quoteString('%' + sv + '%') + "\r\n"

                sql += " AND commune.commune LIKE %s" % self.connector.quoteString('%' + selectedCity + '%')
                sql += "GROUP BY proprio.ccocom, comptecommunal, dnuper, nom_usage, geo_commune\r\n"
                sql += "ORDER BY nom_usage\r\n"

            elif searchByBirthName is True:
                # search by birth name
                sql = "/* search by birth name*/\r\n"
                sql += "WITH proprio AS (\r\n"
                sql += "  SELECT\r\n"
                sql += "    ccocom, comptecommunal, dnuper, dnomus, dprnus,\r\n"
                sql += "    CASE\r\n"
                sql += "        WHEN gtoper = '1' THEN COALESCE(rtrim(dqualp),'')||' '||COALESCE(rtrim(dnomlp),'')||' '||COALESCE(rtrim(dprnlp),'')\r\n"
                sql += "        WHEN gtoper = '2' THEN trim(ddenom)\r\n"
                sql += "    END AS nom_naissance\r\n"
                sql += sqlFrom
                sql += ")\r\n"
                sql += "SELECT nom_naissance, comptecommunal, dnuper, geo_commune\r\n"
                sql += "FROM proprio\r\n"
                sql += cityJoin
                sql += "WHERE 2>1\r\n"

                for sv in searchValues:
                    sql += "AND nom_naissance LIKE %s" % self.connector.quoteString('%' + sv + '%') + "\r\n"

                sql += " AND commune.commune LIKE %s" % self.connector.quoteString('%' + selectedCity + '%') + "\r\n"
                sql += "GROUP BY proprio.ccocom, comptecommunal, dnuper, dnomus, dprnus, nom_naissance, geo_commune\r\n"
                sql += "ORDER BY nom_naissance\r\n"
        sql += ' LIMIT 50'

        data, rowCount, ok = CadastreCommon.fetchDataFromSqlQuery(connector, sql)

        # Write message in log
        msg = u"%s résultats correpondent à '%s'" % (rowCount, searchValue)
        if key == 'adresse' and hasCommuneFilter:
            msg += ' pour la commune %s' % searchCom
        # self.qc.updateLog(msg)

        # Fill in the combobox
        cb = self.searchComboBoxes[key]['widget']
        itemList = []
        foundValues = {}

        maxString = ''
        maxStringSize = 0
        for line in data:
            if key == 'adresse':
                label = '%s | %s %s' % (
                    line[1].strip(),
                    line[2].strip(),
                    line[3].strip()
                )
                val = {'voie': line[0]}

            if key == 'proprietaire':
                # ~ label = '%s - %s | %s' % (line[3], line[2], line[0].strip())
                label = '%s | %s' % (line[1], line[0].strip())
                val = {
                    'cc': ["'%s'" % a for a in line[1].split(',')],
                    'dnuper': line[2]
                }

            itemList.append(label)
            ll = len(label)
            if ll > maxStringSize:
                maxString = label
                maxStringSize = ll

            # Add found values in object
            foundValues[label] = val

        self.searchComboBoxes[key]['foundValues'] = foundValues

        # Refresh list of item in completer
        li = cb.lineEdit()
        co = li.completer()
        co.model().setStringList(itemList)
        co.updateModel()

        # print(co.model().stringList())

        # change width of completer popup
        p = co.popup()
        w = (p.width() - p.viewport().width()) + 2 * p.frameWidth() + p.fontMetrics().boundingRect(maxString).width()
        p.setMinimumWidth(w)

        # cr = QRect() # must define qrect to move it & show popup on left (not working)
        # co.complete(cr)

        # Highlight first item
        # todo

        # We do not fill the combobox (cause it overrides autocompletion)

        # Restore cursor
        QApplication.restoreOverrideCursor()

    def getFeaturesFromSqlQuery(self, layer, filterExpression=None, attributes='*', orderBy=None):
        """
        Get data from a db table,
        optionnally filtered by given expression
        and get corresponding QgsFeature objects
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Get connection parameters
        connectionParams = CadastreCommon.getConnectionParameterFromDbLayer(layer)
        if not connectionParams:
            QApplication.restoreOverrideCursor()
            return None

        # set properties
        self.dbType = connectionParams['dbType']
        self.schema = connectionParams['schema']

        # Use db_manager tool to run the query
        connector = CadastreCommon.getConnectorFromUri(connectionParams)

        # SQL
        sql = ' SELECT %s' % ', '.join(attributes)

        # Replace geo_parcelle by parcelle_info if necessary
        table = connectionParams['table']
        if table == 'geo_parcelle':
            table = 'parcelle_info'
        # Build table name
        f = '"%s"' % table
        if self.dbType == 'postgis':
            f = '"{}"."{}"'.format(connectionParams['schema'], table)

        # SQL
        sql += ' FROM %s' % f
        sql += " WHERE 2>1"
        if filterExpression:
            sql += " AND %s" % filterExpression
        if orderBy:
            sql += ' ORDER BY %s' % ', '.join(orderBy)

        # Get data
        # self.qc.updateLog(sql)
        data, rowCount, ok = CadastreCommon.fetchDataFromSqlQuery(connector, sql)

        # Get features
        features = []
        if rowCount > 0:
            fids = [str(a[0]) for a in data]
            exp = ' "%s" IN ( %s ) ' % (
                attributes[0],
                ','.join(fids)
            )
            request = QgsFeatureRequest().setSubsetOfAttributes(attributes, layer.fields()).setFilterExpression(exp)
            if orderBy:
                request.addOrderBy(orderBy[0])
            for feat in layer.getFeatures(request):
                features.append(feat)

        connector.__del__()

        QApplication.restoreOverrideCursor()
        return features

    def getFeatureFromComboboxValue(self, combo):
        """
        Get the feature corresponding to
        the chosen combobox value
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Get widget
        searchCombo = self.searchComboBoxes[combo]
        cb = searchCombo['widget']

        # Reinit
        self.searchComboBoxes[combo]['chosenFeature'] = None
        feature = cb.itemData(cb.currentIndex())
        if feature:
            self.searchComboBoxes[combo]['chosenFeature'] = feature

        QApplication.restoreOverrideCursor()

    def onCompleterActivated(self, key):
        """
        Triggered when the users chooses an item in the combobox completer popup
        """
        cb = self.searchComboBoxes[key]['widget']
        label = cb.currentText()
        li = cb.lineEdit()
        co = li.completer()
        labellist = []
        labellist.append(label.split('|')[0].strip())
        co.model().setStringList(labellist)
        co.updateModel()
        if label in self.searchComboBoxes[key]['foundValues']:
            chosenValue = self.searchComboBoxes[key]['foundValues'][label]
            self.onSearchItemChoose(key, label, chosenValue)

    def onSearchItemChoose(self, key, label, value):
        """
        Select parcelles corresponding
        to chosen item in combo box
        (adresse, proprietaire)
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Get value
        # combo = self.searchComboBoxes[key]['widget']
        # value = combo.itemData(combo.currentIndex())
        if not value:
            QApplication.restoreOverrideCursor()
            return None

        # Set filter expression for parcell child data
        ckey = self.searchComboBoxes[key]['search']['parcelle_child']
        if key == 'adresse':
            filterExpression = "voie = '%s'" % value['voie']

        if key == 'proprietaire':
            filterExpression = "comptecommunal IN (%s)" % ', '.join(value['cc'])

        [layer, features] = self.setupSearchCombobox(
            ckey,
            filterExpression,
            'sql'
        )

        # Set properties
        self.searchComboBoxes[key]['layer'] = layer
        self.searchComboBoxes[key]['features'] = features
        self.searchComboBoxes[key]['chosenFeature'] = features

        # Set proprietaire id
        if key == 'proprietaire':
            self.searchComboBoxes[key]['id'] = value['cc']

        if features:
            self.qc.updateLog(
                u"%s parcelle(s) trouvée(s) pour '%s'" % (
                    len(features),
                    label
                )
            )
            self.setZoomToChosenSearchCombobox(key)

        QApplication.restoreOverrideCursor()

    def onNonSearchItemChoose(self, key):
        """
        Get feature from chosen item in combobox
        and optionnaly fill its children combobox
        """
        # get feature from the chosen value
        self.getFeatureFromComboboxValue(key)

        # optionnaly also update children combobox
        item = self.searchComboBoxes[key]
        if 'children' in item:
            if not isinstance(item['children'], list):
                return
            for child in item['children']:
                feature = item['chosenFeature']
                ckey = child['key']
                fkey = child['fkey']
                if feature:
                    filterExpression = "%s = '%s' AND lot = '%s'" % (fkey, feature[fkey], feature['lot'])
                    self.setupSearchCombobox(ckey, filterExpression, 'sql')
                else:
                    if child['getIfNoFeature']:
                        self.setupSearchCombobox(ckey, None, 'sql')

    def onNonSearchItemEdit(self, key):
        """
        Empty previous stored feature
        for the combobox every time
        the user edit its content
        """
        self.searchComboBoxes[key]['chosenFeature'] = None

    def onNonSearchItemReset(self, key):
        """
        Unchoose item in combobox
        which also trigger onNonSearchItemChoose above
        """
        self.searchComboBoxes[key]['chosenFeature'] = None
        self.searchComboBoxes[key]['widget'].setCurrentIndex(0)

    def onSearchItemReset(self, key):
        """
        Unchoose item in a searchable combobox
        which also trigger
        """
        self.searchComboBoxes[key]['chosenFeature'] = None
        self.searchComboBoxes[key]['widget'].setCurrentIndex(0)
        self.searchComboBoxes[key]['widget'].lineEdit().selectAll()
        self.searchComboBoxes[key]['widget'].lineEdit().setFocus()
        self.searchComboBoxes[key]['widget'].lineEdit().setText(u'')

    def onSearchItemFocus(self, key):
        """
        Select all content on focus by click
        """
        self.searchComboBoxes[key]['widget'].lineEdit().selectAll()
        self.searchComboBoxes[key]['widget'].lineEdit().setFocus()

    def setZoomToChosenSearchCombobox(self, combo):
        """
        Zoom to the feature(s)
        selected in the give combobox
        """
        # Get widget
        searchCombo = self.searchComboBoxes[combo]
        # cb = searchCombo['widget']

        # Zoom
        if searchCombo['chosenFeature']:
            if isinstance(searchCombo['chosenFeature'], list):
                # buid virtual geom
                f = searchCombo['chosenFeature'][0]
                extent = f.geometry().boundingBox()
                for feat in searchCombo['chosenFeature']:
                    extent.combineExtentWith(feat.geometry().boundingBox())
            else:
                extent = searchCombo['chosenFeature'].geometry().boundingBox()

            # reproject extent if needed
            crsDest = QgsMapSettings().destinationCrs()
            layer = searchCombo['layer']
            crsSrc = layer.crs()
            if crsSrc.authid() != crsDest.authid():
                xform = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
                extent = xform.transform(extent)

            self.mc.setExtent(extent)
            self.mc.refresh()

    def setCenterToChosenSearchCombobox(self, combo):
        """
        Center to the feature(s)
        chosen in the corresponding combobox
        """
        # Get widget
        searchCombo = self.searchComboBoxes[combo]
        # cb = searchCombo['widget']

        # Center
        if searchCombo['chosenFeature']:
            # first get scale
            scale = self.mc.scale()

            # then zoom to geometry extent
            if isinstance(searchCombo['chosenFeature'], list):
                # buid virtual geom
                f = searchCombo['chosenFeature'][0]
                extent = f.geometry().boundingBox()
                for feat in searchCombo['chosenFeature']:
                    extent.combineExtentWith(feat.geometry().boundingBox())
            else:
                extent = searchCombo['chosenFeature'].geometry().boundingBox()

            # reproject extent if needed
            crsDest = QgsMapSettings().destinationCrs()
            layer = searchCombo['layer']
            crsSrc = layer.crs()
            if crsSrc.authid() != crsDest.authid():
                xform = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
                extent = xform.transform(extent)

            self.mc.setExtent(extent)

            # the set the scale back
            self.mc.zoomScale(scale)
            self.mc.refresh()

    def setSelectionToChosenSearchCombobox(self, combo):
        """
        Select the feature(s)
        corresponding to the chosen item
        """
        # Get widget
        searchCombo = self.searchComboBoxes[combo]
        # cb = searchCombo['widget']

        # Select
        if searchCombo['chosenFeature'] and searchCombo['layer']:
            searchCombo['layer'].removeSelection()
            if isinstance(searchCombo['chosenFeature'], list):
                i = [feat.id() for feat in searchCombo['chosenFeature']]
            else:
                i = searchCombo['chosenFeature'].id()

            searchCombo['layer'].select(i)

    def updateConnexionParams(self):
        """
        Update connection settings if broken
        """
        dbtable = self.searchComboBoxes['commune']['table']
        layer = CadastreCommon.getLayerFromLegendByTableProps(dbtable.replace('v_', ''))
        if not layer:
            return

        # Get connection parameters
        connectionParams = CadastreCommon.getConnectionParameterFromDbLayer(layer)

        if not connectionParams:
            return

        self.connectionParams = connectionParams
        self.dbType = connectionParams['dbType']
        self.schema = connectionParams['schema']
        connector = CadastreCommon.getConnectorFromUri(connectionParams)
        self.connector = connector

    def setIdentifierToChosenItem(self, key):
        """
        Select the proprietaire(s)
        corresponding to the chosen item
        """
        w = None
        for item in self.zoomButtons[key]['comboboxes']:
            if self.searchComboBoxes[item]['chosenFeature'] and self.searchComboBoxes[item]['layer']:
                w = item

        if w:
            if w != 'parcelle':
                return
            searchCombo = self.searchComboBoxes[w]

            if not self.connectionParams or not self.connector:
                self.updateConnexionParams()

            if not self.connector:
                return

            # Select
            if searchCombo['chosenFeature'] and searchCombo['layer']:
                feat = searchCombo['chosenFeature']

                if feat:

                    parcelle_dialog = CadastreParcelleDialog(
                        self.iface,
                        searchCombo['layer'],
                        feat,
                        self
                    )
                    parcelle_dialog.show()

                else:
                    self.qc.updateLog(u'Aucune parcelle sélectionnée !')

    def printInfosProprietaires(self):
        """
        Action for selected proprietaire(s)
        print/copy in clipboard/save
        """

        document = QTextDocument()
        document.setHtml(
            "<h1>Parcelle : %s</h1><table width=95%%><tr><td>%s</td></tr></table>" % (
                self.textEdit.toolTip(), self.textEdit.toHtml()
            )
        )

        plugin_dir = str(Path(__file__).resolve().parent.parent)

        printer = QPrinter()
        printer.setPageSize(QPrinter.A4)
        printer.setOrientation(QPrinter.Landscape)
        printer.setPageMargins(5, 10, 5, 10, QPrinter.Millimeter)
        printer.setOutputFormat(QPrinter.NativeFormat)
        dlg = QPrintPreviewDialog(printer)
        dlg.setWindowIcon(QIcon(
            os.path.join(
                plugin_dir, 'icons', "print.png"
            )
        ))
        dlg.setWindowTitle("Aperçu")
        dlg.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        dlg.paintRequested.connect(document.print_)
        dlg.exec_()

    def copyInfosProprietaires(self):
        QApplication.clipboard().setText(
            "<h1>Parcelle : %s</h1><table width=95%%><tr><td>%s</td></tr></table>" % (
                self.textEdit.toolTip(), self.textEdit.toHtml()
            )
        )
        self.qc.updateLog('Texte copié dans le presse papier !')

    def saveInfosProprietaires(self):
        plugin_dir = str(Path(__file__).resolve().parent.parent)

        dlgFile = QFileDialog(self, "Enregistrer sous ...")
        dlgFile.setNameFilters(("All (*.htm*)", "HTML (*.html)", "HTM (*.htm)"))
        dlgFile.selectNameFilter("Fichier HTML (*.html)")
        dlgFile.setDefaultSuffix("html")
        dlgFile.setViewMode(QFileDialog.Detail)
        dlgFile.setDirectory(plugin_dir)
        dlgFile.setAcceptMode(QFileDialog.AcceptSave)

        if not dlgFile.exec_():
            return

        fileName = dlgFile.selectedFiles()[0]
        with open(fileName, 'w', encoding="utf8", errors="surrogateescape") as inFile:
            inFile.write(
                "<h1>Parcelle : %s</h1><table width=95%%><tr><td>%s</td></tr></table>" % (
                    self.textEdit.toolTip(), self.textEdit.toHtml()
                )
            )
            self.qc.updateLog('fichier sauvegarde sous : %s !' % fileName)

    def setCenterToChosenItem(self, key):
        """
        Set map center corresponding
        to the chosen feature(s) for the
        last not null item in the list
        """
        w = None
        for item in self.zoomButtons[key]['comboboxes']:
            if self.searchComboBoxes[item]['chosenFeature'] \
                    and self.searchComboBoxes[item]['layer']:
                w = item
        if w:
            self.setCenterToChosenSearchCombobox(w)

    def setZoomToChosenItem(self, key):
        """
        Zoom to the chosen feature(s) for the
        last not null item in the list
        """
        w = None
        for item in self.zoomButtons[key]['comboboxes']:
            if self.searchComboBoxes[item]['chosenFeature'] \
                    and self.searchComboBoxes[item]['layer']:
                w = item
        if w:
            self.setZoomToChosenSearchCombobox(w)

    def setSelectionToChosenItem(self, key):
        """
        Select the feature(s) for the
        last non null item in the list
        """
        w = None
        for item in self.zoomButtons[key]['comboboxes']:
            if self.searchComboBoxes[item]['chosenFeature'] \
                    and self.searchComboBoxes[item]['layer']:
                w = item
        if w:
            self.setSelectionToChosenSearchCombobox(w)

    def export_proprietaire(self):
        """
        Export the selected proprietaire
        as PDF using the template composer
        filled with appropriate data
        """
        if not self.connectionParams or not self.connector:
            self.updateConnexionParams()

        if not self.connector:
            return

        # Search proprietaire by dnuper
        cc = self.searchComboBoxes['proprietaire']['id']
        if not cc:
            self.qc.updateLog('Aucune donnée trouvée pour ce propriétaire !')
            return

        layer = self.searchComboBoxes['proprietaire']['layer']
        qex = CadastreExport(QgsProject.instance(), layer, 'proprietaire', cc)

        with OverrideCursor(Qt.WaitCursor):
            exports = qex.export_as_pdf()

        if not exports:
            self.qc.updateLog('Problème lors de l\'export PDF')
            self.iface.messageBar().pushCritical(
                "Export PDF", "Erreur lors de l'export PDF")
            return

        parent = Path(exports[0]).parent.absolute()
        self.iface.messageBar().pushSuccess(
            "Export PDF",
            "L'export PDF a été fait avec succès dans <a href=\"{0}\">{0}</a>".format(parent)
        )

    def exportParcelle(self, key):
        """
        Export the selected parcelle
        as PDF using the template composer
        filled with appropriate data
        """
        if not self.connectionParams or not self.connector:
            self.updateConnexionParams()

        if not self.connector:
            return

        feature = self.searchComboBoxes[key]['chosenFeature']
        layer = self.searchComboBoxes[key]['layer']
        if not feature:
            self.qc.updateLog('Aucune parcelle sélectionnée !')
            return

        compte_communal = CadastreCommon.getCompteCommunalFromParcelleId(
            feature['geo_parcelle'],
            self.connectionParams,
            self.connector
        )
        qex = CadastreExport(
            QgsProject.instance(), layer, 'parcelle', compte_communal, feature['geo_parcelle'])

        with OverrideCursor(Qt.WaitCursor):
            exports = qex.export_as_pdf()

        if not exports:
            self.qc.updateLog('Problème lors de l\'export PDF')
            self.iface.messageBar().pushCritical(
                "Export PDF", "Erreur lors de l'export PDF")
            return

        parent = Path(exports[0]).parent.absolute()
        self.iface.messageBar().pushSuccess(
            "Export PDF",
            "L'export PDF a été fait avec succès dans <a href=\"{0}\">{0}</a>".format(parent)
        )

    def onVisibilityChange(self, visible):
        """
        Fill commune combobox when the dock
        becomes visible
        """
        if visible:
            # fix_print_with_import
            # self.setupSearchCombobox('commune', None, 'sql')
            # print("visible")
            pass
        else:
            self.txtLog.clear()
