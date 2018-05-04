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

    histogram_level = []
    col_width = 50
    table_column_width = [col_width, col_width, col_width, col_width, 100]


    def __init__(self, parent=None, data_dict=None):

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Calibrated Transmission")

        self.data_dict = data_dict # Normalization data dictionary  {'filename': [],
                                                                     #'data': [[...],[...]]],
                                                                     #'metadata': [],
                                                                     #'shape': {}}

        # untouched array of images (used to move and rotate images)
        self.data_dict_raw = copy.deepcopy(data_dict)

        # initialization
        self.init_pyqtgrpah()
        self.init_widgets()
        # self.init_table()
        # self.init_parameters()
        # self.init_statusbar()

        # display first image
        self.slider_file_changed(-1)

    # initialization
    def init_statusbar(self):
        self.eventProgress = QtGui.QProgressBar(self.ui.statusbar)
        self.eventProgress.setMinimumSize(300, 20)
        self.eventProgress.setMaximumSize(300, 20)
        self.eventProgress.setVisible(False)
        self.ui.statusbar.addPermanentWidget(self.eventProgress)

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







    # getter
    def get_image_selected(self):
        slider_index = self.ui.file_slider.value()
        _image = self.data_dict['data'][slider_index]
        return _image




    # event handler
    def slider_file_changed(self, index_selected):
        self.display_image()
        self.check_status_next_prev_image_button()
        self.ui.tableWidget.blockSignals(False)

    def add_row_button_clicked(self):
        pass

    def remove_row_button_clicked(self):
        pass

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






















    def display_markers(self, all=False):
        if self.registration_markers_ui is None:
            return

        if all is False:
            _current_tab = self.registration_markers_ui.ui.tabWidget.currentIndex()
            _tab_title = self.registration_markers_ui.ui.tabWidget.tabText(_current_tab)
            self.display_markers_of_tab(marker_name=_tab_title)
        else:
            for _index, _marker_name in enumerate(self.markers_table.keys()):
                self.display_markers_of_tab(marker_name=_marker_name)

    def get_list_short_file_selected(self):
        list_row_selected = self.get_list_row_selected()
        full_list_files = np.array(self.data_dict['file_name'])
        list_file_selected = full_list_files[list_row_selected]
        list_short_file_selected = [os.path.basename(_file) for _file in
                                    list_file_selected]
        return list_short_file_selected

    def display_markers_of_tab(self, marker_name=''):
        self.close_markers_of_tab(marker_name=marker_name)
        # get short name of file selected
        list_short_file_selected = self.get_list_short_file_selected()
        nbr_file_selected = len(list_short_file_selected)
        if nbr_file_selected > 1:
            list_row_selected = self.get_list_row_selected()
        _color_marker = self.markers_table[marker_name]['color']['name']

        pen = self.markers_table[marker_name]['color']['qpen']
        for _index, _file in enumerate(list_short_file_selected):
            _marker_data = self.markers_table[marker_name]['data'][_file]

            x = _marker_data['x']
            y = _marker_data['y']
            width = MarkerDefaultSettings.width
            height = MarkerDefaultSettings.height

            _marker_ui = pg.RectROI([x,y], [width, height], pen=pen)
            self.ui.image_view.addItem(_marker_ui)
            _marker_ui.removeHandle(0)
            _marker_ui.sigRegionChanged.connect(self.marker_has_been_moved)

            if nbr_file_selected > 1: # more than 1 file selected, we need to add the index of the file
                text_ui = self.add_marker_label(file_index= list_row_selected[_index],
                                                marker_index = marker_name,
                                                x=x,
                                                y=y,
                                                color=_color_marker)
                self.markers_table[marker_name]['data'][_file]['label_ui'] = text_ui

            _marker_data['marker_ui'] = _marker_ui

    def marker_has_been_moved(self):
        list_short_file_selected = self.get_list_short_file_selected()
        nbr_file_selected = len(list_short_file_selected)
        if nbr_file_selected > 1:
            list_row_selected = self.get_list_row_selected()

        for _index_marker, _marker_name in enumerate(self.markers_table.keys()):
            _color_marker = self.markers_table[_marker_name]['color']['name']
            for _index_file, _file in enumerate(list_short_file_selected):
                _marker_data = self.markers_table[_marker_name]['data'][_file]
                marker_ui = _marker_data['marker_ui']

                region = marker_ui.getArraySlice(self.live_image,
                                                 self.ui.image_view.imageItem)

                x0 = region[0][0].start
                y0 = region[0][1].start

                self.markers_table[_marker_name]['data'][_file]['x'] = x0
                self.markers_table[_marker_name]['data'][_file]['y'] = y0

                self.registration_markers_ui.update_markers_table_entry(marker_name=_marker_name,
                                                                        file=_file)

                if nbr_file_selected > 1:
                    _label_ui = _marker_data['label_ui']
                    self.ui.image_view.removeItem(_label_ui)
                    _label_ui = self.add_marker_label(file_index = list_row_selected[_index_file],
                                                      marker_index = _index_marker,
                                                      x=x0,
                                                      y=y0,
                                                      color=_color_marker)
                    self.ui.image_view.addItem(_label_ui)
                    self.markers_table[_marker_name]['data'][_file]['label_ui'] = _label_ui

    def add_marker_label(self, file_index=0, marker_index=1, x=0, y=0, color='white'):
        html_color = MarkerDefaultSettings.color_html[color]
        html_text = '<div style="text-align: center">Marker#:'
        html_text += '<span style="color:#' + str(html_color) + ';">' + str(int(marker_index)+1)
        html_text += '</span> - File#:'
        html_text += '<span style="color:#' + str(html_color) + ';">' + str(file_index)
        html_text += '</span>'
        text_ui = pg.TextItem(html=html_text, angle=45, border='w')
        self.ui.image_view.addItem(text_ui)
        text_ui.setPos(x + MarkerDefaultSettings.width, y)
        return text_ui

    def close_markers_of_tab(self, marker_name=''):
        """remove box and label (if they are there) of each marker"""
        _data = self.markers_table[marker_name]['data']
        for _file in _data:
            _marker_ui = _data[_file]['marker_ui']
            if _marker_ui:
                self.ui.image_view.removeItem(_marker_ui)

            _label_ui = _data[_file]['label_ui']
            if _label_ui:
                self.ui.image_view.removeItem(_label_ui)




    def populate_table(self):
        """populate the table using the table_registration dictionary"""
        self.ui.tableWidget.blockSignals(True)
        table_registration = self.table_registration
        for _row in table_registration.keys():
            _row_infos = table_registration[_row]
            self.__insert_table_row(infos=_row_infos, row=_row)
        self.ui.tableWidget.blockSignals(False)

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

        is_reference_image = False
        if row == self.reference_image_index:
            is_reference_image = True

        self.set_item(row, 0, infos['filename'], is_reference_image=is_reference_image)
        self.set_item(row, 1, infos['xoffset'], is_reference_image=is_reference_image)
        self.set_item(row, 2, infos['yoffset'], is_reference_image=is_reference_image)
        self.set_item(row, 3, infos['rotation'], is_reference_image=is_reference_image)

    def set_item(self, row=0, col=0, value='', is_reference_image=False):
        item = QtGui.QTableWidgetItem(str(value))
        self.ui.tableWidget.setItem(row, col, item)
        if is_reference_image:
            item.setBackground(self.color_reference_background)
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)




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

    def change_slider(self, offset=+1):
        self.ui.file_slider.blockSignals(True)
        current_slider_value = self.ui.file_slider.value()
        new_row_selected = current_slider_value + offset
        self.select_row_in_table(row=new_row_selected)
        self.ui.file_slider.setValue(new_row_selected)
        self.check_status_next_prev_image_button()
        self.display_image()
        self.profile_line_moved()
        self.ui.file_slider.blockSignals(False)

    def check_selection_slider_status(self):
        """
        if there is more than one row selected, we need to display the left slider but also
        we need to disable the next, prev buttons and file index slider
        """
        selection = self.ui.tableWidget.selectedRanges()
        if selection:

            list_file_index_widgets = [self.ui.previous_image_button,
                                       self.ui.file_slider,
                                       self.ui.next_image_button]

            top_row = selection[0].topRow()
            bottom_row = selection[0].bottomRow()
            if np.abs(bottom_row - top_row) >= 1: # show selection images widgets
                self.ui.selection_groupBox.setVisible(True)
                self.ui.top_row_label.setText("Row {}".format(top_row+1))
                self.ui.bottom_row_label.setText("Row {}".format(bottom_row+1))
                self.ui.opacity_selection_slider.setMinimum(top_row*100)
                self.ui.opacity_selection_slider.setMaximum(bottom_row*100)
                self.ui.opacity_selection_slider.setSliderPosition(top_row*100)
                _file_index_status = False
            else:
                self.ui.selection_groupBox.setVisible(False)
                _file_index_status = True

            for _widget in list_file_index_widgets:
                _widget.setVisible(_file_index_status)

    # Utilities

    def get_list_row_selected(self):
        table_selection = self.ui.tableWidget.selectedRanges()

        # that means we selected the first row
        if table_selection == []:
            return [0]

        table_selection = table_selection[0]
        top_row = table_selection.topRow()
        bottom_row = table_selection.bottomRow() + 1

        return np.arange(top_row, bottom_row)

    def check_registration_tool_widgets(self):
        """if the registration tool is active, and the reference image is the only row selected,
        disable the widgets"""
        if self.registration_tool_ui:
            self.registration_tool_ui.update_status_widgets()

    def set_widget_status(self, list_ui=[], enabled=True):
        for _ui in list_ui:
            _ui.setEnabled(enabled)

    def all_table_cell_modified(self):
        nbr_row = self.ui.tableWidget.rowCount()
        for _row in np.arange(nbr_row):
            self.modified_images(list_row=[_row])
            self.profile_line_moved()

    # Event handler



    def table_row_clicked(self, row=-1):
        self.ui.file_slider.blockSignals(True)
        if row == -1:
            row = self.ui.tableWidget.currentRow()
        else:
            self.ui.file_slider.setValue(row)

        self.display_image()
        self.check_selection_slider_status()
        self.profile_line_moved()
        self.check_selection_slider_status()
        self.check_status_next_prev_image_button()
        self.check_registration_tool_widgets()
        self.display_markers(all=True)
        self.ui.file_slider.blockSignals(False)




    def ok_button_clicked(self):
        self.close()

    def export_button_clicked(self):
        _export_folder = QFileDialog.getExistingDirectory(self,
                                                          directory=self.working_dir,
                                                          caption = "Select Output Folder",
                                                          options=QFileDialog.ShowDirsOnly)
        if _export_folder:
            o_export = ExportRegistration(parent=self, export_folder=_export_folder)
            o_export.run()
            QtGui.QApplication.processEvents()

    def closeEvent(self, event=None):
        if self.registration_tool_ui:
            self.registration_tool_ui.close()
        if self.registration_markers_ui:
            self.registration_markers_ui.close()
        if self.registration_profile_ui:
            self.registration_profile_ui.close()


    def selection_all_clicked(self):
        _is_checked = self.ui.selection_all.isChecked()

        list_widgets = [self.ui.top_row_label,
                        self.ui.bottom_row_label,
                        self.ui.opacity_selection_slider]
        for _widget in list_widgets:
            _widget.setEnabled(not _is_checked)
        self.display_image()
        self.profile_line_moved()

    def selection_slider_changed(self):
        # self.update_selection_images()
        self.display_image()
        self.profile_line_moved()

    def selection_slider_moved(self):
        # self.update_selection_images()
        self.display_image()
        self.profile_line_moved()

    def manual_registration_button_clicked(self):
        """launch the manual registration tool"""
        o_registration_tool = RegistrationManualLauncher(parent=self)
        self.set_widget_status(list_ui=[self.ui.auto_registration_button],
                           enabled=False)

    def auto_registration_button_clicked(self):
        o_registration_auto_confirmed = RegistrationAutoConfirmationLauncher(parent=self)

    def markers_registration_button_clicked(self):
        o_markers_registration = RegistrationMarkersLauncher(parent=self)
        self.set_widget_status(list_ui=[self.ui.auto_registration_button],
                           enabled=False)

    def profiler_registration_button_clicked(self):
        o_registration_profile = RegistrationProfileLauncher(parent=self)

    def start_auto_registration(self):
        o_auto_register = RegistrationAuto(parent=self,
                                           reference_image=self.reference_image,
                                           floating_images=self.data_dict['data'])
        o_auto_register.auto_align()

    def grid_display_checkBox_clicked(self):
        self.display_live_image()

    def grid_size_slider_moved(self, position):
        self.display_live_image()

    def grid_size_slider_pressed(self):
        self.display_live_image()
