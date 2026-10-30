__copyright__ = "Copyright 2026, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import os

from qgis.PyQt.QtGui import QTextCursor
from qgis.PyQt.QtWidgets import QApplication, QLabel, QProgressBar, QTextEdit

from ..feedback import CadastreFeedback
from ..logger import Logger


def append_log(text_edit: QTextEdit, msg: str):
    """Append an HTML message at the end of the given text edit."""
    if os.getenv("CI", "").lower() == "true":
        # Running headless, hack to see logs
        Logger.info(msg)
        return

    text_edit.ensureCursorVisible()
    prefix = '<span style="font-weight:normal;">'
    suffix = "</span>"
    text_edit.append(f"{prefix} {msg} {suffix}")
    c = text_edit.textCursor()
    c.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.MoveAnchor)
    text_edit.setTextCursor(c)
    QApplication.instance().processEvents()


class CadastreDialogFeedback(CadastreFeedback):
    """Feedback writing messages and progress into the widgets of a dialog.

    Business classes (import, loading) only know the CadastreFeedback API,
    so they can also run without any UI.
    """

    def __init__(
        self,
        txt_log: QTextEdit,
        progress_bar: QProgressBar,
        step_label: QLabel | None = None,
        sub_step_label: QLabel | None = None,
    ):
        super().__init__()
        self._txt_log = txt_log
        self._progress_bar = progress_bar
        self._step_label = step_label
        self._sub_step_label = sub_step_label
        self.progressChanged.connect(self._on_progress_changed)

    def pushInfo(self, info: str):
        # Do not call the parent method: it would also write into the QGIS message log
        append_log(self._txt_log, info)

    def pushWarning(self, warning: str):
        append_log(self._txt_log, warning)

    def reportError(self, error: str, fatalError: bool = False):
        append_log(self._txt_log, error)

    def setProgressText(self, text: str):
        if self._step_label:
            self._step_label.setText(f"<b>{text}</b>")

    def setSubStepText(self, text: str):
        if self._sub_step_label:
            self._sub_step_label.setText(text)

    def _on_progress_changed(self, progress: float):
        self._progress_bar.setValue(int(progress))
        QApplication.instance().processEvents()
