# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qadastre_load_form.ui'
#
# Created: Mon Jul 15 17:54:09 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_qadastre_load_form(object):
    def setupUi(self, qadastre_load_form):
        qadastre_load_form.setObjectName(_fromUtf8("qadastre_load_form"))
        qadastre_load_form.resize(450, 569)
        self.verticalLayout = QtGui.QVBoxLayout(qadastre_load_form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scrollArea_3 = QtGui.QScrollArea(qadastre_load_form)
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollArea_3.setObjectName(_fromUtf8("scrollArea_3"))
        self.scrollAreaWidgetContents_3 = QtGui.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 430, 549))
        self.scrollAreaWidgetContents_3.setObjectName(_fromUtf8("scrollAreaWidgetContents_3"))
        self.verticalLayout_13 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.verticalLayout_13.setObjectName(_fromUtf8("verticalLayout_13"))
        self.groupBox = QtGui.QGroupBox(self.scrollAreaWidgetContents_3)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.comboBox = QtGui.QComboBox(self.groupBox)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.comboBox, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.comboBox_2 = QtGui.QComboBox(self.groupBox)
        self.comboBox_2.setObjectName(_fromUtf8("comboBox_2"))
        self.gridLayout.addWidget(self.comboBox_2, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.comboBox_3 = QtGui.QComboBox(self.groupBox)
        self.comboBox_3.setObjectName(_fromUtf8("comboBox_3"))
        self.gridLayout.addWidget(self.comboBox_3, 2, 1, 1, 1)
        self.verticalLayout_6.addLayout(self.gridLayout)
        self.label_10 = QtGui.QLabel(self.groupBox)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.verticalLayout_6.addWidget(self.label_10)
        self.verticalLayout_13.addWidget(self.groupBox)
        self.groupBox_5 = QtGui.QGroupBox(self.scrollAreaWidgetContents_3)
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.verticalLayout_14 = QtGui.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_14.setObjectName(_fromUtf8("verticalLayout_14"))
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.label_12 = QtGui.QLabel(self.groupBox_5)
        self.label_12.setMaximumSize(QtCore.QSize(70, 16777215))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.horizontalLayout_8.addWidget(self.label_12)
        self.comboBox_5 = QtGui.QComboBox(self.groupBox_5)
        self.comboBox_5.setObjectName(_fromUtf8("comboBox_5"))
        self.comboBox_5.addItem(_fromUtf8(""))
        self.horizontalLayout_8.addWidget(self.comboBox_5)
        self.pushButton = QtGui.QPushButton(self.groupBox_5)
        self.pushButton.setMaximumSize(QtCore.QSize(80, 16777215))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.horizontalLayout_8.addWidget(self.pushButton)
        self.verticalLayout_14.addLayout(self.horizontalLayout_8)
        self.verticalLayout_13.addWidget(self.groupBox_5)
        self.groupBox_6 = QtGui.QGroupBox(self.scrollAreaWidgetContents_3)
        self.groupBox_6.setObjectName(_fromUtf8("groupBox_6"))
        self.verticalLayout_15 = QtGui.QVBoxLayout(self.groupBox_6)
        self.verticalLayout_15.setObjectName(_fromUtf8("verticalLayout_15"))
        self.label_11 = QtGui.QLabel(self.groupBox_6)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.verticalLayout_15.addWidget(self.label_11)
        self.comboBox_6 = QtGui.QComboBox(self.groupBox_6)
        self.comboBox_6.setObjectName(_fromUtf8("comboBox_6"))
        self.comboBox_6.addItem(_fromUtf8(""))
        self.comboBox_6.addItem(_fromUtf8(""))
        self.comboBox_6.addItem(_fromUtf8(""))
        self.verticalLayout_15.addWidget(self.comboBox_6)
        self.verticalLayout_13.addWidget(self.groupBox_6)
        self.txtLoadingDataLog = QtGui.QTextEdit(self.scrollAreaWidgetContents_3)
        self.txtLoadingDataLog.setObjectName(_fromUtf8("txtLoadingDataLog"))
        self.verticalLayout_13.addWidget(self.txtLoadingDataLog)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_13.addItem(spacerItem)
        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_3)
        self.verticalLayout.addWidget(self.scrollArea_3)

        self.retranslateUi(qadastre_load_form)
        QtCore.QMetaObject.connectSlotsByName(qadastre_load_form)

    def retranslateUi(self, qadastre_load_form):
        qadastre_load_form.setWindowTitle(QtGui.QApplication.translate("qadastre_load_form", "Qadastre", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("qadastre_load_form", "Base de données de travail", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("qadastre_load_form", "Type de base", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(0, QtGui.QApplication.translate("qadastre_load_form", "pgsql", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(1, QtGui.QApplication.translate("qadastre_load_form", "sqlite", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("qadastre_load_form", "Connexions", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("qadastre_load_form", "Schéma", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("qadastre_load_form", "Connecté à", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_5.setTitle(QtGui.QApplication.translate("qadastre_load_form", "Styles à appliquer", None, QtGui.QApplication.UnicodeUTF8))
        self.label_12.setText(QtGui.QApplication.translate("qadastre_load_form", "Thème", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_5.setItemText(0, QtGui.QApplication.translate("qadastre_load_form", "Défaut", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("qadastre_load_form", "Importer", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_6.setTitle(QtGui.QApplication.translate("qadastre_load_form", "Surcharge", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("qadastre_load_form", "Comportement lors du chargement\n"
"si des données sont déjà ouvertes dans le projet", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_6.setItemText(0, QtGui.QApplication.translate("qadastre_load_form", "Conserver les couches actuelles", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_6.setItemText(1, QtGui.QApplication.translate("qadastre_load_form", "Remplacer par les données de la table", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_6.setItemText(2, QtGui.QApplication.translate("qadastre_load_form", "Annuler tout le chargement", None, QtGui.QApplication.UnicodeUTF8))
        self.txtLoadingDataLog.setHtml(QtGui.QApplication.translate("qadastre_load_form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Log</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

