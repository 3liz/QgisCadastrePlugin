# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cadastre_option_form.ui'
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

class Ui_cadastre_option_form(object):
    def setupUi(self, cadastre_option_form):
        cadastre_option_form.setObjectName(_fromUtf8("cadastre_option_form"))
        cadastre_option_form.resize(469, 525)
        self.verticalLayout = QtGui.QVBoxLayout(cadastre_option_form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scrollArea = QtGui.QScrollArea(cadastre_option_form)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 449, 505))
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
        self.btInterfaceCadastre = QtGui.QPushButton(self.groupBox_7)
        self.btInterfaceCadastre.setObjectName(_fromUtf8("btInterfaceCadastre"))
        self.horizontalLayout_9.addWidget(self.btInterfaceCadastre)
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
        self.inMajicBati = QtGui.QLineEdit(self.groupBox)
        self.inMajicBati.setObjectName(_fromUtf8("inMajicBati"))
        self.gridLayout.addWidget(self.inMajicBati, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.inMajicProp = QtGui.QLineEdit(self.groupBox)
        self.inMajicProp.setObjectName(_fromUtf8("inMajicProp"))
        self.gridLayout.addWidget(self.inMajicProp, 5, 1, 1, 1)
        self.inMajicLotlocal = QtGui.QLineEdit(self.groupBox)
        self.inMajicLotlocal.setObjectName(_fromUtf8("inMajicLotlocal"))
        self.gridLayout.addWidget(self.inMajicLotlocal, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.inMajicFantoir = QtGui.QLineEdit(self.groupBox)
        self.inMajicFantoir.setObjectName(_fromUtf8("inMajicFantoir"))
        self.gridLayout.addWidget(self.inMajicFantoir, 1, 1, 1, 1)
        self.inMajicNbati = QtGui.QLineEdit(self.groupBox)
        self.inMajicNbati.setObjectName(_fromUtf8("inMajicNbati"))
        self.gridLayout.addWidget(self.inMajicNbati, 3, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 5, 0, 1, 1)
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 4, 0, 1, 1)
        self.inMajicPdl = QtGui.QLineEdit(self.groupBox)
        self.inMajicPdl.setObjectName(_fromUtf8("inMajicPdl"))
        self.gridLayout.addWidget(self.inMajicPdl, 4, 1, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.inTempDir = QtGui.QLineEdit(self.groupBox_2)
        self.inTempDir.setObjectName(_fromUtf8("inTempDir"))
        self.horizontalLayout.addWidget(self.inTempDir)
        self.btTempDir = QtGui.QToolButton(self.groupBox_2)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/cadastre/icons/open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btTempDir.setIcon(icon)
        self.btTempDir.setObjectName(_fromUtf8("btTempDir"))
        self.horizontalLayout.addWidget(self.btTempDir)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addWidget(self.groupBox_2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(self.scrollAreaWidgetContents)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(cadastre_option_form)
        QtCore.QMetaObject.connectSlotsByName(cadastre_option_form)
        cadastre_option_form.setTabOrder(self.scrollArea, self.btInterfaceCadastre)
        cadastre_option_form.setTabOrder(self.btInterfaceCadastre, self.btInterfaceQgis)
        cadastre_option_form.setTabOrder(self.btInterfaceQgis, self.inMajicBati)
        cadastre_option_form.setTabOrder(self.inMajicBati, self.inMajicFantoir)
        cadastre_option_form.setTabOrder(self.inMajicFantoir, self.inMajicLotlocal)
        cadastre_option_form.setTabOrder(self.inMajicLotlocal, self.inMajicNbati)
        cadastre_option_form.setTabOrder(self.inMajicNbati, self.inMajicPdl)
        cadastre_option_form.setTabOrder(self.inMajicPdl, self.inMajicProp)
        cadastre_option_form.setTabOrder(self.inMajicProp, self.buttonBox)

    def retranslateUi(self, cadastre_option_form):
        cadastre_option_form.setWindowTitle(_translate("cadastre_option_form", "Cadastre", None))
        self.groupBox_7.setTitle(_translate("cadastre_option_form", "Interface QGIS", None))
        self.label_13.setText(_translate("cadastre_option_form", "Vous pouvez choisir d\'appliquer une interface\n"
"simplifiée de QGIS pour consulter le cadastre\n"
"ou de revenir à l\'interface par défaut", None))
        self.btInterfaceCadastre.setText(_translate("cadastre_option_form", "Interface Cadastre", None))
        self.btInterfaceQgis.setText(_translate("cadastre_option_form", "Interface QGIS", None))
        self.groupBox.setTitle(_translate("cadastre_option_form", "Nom des fichiers MAJIC", None))
        self.label.setText(_translate("cadastre_option_form", "BATI", None))
        self.label_2.setText(_translate("cadastre_option_form", "FANTOIR", None))
        self.label_4.setText(_translate("cadastre_option_form", "NBATI", None))
        self.label_3.setText(_translate("cadastre_option_form", "LOTLOCAL", None))
        self.label_5.setText(_translate("cadastre_option_form", "PROP", None))
        self.label_6.setText(_translate("cadastre_option_form", "PDL", None))
        self.groupBox_2.setTitle(_translate("cadastre_option_form", "Répertoire temporaire", None))
        self.btTempDir.setText(_translate("cadastre_option_form", "...", None))

import resource_rc
