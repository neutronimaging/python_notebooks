from IPython.core.display import HTML
import pandas as pd
import numpy as np
from IPython.core.display import display
import os
from qtpy.QtWidgets import QMainWindow
import copy

from __code import load_ui
from __code.ipywe import fileselector
from __code._utilities.file import retrieve_metadata_value_from_ascii_file
from __code.wave_front_dynamics.algorithms import ListAlgorithm
from __code.wave_front_dynamics.initialization import Initialization
from __code.wave_front_dynamics.event_handler import EventHandler
from __code.wave_front_dynamics.display import Display
from __code.wave_front_dynamics.export import Export


class WaveFrontDynamics:

    list_of_ascii_files = None
    list_of_original_image_files = None
    list_of_data = None

    list_timestamp = None

    def __init__(self, working_dir="~/"):
        self.working_dir = working_dir

    def select_data(self):
        self.list_data_widget = fileselector.FileSelectorPanel(instruction='select linear profile ASCII or Radial Profile list of ascii files ...',
                                                               start_dir=self.working_dir,
                                                               next=self.load_data,
                                                               filters={"ASCII": "*.txt"},
                                                               default_filter="ASCII",
                                                               multiple=True)
        self.list_data_widget.show()

    def load_data(self, list_of_ascii_files=None):

        print(f"top of load_data")
        print(f"{list_of_ascii_files =}")

        if list_of_ascii_files is None:
            return

        list_of_ascii_files.sort()
        self.list_of_ascii_files = list_of_ascii_files

        print(f"{list_of_ascii_files =}")
        return

        list_of_data = []
        list_of_original_image_files = []
        list_of_timestamp = []
        for _file in list_of_ascii_files:
            _data = pd.read_csv(_file,
                                skiprows=6,
                                delimiter=",",
                                names=['pixel', 'mean counts'],
                                dtype=float,
                                index_col=0)
            list_of_data.append(_data)
            _original_image_file = retrieve_metadata_value_from_ascii_file(filename=_file,
                                                                           metadata_name="# source image")
            list_of_original_image_files.append(_original_image_file)
            _time_stamp = retrieve_metadata_value_from_ascii_file(filename=_file,
                                                                  metadata_name="# timestamp")
            list_of_timestamp.append(_time_stamp)

        self.list_timestamp = list_of_timestamp
        self.list_of_data = list_of_data
        self.list_of_original_image_files = list_of_original_image_files

        nbr_files = str(len(list_of_ascii_files))
        display(HTML('<span style="font-size: 20px; color:blue">Notebooks successfully loaded the ' + nbr_files +
                     ' ASCII profile files!</span>'))


