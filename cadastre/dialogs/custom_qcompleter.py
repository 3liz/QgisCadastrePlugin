__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from qgis.PyQt.QtCore import (
    QRegularExpression,
    QSortFilterProxyModel,
    QStringListModel,
)
from qgis.PyQt.QtWidgets import QCompleter


class CustomQCompleter(QCompleter):
    """
    Custom completer (to allow completion when string found anywhere
    adapted from: http://stackoverflow.com/a/7767999/2156909
    """

    def __init__(self, *args):  # parent=None):
        super().__init__(*args)
        self.local_completion_prefix = ""
        self.source_model = None
        self.filterProxyModel = QSortFilterProxyModel(self)
        self.usingOriginalModel = False

    def setModel(self, model):
        self.source_model = model
        self.filterProxyModel = QSortFilterProxyModel(self)
        self.filterProxyModel.setSourceModel(self.source_model)
        super().setModel(self.filterProxyModel)
        self.usingOriginalModel = True

    def updateModel(self):
        if not self.usingOriginalModel:
            self.filterProxyModel.setSourceModel(self.source_model)

        pattern = QRegularExpression(self.local_completion_prefix,
                                    QRegularExpression.PatternOption.CaseInsensitiveOption
                                    )

        self.filterProxyModel.setFilterRegularExpression(pattern)

    def splitPath(self, path):
        self.local_completion_prefix = path
        self.updateModel()
        if self.filterProxyModel.rowCount() == 0:
            self.usingOriginalModel = False
            self.filterProxyModel.setSourceModel(QStringListModel([path]))
            return [path]

        return []
