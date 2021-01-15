from qtpy.QtWidgets import QMainWindow, QVBoxLayout, QProgressBar, QApplication
import os
import numpy as np

from __code import load_ui
from __code.hfir_reactor_element_analysis.initialization import Initialization
from __code.hfir_reactor_element_analysis.event_handler import EventHandler


class InterfaceHandler:

    def __init__(self, working_dir=None, o_selection=None):
        o_interface = Interface(o_selection=o_selection,
                                working_dir=working_dir)
        o_interface.show()
        self.o_interface = o_interface


class Interface(QMainWindow):

    NUMBER_OF_FUEL_ELEMENTS = 369
    MINIMUM_NUMBER_OF_ANGLE_DATA_POINTS = 50

    profiles_plot = None
    elements_position_plot = None
    global_list_of_xy_max = None

    def __init__(self, parent=None, o_selection=None, working_dir=None):
        self.o_selection = o_selection
        self.o_pandas = o_selection.pandas_obj
        self.working_dir = working_dir
        self.list_angles = self.o_pandas.index

        super(Interface, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_hfir_reactor_element_local_max.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Data fitting")

        o_init = Initialization(parent=self)
        o_init.matplotlib()
        o_init.widgets()
        o_init.statusbar()

    # event handler
    def list_of_images_selection_changed(self):
        o_event = EventHandler(parent=self)
        o_event.list_of_images_selection_changed()

    def plot_type_changed(self):
        self.list_of_images_selection_changed()

    def list_of_images_right_click(self, position=None):
        o_event = EventHandler(parent=self)
        o_event.list_of_images_right_click()

    def get_list_file_index_selected(self):
        nbr_row = self.ui.listWidget.count()
        list_file_selected = []
        for _row in np.arange(nbr_row):
            _item = self.ui.listWidget.item(_row)
            if _item.isSelected():
                list_file_selected.append(_row)
        return list_file_selected

    def calculate_elements_position_clicked(self):
        self.ui.setEnabled(False)
        o_event = EventHandler(parent=self)
        o_event.calculate_elements_position()
        self.ui.setEnabled(True)

    def high_threshold_moved(self, value):
        o_event = EventHandler(parent=self)
        o_event.high_threshold_moved(value=value)
        self.list_of_images_selection_changed()

    def high_threshold_clicked(self):
        value = self.ui.high_threshold_slider.value()
        o_event = EventHandler(parent=self)
        o_event.high_threshold_moved(value=value)
        self.list_of_images_selection_changed()

    def low_threshold_moved(self, value):
        o_event = EventHandler(parent=self)
        o_event.low_threshold_moved(value=value)
        self.list_of_images_selection_changed()

    def low_threshold_clicked(self):
        value = self.ui.low_threshold_slider.value()
        o_event = EventHandler(parent=self)
        o_event.low_threshold_moved(value=value)
        self.list_of_images_selection_changed()

    def list_of_images_tableWidget_right_clicked(self, position):
        print("here")
