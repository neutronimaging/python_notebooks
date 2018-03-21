import ipywe.fileselector

from IPython.core.display import HTML
from IPython.core.display import display
from ipywidgets import widgets

import numpy as np
import os
import re
import glob
from scipy.special import erf
from scipy.optimize import curve_fit
import pprint

import pyqtgraph as pg
from pyqtgraph.dockarea import *

from __code.file_handler import make_ascii_file

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from NeuNorm.normalization import Normalization


from __code.ui_registration  import Ui_MainWindow as UiMainWindow


class RegistrationUi(QMainWindow):

    table_registration = {} # dictionary that populate the table

    table_column_width = [650, 80, 80, 80]

    # image view
    histogram_level = []

    # by default, the reference image is the first image
    reference_image_index = 0
    reference_image = []

    # image currently display in image_view
    live_image = []

    def __init__(self, parent=None, data_dict=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Registration")

        self.data_dict = data_dict # Normalization data dictionary  {'filename': [],
                                                                     #'data': [[...],[...]]],
                                                                     #'metadata': [],
                                                                     #'shape': {}}
        self.reference_image = self.data_dict['data'][self.reference_image_index]

        # initialization
        self.init_pyqtgrpah()
        self.init_widgets()
        self.init_table()

        # display line profile
        self.profile_line_moved()

    # initialization
    def init_pyqtgrpah(self):
        area = DockArea()
        area.setVisible(True)
        d1 = Dock("Registered Image", size=(400, 600))
        d2 = Dock("Profile", size=(400, 200))

        area.addDock(d1, 'top')
        area.addDock(d2, 'bottom')

        # registered image
        self.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.ui.image_view.ui.menuBtn.hide()
        self.ui.image_view.ui.roiBtn.hide()
        # profile selection tool
        self.ui.profile_line = pg.LineSegmentROI([[50, 50], [100, 100]], pen='r')
        self.ui.image_view.addItem(self.ui.profile_line)
        d1.addWidget(self.ui.image_view)
        self.ui.profile_line.sigRegionChanged.connect(self.profile_line_moved)

        # profile
        self.ui.profile = pg.PlotWidget(title='Profile')
        self.ui.profile.plot()
        d2.addWidget(self.ui.profile)

        # set up layout
        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(area)

        self.ui.pyqtgraph_widget.setLayout(vertical_layout)

    def init_widgets(self):
        """size and label of any widgets"""
        self.ui.splitter.setSizes([800, 100])

        # update size of table columns
        nbr_columns = self.ui.tableWidget.columnCount()
        for _col in range(nbr_columns):
            self.ui.tableWidget.setColumnWidth(_col, self.table_column_width[_col])

        # update slidewidget of files
        nbr_files = len(self.data_dict['file_name'])
        self.ui.file_slider.setMinimum(1)
        self.ui.file_slider.setMaximum(nbr_files-1)

        # reference image
        reference_image = self.data_dict['file_name'][0]
        self.ui.reference_image_label.setText(reference_image)


    def init_table(self):
        """populate the table with list of file names and default xoffset, yoffset and rotation"""
        list_file_names = self.data_dict['file_name']
        table_registration = {}

        _row_index = 0
        for _file_index, _file in enumerate(list_file_names):

            # first row is the reference row
            if _file_index == self.reference_image_index:
                continue

            _row_infos = {}

            # col 0 - file name
            _row_infos['filename'] = _file
            _row_infos['xoffset'] = 0
            _row_infos['yoffset'] = 0
            _row_infos['rotation'] = 0

            table_registration[_row_index] = _row_infos
            _row_index += 1

        self.table_registration = table_registration
        self.populate_table()

        #select first row
        self.select_row_in_table(0)

    def profile_line_moved(self):
        """update profile plot"""
        d2 = self.ui.profile_line.getArrayRegion(self.live_image, self.ui.image_view.imageItem)
        self.ui.profile.clear()
        self.ui.profile.plot(d2)

        image_selected = self.get_image_selected()
        reference_image = self.reference_image

    def populate_table(self):
        """populate the table using the table_registration dictionary"""
        table_registration = self.table_registration
        for _row in table_registration.keys():
            _row_infos = table_registration[_row]
            self.__insert_table_row(infos=_row_infos, row=_row)

    def refresh_table(self):
        """refresh table contain by removing first everything before repopulating it"""
        self.__clear_table()
        self.populate_table()

    def __clear_table(self):
        nbr_row = self.ui.tableWidget.rowCount()
        for _row in np.arange(nbr_row):
            self.ui.tableWidget.removeRow(0)

    def __insert_table_row(self, infos={}, row=-1):
        self.ui.tableWidget.insertRow(row)
        self.__set_item(row, 0, infos['filename'])
        self.__set_item(row, 1, infos['xoffset'])
        self.__set_item(row, 2, infos['rotation'])

    def __set_item(self, row=0, col=0, value=''):
        item = QtGui.QTableWidgetItem(str(value))
        self.ui.tableWidget.setItem(row, col, item)

    def get_image_selected(self):
        index_selected = self.ui.file_slider.value()
        _image = self.data_dict['data'][index_selected]
        return _image

    def display_image(self):
        _image = self.get_image_selected()

        _view = self.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.histogram_level == []:
            first_update = True
        _histo_widget = self.ui.image_view.getHistogramWidget()
        self.histogram_level = _histo_widget.getLevels()

        _opacity_coefficient = self.ui.opacity_slider.value() # betwween 0 and 100
        _opacity_image = _opacity_coefficient / 100.
        _image = np.transpose(_image) * _opacity_image

        _opacity_reference = 1 - _opacity_image
        _reference_image = np.transpose(self.reference_image) * _opacity_reference

        _final_image = _reference_image + _image
        self.ui.image_view.setImage(_final_image)
        self.live_image = _final_image

        _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.histogram_level[0], self.histogram_level[1])

    def select_row_in_table(self, row=0):
        nbr_col = self.ui.tableWidget.columnCount()
        nbr_row = self.ui.tableWidget.rowCount()

        # clear previous selection
        full_range = QtGui.QTableWidgetSelectionRange(0, 0, nbr_row-1, nbr_col-1)
        self.ui.tableWidget.setRangeSelected(full_range, False)

        # select file of interest
        selection_range = QtGui.QTableWidgetSelectionRange(row, 0, row, nbr_col-1)
        self.ui.tableWidget.setRangeSelected(selection_range, True)

        self.ui.tableWidget.showRow(row)

    # Event handler

    def opacity_changed(self, opacity_value):
        self.display_image()

    def table_row_clicked(self):
        self.ui.file_slider.blockSignals(True)
        row = self.ui.tableWidget.currentRow()
        self.ui.file_slider.setValue(row+1)
        self.display_image()
        self.profile_line_moved()
        self.ui.file_slider.blockSignals(False)

    def slider_file_changed(self, index_selected):
        self.ui.tableWidget.blockSignals(True)
        self.display_image()
        self.select_row_in_table(row=index_selected-1)
        self.profile_line_moved()
        self.ui.tableWidget.blockSignals(False)

    def help_button_clicked(self):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/registration/")

    def ok_button_clicked(self):
        # do soemthing here
        self.close()

    def cancel_button_clicked(self):
        self.close()


class RegistrationFileSelection(object):

    def __init__(self, working_dir='./'):
        self.working_dir = working_dir

    def select_file_help(self, value):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/file_selector/#select_profile")

    def load_files(self, files):
        o_norm = Normalization()
        o_norm.load(file=files, notebook=True)
        self.data_dict = o_norm.data

    def select_data(self):
        help_ui = widgets.Button(description="HELP",
                                 button_style='info')
        help_ui.on_click(self.select_file_help)
        display(help_ui)

        self.files_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Images ...',
                                                             start_dir=self.working_dir,
                                                             next=self.load_files,
                                                             multiple=True)

        self.files_ui.show()
