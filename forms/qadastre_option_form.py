# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qadastre_option_form.ui'
#
# Created: Thu Sep 19 11:35:32 2013
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
        qadastre_option_form.resize(395, 471)
        self.verticalLayout = QtGui.QVBoxLayout(qadastre_option_form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scrollArea = QtGui.QScrollArea(qadastre_option_form)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 375, 451))
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
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(self.scrollAreaWidgetContents)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(qadastre_option_form)
        QtCore.QMetaObject.connectSlotsByName(qadastre_option_form)
        qadastre_option_form.setTabOrder(self.scrollArea, self.btInterfaceQadastre)
        qadastre_option_form.setTabOrder(self.btInterfaceQadastre, self.btInterfaceQgis)
        qadastre_option_form.setTabOrder(self.btInterfaceQgis, self.inMajicBati)
        qadastre_option_form.setTabOrder(self.inMajicBati, self.inMajicFantoir)
        qadastre_option_form.setTabOrder(self.inMajicFantoir, self.inMajicLotlocal)
        qadastre_option_form.setTabOrder(self.inMajicLotlocal, self.inMajicNbati)
        qadastre_option_form.setTabOrder(self.inMajicNbati, self.inMajicPdl)
        qadastre_option_form.setTabOrder(self.inMajicPdl, self.inMajicProp)
        qadastre_option_form.setTabOrder(self.inMajicProp, self.buttonBox)

    def retranslateUi(self, qadastre_option_form):
        qadastre_option_form.setWindowTitle(_translate("qadastre_option_form", "Qadastre", None))
        self.groupBox_7.setTitle(_translate("qadastre_option_form", "Interface QGIS", None))
        self.label_13.setText(_translate("qadastre_option_form", "Vous pouvez choisir d\'appliquer une interface\n"
"simplifiée de QGIS pour consulter le cadastre\n"
"ou de revenir à l\'interface par défaut", None))
        self.btInterfaceQadastre.setText(_translate("qadastre_option_form", "Interface Qadastre", None))
        self.btInterfaceQgis.setText(_translate("qadastre_option_form", "Interface QGIS", None))
        self.groupBox.setTitle(_translate("qadastre_option_form", "Nom des fichiers MAJIC", None))
        self.label.setText(_translate("qadastre_option_form", "BATI", None))
        self.label_2.setText(_translate("qadastre_option_form", "FANTOIR", None))
        self.label_4.setText(_translate("qadastre_option_form", "NBATI", None))
        self.label_3.setText(_translate("qadastre_option_form", "LOTLOCAL", None))
        self.label_5.setText(_translate("qadastre_option_form", "PROP", None))
        self.label_6.setText(_translate("qadastre_option_form", "PDL", None))

