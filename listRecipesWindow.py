# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'listRecipesWindow.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(513, 584)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../.designer/backup/app_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.listRecipes = QtWidgets.QListWidget(Dialog)
        self.listRecipes.setObjectName("listRecipes")
        self.verticalLayout.addWidget(self.listRecipes)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnInspect = QtWidgets.QPushButton(Dialog)
        self.btnInspect.setObjectName("btnInspect")
        self.horizontalLayout.addWidget(self.btnInspect, 0, QtCore.Qt.AlignLeft)
        self.btnAdd = QtWidgets.QPushButton(Dialog)
        self.btnAdd.setObjectName("btnAdd")
        self.horizontalLayout.addWidget(self.btnAdd, 0, QtCore.Qt.AlignHCenter)
        self.btnClose = QtWidgets.QPushButton(Dialog)
        self.btnClose.setObjectName("btnClose")
        self.horizontalLayout.addWidget(self.btnClose, 0, QtCore.Qt.AlignRight)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Recetas"))
        self.btnInspect.setText(_translate("Dialog", "Inspeccionar"))
        self.btnAdd.setText(_translate("Dialog", "Añadir al calendario"))
        self.btnClose.setText(_translate("Dialog", "Cerrar"))
