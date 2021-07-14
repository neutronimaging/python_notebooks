# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/j35/git/python_notebooks/notebooks/ui/ui_registration_markers.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(594, 531)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setObjectName("tabWidget")
        self.horizontalLayout_3.addWidget(self.tabWidget)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.add_marker_button = QtWidgets.QPushButton(Dialog)
        self.add_marker_button.setObjectName("add_marker_button")
        self.verticalLayout.addWidget(self.add_marker_button)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.remove_marker_button = QtWidgets.QPushButton(Dialog)
        self.remove_marker_button.setObjectName("remove_marker_button")
        self.verticalLayout.addWidget(self.remove_marker_button)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.marker_color_widget = QtWidgets.QComboBox(Dialog)
        self.marker_color_widget.setObjectName("marker_color_widget")
        self.marker_color_widget.addItem("")
        self.marker_color_widget.addItem("")
        self.marker_color_widget.addItem("")
        self.marker_color_widget.addItem("")
        self.marker_color_widget.addItem("")
        self.marker_color_widget.addItem("")
        self.horizontalLayout_2.addWidget(self.marker_color_widget)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.run_registration_button = QtWidgets.QPushButton(Dialog)
        self.run_registration_button.setObjectName("run_registration_button")
        self.horizontalLayout_2.addWidget(self.run_registration_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(-1)
        self.add_marker_button.clicked.connect(Dialog.add_marker_button_clicked)
        self.remove_marker_button.clicked.connect(Dialog.remove_marker_button_clicked)
        self.marker_color_widget.currentIndexChanged['QString'].connect(Dialog.marker_color_changed)
        self.tabWidget.currentChanged['int'].connect(Dialog.marker_tab_changed)
        self.run_registration_button.clicked.connect(Dialog.run_registration_button_clicked)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Markers"))
        self.add_marker_button.setText(_translate("Dialog", "+"))
        self.remove_marker_button.setText(_translate("Dialog", "-"))
        self.label.setText(_translate("Dialog", "Color"))
        self.marker_color_widget.setItemText(0, _translate("Dialog", "white"))
        self.marker_color_widget.setItemText(1, _translate("Dialog", "yellow"))
        self.marker_color_widget.setItemText(2, _translate("Dialog", "green"))
        self.marker_color_widget.setItemText(3, _translate("Dialog", "red"))
        self.marker_color_widget.setItemText(4, _translate("Dialog", "blue"))
        self.marker_color_widget.setItemText(5, _translate("Dialog", "black"))
        self.run_registration_button.setText(_translate("Dialog", "Align Images Using Markers"))
