import numpy as np
import copy

from __code._utilities.parent import Parent
from __code.wave_front_dynamics.get import Get
from __code.wave_front_dynamics.algorithms import Algorithms


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

    def prepare_data_file_index_slider_changed(self, slider_value=None):
        if slider_value is None:
            slider_value = self.parent.ui.file_index_horizontalSlider.value()

        self.parent.ui.file_index_value_label.setText(str(slider_value))

    def prepare_data_bin_size_changed(self, slider_value=None):
        if slider_value is None:
            slider_value = self.parent.ui.bin_value_horizontalSlider.value()

        self.parent.ui.bin_value_label.setText(str(slider_value))
