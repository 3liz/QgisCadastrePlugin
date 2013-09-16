# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qadastre_option_form.ui'
#
# Created: Mon Sep 16 17:01:01 2013
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_qadastre_option_form(object):
    def setupUi(self, qadastre_option_form):
        qadastre_option_form.setObjectName(_fromUtf8("qadastre_option_form"))
        qadastre_option_form.resize(395, 317)
        self.verticalLayout = QtGui.QVBoxLayout(qadastre_option_form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scrollArea = QtGui.QScrollArea(qadastre_option_form)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 375, 297))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox_7 = QtGui.QGroupBox(self.scrollAreaWidgetContents)
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
        self.verticalLayout_2.addWidget(self.groupBox_7)
        self.groupBox = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.lineEdit = QtGui.QLineEdit(self.groupBox)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(qadastre_option_form)
        QtCore.QMetaObject.connectSlotsByName(qadastre_option_form)

    def retranslateUi(self, qadastre_option_form):
        qadastre_option_form.setWindowTitle(_translate("qadastre_option_form", "Qadastre", None))
        self.groupBox_7.setTitle(_translate("qadastre_option_form", "Interface QGIS", None))
        self.label_13.setText(_translate("qadastre_option_form", "Vous pouvez choisir d\'appliquer une interface\n"
"simplifiée de QGIS pour consulter le cadastre\n"
"ou de revenir à l\'interface par défaut", None))
        self.btInterfaceQadastre.setText(_translate("qadastre_option_form", "Interface Qadastre", None))
        self.btInterfaceQgis.setText(_translate("qadastre_option_form", "Interface QGIS", None))
        self.groupBox.setTitle(_translate("qadastre_option_form", "Nom des fichiers MAJIC", None))
        self.label.setText(_translate("qadastre_option_form", "non bâti", None))

