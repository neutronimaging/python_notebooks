# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/j35/git/python_notebooks/notebooks/ui/ui_profile.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1365, 811)
        MainWindow.setMinimumSize(QtCore.QSize(0, 300))
        MainWindow.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.splitter_2 = QtWidgets.QSplitter(self.tab)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName("splitter_2")
        self.splitter = QtWidgets.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox = QtWidgets.QGroupBox(self.layoutWidget)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.grid_display_checkBox = QtWidgets.QCheckBox(self.groupBox)
        self.grid_display_checkBox.setMaximumSize(QtCore.QSize(70, 16777215))
        self.grid_display_checkBox.setObjectName("grid_display_checkBox")
        self.horizontalLayout_6.addWidget(self.grid_display_checkBox)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setText("")
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_6.addWidget(self.label_4)
        self.display_size_label = QtWidgets.QLabel(self.groupBox)
        self.display_size_label.setEnabled(False)
        self.display_size_label.setMaximumSize(QtCore.QSize(40, 16777215))
        self.display_size_label.setObjectName("display_size_label")
        self.horizontalLayout_6.addWidget(self.display_size_label)
        self.grid_size_slider = QtWidgets.QSlider(self.groupBox)
        self.grid_size_slider.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grid_size_slider.sizePolicy().hasHeightForWidth())
        self.grid_size_slider.setSizePolicy(sizePolicy)
        self.grid_size_slider.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.grid_size_slider.setMinimum(1)
        self.grid_size_slider.setMaximum(200)
        self.grid_size_slider.setProperty("value", 100)
        self.grid_size_slider.setOrientation(QtCore.Qt.Horizontal)
        self.grid_size_slider.setObjectName("grid_size_slider")
        self.horizontalLayout_6.addWidget(self.grid_size_slider)
        self.display_transparency_label = QtWidgets.QLabel(self.groupBox)
        self.display_transparency_label.setEnabled(False)
        self.display_transparency_label.setObjectName("display_transparency_label")
        self.horizontalLayout_6.addWidget(self.display_transparency_label)
        self.transparency_slider = QtWidgets.QSlider(self.groupBox)
        self.transparency_slider.setEnabled(False)
        self.transparency_slider.setMaximum(100)
        self.transparency_slider.setProperty("value", 50)
        self.transparency_slider.setOrientation(QtCore.Qt.Horizontal)
        self.transparency_slider.setObjectName("transparency_slider")
        self.horizontalLayout_6.addWidget(self.transparency_slider)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.right_rotation_button_fast = QtWidgets.QPushButton(self.layoutWidget)
        self.right_rotation_button_fast.setMinimumSize(QtCore.QSize(0, 200))
        self.right_rotation_button_fast.setMaximumSize(QtCore.QSize(50, 200))
        self.right_rotation_button_fast.setText("")
        self.right_rotation_button_fast.setObjectName("right_rotation_button_fast")
        self.verticalLayout_5.addWidget(self.right_rotation_button_fast)
        self.right_rotation_button_slow = QtWidgets.QPushButton(self.layoutWidget)
        self.right_rotation_button_slow.setMinimumSize(QtCore.QSize(0, 100))
        self.right_rotation_button_slow.setMaximumSize(QtCore.QSize(50, 100))
        self.right_rotation_button_slow.setText("")
        self.right_rotation_button_slow.setObjectName("right_rotation_button_slow")
        self.verticalLayout_5.addWidget(self.right_rotation_button_slow)
        self.horizontalLayout_5.addLayout(self.verticalLayout_5)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pyqtgraph_widget = QtWidgets.QWidget(self.layoutWidget)
        self.pyqtgraph_widget.setObjectName("pyqtgraph_widget")
        self.horizontalLayout_2.addWidget(self.pyqtgraph_widget)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.previous_image_button = QtWidgets.QPushButton(self.layoutWidget)
        self.previous_image_button.setEnabled(False)
        self.previous_image_button.setObjectName("previous_image_button")
        self.horizontalLayout_3.addWidget(self.previous_image_button)
        self.file_slider = QtWidgets.QSlider(self.layoutWidget)
        self.file_slider.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.file_slider.setOrientation(QtCore.Qt.Horizontal)
        self.file_slider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.file_slider.setObjectName("file_slider")
        self.horizontalLayout_3.addWidget(self.file_slider)
        self.image_slider_value = QtWidgets.QLabel(self.layoutWidget)
        self.image_slider_value.setMinimumSize(QtCore.QSize(30, 0))
        self.image_slider_value.setMaximumSize(QtCore.QSize(30, 16777215))
        self.image_slider_value.setBaseSize(QtCore.QSize(50, 0))
        self.image_slider_value.setObjectName("image_slider_value")
        self.horizontalLayout_3.addWidget(self.image_slider_value)
        self.next_image_button = QtWidgets.QPushButton(self.layoutWidget)
        self.next_image_button.setObjectName("next_image_button")
        self.horizontalLayout_3.addWidget(self.next_image_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_6 = QtWidgets.QLabel(self.layoutWidget)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_8.addWidget(self.label_6)
        self.filename = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filename.sizePolicy().hasHeightForWidth())
        self.filename.setSizePolicy(sizePolicy)
        self.filename.setObjectName("filename")
        self.horizontalLayout_8.addWidget(self.filename)
        self.verticalLayout_2.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_5.addLayout(self.verticalLayout_2)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.left_rotation_button_fast = QtWidgets.QPushButton(self.layoutWidget)
        self.left_rotation_button_fast.setMinimumSize(QtCore.QSize(0, 200))
        self.left_rotation_button_fast.setMaximumSize(QtCore.QSize(50, 200))
        self.left_rotation_button_fast.setText("")
        self.left_rotation_button_fast.setObjectName("left_rotation_button_fast")
        self.verticalLayout_6.addWidget(self.left_rotation_button_fast)
        self.left_rotation_button_slow = QtWidgets.QPushButton(self.layoutWidget)
        self.left_rotation_button_slow.setMinimumSize(QtCore.QSize(0, 100))
        self.left_rotation_button_slow.setMaximumSize(QtCore.QSize(50, 100))
        self.left_rotation_button_slow.setText("")
        self.left_rotation_button_slow.setObjectName("left_rotation_button_slow")
        self.verticalLayout_6.addWidget(self.left_rotation_button_slow)
        self.horizontalLayout_5.addLayout(self.verticalLayout_6)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.layoutWidget1 = QtWidgets.QWidget(self.splitter)
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.tableWidget = QtWidgets.QTableWidget(self.layoutWidget1)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        self.gridLayout.addWidget(self.tableWidget, 1, 0, 1, 1)
        self.tableWidget_2 = QtWidgets.QTableWidget(self.layoutWidget1)
        self.tableWidget_2.setMaximumSize(QtCore.QSize(100, 16777215))
        self.tableWidget_2.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableWidget_2.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.setColumnCount(1)
        self.tableWidget_2.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(0, item)
        self.tableWidget_2.horizontalHeader().setVisible(True)
        self.tableWidget_2.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.tableWidget_2, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.layoutWidget1)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(193, 22, 45))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(193, 22, 45))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(193, 22, 45))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(193, 22, 45))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.HighlightedText, brush)
        brush = QtGui.QBrush(QtGui.QColor(193, 22, 45))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(193, 22, 45))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(193, 22, 45))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(193, 22, 45))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(193, 22, 45))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.HighlightedText, brush)
        brush = QtGui.QBrush(QtGui.QColor(193, 22, 45))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(69, 69, 69))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(69, 69, 69))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(106, 104, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(193, 22, 45))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.HighlightedText, brush)
        brush = QtGui.QBrush(QtGui.QColor(193, 22, 45))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        self.label_3.setPalette(palette)
        self.label_3.setTextFormat(QtCore.Qt.AutoText)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.pushButton_4 = QtWidgets.QPushButton(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.pushButton_4.setFont(font)
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout_4.addWidget(self.pushButton_4)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.groupBox_2 = QtWidgets.QGroupBox(self.layoutWidget1)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.profile_direction_x_axis = QtWidgets.QRadioButton(self.groupBox_2)
        self.profile_direction_x_axis.setChecked(False)
        self.profile_direction_x_axis.setObjectName("profile_direction_x_axis")
        self.horizontalLayout_7.addWidget(self.profile_direction_x_axis)
        self.profile_direction_y_axis = QtWidgets.QRadioButton(self.groupBox_2)
        self.profile_direction_y_axis.setChecked(True)
        self.profile_direction_y_axis.setObjectName("profile_direction_y_axis")
        self.horizontalLayout_7.addWidget(self.profile_direction_y_axis)
        self.horizontalLayout_4.addWidget(self.groupBox_2)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.pushButton_5 = QtWidgets.QPushButton(self.layoutWidget1)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.pushButton_5.setFont(font)
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout_4.addWidget(self.pushButton_5)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.profile_widget = QtWidgets.QWidget(self.splitter_2)
        self.profile_widget.setObjectName("profile_widget")
        self.verticalLayout_4.addWidget(self.splitter_2)
        self.tabWidget.addTab(self.tab, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.tab_3)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.all_plots_hori_splitter = QtWidgets.QSplitter(self.tab_3)
        self.all_plots_hori_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.all_plots_hori_splitter.setObjectName("all_plots_hori_splitter")
        self.all_plots_widget = QtWidgets.QWidget(self.all_plots_hori_splitter)
        self.all_plots_widget.setObjectName("all_plots_widget")
        self.layoutWidget2 = QtWidgets.QWidget(self.all_plots_hori_splitter)
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.layoutWidget2)
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.label_5 = QtWidgets.QLabel(self.layoutWidget2)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_9.addWidget(self.label_5)
        self.all_plots_verti_splitter = QtWidgets.QSplitter(self.layoutWidget2)
        self.all_plots_verti_splitter.setOrientation(QtCore.Qt.Vertical)
        self.all_plots_verti_splitter.setObjectName("all_plots_verti_splitter")
        self.all_plots_file_name_table = QtWidgets.QTableWidget(self.all_plots_verti_splitter)
        self.all_plots_file_name_table.setAlternatingRowColors(True)
        self.all_plots_file_name_table.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.all_plots_file_name_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.all_plots_file_name_table.setObjectName("all_plots_file_name_table")
        self.all_plots_file_name_table.setColumnCount(1)
        self.all_plots_file_name_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.all_plots_file_name_table.setHorizontalHeaderItem(0, item)
        self.all_plots_file_name_table.horizontalHeader().setStretchLastSection(True)
        self.all_plots_file_name_table.verticalHeader().setStretchLastSection(False)
        self.all_plots_profiles_table = QtWidgets.QTableWidget(self.all_plots_verti_splitter)
        self.all_plots_profiles_table.setAlternatingRowColors(True)
        self.all_plots_profiles_table.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.all_plots_profiles_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.all_plots_profiles_table.setObjectName("all_plots_profiles_table")
        self.all_plots_profiles_table.setColumnCount(1)
        self.all_plots_profiles_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.all_plots_profiles_table.setHorizontalHeaderItem(0, item)
        self.all_plots_profiles_table.horizontalHeader().setStretchLastSection(True)
        self.all_plots_profiles_table.verticalHeader().setStretchLastSection(False)
        self.verticalLayout_9.addWidget(self.all_plots_verti_splitter)
        self.verticalLayout_10.addWidget(self.all_plots_hori_splitter)
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.summary_table = QtWidgets.QTableWidget(self.tab_2)
        self.summary_table.setAlternatingRowColors(True)
        self.summary_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.summary_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.summary_table.setObjectName("summary_table")
        self.summary_table.setColumnCount(3)
        self.summary_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.summary_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.summary_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.summary_table.setHorizontalHeaderItem(2, item)
        self.verticalLayout_8.addWidget(self.summary_table)
        self.tabWidget.addTab(self.tab_2, "")
        self.verticalLayout_7.addWidget(self.tabWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.export_button = QtWidgets.QPushButton(self.centralwidget)
        self.export_button.setObjectName("export_button")
        self.horizontalLayout.addWidget(self.export_button)
        self.verticalLayout_7.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1365, 24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionExport_Profile = QtWidgets.QAction(MainWindow)
        self.actionExport_Profile.setObjectName("actionExport_Profile")
        self.actionWater_Intake = QtWidgets.QAction(MainWindow)
        self.actionWater_Intake.setObjectName("actionWater_Intake")
        self.actionImportedFilesMetadata = QtWidgets.QAction(MainWindow)
        self.actionImportedFilesMetadata.setObjectName("actionImportedFilesMetadata")
        self.actionBy_Time_Stamp = QtWidgets.QAction(MainWindow)
        self.actionBy_Time_Stamp.setObjectName("actionBy_Time_Stamp")
        self.actionBy_File_Name = QtWidgets.QAction(MainWindow)
        self.actionBy_File_Name.setObjectName("actionBy_File_Name")
        self.actionDsc_files = QtWidgets.QAction(MainWindow)
        self.actionDsc_files.setObjectName("actionDsc_files")
        self.actionDsc = QtWidgets.QAction(MainWindow)
        self.actionDsc.setObjectName("actionDsc")
        self.actionWater_Intake_2 = QtWidgets.QAction(MainWindow)
        self.actionWater_Intake_2.setObjectName("actionWater_Intake_2")
        self.actionProfiles = QtWidgets.QAction(MainWindow)
        self.actionProfiles.setObjectName("actionProfiles")

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.file_slider.sliderMoved['int'].connect(MainWindow.slider_file_changed) # type: ignore
        self.file_slider.valueChanged['int'].connect(MainWindow.slider_file_changed) # type: ignore
        self.previous_image_button.clicked.connect(MainWindow.previous_image_button_clicked) # type: ignore
        self.next_image_button.clicked.connect(MainWindow.next_image_button_clicked) # type: ignore
        self.export_button.clicked.connect(MainWindow.export_button_clicked) # type: ignore
        self.pushButton.clicked.connect(MainWindow.help_button_clicked) # type: ignore
        self.pushButton_4.clicked.connect(MainWindow.remove_row_button_clicked) # type: ignore
        self.pushButton_5.clicked.connect(MainWindow.add_row_button_clicked) # type: ignore
        self.grid_display_checkBox.clicked.connect(MainWindow.display_grid_clicked) # type: ignore
        self.grid_size_slider.sliderPressed.connect(MainWindow.grid_size_slider_clicked) # type: ignore
        self.grid_size_slider.sliderMoved['int'].connect(MainWindow.grid_size_slider_moved) # type: ignore
        self.transparency_slider.sliderPressed.connect(MainWindow.transparency_slider_clicked) # type: ignore
        self.transparency_slider.sliderMoved['int'].connect(MainWindow.transparency_slider_moved) # type: ignore
        self.right_rotation_button_fast.clicked.connect(MainWindow.right_rotation_fast_clicked) # type: ignore
        self.right_rotation_button_slow.clicked.connect(MainWindow.right_rotation_slow_clicked) # type: ignore
        self.left_rotation_button_fast.clicked.connect(MainWindow.left_rotation_fast_clicked) # type: ignore
        self.left_rotation_button_slow.clicked.connect(MainWindow.left_rotation_slow_clicked) # type: ignore
        self.tableWidget.itemSelectionChanged.connect(MainWindow.table_widget_selection_changed) # type: ignore
        self.tableWidget_2.itemSelectionChanged.connect(MainWindow.table_widget_2_selection_changed) # type: ignore
        self.tableWidget.cellChanged['int','int'].connect(MainWindow.table_widget_cell_changed) # type: ignore
        self.grid_size_slider.sliderReleased.connect(MainWindow.grid_size_slider_released) # type: ignore
        self.profile_direction_x_axis.clicked.connect(MainWindow.profile_along_axis_changed) # type: ignore
        self.profile_direction_y_axis.clicked.connect(MainWindow.profile_along_axis_changed) # type: ignore
        self.tabWidget.currentChanged['int'].connect(MainWindow.tab_changed) # type: ignore
        self.all_plots_file_name_table.itemSelectionChanged.connect(MainWindow.update_all_plots) # type: ignore
        self.all_plots_profiles_table.itemSelectionChanged.connect(MainWindow.update_all_plots) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Profile"))
        self.groupBox.setTitle(_translate("MainWindow", "Grid"))
        self.grid_display_checkBox.setText(_translate("MainWindow", "Display"))
        self.display_size_label.setText(_translate("MainWindow", "Size"))
        self.display_transparency_label.setText(_translate("MainWindow", "Transparency"))
        self.previous_image_button.setText(_translate("MainWindow", "Prev. Image"))
        self.image_slider_value.setText(_translate("MainWindow", "0"))
        self.next_image_button.setText(_translate("MainWindow", "Next Image"))
        self.label_6.setText(_translate("MainWindow", "File name:"))
        self.filename.setText(_translate("MainWindow", "N/A"))
        self.label.setText(_translate("MainWindow", "Guide"))
        self.label_2.setText(_translate("MainWindow", "Profile"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Enabled"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "X0"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Y0"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Width"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Height"))
        item = self.tableWidget_2.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Width"))
        self.label_3.setText(_translate("MainWindow", "ROI of selected row is displayed in RED"))
        self.pushButton_4.setText(_translate("MainWindow", "-"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Profile Direction"))
        self.profile_direction_x_axis.setText(_translate("MainWindow", "x-axis"))
        self.profile_direction_y_axis.setText(_translate("MainWindow", "y-axis"))
        self.pushButton_5.setText(_translate("MainWindow", "+"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Measurement"))
        self.label_5.setText(_translate("MainWindow", "Select the FILE(s) and the PROFILE(s) you want to display!"))
        item = self.all_plots_file_name_table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "File Names"))
        item = self.all_plots_profiles_table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Profiles"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "All Profiles / All Images"))
        item = self.summary_table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Files Name"))
        item = self.summary_table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Time Stamp"))
        item = self.summary_table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Relative Time (s)"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Summary"))
        self.pushButton.setText(_translate("MainWindow", "Help"))
        self.export_button.setText(_translate("MainWindow", "Export Profiles ..."))
        self.actionExport_Profile.setText(_translate("MainWindow", "Profiles ..."))
        self.actionWater_Intake.setText(_translate("MainWindow", "Water Intake ..."))
        self.actionImportedFilesMetadata.setText(_translate("MainWindow", "Imported Files and Metadata ..."))
        self.actionBy_Time_Stamp.setText(_translate("MainWindow", "by Time Stamp"))
        self.actionBy_File_Name.setText(_translate("MainWindow", "by File Name"))
        self.actionDsc_files.setText(_translate("MainWindow", "dsc files ..."))
        self.actionDsc.setText(_translate("MainWindow", "dsc ..."))
        self.actionWater_Intake_2.setText(_translate("MainWindow", "Water Intake ..."))
        self.actionProfiles.setText(_translate("MainWindow", "Profiles ..."))
