from IPython.core.display import HTML
from IPython.core.display import display
import numpy as np
import os
from skimage import transform
from scipy.ndimage.interpolation import shift
import copy
from qtpy.QtWidgets import QMainWindow,QTableWidgetSelectionRange, QTableWidgetItem
from qtpy import QtGui, QtCore
import webbrowser

from __code import load_ui

from __code._utilities.table_handler import TableHandler
from __code.registration.event_handler import EventHandler
from __code.registration.marker_handler import MarkerHandler
from __code.registration.get import Get
from __code.registration.display import Display
from __code.registration.initialization import Initialization
from __code.registration.registration_marker import RegistrationMarkersLauncher
from __code.registration.export import Export
from __code.registration.registration_auto import RegistrationAuto
from __code.registration.registration_auto_confirmation import RegistrationAutoConfirmationLauncher
from __code.registration.manual import ManualLauncher
from __code.registration.registration_profile import RegistrationProfileLauncher
from __code.registration.check import Check

import warnings
warnings.filterwarnings('ignore')


class RegistrationUi(QMainWindow):

    table_registration = {}  # dictionary that populate the table

    table_column_width = [650, 80, 80, 80]
    value_to_copy = None

    # image view
    histogram_level = None

    # by default, the reference image is the first image
    reference_image_index = 0
    reference_image = None
    reference_image_short_name = ''
    color_reference_background = QtGui.QColor(50, 250, 50)
    color_reference_profile = [50, 250, 50]

    nbr_files = 0

    # image currently display in image_view
    live_image = []

    # grid on top of images
    grid_view = {'pos': None,
                 'adj': None,
                 'item': None,
                 'color': (0, 0, 255, 255, 1)}

    new_reference_image = True
    list_rgb_profile_color = None

    # external registration ui
    registration_tool_ui = None
    registration_auto_confirmation_ui = None
    registration_markers_ui = None
    registration_profile_ui = None

    # markers table
    # markers_table = {'1': {'data': {'file_0': {'x': 0, 'y':10, 'marker_ui': None, 'label_ui': None},
    #                                 'file_1': {'x': 0, 'y':10, 'marker_ui': None. 'label_ui': None},
    #                                 'file_2': {'x': 0, 'y':10, 'marker_ui': None, 'label_ui': None},
    #                                   ... },
    #                        'ui': None,
    #                        'color': {'qpen': None,
    #                                  'name': ""},
    #                 {'2': .... }
    markers_table = {}
    markers_table_column_width = [330, 50, 50, 250]
    marker_table_buffer_cell = None

    # initial position of the marker (None means that no row has been selected yet)
    markers_initial_position = {'row': None,
                                'tab_name': '1'}

    def __init__(self, parent=None, data_dict=None):

        super(QMainWindow, self).__init__(parent)

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that will pop up in a few seconds \
            (maybe hidden behind this browser!)</span>'))
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_registration.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)

        self.setWindowTitle("Registration")

        self.data_dict = data_dict  # Normalization data dictionary  {'filename': [],
                                                                     #'data': [[...],[...]]],
                                                                     #'metadata': [],
                                                                     #'shape': {}}

        # untouched array of images (used to move and rotate images)
        self.data_dict_raw = copy.deepcopy(data_dict)
        self.reference_image = self.data_dict['data'][self.reference_image_index]
        self.working_dir = os.path.dirname(self.data_dict['file_name'][0])
        self.reference_image_short_name = str(os.path.basename(self.data_dict['file_name'][0]))

        # initialization
        o_init = Initialization(parent=self)
        o_init.run_all()

        # display line profile
        o_event = EventHandler(parent=self)
        o_event.profile_line_moved()

        self.new_reference_image = False
        self.ui.selection_reference_opacity_groupBox.setVisible(False) # because by default first row = reference selected

    def filter_checkbox_clicked(self):
        self.ui.filter_groupBox.setEnabled(self.ui.filter_checkBox.isChecked())
        o_event = EventHandler(parent=self)
        o_event.update_table_according_to_filter()

    def filter_value_changed(self, value):
        o_event = EventHandler(parent=self)
        o_event.update_table_according_to_filter()

    def filter_algo_changed(self, index):
        o_event = EventHandler(parent=self)
        o_event.update_table_according_to_filter()

    def filter_column_changed(self, index):
        o_event = EventHandler(parent=self)
        o_event.update_table_according_to_filter()

    def table_right_click(self):
        o_event = EventHandler(parent=self)
        o_event.table_right_click()

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
        item = QTableWidgetItem(str(value))
        self.ui.tableWidget.setItem(row, col, item)
        if is_reference_image:
            item.setBackground(self.color_reference_background)
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def display_image(self):
        o_display = Display(parent=self)
        o_display.image()

    def select_row_in_table(self, row=0, user_selected_row=True):

        if not user_selected_row:
            self.ui.tableWidget.blockSignals(True)

        nbr_col = self.ui.tableWidget.columnCount()
        nbr_row = self.ui.tableWidget.rowCount()

        # clear previous selection
        full_range = QTableWidgetSelectionRange(0, 0, nbr_row-1, nbr_col-1)
        self.ui.tableWidget.setRangeSelected(full_range, False)

        # select file of interest
        selection_range = QTableWidgetSelectionRange(row, 0, row, nbr_col-1)
        self.ui.tableWidget.setRangeSelected(selection_range, True)

        self.ui.tableWidget.showRow(row)

        if not user_selected_row:
            self.ui.tableWidget.blockSignals(False)

    def change_slider(self, offset=+1):
        self.ui.file_slider.blockSignals(True)

        current_slider_value = self.ui.file_slider.value()

        new_row_selected = current_slider_value + offset

        self.select_row_in_table(row=new_row_selected, user_selected_row=False)
        self.ui.file_slider.setValue(new_row_selected)

        o_check = Check(parent=self)
        o_check.status_next_prev_image_button()

        o_display = Display(parent=self)
        o_display.image()

        o_event = EventHandler(parent=self)
        o_event.profile_line_moved()

        self.ui.file_slider.blockSignals(False)

    def set_widget_status(self, list_ui=[], enabled=True):
        for _ui in list_ui:
            _ui.setEnabled(enabled)

    def all_table_cell_modified(self):
        nbr_row = self.ui.tableWidget.rowCount()
        o_event = EventHandler(parent=self)

        for _row in np.arange(nbr_row):
            o_event.modified_images(list_row=[_row])
            o_event.profile_line_moved()

    def opacity_changed(self, opacity_value):
        self.display_image()

    def table_row_clicked(self, row=-1):
        self.ui.file_slider.blockSignals(True)
        if row == -1:
            row = self.ui.tableWidget.currentRow()
        else:
            self.ui.file_slider.setValue(row)

        o_event = EventHandler(parent=self)

        o_event.modified_images(list_row=[row])

        o_display = Display(parent=self)
        o_display.image()

        # self.check_selection_slider_status()

        o_event.profile_line_moved()

        # self.check_selection_slider_status()

        o_check = Check(parent=self)
        o_check.status_next_prev_image_button()
        o_check.registration_tool_widgets()
        o_check.selection_slider_status()

        o_marker = MarkerHandler(parent=self)
        o_marker.display_markers(all=True)

        self.ui.file_slider.blockSignals(False)

    def table_cell_modified(self, row=-1, column=-1):
        o_get = Get(parent=self)
        list_row_selected = o_get.list_row_selected()
        o_event = EventHandler(parent=self)
        o_event.modified_images(list_row=list_row_selected)

        o_display = Display(parent=self)
        o_display.image()

        o_event.profile_line_moved()

    def slider_file_changed(self, index_selected):
        self.ui.tableWidget.blockSignals(True)
        self.select_row_in_table(row=index_selected)
        self.display_image()

        o_event = EventHandler(parent=self)
        o_event.profile_line_moved()

        o_check = Check(parent=self)
        o_check.status_next_prev_image_button()

        self.ui.tableWidget.blockSignals(False)

    def help_button_clicked(self):
        webbrowser.open("https://neutronimaging.pages.ornl.gov/tutorial/notebooks/registration/")

    def ok_button_clicked(self):
        self.close()

    def export_button_clicked(self):
        o_export = Export(parent=self)
        o_export.run()

    def closeEvent(self, event=None):
        if self.registration_tool_ui:
            self.registration_tool_ui.close()
        if self.registration_markers_ui:
            self.registration_markers_ui.close()
        if self.registration_profile_ui:
            self.registration_profile_ui.close()

    def previous_image_button_clicked(self):
        self.change_slider(offset=-1)

    def next_image_button_clicked(self):
        self.change_slider(offset=+1)

    def selection_all_clicked(self):
        _is_checked = self.ui.selection_all.isChecked()

        list_widgets = [self.ui.top_row_label,
                        self.ui.bottom_row_label,
                        self.ui.opacity_selection_slider]
        for _widget in list_widgets:
            _widget.setEnabled(not _is_checked)
        self.display_image()
        o_event = EventHandler(parent=self)
        o_event.profile_line_moved()

    def profile_line_moved(self):
        o_event = EventHandler(parent=self)
        o_event.profile_line_moved()

    def selection_slider_changed(self):
        # self.update_selection_images()
        self.display_image()
        o_event = EventHandler(parent=self)
        o_event.profile_line_moved()

    def selection_slider_moved(self):
        # self.update_selection_images()
        self.display_image()
        o_event = EventHandler(parent=self)
        o_event.profile_line_moved()

    def manual_registration_button_clicked(self):
        """launch the manual registration tool"""
        o_registration_tool = ManualLauncher(parent=self)
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
        o_display = Display(parent=self)
        o_display.live_image()

    def grid_size_slider_moved(self, position):
        o_display = Display(parent=self)
        o_display.live_image()

    def grid_size_slider_pressed(self):
        o_display = Display(parent=self)
        o_display.live_image()
