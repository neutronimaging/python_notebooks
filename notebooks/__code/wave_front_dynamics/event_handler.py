from qtpy import QtGui

from __code._utilities.parent import Parent
from __code._utilities.status_message import StatusMessageStatus, show_status_message
from __code.wave_front_dynamics.get import Get
from __code.wave_front_dynamics.algorithms import Algorithms, ListAlgorithm
from __code.wave_front_dynamics.display import Display


class EventHandler(Parent):

    def data_range_changed(self):
        min_range = self.parent.ui.left_range_slider.value()
        max_range = self.parent.ui.right_range_slider.value()
        self.parent.data_range['min'] = min_range
        self.parent.data_range['max'] = max_range

        o_display = Display(parent=self.parent)
        o_display.update_prepare_data_plot()

    def prepare_all_data(self):
        list_of_data = self.parent.list_of_data
        o_get = Get(parent=self.parent)
        bin_size = o_get.prepare_data_bin_size()
        bin_type = o_get.prepare_data_bin_type()

        self.parent.event_progress.setMaximum(len(list_of_data))
        self.parent.event_progress.setValue(0)
        self.parent.event_progress.setVisible(True)
        QtGui.QGuiApplication.processEvents()

        list_of_data_prepared = []
        for _index, _data in enumerate(list_of_data):
            _data = o_get.working_range_of_data(data=_data)
            prepared_data = Algorithms.bin_data(data=_data, bin_size=bin_size, bin_type=bin_type)
            list_of_data_prepared.append(prepared_data)
            self.parent.event_progress.setValue(_index + 1)
            QtGui.QGuiApplication.processEvents()

        self.parent.list_of_data_prepared = list_of_data_prepared
        self.parent.event_progress.setVisible(False)
        QtGui.QGuiApplication.processEvents()

    def prepare_data_file_index_slider_changed(self, slider_value=None):
        if slider_value is None:
            slider_value = self.parent.ui.file_index_horizontalSlider.value()

        self.parent.ui.file_index_value_label.setText(str(slider_value))

    def prepare_data_bin_size_changed(self, slider_value=None):
        if slider_value is None:
            slider_value = self.parent.ui.bin_value_horizontalSlider.value()

        self.parent.ui.bin_value_label.setText(str(slider_value))

    def calculate_edge_position(self):
        o_get = Get(parent=self.parent)
        edge_calculation_algorithm = o_get.edge_calculation_algorithms()

        if edge_calculation_algorithm == ListAlgorithm.all:

            o_display = Display(parent=self.parent)
            o_display.clear_plots()
            self.reset_peak_value_arrays()

            list_algo = [ListAlgorithm.sliding_average,
                         ListAlgorithm.error_function,
                         ListAlgorithm.change_point]
            for _algo in list_algo:
                self.running_algo(algorithm=_algo)
                self.check_status_of_edge_calculation_checkboxes()
                o_display.display_current_selected_profile_and_edge_position()
                o_display.display_all_edge_positions()
        else:
            self.running_algo(algorithm=edge_calculation_algorithm)

    def running_algo(self, algorithm=None):
        list_of_data_prepared = self.parent.list_of_data_prepared

        show_status_message(parent=self.parent,
                            message=f"Running {algorithm} ...",
                            status=StatusMessageStatus.working)

        o_algo = Algorithms(list_data=list_of_data_prepared,
                            ignore_first_dataset=False,
                            algorithm_selected=algorithm,
                            progress_bar_ui=self.parent.event_progress)
        self.parent.peak_value_arrays[algorithm] = \
            o_algo.get_peak_value_array(algorithm_selected=algorithm)
        self.parent.data_have_been_reversed_in_calculation = o_algo.data_have_been_reversed_in_calculation

        show_status_message(parent=self.parent,
                            message=f"Running {algorithm}: Done",
                            status=StatusMessageStatus.ready,
                            duration_s=10)

    def edge_calculation_file_index_slider_changed(self, slider_value=None):
        if slider_value is None:
            slider_value = self.parent.ui.edge_calculation_file_index_slider.value()

        self.parent.ui.edge_calculation_file_index_value.setText(str(slider_value))

    def check_status_of_edge_calculation_checkboxes(self):
        enable_sliding_average_button = True
        enable_change_point_button = True
        enable_error_function_button = True
        if self.parent.peak_value_arrays[ListAlgorithm.sliding_average] is None:
            enable_sliding_average_button = False
        if self.parent.peak_value_arrays[ListAlgorithm.change_point] is None:
            enable_change_point_button = False
        if self.parent.peak_value_arrays[ListAlgorithm.error_function] is None:
            enable_error_function_button = False

        self.parent.ui.plot_edge_calculation_sliding_average.setEnabled(enable_sliding_average_button)
        self.parent.ui.plot_edge_calculation_error_function.setEnabled(enable_error_function_button)
        self.parent.ui.plot_edge_calculation_change_point.setEnabled(enable_change_point_button)

        if enable_sliding_average_button:
            self.parent.ui.plot_edge_calculation_sliding_average.setChecked(True)
        if enable_change_point_button:
            self.parent.ui.plot_edge_calculation_change_point.setChecked(True)
        if enable_error_function_button:
            self.parent.ui.plot_edge_calculation_error_function.setChecked(True)

    def reset_peak_value_arrays(self):
        self.parent.peak_value_arrays = {ListAlgorithm.sliding_average: None,
                                         ListAlgorithm.change_point: None,
                                         ListAlgorithm.error_function: None}

    def check_status_of_export_button(self):
        enabled_state = False
        for _key in self.parent.peak_value_arrays.keys():
            value = self.parent.peak_value_arrays[_key]
            if not (value is None):
                enabled_state = True
                break
        self.parent.ui.export_button.setEnabled(enabled_state)
