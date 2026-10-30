__copyright__ = "Copyright 2026, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from qgis.core import QgsProcessingFeedback


class CadastreFeedback(QgsProcessingFeedback):
    """Processing feedback with a sub step text, used by the import."""

    def setSubStepText(self, text: str):
        """Text of the current sub step, displayed below the step text. Nothing by default."""
