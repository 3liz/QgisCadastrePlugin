__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import os.path

from pathlib import Path

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

from cadastre.cadastre_loading import CadastreLoading
from cadastre.tools import set_window_title

LOAD_FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        str(Path(__file__).resolve().parent.parent),
        'forms',
        'cadastre_load_form.ui'
    )
)


class CadastreLoadDialog(QDialog, LOAD_FORM_CLASS):

    """ Load data from database. """

    def __init__(self, iface, cadastre_search_dialog, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.setupUi(self)
        self.setWindowTitle(f'{self.windowTitle()} {set_window_title()}')
        self.mc = self.iface.mapCanvas()

        self.cadastre_search_dialog = cadastre_search_dialog

        # common cadastre methods
        from cadastre.dialogs.dialog_common import CadastreCommon
        self.qc = CadastreCommon(self)
        self.ql = CadastreLoading(self)

        # spatialite support
        self.hasSpatialiteSupport = CadastreCommon.hasSpatialiteSupport()
        if not self.hasSpatialiteSupport:
            self.liDbType.removeItem(2)

        # Set initial values
        self.go = True
        self.step = 0
        self.totalSteps = 0
        self.dbType = None
        self.dbpluginclass = None
        self.connectionName = None
        self.connection = None
        self.db = None
        self.schema = None
        self.schemaList = None
        self.hasStructure = None

        # Get style list
        self.getStyleList()

        # Signals/Slot Connections
        self.liDbType.currentIndexChanged[str].connect(self.qc.updateConnectionList)
        self.liDbConnection.currentIndexChanged[str].connect(self.qc.updateSchemaList)
        self.btProcessLoading.clicked.connect(self.onProcessLoadingClicked)
        self.ql.cadastreLoadingFinished.connect(self.onLoadingEnd)

        self.btLoadSqlLayer.clicked.connect(self.onLoadSqlLayerClicked)

        self.rejected.connect(self.onClose)
        self.buttonBox.rejected.connect(self.onClose)

        self.qc.load_default_values()

    def onClose(self):
        """
        Close dialog
        """
        if self.db:
            self.db.connector.__del__()
        self.close()

    def getStyleList(self):
        """
        Get the list of style directories
        inside the plugin dir
        and add combobox item
        """
        spath = os.path.join(self.qc.plugin_dir, "styles/")
        dirs = os.listdir(spath)
        dirs = [a for a in dirs if os.path.isdir(os.path.join(spath, a))]
        dirs.sort()
        cb = self.liTheme
        cb.clear()
        for d in dirs:
            cb.addItem('%s' % d, d)

    def onProcessLoadingClicked(self):
        """
        Activate the loading of layers
        from database tables
        when user clicked on button
        """
        if self.connection:
            if self.db:
                self.ql.process_loading()

    def onLoadSqlLayerClicked(self):
        """
        Loads a layer
        from given SQL
        when user clicked on button
        """
        if self.connection:
            if self.db:
                self.ql.load_sql_layer()

    def onLoadingEnd(self):
        """
        Actions to trigger
        when all the layers
        have been loaded
        """
        self.cadastre_search_dialog.checkMajicContent()
        self.cadastre_search_dialog.clearComboboxes()
        self.cadastre_search_dialog.setupSearchCombobox('commune', None, 'sql')
        self.cadastre_search_dialog.setupSearchCombobox('commune_proprietaire', None, 'sql')
        # self.cadastre_search_dialog.setupSearchCombobox('section', None, 'sql')
