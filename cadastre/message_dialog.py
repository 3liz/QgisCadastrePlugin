__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import os.path
import sys

from pathlib import Path

from qgis.PyQt.QtWidgets import QDialog

sys.path.append(os.path.join(str(Path(__file__).resolve().parent), 'forms'))

from qgis.PyQt import uic

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