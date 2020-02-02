from IPython.core.display import HTML
from IPython.display import display
from collections import OrderedDict
import pyqtgraph as pg
import numpy as np
import os

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from NeuNorm.normalization import Normalization

from __code.ui_panoramic_stitching import Ui_MainWindow as UiMainWindow
from __code.file_folder_browser import FileFolderBrowser


class InterfaceHandler(FileFolderBrowser):

    def __init__(self, working_dir=''):
        super(InterfaceHandler, self).__init__(working_dir=working_dir)

    def load(self):
        list_images = self.list_images_ui.selected
        o_norm = Normalization()
        o_norm.load(file=list_images, notebook=True)
        self.o_norm = o_norm


class Interface(QMainWindow):

    master_dict = {}
    tableWidget_columns_size = [400, 400, 100]

    def __init__(self, parent=None, o_norm=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        self.o_norm = o_norm

        self.list_files = self.o_norm.data['sample']['file_name']
        self.basename_list_files = [os.path.basename(_file) for _file in self.list_files]
        self.list_data = self.o_norm.data['sample']['data']

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.init_statusbar()
        self.setWindowTitle("Panoramic Stitching")

        self.init_pyqtgraph()
        self.initialize_master_dict()
        self.init_table()
        self.init_widgets()

    # event handler
    def table_widget_selection_changed(self):
        print("selection changed")

    def table_widget_target_image_changed(self, index):
        print("target selection changed")

    def init_pyqtgraph(self):
        self.ui.reference_view = pg.ImageView()
        self.ui.reference_view.ui.roiBtn.hide()
        self.ui.reference_view.ui.menuBtn.hide()
        self.ui.target_view = pg.ImageView()
        self.ui.target_view.ui.roiBtn.hide()
        self.ui.target_view.ui.menuBtn.hide()
        reference_layout = QtGui.QVBoxLayout()
        reference_layout.addWidget(self.ui.reference_view)
        target_layout = QtGui.QVBoxLayout()
        target_layout.addWidget(self.ui.target_view)
        self.ui.reference_widget.setLayout(reference_layout)
        self.ui.target_widget.setLayout(target_layout)

    def initialize_master_dict(self):
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

        list_files = self.list_files
        for _file in list_files:
            master_dict[_file] = _each_file_dict.copy()

        self.master_dict = master_dict

    def init_table(self):
        master_dict = self.master_dict
        for _row, _file_name in enumerate(master_dict.keys()):

            # skip the last one
            if _row == (len(master_dict.keys())-1):
                break

            self.ui.tableWidget.insertRow(_row)

            _dict_of_this_row = master_dict[_file_name]

            # file name
            _item = QtGui.QTableWidgetItem(os.path.basename(_file_name))
            self.ui.tableWidget.setItem(_row, 0, _item)

            # target image
            _combobox = QtGui.QComboBox()
            _combobox.blockSignals(True)
            _combobox.currentIndexChanged.connect(self.table_widget_target_image_changed)
            _combobox.addItems(self.basename_list_files[1:])
            _combobox.setCurrentIndex(_row+1)
            _combobox.blockSignals(False)
            self.ui.tableWidget.setCellWidget(_row, 1, _combobox)

            # status
            _item = QtGui.QTableWidgetItem(_dict_of_this_row['status'])
            self.ui.tableWidget.setItem(_row, 2, _item)

        for _column_index, _width in enumerate(self.tableWidget_columns_size):
            self.ui.tableWidget.setColumnWidth(_column_index, _width)

    def init_widgets(self):
        self.ui.run_stitching_button.setEnabled(False)
        self.ui.export_button.setEnabled(False)

    def init_statusbar(self):
        self.eventProgress = QtGui.QProgressBar(self.ui.statusbar)
        self.eventProgress.setMinimumSize(20, 14)
        self.eventProgress.setMaximumSize(540, 100)
        self.eventProgress.setVisible(False)
        self.ui.statusbar.addPermanentWidget(self.eventProgress)

    def apply_clicked(self):
        # do stuff
        self.close()

    def cancel_clicked(self):
        self.close()

    def display_image(self, image):
        self.ui.image_view.setImage(image)

    def closeEvent(self, eventhere=None):
        print("Leaving Panoramic Stitching UI")



