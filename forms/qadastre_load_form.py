# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qadastre_load_form.ui'
#
# Created: Wed Sep 11 11:22:37 2013
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
        qadastre_load_form.resize(281, 625)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scrollArea_3 = QtGui.QScrollArea(self.dockWidgetContents)
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollArea_3.setObjectName(_fromUtf8("scrollArea_3"))
        self.scrollAreaWidgetContents_3 = QtGui.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 261, 580))
        self.scrollAreaWidgetContents_3.setObjectName(_fromUtf8("scrollAreaWidgetContents_3"))
        self.verticalLayout_13 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.verticalLayout_13.setObjectName(_fromUtf8("verticalLayout_13"))
        self.groupBox = QtGui.QGroupBox(self.scrollAreaWidgetContents_3)
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
        self.liTheme = QtGui.QComboBox(self.groupBox_5)
        self.liTheme.setObjectName(_fromUtf8("liTheme"))
        self.liTheme.addItem(_fromUtf8(""))
        self.horizontalLayout_8.addWidget(self.liTheme)
        self.verticalLayout_14.addLayout(self.horizontalLayout_8)
        self.verticalLayout_13.addWidget(self.groupBox_5)
        self.groupBox_6 = QtGui.QGroupBox(self.scrollAreaWidgetContents_3)
        self.groupBox_6.setObjectName(_fromUtf8("groupBox_6"))
        self.verticalLayout_15 = QtGui.QVBoxLayout(self.groupBox_6)
        self.verticalLayout_15.setObjectName(_fromUtf8("verticalLayout_15"))
        self.liOverrideLayer = QtGui.QComboBox(self.groupBox_6)
        self.liOverrideLayer.setObjectName(_fromUtf8("liOverrideLayer"))
        self.liOverrideLayer.addItem(_fromUtf8(""))
        self.liOverrideLayer.addItem(_fromUtf8(""))
        self.verticalLayout_15.addWidget(self.liOverrideLayer)
        self.verticalLayout_13.addWidget(self.groupBox_6)
        self.btProcessLoading = QtGui.QPushButton(self.scrollAreaWidgetContents_3)
        self.btProcessLoading.setObjectName(_fromUtf8("btProcessLoading"))
        self.verticalLayout_13.addWidget(self.btProcessLoading)
        self.pbProcess = QtGui.QProgressBar(self.scrollAreaWidgetContents_3)
        self.pbProcess.setProperty("value", 0)
        self.pbProcess.setObjectName(_fromUtf8("pbProcess"))
        self.verticalLayout_13.addWidget(self.pbProcess)
        self.txtLog = QtGui.QTextEdit(self.scrollAreaWidgetContents_3)
        self.txtLog.setObjectName(_fromUtf8("txtLog"))
        self.verticalLayout_13.addWidget(self.txtLog)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_13.addItem(spacerItem)
        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_3)
        self.verticalLayout.addWidget(self.scrollArea_3)
        qadastre_load_form.setWidget(self.dockWidgetContents)

        self.retranslateUi(qadastre_load_form)
        QtCore.QMetaObject.connectSlotsByName(qadastre_load_form)

    def retranslateUi(self, qadastre_load_form):
        qadastre_load_form.setWindowTitle(QtGui.QApplication.translate("qadastre_load_form", "Qadastre - Charger les données", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("qadastre_load_form", "Base de données de travail", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("qadastre_load_form", "Connexions", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("qadastre_load_form", "Schéma", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("qadastre_load_form", "Type de base", None, QtGui.QApplication.UnicodeUTF8))
        self.liDbType.setItemText(0, QtGui.QApplication.translate("qadastre_load_form", "-- Choisir --", None, QtGui.QApplication.UnicodeUTF8))
        self.liDbType.setItemText(1, QtGui.QApplication.translate("qadastre_load_form", "Postgis", None, QtGui.QApplication.UnicodeUTF8))
        self.liDbType.setItemText(2, QtGui.QApplication.translate("qadastre_load_form", "Spatialite", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_5.setTitle(QtGui.QApplication.translate("qadastre_load_form", "Styles à appliquer", None, QtGui.QApplication.UnicodeUTF8))
        self.label_12.setText(QtGui.QApplication.translate("qadastre_load_form", "Thème", None, QtGui.QApplication.UnicodeUTF8))
        self.liTheme.setItemText(0, QtGui.QApplication.translate("qadastre_load_form", "classique", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_6.setTitle(QtGui.QApplication.translate("qadastre_load_form", "Surcharge", None, QtGui.QApplication.UnicodeUTF8))
        self.liOverrideLayer.setToolTip(QtGui.QApplication.translate("qadastre_load_form", "<html><head/><body><p>Comportement lors du chargement si des données sont déjà ouvertes dans le projet</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.liOverrideLayer.setItemText(0, QtGui.QApplication.translate("qadastre_load_form", "Conserver", None, QtGui.QApplication.UnicodeUTF8))
        self.liOverrideLayer.setItemText(1, QtGui.QApplication.translate("qadastre_load_form", "Remplacer", None, QtGui.QApplication.UnicodeUTF8))
        self.btProcessLoading.setText(QtGui.QApplication.translate("qadastre_load_form", "Charger les données", None, QtGui.QApplication.UnicodeUTF8))
        self.txtLog.setHtml(QtGui.QApplication.translate("qadastre_load_form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

