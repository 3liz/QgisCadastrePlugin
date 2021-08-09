__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"


from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QPushButton


class CustomPushButton(QPushButton):
    def __init__(self, *args):
        super(CustomPushButton, self).__init__(*args)

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
