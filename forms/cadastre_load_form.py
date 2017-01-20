# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/vagrant/cadastre_load_form.ui'
#
# Created: Thu Jan 12 21:37:33 2017
#      by: PyQt4 UI code generator 4.11.2
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

class Ui_cadastre_load_form(object):
    def setupUi(self, cadastre_load_form):
        cadastre_load_form.setObjectName(_fromUtf8("cadastre_load_form"))
        cadastre_load_form.resize(523, 603)
        self.verticalLayout = QtGui.QVBoxLayout(cadastre_load_form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scrollArea = QtGui.QScrollArea(cadastre_load_form)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 503, 550))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.liDbConnection = QtGui.QComboBox(self.groupBox)
        self.liDbConnection.setObjectName(_fromUtf8("liDbConnection"))
        self.gridLayout.addWidget(self.liDbConnection, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.liDbSchema = QtGui.QComboBox(self.groupBox)
        self.liDbSchema.setObjectName(_fromUtf8("liDbSchema"))
        self.gridLayout.addWidget(self.liDbSchema, 2, 1, 1, 1)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.liDbType = QtGui.QComboBox(self.groupBox)
        self.liDbType.setObjectName(_fromUtf8("liDbType"))
        self.liDbType.addItem(_fromUtf8(""))
        self.liDbType.addItem(_fromUtf8(""))
        self.liDbType.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.liDbType, 0, 1, 1, 1)
        self.verticalLayout_6.addLayout(self.gridLayout)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.groupBox_5 = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.verticalLayout_14 = QtGui.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_14.setObjectName(_fromUtf8("verticalLayout_14"))
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.label_12 = QtGui.QLabel(self.groupBox_5)
        self.label_12.setMaximumSize(QtCore.QSize(70, 16777215))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.horizontalLayout_8.addWidget(self.label_12)
        self.liTheme = QtGui.QComboBox(self.groupBox_5)
        self.liTheme.setObjectName(_fromUtf8("liTheme"))
        self.liTheme.addItem(_fromUtf8(""))
        self.horizontalLayout_8.addWidget(self.liTheme)
        self.verticalLayout_14.addLayout(self.horizontalLayout_8)
        self.verticalLayout_2.addWidget(self.groupBox_5)
        self.groupBox_2 = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.cbMainLayersOnly = QtGui.QCheckBox(self.groupBox_2)
        self.cbMainLayersOnly.setObjectName(_fromUtf8("cbMainLayersOnly"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.cbMainLayersOnly)
        self.verticalLayout_3.addLayout(self.formLayout)
        self.verticalLayout_2.addWidget(self.groupBox_2)
        self.btProcessLoading = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.btProcessLoading.setObjectName(_fromUtf8("btProcessLoading"))
        self.verticalLayout_2.addWidget(self.btProcessLoading)
        self.pbProcess = QtGui.QProgressBar(self.scrollAreaWidgetContents)
        self.pbProcess.setProperty("value", 0)
        self.pbProcess.setObjectName(_fromUtf8("pbProcess"))
        self.verticalLayout_2.addWidget(self.pbProcess)
        self.txtLog = QtGui.QTextEdit(self.scrollAreaWidgetContents)
        self.txtLog.setObjectName(_fromUtf8("txtLog"))
        self.verticalLayout_2.addWidget(self.txtLog)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.buttonBox = QtGui.QDialogButtonBox(cadastre_load_form)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(cadastre_load_form)
        QtCore.QMetaObject.connectSlotsByName(cadastre_load_form)

    def retranslateUi(self, cadastre_load_form):
        cadastre_load_form.setWindowTitle(_translate("cadastre_load_form", "Cadastre", None))
        self.groupBox.setTitle(_translate("cadastre_load_form", "Base de données de travail", None))
        self.label_2.setText(_translate("cadastre_load_form", "Connexions", None))
        self.label_3.setText(_translate("cadastre_load_form", "Schéma", None))
        self.label.setText(_translate("cadastre_load_form", "Type de base", None))
        self.liDbType.setItemText(0, _translate("cadastre_load_form", "-- Choisir --", None))
        self.liDbType.setItemText(1, _translate("cadastre_load_form", "Postgis", None))
        self.liDbType.setItemText(2, _translate("cadastre_load_form", "Spatialite", None))
        self.groupBox_5.setTitle(_translate("cadastre_load_form", "Styles à appliquer", None))
        self.label_12.setText(_translate("cadastre_load_form", "Thème", None))
        self.liTheme.setItemText(0, _translate("cadastre_load_form", "classique", None))
        self.groupBox_2.setTitle(_translate("cadastre_load_form", "Couches", None))
        self.cbMainLayersOnly.setText(_translate("cadastre_load_form", "Ajouter seulement Communes, sections, parcelles et bâti", None))
        self.btProcessLoading.setText(_translate("cadastre_load_form", "Charger les données", None))
        self.txtLog.setHtml(_translate("cadastre_load_form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; font-style:italic;\">Pensez à supprimer les couches Cadastre du projet QGIS avant d\'en importer d\'autres</span></p></body></html>", None))

import resource_rc
