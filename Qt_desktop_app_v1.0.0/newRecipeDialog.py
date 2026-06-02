# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newRecipeDialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_newRecipeDialog(object):
    def setupUi(self, newRecipeDialog):
        newRecipeDialog.setObjectName("newRecipeDialog")
        newRecipeDialog.resize(299, 128)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("app_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        newRecipeDialog.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(newRecipeDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelName = QtWidgets.QLabel(newRecipeDialog)
        self.labelName.setObjectName("labelName")
        self.horizontalLayout.addWidget(self.labelName)
        self.lineNameInput = QtWidgets.QLineEdit(newRecipeDialog)
        self.lineNameInput.setObjectName("lineNameInput")
        self.horizontalLayout.addWidget(self.lineNameInput)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.btnOptions = QtWidgets.QDialogButtonBox(newRecipeDialog)
        self.btnOptions.setOrientation(QtCore.Qt.Horizontal)
        self.btnOptions.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.btnOptions.setCenterButtons(True)
        self.btnOptions.setObjectName("btnOptions")
        self.gridLayout.addWidget(self.btnOptions, 1, 0, 1, 1)

        self.retranslateUi(newRecipeDialog)
        self.btnOptions.accepted.connect(newRecipeDialog.accept)
        self.btnOptions.rejected.connect(newRecipeDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(newRecipeDialog)

    def retranslateUi(self, newRecipeDialog):
        _translate = QtCore.QCoreApplication.translate
        newRecipeDialog.setWindowTitle(_translate("newRecipeDialog", "Nueva Receta"))
        self.labelName.setText(_translate("newRecipeDialog", "Nombre"))
