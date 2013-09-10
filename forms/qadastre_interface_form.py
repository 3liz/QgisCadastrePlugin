# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qadastre_interface_form.ui'
#
# Created: Tue Sep 10 18:33:16 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_qadastre_interface_form(object):
    def setupUi(self, qadastre_interface_form):
        qadastre_interface_form.setObjectName(_fromUtf8("qadastre_interface_form"))
        qadastre_interface_form.resize(362, 297)
        self.verticalLayout = QtGui.QVBoxLayout(qadastre_interface_form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox_7 = QtGui.QGroupBox(qadastre_interface_form)
        self.groupBox_7.setObjectName(_fromUtf8("groupBox_7"))
        self.verticalLayout_9 = QtGui.QVBoxLayout(self.groupBox_7)
        self.verticalLayout_9.setObjectName(_fromUtf8("verticalLayout_9"))
        self.label_13 = QtGui.QLabel(self.groupBox_7)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.verticalLayout_9.addWidget(self.label_13)
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.btInterfaceQadastre = QtGui.QPushButton(self.groupBox_7)
        self.btInterfaceQadastre.setObjectName(_fromUtf8("btInterfaceQadastre"))
        self.horizontalLayout_9.addWidget(self.btInterfaceQadastre)
        self.btInterfaceQgis = QtGui.QPushButton(self.groupBox_7)
        self.btInterfaceQgis.setObjectName(_fromUtf8("btInterfaceQgis"))
        self.horizontalLayout_9.addWidget(self.btInterfaceQgis)
        self.verticalLayout_9.addLayout(self.horizontalLayout_9)
        self.lineEdit = QtGui.QLineEdit(self.groupBox_7)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.verticalLayout_9.addWidget(self.lineEdit)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_9.addItem(spacerItem)
        self.verticalLayout.addWidget(self.groupBox_7)

        self.retranslateUi(qadastre_interface_form)
        QtCore.QMetaObject.connectSlotsByName(qadastre_interface_form)

    def retranslateUi(self, qadastre_interface_form):
        qadastre_interface_form.setWindowTitle(QtGui.QApplication.translate("qadastre_interface_form", "Qadastre", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_7.setTitle(QtGui.QApplication.translate("qadastre_interface_form", "Interface QGIS", None, QtGui.QApplication.UnicodeUTF8))
        self.label_13.setText(QtGui.QApplication.translate("qadastre_interface_form", "Vous pouvez choisir d\'appliquer une interface\n"
"simplifiée de QGIS pour consulter le cadastre\n"
"ou de revenir à l\'interface par défaut", None, QtGui.QApplication.UnicodeUTF8))
        self.btInterfaceQadastre.setText(QtGui.QApplication.translate("qadastre_interface_form", "Interface Qadastre", None, QtGui.QApplication.UnicodeUTF8))
        self.btInterfaceQgis.setText(QtGui.QApplication.translate("qadastre_interface_form", "Interface QGIS", None, QtGui.QApplication.UnicodeUTF8))

