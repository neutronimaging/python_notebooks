from IPython.core.display import HTML
from IPython.core.display import display

import os
import numpy as np
import pyqtgraph as pg
from pyqtgraph.dockarea import *

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui, QtWidgets
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtWidgets import QApplication, QMainWindow

from __code.ui_registration_profile import Ui_MainWindow as UiMainWindowProfile



class RegistrationProfileUi(QMainWindow):

    does_top_parent_exist = False

    data_dict = None
    table_column_width = [350, 100, 100, 100, 100]

    # reference file
    reference_image_index = 0
    reference_image = []
    reference_image_short_name = ''
    color_reference_background = QtGui.QColor(50, 250, 50)

    # image display
    histogram_level = []

    def __init__(self, parent=None, data_dict=None):

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindowProfile()
        self.ui.setupUi(self)
        self.setWindowTitle("Registration Profile Tool")

        self.init_widgets()
        self.init_pyqtgraph()
        self.init_statusbar()

        self.parent = parent
        if parent:
            self.data_dict = self.parent.data_dict
            self.does_top_parent_exist = True
        elif data_dict:
            display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
                (maybe hidden behind this browser!)</span>'))
            self.data_dict = data_dict
        else:
            raise ValueError("please provide data_dict")

        self.init_reference_image()
        self.init_table()

        self.display_selected_row()

    ## Initialization

    def init_statusbar(self):
        self.eventProgress = QtGui.QProgressBar(self.ui.statusbar)
        self.eventProgress.setMinimumSize(300, 20)
        self.eventProgress.setMaximumSize(300, 20)
        self.eventProgress.setVisible(True)
        self.ui.statusbar.addPermanentWidget(self.eventProgress)

    def init_widgets(self):
        # no need to show save and close if not called from parent UI
        if self.parent is None:
            self.ui.save_and_close_button.setVisible(False)

        # table columns
        self.ui.tableWidget.blockSignals(True)
        nbr_columns = self.ui.tableWidget.columnCount()
        for _col in range(nbr_columns):
            self.ui.tableWidget.setColumnWidth(_col, self.table_column_width[_col])
        self.ui.tableWidget.blockSignals(False)

    def init_pyqtgraph(self):
        area = DockArea()
        area.setVisible(True)
        d1 = Dock("Registered Image", size=(600, 600))
        d2 = Dock("Horizontal Profile", size=(300, 200))
        d3 = Dock("Vertical Profile", size=(300, 200))
        d4 = Dock("Peaks Position", size=(600, 600))

        area.addDock(d2, 'top')
        area.addDock(d1, 'left', d2)
        area.addDock(d4, 'above', d1)
        area.addDock(d3, 'bottom', d2)
        area.moveDock(d1, 'above', d4)

        # registered image ara (left dock)
        self.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.ui.image_view.ui.menuBtn.hide()
        self.ui.image_view.ui.roiBtn.hide()
        d1.addWidget(self.ui.image_view)

        # horizontal profile area
        self.ui.hori_profile = pg.PlotWidget(title='Horizontal Profile')
        self.ui.hori_profile.plot()
        d2.addWidget(self.ui.hori_profile)

        # vertical profile area
        self.ui.verti_profile = pg.PlotWidget(title='Vertical Profile')
        self.ui.verti_profile.plot()
        d3.addWidget(self.ui.verti_profile)

        # all peaks position
        self.ui.peaks = pg.PlotWidget(title='All Peaks')
        self.ui.peaks.plot()
        d4.addWidget(self.ui.peaks)

        # set up layout
        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(area)

        self.ui.pyqtgraph_widget.setLayout(vertical_layout)

    def init_reference_image(self):
        if self.does_top_parent_exist:
            self.reference_image_index = self.parent.reference_image_index
            self.reference_image = self.parent.reference_image
            self.reference_image_short_name = self.parent.reference_image_short_name
        else:
            self.reference_image = self.data_dict['data'][self.reference_image_index]
            self.reference_image_short_name = os.path.basename(self.data_dict['file_name'][self.reference_image_index])

    def init_table(self):
        data_dict = self.data_dict
        _list_files = data_dict['file_name']
        _short_list_files = [os.path.basename(_file) for _file in _list_files]

        self.ui.tableWidget.blockSignals(True)
        for _row, _file in enumerate(_short_list_files):
            self.ui.tableWidget.insertRow(_row)
            self.__set_item(_row, 0, _file)
            self.__set_item(_row, 1, 'N/A')
            self.__set_item(_row, 2, 'N/A')
            self.__set_item(_row, 3, 'N/A')
            self.__set_item(_row, 4, 'N/A')

        # select first row by default
        self.select_table_row(0)

        self.ui.tableWidget.blockSignals(False)

    def select_table_row(self, row):
        nbr_col = self.ui.tableWidget.columnCount()
        nbr_row = self.ui.tableWidget.rowCount()

        # clear previous selection
        full_range = QtGui.QTableWidgetSelectionRange(0, 0, nbr_row-1, nbr_col-1)
        self.ui.tableWidget.setRangeSelected(full_range, False)

        # select file of interest
        selection_range = QtGui.QTableWidgetSelectionRange(row, 0, row, nbr_col-1)
        self.ui.tableWidget.setRangeSelected(selection_range, True)

        self.ui.tableWidget.showRow(row)

    def __set_item(self, row=0, col=0, value=''):
        item = QtGui.QTableWidgetItem(str(value))
        self.ui.tableWidget.setItem(row, col, item)
        if row == self.reference_image_index:
            item.setBackground(self.color_reference_background)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def get_selected_row(self):
        """table only allows selection of one row at a time, so top and bottom row are the same"""
        table_selection = self.ui.tableWidget.selectedRanges()
        table_selection = table_selection[0]
        top_row = table_selection.topRow()
        return top_row

    def display_selected_row(self):
        selected_row = self.get_selected_row()
        _image = self.data_dict['data'][selected_row]

        # save and load histogram for consistancy between images
        _view = self.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()
        first_update = False
        if self.histogram_level == []:
            first_update = True
        _histo_widget = self.ui.image_view.getHistogramWidget()
        self.histogram_level = _histo_widget

        ## display here according to transparency
        if selected_row != self.reference_image_index:
            _opacity_coefficient = self.ui.opacity_slider.value()  # betwween 0 and 100
            _opacity_image = _opacity_coefficient / 100.
            _image = np.transpose(_image) * _opacity_image

            _opacity_selected = 1 - _opacity_image
            _reference_image = np.transpose(self.reference_image) * _opacity_selected

            _final_image = _reference_image + _image

        else:
            _final_image = self.reference_image

        self.ui.image_view.setImage(_final_image)

        _view_box.setState(_state)
        if not first_update:
            _histo_widget.setLevels(self.histogram_level[0],
                                    self.histogram_level[1])

    ## Event Handler

    def calculate_markers_button_clicked(self):
        pass

    def help_button_clicked(self):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/registration/")

    def slider_file_changed(self, value):
        pass

    def previous_image_button_clicked(self):
        print("previous")

    def next_image_button_clicked(self):
        pass

    def registered_all_images_button_clicked(self):
        print("registered all images")

    def cancel_button_clicked(self):
        if self.parent:
            self.parent.registration_profile_ui = None
        self.close()

    def save_and_close_button_clicked(self):
        """save registered images back to the main UI"""
        self.cancel_button_clicked()

    def opacity_slider_moved(self, value):
        print("opacity slider")

    def closeEvent(self, c):
        print("here")
        if self.parent:
            self.parent.registration_profile_ui = None
        self.close()