class WaveFrontDynamicsUI(QMainWindow):

    list_of_ascii_files = None
    nbr_files = None
    boolean_list_of_files_to_use = None
    list_of_original_image_files = None
    list_of_original_image_files_to_use = None

    # raw
    list_of_data = None
    list_timestamp = None

    # after being prepared
    list_of_data_prepared = None
    list_of_timestamp_of_data_prepared = None

    peak_value_arrays = {ListAlgorithm.sliding_average: None,
                         ListAlgorithm.change_point   : None,
                         ListAlgorithm.error_function : None}

    data_range = {'min': np.NaN,
                  'max': np.NaN}
    max_number_of_data_points = np.NaN

    # matplotlib
    prepare_data_plot = None

    def __init__(self, parent=None, working_dir="./", wave_front_dynamics=None):

        display(HTML('<span style="font-size: 20px; color:blue">Launched UI! '
                     '(maybe hidden behind this browser!)</span>'))

        self.working_dir = working_dir
        self.wave_front_dynamics = wave_front_dynamics

        self.list_of_data = wave_front_dynamics.list_of_data
        self.list_timestamp = wave_front_dynamics.list_timestamp
        self.list_of_original_image_files = wave_front_dynamics.list_of_original_image_files
        self.list_of_original_image_files_to_use = copy.deepcopy(wave_front_dynamics.list_of_original_image_files)
        if self.list_of_data is None:
            display(HTML('<span style="font-size: 20px; color:red">No ASCII file loaded!</span>'))
            return

        self.nbr_files = len(self.list_of_data)

        super(QMainWindow, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_wave_front_dynamics.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Define center and sector of profile")

        o_init = Initialization(parent=self)
        o_init.all()

        self.prepare_data_file_index_pressed()
        self.prepare_data_bin_size_pressed()

        # first file used as reference
        t0 = float(self.list_timestamp[0])
        self.list_relative_timestamp = [float(_time) - t0 for _time in self.list_timestamp]
        o_event = EventHandler(parent=self)
        o_event.update_list_of_relative_timestamp_of_prepared_data()

    # event handler - prepare data tab
    def prepare_data_file_index_pressed(self):
        o_event = EventHandler(parent=self)
        o_event.prepare_data_file_index_slider_changed()
        o_event.check_state_of_prepare_data_plot()

        o_display = Display(parent=self)
        o_display.update_prepare_data_plot()

    def prepare_data_file_index_moved(self, value):
        o_event = EventHandler(parent=self)
        o_event.prepare_data_file_index_slider_changed()

        o_display = Display(parent=self)
        o_display.update_prepare_data_plot()
        o_event.check_state_of_prepare_data_plot()

    def prepare_data_bin_size_pressed(self):
        o_event = EventHandler(parent=self)
        o_event.prepare_data_bin_size_changed()

        o_display = Display(parent=self)
        o_display.update_prepare_data_plot()

    def prepare_data_bin_size_moved(self, value):
        o_event = EventHandler(parent=self)
        o_event.prepare_data_bin_size_changed()

        o_display = Display(parent=self)
        o_display.update_prepare_data_plot()

    def prepare_data_bin_type_changed(self):
        o_display = Display(parent=self)
        o_display.update_prepare_data_plot()

    def update_prepare_data_plot(self):
        o_display = Display(parent=self)
        o_display.update_prepare_data_plot()

    def prepare_data_data_range_changed(self, value):
        o_event = EventHandler(parent=self)
        o_event.data_range_changed()

    def prepare_data_data_range_clicked(self):
        o_event = EventHandler(parent=self)
        o_event.data_range_changed()

    def use_this_file_checkbox_clicked(self):
        o_event = EventHandler(parent=self)
        o_event.use_this_file_clicked()
        o_event.check_state_of_prepare_data_plot()
        o_event.update_list_of_relative_timestamp_of_prepared_data()
        o_event.update_list_of_original_image_files_to_use()

    # event handler - edge calculation tab
    def edge_calculation_calculate_pressed(self):
        o_event = EventHandler(parent=self)
        o_event.prepare_all_data()
        o_event.calculate_edge_position()
        o_event.check_status_of_edge_calculation_buttons()
        o_display = Display(parent=self)
        o_display.display_current_selected_profile_and_edge_position()
        o_display.display_all_edge_positions()

    def edge_calculation_file_index_slider_pressed(self):
        o_event = EventHandler(parent=self)
        o_event.edge_calculation_file_index_slider_changed()
        o_display = Display(parent=self)
        o_display.display_current_selected_profile_and_edge_position()
        o_display.display_all_edge_positions()

    def edge_calculation_file_index_slider_moved(self, value):
        o_event = EventHandler(parent=self)
        o_event.edge_calculation_file_index_slider_changed(value)
        o_display = Display(parent=self)
        o_display.display_current_selected_profile_and_edge_position()
        o_display.display_all_edge_positions()

    def edge_calculation_algorithms_changed(self):
        o_display = Display(parent=self)
        o_display.display_current_selected_profile_and_edge_position()
        o_display.display_all_edge_positions()

    def edge_calculation_algorithm_to_plot_changed(self):
        o_display = Display(parent=self)
        o_display.display_current_selected_profile_and_edge_position()
        o_display.display_all_edge_positions()

    def edge_calculation_export_button_pressed(self):
        o_export = Export(parent=self)
        o_export.run()
