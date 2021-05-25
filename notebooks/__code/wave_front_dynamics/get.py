from __code._utilities.parent import Parent
from __code.wave_front_dynamics.algorithms import ListAlgorithm


class Get(Parent):

    def prepare_data_bin_size(self):
        return self.parent.ui.bin_value_horizontalSlider.value()

    def prepare_data_file_index(self):
        return self.parent.ui.file_index_horizontalSlider.value()

    def prepare_data_bin_type(self):
        if self.parent.ui.prepare_data_bin_type_mean.isChecked():
            return 'mean'
        elif self.parent.ui.prepare_data_bin_type_median.isChecked():
            return 'median'
        else:
            raise NotImplementedError("data bin type not implemented!")

    def edge_calculation_algorithms(self):
        if self.parent.ui.edge_calculation_sliding_average.isChecked():
            return ListAlgorithm.sliding_average
        elif self.parent.ui.edge_calculation_error_function.isChecked():
            return ListAlgorithm.error_function
        elif self.parent.ui.edge_calculation_change_point.isChecked():
            return ListAlgorithm.change_point
        elif self.parent.ui.edge_calculation_all.isChecked():
            return ListAlgorithm.all
        else:
            raise NotImplementedError("edge calculation algorithms not implemented yet!")

    def edge_calculation_file_index_selected(self):
        return self.parent.ui.edge_calculation_file_index_slider.value()

    def edge_calculation_algorithms_to_plot(self):
        to_plot = []
        if self.parent.ui.plot_edge_calculation_sliding_average.isChecked():
            to_plot.append(ListAlgorithm.sliding_average)
        if self.parent.ui.plot_edge_calculation_error_function.isChecked():
            to_plot.append(ListAlgorithm.error_function)
        if self.parent.ui.plot_edge_calculation_change_point.isChecked():
            to_plot.append(ListAlgorithm.change_point)
        return to_plot
