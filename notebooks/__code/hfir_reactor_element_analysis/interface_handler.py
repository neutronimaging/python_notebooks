from qtpy.QtWidgets import QMainWindow
import os
import numpy as np

from __code import load_ui
from __code.hfir_reactor_element_analysis.initialization import Initialization
from __code.hfir_reactor_element_analysis.event_handler import EventHandler
from __code.hfir_reactor_element_analysis.export_data import ExportData


class InterfaceHandler:

    def __init__(self, working_dir=None, o_selection=None):
        o_interface = Interface(o_selection=o_selection,
                                working_dir=working_dir)
        o_interface.show()
        self.o_interface = o_interface


class Interface(QMainWindow):

    NUMBER_OF_FUEL_ELEMENTS = 369
    MINIMUM_NUMBER_OF_ANGLE_DATA_POINTS = 50
    ELEMENTS_POSITION_OUTLIERS = 10  # number of data points to remove before calculating mean x position

    profiles_plot = None
    elements_position_plot = None
    global_list_of_xy_max = None

    elements_position_raw_table = None
    elements_position_formatted_raw_table = None
    list_mean_position_of_elements = None

    percent_of_outliers_to_reject = 10   # %

    def __init__(self, parent=None, o_selection=None, working_dir=None):
        self.o_selection = o_selection
        self.o_pandas = o_selection.pandas_obj
        self.working_dir = working_dir
        self.list_angles = self.o_pandas.index
        self.list_of_images = [_image.strip() for _image in o_selection.column_labels[1:]]

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
        o_init.table_of_metadata()

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
        self.list_of_images_selection_changed()
        o_event.populate_elements_position_tab()
        self.ui.setEnabled(True)
        self.ui.tabWidget.setTabEnabled(1, True)

    def threshold_moved(self, value):
        o_event = EventHandler(parent=self)
        o_event.threshold_moved(value=value)
        self.list_of_images_selection_changed()

    def threshold_clicked(self):
        value = self.ui.threshold_slider.value()
        o_event = EventHandler(parent=self)
        o_event.threshold_moved(value=value)
        self.list_of_images_selection_changed()

    def export_table_data_pushButton_clicked(self):
        o_export = ExportData(parent=self)
        o_export.run()

    def elements_position_tolerance_value_changed(self):
        o_event = EventHandler(parent=self)
        # o_event.calculate_average_x_for_each_element()
        o_event.populate_elements_position_table()

    def click_on_elements_position_plot(self, event):
        file_index = np.int(event.ydata)
        list_of_images = self.list_of_images
        self.ui.elements_position_file_name_label.setText(list_of_images[file_index])

    def refresh_table_clicked(self):
        o_event = EventHandler(parent=self)
        o_event.populate_elements_position_tab()
