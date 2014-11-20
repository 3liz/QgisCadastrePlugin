# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/cadastre_message_form.ui'
#
# Created: Thu Nov 20 11:43:07 2014
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_cadastre_message_form(object):
    def setupUi(self, cadastre_message_form):
        cadastre_message_form.setObjectName(_fromUtf8("cadastre_message_form"))
        cadastre_message_form.resize(796, 401)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(cadastre_message_form.sizePolicy().hasHeightForWidth())
        cadastre_message_form.setSizePolicy(sizePolicy)
        self.verticalLayout = QtGui.QVBoxLayout(cadastre_message_form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scrollArea = QtGui.QScrollArea(cadastre_message_form)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 776, 348))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.teMessage = QtGui.QTextEdit(self.scrollAreaWidgetContents)
        self.teMessage.setObjectName(_fromUtf8("teMessage"))
        self.verticalLayout_2.addWidget(self.teMessage)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.buttonBox = QtGui.QDialogButtonBox(cadastre_message_form)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(cadastre_message_form)
        QtCore.QMetaObject.connectSlotsByName(cadastre_message_form)

    def retranslateUi(self, cadastre_message_form):
        cadastre_message_form.setWindowTitle(_translate("cadastre_message_form", "Cadastre - Notes de version", None))

import resource_rc
