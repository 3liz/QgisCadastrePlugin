__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import os.path
import sys

from pathlib import Path

from qgis.PyQt.QtGui import QPixmap
from qgis.PyQt.QtWidgets import QDialog

sys.path.append(os.path.join(str(Path(__file__).resolve().parent), 'forms'))


# db_manager scripts
from qgis.PyQt import uic

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
