# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/cadastre_print_form.ui'
#
# Created: Mon Dec 30 10:35:08 2013
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

class Ui_cadastre_print_form(object):
    def setupUi(self, cadastre_print_form):
        cadastre_print_form.setObjectName(_fromUtf8("cadastre_print_form"))
        cadastre_print_form.resize(255, 43)
        self.verticalLayout = QtGui.QVBoxLayout(cadastre_print_form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.pbPrint = QtGui.QProgressBar(cadastre_print_form)
        self.pbPrint.setProperty("value", 0)
        self.pbPrint.setObjectName(_fromUtf8("pbPrint"))
        self.verticalLayout.addWidget(self.pbPrint)

        self.retranslateUi(cadastre_print_form)
        QtCore.QMetaObject.connectSlotsByName(cadastre_print_form)

    def retranslateUi(self, cadastre_print_form):
        cadastre_print_form.setWindowTitle(_translate("cadastre_print_form", "Cadastre - Export multiple", None))

