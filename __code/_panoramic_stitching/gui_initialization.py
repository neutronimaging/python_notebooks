from collections import OrderedDict
import pyqtgraph as pg
import numpy as np
import os
import copy

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from __code._panoramic_stitching import config

DEFAULT_ROI = [0, 50, 75, 250]  # x0, y0, width, height for reference only
BUTTON_SIZE = {'single_arrow': {'width': 50,
                                'height': 50},
               'double_arrow': {'width': 65,
                                'height': 50},
               'single_vertical_arrow': {'width': 50,
                                         'height': 50}
               }


class GuiInitialization:

    def __init__(self, parent=None, configuration=''):
        self.parent = parent
        self.configuration = configuration

    def all(self):
        self.master_dict()
        self.load_configuration()
        self.pyqtgraph()
        self.widgets()
        self.table()
        self.statusbar()
        self.splitters()
        self.table_selection()

    def pyqtgraph(self):
        self.parent.ui.reference_view = pg.ImageView(view=pg.PlotItem())
        self.parent.ui.reference_view.ui.roiBtn.hide()
        self.parent.ui.reference_view.ui.menuBtn.hide()
        self.parent.pyqtgraph_image_view['reference'] = self.parent.ui.reference_view

        self.parent.ui.target_view = pg.ImageView(view=pg.PlotItem())
        self.parent.ui.target_view.ui.roiBtn.hide()
        self.parent.ui.target_view.ui.menuBtn.hide()
        self.parent.pyqtgraph_image_view['target'] = self.parent.ui.target_view

        reference_layout = QtGui.QVBoxLayout()
        reference_layout.addWidget(self.parent.ui.reference_view)
        target_layout = QtGui.QVBoxLayout()
        target_layout.addWidget(self.parent.ui.target_view)
        self.parent.ui.reference_widget.setLayout(reference_layout)
        self.parent.ui.target_widget.setLayout(target_layout)

    def master_dict(self):
        master_dict = OrderedDict()
        _each_file_dict = {'associated_with_file_index': 0,
                           'reference_combobox_file_index': 0,
                           'reference_roi': {'x0': DEFAULT_ROI[0],
                                             'y0': DEFAULT_ROI[1],
                                             'width': DEFAULT_ROI[2],
                                             'height': DEFAULT_ROI[3]},
                           'target_combobox_file_index': 0,
                           'target_roi':  {'x0': DEFAULT_ROI[0],
                                           'y0': DEFAULT_ROI[1],
                                           'width': DEFAULT_ROI[2]*self.parent.target_box_size_coefficient['x'],
                                           'height': DEFAULT_ROI[3]*self.parent.target_box_size_coefficient['y']},
                           'status': ""}

        list_files = self.parent.list_files
        for _row in np.arange(len(list_files)-1):
            master_dict[_row] = copy.deepcopy(_each_file_dict)

        self.parent.master_dict = master_dict

    def table(self):
        master_dict = self.parent.master_dict
        self.parent.ui.tableWidget.blockSignals(True)
        for _row, _file_name in enumerate(self.parent.list_reference['files'][:-1]):

            self.parent.ui.tableWidget.insertRow(_row)

            _dict_of_this_row = master_dict[_row]

            # reference image
            _combobox_ref = QtGui.QComboBox()
            _combobox_ref.blockSignals(True)
            _combobox_ref.currentIndexChanged.connect(self.parent.table_widget_reference_image_changed)
            _combobox_ref.addItems(self.parent.list_reference['basename_files'])
            _combobox_ref.setCurrentIndex(_dict_of_this_row['reference_combobox_file_index'])
            _combobox_ref.blockSignals(False)
            self.parent.ui.tableWidget.setCellWidget(_row, 0, _combobox_ref)

            # target image
            _combobox = QtGui.QComboBox()
            _combobox.blockSignals(True)
            _combobox.currentIndexChanged.connect(self.parent.table_widget_target_image_changed)
            _combobox.addItems(self.parent.list_target['basename_files'])
            _combobox.setCurrentIndex(_dict_of_this_row['target_combobox_file_index'])
            _combobox.blockSignals(False)
            self.parent.ui.tableWidget.setCellWidget(_row, 1, _combobox)

            # status
            _item = QtGui.QTableWidgetItem(_dict_of_this_row['status'])
            self.parent.ui.tableWidget.setItem(_row, 2, _item)

        self.parent.ui.tableWidget.blockSignals(False)

        for _column_index, _width in enumerate(self.parent.tableWidget_columns_size):
            self.parent.ui.tableWidget.setColumnWidth(_column_index, _width)

    def widgets(self):
        self.parent.ui.run_stitching_button.setEnabled(False)
        self.parent.ui.export_button.setEnabled(False)

        up_arrow_file = GuiInitialization.__make_full_file_name_to_static_folder_of(config.button['up']
                                                                                                  ['released'])
        self.parent.ui.up_button.setIcon(QtGui.QIcon(up_arrow_file))
        left_left_arrow_file = GuiInitialization.__make_full_file_name_to_static_folder_of(config.button['left_left']
                                                                                      ['released'])
        self.parent.ui.left_left_button.setIcon(QtGui.QIcon(left_left_arrow_file))
        left_arrow_file = GuiInitialization.__make_full_file_name_to_static_folder_of(config.button['left']
                                                                                      ['released'])
        self.parent.ui.left_button.setIcon(QtGui.QIcon(left_arrow_file))
        right_arrow_file = GuiInitialization.__make_full_file_name_to_static_folder_of(config.button['right']
                                                                                       ['released'])
        self.parent.ui.right_button.setIcon(QtGui.QIcon(right_arrow_file))
        right_right_arrow_file = GuiInitialization.__make_full_file_name_to_static_folder_of(config.button['right_right']
                                                                                       ['released'])
        self.parent.ui.right_right_button.setIcon(QtGui.QIcon(right_right_arrow_file))

        down_arrow_file = GuiInitialization.__make_full_file_name_to_static_folder_of(config.button['down']
                                                                                                  ['released'])
        self.parent.ui.down_button.setIcon(QtGui.QIcon(down_arrow_file))

        list_ui = [self.parent.ui.left_button,
                   self.parent.ui.right_button]
        GuiInitialization.__set_widgets_size(widgets=list_ui,
                                             width=BUTTON_SIZE['single_arrow']['width'],
                                             height=BUTTON_SIZE['single_arrow']['height'])

        list_ui = [self.parent.ui.left_left_button,
                   self.parent.ui.right_right_button]
        GuiInitialization.__set_widgets_size(widgets=list_ui,
                                             width=BUTTON_SIZE['double_arrow']['width'],
                                             height=BUTTON_SIZE['double_arrow']['height'])

        list_ui = [self.parent.ui.up_button,
                   self.parent.ui.down_button]
        GuiInitialization.__set_widgets_size(widgets=list_ui,
                                             width=BUTTON_SIZE['single_vertical_arrow']['width'],
                                             height=BUTTON_SIZE['single_vertical_arrow']['height'])

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

    def load_configuration(self):
        master_dict = self.parent.master_dict.copy()
        configuration = self.configuration

        import json
        with open(configuration) as json_file:
            configuration_roi = json.load(json_file)

        for _row in list(master_dict.keys()):
            configuration_roi_row = configuration_roi[str(_row)]
            master_dict_row = master_dict[_row]

            roi_row_reference = configuration_roi_row['reference']
            master_dict_row['reference_roi'] = {'x0': np.int(roi_row_reference['x0']),
                                                'y0': np.int(roi_row_reference['y0']),
                                                'width': np.int(roi_row_reference['width']),
                                                'height': np.int(roi_row_reference['height'])}
            master_dict_row['reference_combobox_file_index'] = np.int(roi_row_reference['file_index'])

            roi_row_target = configuration_roi_row['target']
            master_dict_row['target_combobox_file_index'] = np.int(roi_row_target['file_index'])
            master_dict_row['target_roi'] = {'x0': np.int(roi_row_target['x0']),
                                             'y0': np.int(roi_row_target['y0']),
                                             'width': np.int(roi_row_target['width']),
                                             'height': np.int(roi_row_target['height'])}

            configuration_roi[str(_row)] = configuration_roi_row

    @staticmethod
    def __make_full_file_name_to_static_folder_of(file_name):
        _file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        full_path_file = os.path.abspath(os.path.join(_file_path, file_name))
        return full_path_file

    @staticmethod
    def __set_widgets_size(widgets=[], width=10, height=10):
        for _widget in widgets:
            _widget.setIconSize(QtCore.QSize(width, height))
