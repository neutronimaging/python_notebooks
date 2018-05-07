import ipywe.fileselector

from IPython.core.display import HTML
from IPython.core.display import display
from ipywidgets import widgets

import numpy as np
import os
from skimage import transform
from scipy.ndimage.interpolation import shift
from skimage.feature import register_translation
import copy
from __code.file_handler import retrieve_time_stamp

import pprint

import pyqtgraph as pg
from pyqtgraph.dockarea import *

from __code.color import  Color

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui, QtWidgets
    from PyQt4.QtGui import QMainWindow, QDialog
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

from NeuNorm.normalization import Normalization


from __code.ui_calibrated_transmission import Ui_MainWindow as UiMainWindow


class CalibratedTransmissionUi(QMainWindow):

    data_dict = {}
    timestamp_dict = {}

    histogram_level = []
    col_width = 65
    table_column_width = [col_width, col_width, col_width, col_width, 100]
    summary_table_width = [300, 150, 100]
    default_measurement_roi = {'x0': 0, 'y0': 0,
                               'width': np.NaN, 'height': np.NaN}

    roi_ui_measurement = list() # keep record of all the pyqtgraph.ROI ui

    def __init__(self, parent=None, data_dict=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Calibrated Transmission")

        self.data_dict = data_dict # Normalization data dictionary  {'file_name': [],
                                                                     #'data': [[...],[...]]],
                                                                     #'metadata': [],
                                                                     #'shape': {}}

        # untouched array of images (used to move and rotate images)
        self.data_dict_raw = copy.deepcopy(data_dict)

        # initialization
        self.init_timestamp_dict()
        self.init_table()
        self.init_pyqtgrpah()
        self.init_widgets()
        self.init_parameters()
        # self.init_statusbar()

        # display first image
        self.slider_file_changed(-1)

    # initialization
    def init_timestamp_dict(self):
        list_files = self.data_dict['file_name']
        self.timestamp_dict = retrieve_time_stamp(list_files)

    def init_statusbar(self):
        self.eventProgress = QtGui.QProgressBar(self.ui.statusbar)
        self.eventProgress.setMinimumSize(300, 20)
        self.eventProgress.setMaximumSize(300, 20)
        self.eventProgress.setVisible(False)
        self.ui.statusbar.addPermanentWidget(self.eventProgress)

    def init_table(self):
        list_files_full_name = self.data_dict['file_name']
        list_files_short_name = [os.path.basename(_file) for _file in list_files_full_name]

        list_time_stamp = self.timestamp_dict['list_time_stamp']
        list_time_stamp_user_format = self.timestamp_dict['list_time_stamp_user_format']
        time_0 = list_time_stamp[0]
        for _row, _file in enumerate(list_files_short_name):
            self.ui.summary_table.insertRow(_row)
            self.set_item_summary_table(row=_row, col=0, value=_file)
            self.set_item_summary_table(row=_row, col=1, value=list_time_stamp_user_format[_row])
            _offset = list_time_stamp[_row] - time_0
            self.set_item_summary_table(row=_row, col=2, value="{:0.2f}".format(_offset))

    # def init_parameters(self):
    #     nbr_files = len(self.data_dict['file_name'])
    #     self.nbr_files = nbr_files
    #     _color = Color()
    #     self.list_rgb_profile_color = _color.get_list_rgb(nbr_color=nbr_files)
    #
    #     o_marker = MarkerDefaultSettings(image_reference=self.reference_image)
    #     self.o_MarkerDefaultSettings = o_marker

    def init_pyqtgrpah(self):
        # image
        self.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.ui.image_view.ui.menuBtn.hide()
        self.ui.image_view.ui.roiBtn.hide()
        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(self.ui.image_view)
        self.ui.pyqtgraph_widget.setLayout(vertical_layout)

        # measurement
        self.ui.measurement_view = pg.ImageView(view=pg.PlotItem())
        self.ui.measurement_view.ui.menuBtn.hide()
        self.ui.measurement_view.ui.roiBtn.hide()
        vertical_layout2 = QtGui.QVBoxLayout()
        vertical_layout2.addWidget(self.ui.measurement_view)
        self.ui.measurement_widget.setLayout(vertical_layout2)

    def init_widgets(self):
        """size and label of any widgets"""
        self.ui.splitter.setSizes([250, 130])

        # file slider
        self.ui.file_slider.setMaximum(len(self.data_dict['data'])-1)

        # update size of table columns
        nbr_columns = self.ui.tableWidget.columnCount()
        for _col in range(nbr_columns):
            self.ui.tableWidget.setColumnWidth(_col, self.table_column_width[_col])

        # update size of summary table
        nbr_columns = self.ui.summary_table.columnCount()
        for _col in range(nbr_columns):
            self.ui.summary_table.setColumnWidth(_col, self.summary_table_width[_col])

    def init_parameters(self):
        # init the position of the measurement ROI
        [height, width] = np.shape(self.data_dict['data'][0])
        self.default_measurement_roi['width'] = np.int(width/10)
        self.default_measurement_roi['height'] = np.int(height/10)

    # main methods
    def display_image(self):
        """display the image selected by the file slider"""

        _image = self.get_image_selected()

        _view = self.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.histogram_level == []:
            first_update = True
        _histo_widget = self.ui.image_view.getHistogramWidget()
        self.histogram_level = _histo_widget.getLevels()

        _image = np.transpose(_image)
        self.ui.image_view.setImage(_image)
        self.live_image = _image
        _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.histogram_level[0], self.histogram_level[1])

    def remove_row(self, row=-1):
        if row == -1:
            return
        self.ui.tableWidget.removeRow(row)

        nbr_row = self.ui.tableWidget.rowCount()
        if row == nbr_row:
            row -= 1

        if nbr_row > 0:
            nbr_col = self.ui.tableWidget.columnCount()
            new_selection = QtGui.QTableWidgetSelectionRange(row, 0, row, nbr_col - 1)
            self.ui.tableWidget.setRangeSelected(new_selection, True)

    def insert_row(self, row=-1):
        if row == -1:
            row = 0

        default_values = self.default_measurement_roi

        self.ui.tableWidget.insertRow(row)
        self.set_item_main_table(row=row, col=0, value=default_values['x0'])
        self.set_item_main_table(row=row, col=1, value=default_values['y0'])
        self.set_item_main_table(row=row, col=2, value=default_values['width'])
        self.set_item_main_table(row=row, col=3, value=default_values['height'])

        # select new entry
        nbr_row = self.ui.tableWidget.rowCount()
        nbr_col = self.ui.tableWidget.columnCount()
        full_range = QtGui.QTableWidgetSelectionRange(0, 0, nbr_row-1, nbr_col-1)
        self.ui.tableWidget.setRangeSelected(full_range, False)
        new_selection = QtGui.QTableWidgetSelectionRange(row, 0, row, nbr_col-1)
        self.ui.tableWidget.setRangeSelected(new_selection, True)

    def insert_column_in_summary_table(self, roi_index=-1):
        col_offset = 3
        if roi_index == -1:
            roi_index = 0

        roi_index += col_offset
        self.ui.summary_table.insertColumn(roi_index)
        item = QtWidgets.QTableWidgetItem()
        self.ui.summary_table.setHorizontalHeaderItem(roi_index, item)

        self.renamed_summary_table_region_header()

    def renamed_summary_table_region_header(self):
        # rename all the headers
        nbr_col = self.ui.summary_table.columnCount()
        if nbr_col <= 3:
            return

        _index = 1
        for _col in np.arange(3, nbr_col):
            item = self.ui.summary_table.horizontalHeaderItem(_col)
            item.setText("Region {}".format(_index))
            _index += 1

    def update_mean_counts(self, row=-1, all=False):
        if all == True:
            nbr_row = self.ui.tableWidget.rowCount()
            for _row in np.arange(nbr_row):
                self.update_mean_counts(row=_row)
        else:
            # FIXME
            pass

    def insert_measurement_roi_ui(self, row=-1):
        new_roi = None
        self.roi_ui_measurement.insert(row, new_roi)

    def remove_measurement_roi_ui(self, row=-1):
        """roi_ui_measurement is where the ROI ui (pyqtgraph) are saved"""
        if row == -1:
            return
        old_roi = self.roi_ui_measurement[row]
        self.roi_ui_measurement.remove(old_roi)

    # setter
    def set_item_main_table(self, row=0, col=0, value=''):
        item = QtGui.QTableWidgetItem(str(value))
        self.ui.tableWidget.setItem(row, col, item)
        if col == 4:
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def set_item_summary_table(self, row=0, col=0, value=''):
        item = QtGui.QTableWidgetItem(str(value))
        self.ui.summary_table.setItem(row, col, item)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    # getter
    def get_image_selected(self):
        slider_index = self.ui.file_slider.value()
        _image = self.data_dict['data'][slider_index]
        return _image

    def get_selected_row(self):
        selection = self.ui.tableWidget.selectedRanges()
        if selection:
            top_row = selection[0].topRow()
            return top_row
        else:
            return -1

    def check_status_next_prev_image_button(self):
        """this will enable or not the prev or next button next to the slider file image"""
        current_slider_value = self.ui.file_slider.value()
        min_slider_value = self.ui.file_slider.minimum()
        max_slider_value = self.ui.file_slider.maximum()

        _prev = True
        _next = True

        if current_slider_value == min_slider_value:
            _prev = False
        elif current_slider_value == max_slider_value:
            _next = False

        self.ui.previous_image_button.setEnabled(_prev)
        self.ui.next_image_button.setEnabled(_next)

    # event handler
    def use_calibration_checked(self):
        cali_button_checked = self.ui.use_calibration_checkbox.isChecked()
        self.ui.region1.setEnabled(cali_button_checked)
        self.ui.region2.setEnabled(cali_button_checked)

    def slider_file_changed(self, index_selected):
        self.display_image()
        self.check_status_next_prev_image_button()
        self.ui.tableWidget.blockSignals(False)

    def add_row_button_clicked(self):
        selected_row = self.get_selected_row()
        self.insert_row(row=selected_row)
        self.insert_column_in_summary_table(roi_index=selected_row)
        self.insert_measurement_roi_ui(row=selected_row)
        self.update_mean_counts(row=selected_row)

    def remove_row_button_clicked(self):
        selected_row = self.get_selected_row()
        self.remove_row(row=selected_row)
        self.remove_measurement_roi_ui(row=selected_row)

    def cell_changed(self, a, b, c, d):
        pass

    def export_button_clicked(self):
        pass

    def previous_image_button_clicked(self):
        self.change_slider(offset = -1)

    def next_image_button_clicked(self):
        self.change_slider(offset = +1)

    def help_button_clicked(self):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/registration/")

    def closeEvent(self, event=None):
        pass




    #
    #
    # def select_row_in_table(self, row=0):
    #     nbr_col = self.ui.tableWidget.columnCount()
    #     nbr_row = self.ui.tableWidget.rowCount()
    #
    #     # clear previous selection
    #     full_range = QtGui.QTableWidgetSelectionRange(0, 0, nbr_row-1, nbr_col-1)
    #     self.ui.tableWidget.setRangeSelected(full_range, False)
    #
    #     # select file of interest
    #     selection_range = QtGui.QTableWidgetSelectionRange(row, 0, row, nbr_col-1)
    #     self.ui.tableWidget.setRangeSelected(selection_range, True)
    #
    #     self.ui.tableWidget.showRow(row)
    #
    #
    # def change_slider(self, offset=+1):
    #     self.ui.file_slider.blockSignals(True)
    #     current_slider_value = self.ui.file_slider.value()
    #     new_row_selected = current_slider_value + offset
    #     self.select_row_in_table(row=new_row_selected)
    #     self.ui.file_slider.setValue(new_row_selected)
    #     self.check_status_next_prev_image_button()
    #     self.display_image()
    #     self.profile_line_moved()
    #     self.ui.file_slider.blockSignals(False)
    #
    # def check_selection_slider_status(self):
    #     """
    #     if there is more than one row selected, we need to display the left slider but also
    #     we need to disable the next, prev buttons and file index slider
    #     """
    #     selection = self.ui.tableWidget.selectedRanges()
    #     if selection:
    #
    #         list_file_index_widgets = [self.ui.previous_image_button,
    #                                    self.ui.file_slider,
    #                                    self.ui.next_image_button]
    #
    #         top_row = selection[0].topRow()
    #         bottom_row = selection[0].bottomRow()
    #         if np.abs(bottom_row - top_row) >= 1: # show selection images widgets
    #             self.ui.selection_groupBox.setVisible(True)
    #             self.ui.top_row_label.setText("Row {}".format(top_row+1))
    #             self.ui.bottom_row_label.setText("Row {}".format(bottom_row+1))
    #             self.ui.opacity_selection_slider.setMinimum(top_row*100)
    #             self.ui.opacity_selection_slider.setMaximum(bottom_row*100)
    #             self.ui.opacity_selection_slider.setSliderPosition(top_row*100)
    #             _file_index_status = False
    #         else:
    #             self.ui.selection_groupBox.setVisible(False)
    #             _file_index_status = True
    #
    #         for _widget in list_file_index_widgets:
    #             _widget.setVisible(_file_index_status)
    #
    # # Utilities
    #
    # def get_list_row_selected(self):
    #     table_selection = self.ui.tableWidget.selectedRanges()
    #
    #     # that means we selected the first row
    #     if table_selection == []:
    #         return [0]
    #
    #     table_selection = table_selection[0]
    #     top_row = table_selection.topRow()
    #     bottom_row = table_selection.bottomRow() + 1
    #
    #     return np.arange(top_row, bottom_row)
    #
    # def check_registration_tool_widgets(self):
    #     """if the registration tool is active, and the reference image is the only row selected,
    #     disable the widgets"""
    #     if self.registration_tool_ui:
    #         self.registration_tool_ui.update_status_widgets()
    #
    # def set_widget_status(self, list_ui=[], enabled=True):
    #     for _ui in list_ui:
    #         _ui.setEnabled(enabled)
    #
    # def all_table_cell_modified(self):
    #     nbr_row = self.ui.tableWidget.rowCount()
    #     for _row in np.arange(nbr_row):
    #         self.modified_images(list_row=[_row])
    #         self.profile_line_moved()
    #
    # # Event handler
    #
    #
    #
    # def table_row_clicked(self, row=-1):
    #     self.ui.file_slider.blockSignals(True)
    #     if row == -1:
    #         row = self.ui.tableWidget.currentRow()
    #     else:
    #         self.ui.file_slider.setValue(row)
    #
    #     self.display_image()
    #     self.check_selection_slider_status()
    #     self.profile_line_moved()
    #     self.check_selection_slider_status()
    #     self.check_status_next_prev_image_button()
    #     self.check_registration_tool_widgets()
    #     self.display_markers(all=True)
    #     self.ui.file_slider.blockSignals(False)
    #
    #
    #
    #
    # def ok_button_clicked(self):
    #     self.close()
    #
    # def export_button_clicked(self):
    #     _export_folder = QFileDialog.getExistingDirectory(self,
    #                                                       directory=self.working_dir,
    #                                                       caption = "Select Output Folder",
    #                                                       options=QFileDialog.ShowDirsOnly)
    #     if _export_folder:
    #         o_export = ExportRegistration(parent=self, export_folder=_export_folder)
    #         o_export.run()
    #         QtGui.QApplication.processEvents()
    #
    #
    #
    # def selection_all_clicked(self):
    #     _is_checked = self.ui.selection_all.isChecked()
    #
    #     list_widgets = [self.ui.top_row_label,
    #                     self.ui.bottom_row_label,
    #                     self.ui.opacity_selection_slider]
    #     for _widget in list_widgets:
    #         _widget.setEnabled(not _is_checked)
    #     self.display_image()
    #     self.profile_line_moved()
    #
