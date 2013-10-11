# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cadastre_parcelle_form.ui'
#
# Created: Fri Oct 11 18:46:38 2013
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

class Ui_cadastre_parcelle_form(object):
    def setupUi(self, cadastre_parcelle_form):
        cadastre_parcelle_form.setObjectName(_fromUtf8("cadastre_parcelle_form"))
        cadastre_parcelle_form.resize(420, 477)
        self.verticalLayout = QtGui.QVBoxLayout(cadastre_parcelle_form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scrollArea = QtGui.QScrollArea(cadastre_parcelle_form)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 400, 424))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.parcelleInfo = QtGui.QTextEdit(self.groupBox)
        self.parcelleInfo.setObjectName(_fromUtf8("parcelleInfo"))
        self.verticalLayout_3.addWidget(self.parcelleInfo)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.proprietairesInfo = QtGui.QTextEdit(self.groupBox_2)
        self.proprietairesInfo.setObjectName(_fromUtf8("proprietairesInfo"))
        self.verticalLayout_4.addWidget(self.proprietairesInfo)
        self.verticalLayout_2.addWidget(self.groupBox_2)
        self.groupBox_3 = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btExportParcelle = QtGui.QPushButton(self.groupBox_3)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/cadastre/icons/releve.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btExportParcelle.setIcon(icon)
        self.btExportParcelle.setObjectName(_fromUtf8("btExportParcelle"))
        self.horizontalLayout.addWidget(self.btExportParcelle)
        self.btExportProprietaire = QtGui.QPushButton(self.groupBox_3)
        self.btExportProprietaire.setIcon(icon)
        self.btExportProprietaire.setObjectName(_fromUtf8("btExportProprietaire"))
        self.horizontalLayout.addWidget(self.btExportProprietaire)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.btCentrer = QtGui.QPushButton(self.groupBox_3)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/cadastre/icons/centrer.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btCentrer.setIcon(icon1)
        self.btCentrer.setObjectName(_fromUtf8("btCentrer"))
        self.horizontalLayout_2.addWidget(self.btCentrer)
        self.btZoomer = QtGui.QPushButton(self.groupBox_3)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/cadastre/icons/zoom.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btZoomer.setIcon(icon2)
        self.btZoomer.setObjectName(_fromUtf8("btZoomer"))
        self.horizontalLayout_2.addWidget(self.btZoomer)
        self.btSelectionner = QtGui.QPushButton(self.groupBox_3)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/cadastre/icons/select.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btSelectionner.setIcon(icon3)
        self.btSelectionner.setObjectName(_fromUtf8("btSelectionner"))
        self.horizontalLayout_2.addWidget(self.btSelectionner)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.btParcellesProprietaire = QtGui.QPushButton(self.groupBox_3)
        self.btParcellesProprietaire.setIcon(icon3)
        self.btParcellesProprietaire.setObjectName(_fromUtf8("btParcellesProprietaire"))
        self.horizontalLayout_3.addWidget(self.btParcellesProprietaire)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)
        self.verticalLayout_2.addWidget(self.groupBox_3)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.buttonBox = QtGui.QDialogButtonBox(cadastre_parcelle_form)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(cadastre_parcelle_form)
        QtCore.QMetaObject.connectSlotsByName(cadastre_parcelle_form)
        cadastre_parcelle_form.setTabOrder(self.scrollArea, self.parcelleInfo)
        cadastre_parcelle_form.setTabOrder(self.parcelleInfo, self.proprietairesInfo)
        cadastre_parcelle_form.setTabOrder(self.proprietairesInfo, self.btExportParcelle)
        cadastre_parcelle_form.setTabOrder(self.btExportParcelle, self.btExportProprietaire)
        cadastre_parcelle_form.setTabOrder(self.btExportProprietaire, self.btCentrer)
        cadastre_parcelle_form.setTabOrder(self.btCentrer, self.btZoomer)
        cadastre_parcelle_form.setTabOrder(self.btZoomer, self.btSelectionner)
        cadastre_parcelle_form.setTabOrder(self.btSelectionner, self.buttonBox)

    def retranslateUi(self, cadastre_parcelle_form):
        cadastre_parcelle_form.setWindowTitle(_translate("cadastre_parcelle_form", "Cadastre - Informations Parcelle", None))
        self.groupBox.setTitle(_translate("cadastre_parcelle_form", "Résumé", None))
        self.groupBox_2.setTitle(_translate("cadastre_parcelle_form", "Propriétaire(s)", None))
        self.groupBox_3.setTitle(_translate("cadastre_parcelle_form", "Actions", None))
        self.btExportParcelle.setText(_translate("cadastre_parcelle_form", "Relevé parcellaire", None))
        self.btExportProprietaire.setText(_translate("cadastre_parcelle_form", "Relevé de propriété", None))
        self.btCentrer.setText(_translate("cadastre_parcelle_form", "Centrer", None))
        self.btZoomer.setText(_translate("cadastre_parcelle_form", "Zoomer", None))
        self.btSelectionner.setText(_translate("cadastre_parcelle_form", "Sélect.", None))
        self.btParcellesProprietaire.setText(_translate("cadastre_parcelle_form", "Sélectionner les parcelles du propriétaire", None))

import resource_rc
