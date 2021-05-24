import numpy as np
import copy
import time
from qtpy import QtGui

from __code._utilities.parent import Parent
from __code.wave_front_dynamics.get import Get
from __code.wave_front_dynamics.algorithms import Algorithms, ListAlgorithm


class EventHandler(Parent):

    def update_prepare_data_plot(self):
        self.parent.ui.prepare_data_plot.axes.clear()
        o_get = Get(parent=self.parent)
        bin_size = o_get.prepare_data_bin_size()
        bin_type = o_get.prepare_data_bin_type()
        file_index = o_get.prepare_data_file_index()

        data = copy.deepcopy(self.parent.list_of_data[file_index])
        new_data = Algorithms.bin_data(data=data, bin_size=bin_size, bin_type=bin_type)

        self.parent.ui.prepare_data_plot.axes.plot(new_data)
        self.parent.ui.prepare_data_plot.draw()

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
        list_of_data_prepared = self.parent.list_of_data_prepared

        self.parent.event_progress.setMaximum(len(list_of_data_prepared))
        self.parent.event_progress.setValue(0)
        self.parent.event_progress.setVisible(True)
        QtGui.QGuiApplication.processEvents()

        o_algo = Algorithms(list_data=list_of_data_prepared,
                            ignore_first_dataset=False,
                            algorithm_selected=edge_calculation_algorithm,
                            progress_bar_ui=self.parent.event_progress)
        self.parent.peak_value_arrays[edge_calculation_algorithm] = \
            o_algo.get_peak_value_array(algorithm_selected=edge_calculation_algorithm)
        self.parent.data_have_been_reversed_in_calculation = o_algo.data_have_been_reversed_in_calculation

    def edge_calculation_file_index_slider_changed(self, slider_value=None):
        if slider_value is None:
            slider_value = self.parent.ui.edge_calculation_file_index_slider.value()

        self.parent.ui.edge_calculation_file_index_value.setText(str(slider_value))
