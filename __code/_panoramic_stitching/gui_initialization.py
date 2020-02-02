from collections import OrderedDict
import pyqtgraph as pg
import os
import numpy as np

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow


class GuiInitialization:

    def __init__(self, parent=None):
        self.parent = parent

    def all(self):
        self.pyqtgraph()
        self.master_dict()
        self.widgets()
        self.table()
        self.statusbar()
        self.splitters()
        self.table_selection()

    def pyqtgraph(self):
        self.parent.ui.reference_view = pg.ImageView()
        self.parent.ui.reference_view.ui.roiBtn.hide()
        self.parent.ui.reference_view.ui.menuBtn.hide()
        self.parent.ui.target_view = pg.ImageView()
        self.parent.ui.target_view.ui.roiBtn.hide()
        self.parent.ui.target_view.ui.menuBtn.hide()
        reference_layout = QtGui.QVBoxLayout()
        reference_layout.addWidget(self.parent.ui.reference_view)
        target_layout = QtGui.QVBoxLayout()
        target_layout.addWidget(self.parent.ui.target_view)
        self.parent.ui.reference_widget.setLayout(reference_layout)
        self.parent.ui.target_widget.setLayout(target_layout)

    def master_dict(self):
        master_dict = OrderedDict()
        _each_file_dict = {'associated_with_file_index': 0,
                           'reference_roi': {'x0': np.NaN,
                                             'y0': np.NaN,
                                             'width': np.NaN,
                                             'height': np.NaN},
                           'target_roi':  {'x0': np.NaN,
                                           'y0': np.NaN,
                                           'width': np.NaN,
                                           'height': np.NaN},
                           'status': ""}

        list_files = self.parent.list_files
        for _file in list_files:
            master_dict[_file] = _each_file_dict.copy()

        self.parent.master_dict = master_dict

    def table(self):
        master_dict = self.parent.master_dict
        for _row, _file_name in enumerate(self.parent.list_reference['files']):

            self.parent.ui.tableWidget.insertRow(_row)

            _dict_of_this_row = master_dict[_file_name]

            # file name
            _item = QtGui.QTableWidgetItem(os.path.basename(_file_name))
            self.parent.ui.tableWidget.setItem(_row, 0, _item)

            # target image
            _combobox = QtGui.QComboBox()
            _combobox.blockSignals(True)
            _combobox.currentIndexChanged.connect(self.parent.table_widget_target_image_changed)
            _combobox.addItems(self.parent.list_target['basename_files'])
            _combobox.setCurrentIndex(_row)
            _combobox.blockSignals(False)
            self.parent.ui.tableWidget.setCellWidget(_row, 1, _combobox)

            # status
            _item = QtGui.QTableWidgetItem(_dict_of_this_row['status'])
            self.parent.ui.tableWidget.setItem(_row, 2, _item)

        for _column_index, _width in enumerate(self.parent.tableWidget_columns_size):
            self.parent.ui.tableWidget.setColumnWidth(_column_index, _width)

    def widgets(self):
        self.parent.ui.run_stitching_button.setEnabled(False)
        self.parent.ui.export_button.setEnabled(False)

    def statusbar(self):
        self.parent.eventProgress = QtGui.QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)

    def splitters(self):
        self.parent.ui.main_vertical_splitter.setSizes([100, 0])
        self.parent.ui.splitter_between_previews_and_table.setSizes([90, 10])

    def table_selection(self):
        nbr_column = self.parent.ui.tableWidget.columnCount()
        _selection = QtGui.QTableWidgetSelectionRange(0, 0, 0, nbr_column-1)
        self.parent.ui.tableWidget.setRangeSelected(_selection, True)
