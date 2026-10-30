__copyright__ = "Copyright 2026, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import re

from html import unescape

from qgis.core import QgsProcessingFeedback


class CadastreFeedback(QgsProcessingFeedback):
    """Processing feedback with a sub step text, used by the import."""

    def setSubStepText(self, text: str):
        """Text of the current sub step, displayed below the step text. Nothing by default."""


def html_to_text(html: str) -> str:
    """Convert the HTML messages of the import to plain text"""
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    return unescape(text).strip()


class CadastreProcessingFeedback(CadastreFeedback):
    """Send the messages and the progress of the import to the feedback of a Processing algorithm."""

    def __init__(self, feedback: QgsProcessingFeedback):
        super().__init__()
        self._feedback = feedback
        self.progressChanged.connect(feedback.setProgress)

    def pushInfo(self, info: str):
        # Do not call the parent method: it would also write into the QGIS message log
        self._feedback.pushInfo(html_to_text(info))

    def pushWarning(self, warning: str):
        self._feedback.pushWarning(html_to_text(warning))

    def reportError(self, error: str, fatalError: bool = False):
        self._feedback.reportError(html_to_text(error), fatalError)

    def setProgressText(self, text: str):
        self._feedback.setProgressText(text)
