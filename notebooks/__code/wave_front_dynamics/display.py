from __code._utilities.parent import Parent
from __code.wave_front_dynamics.get import Get
from __code.wave_front_dynamics.algorithms import ListAlgorithm

from __code.wave_front_dynamics import algorithms_colors, algorithms_symbol


class Display(Parent):

    def display_current_selected_profile_and_edge_position(self):

        self.parent.ui.calculated_edges_plot.axes.clear()
        self.parent.ui.calculated_edges_plot.draw()

        o_get = Get(parent=self.parent)
        list_edge_calculation_algorithm = o_get.edge_calculation_algorithms_to_plot()
        if not list_edge_calculation_algorithm:
            return

        list_of_data_prepared = self.parent.list_of_data_prepared
        file_index_selected = o_get.edge_calculation_file_index_selected()

        data_to_plot = list_of_data_prepared[file_index_selected]
        self.parent.ui.calculated_edges_plot.axes.clear()
        self.parent.ui.calculated_edges_plot.axes.plot(data_to_plot)

        for edge_calculation_algorithm in list_edge_calculation_algorithm:

            peak_value_array = self.parent.peak_value_arrays[edge_calculation_algorithm]
            if peak_value_array is None:
                return

            color = algorithms_colors[edge_calculation_algorithm]

            peak_value_array = self.parent.peak_value_arrays[edge_calculation_algorithm]
            edge_position = peak_value_array[file_index_selected]
            self.parent.ui.calculated_edges_plot.axes.axvline(edge_position,
                                                              linestyle='--',
                                                              color=color)

        self.parent.ui.calculated_edges_plot.axes.set_xlabel("Pixel (relative position) ")
        self.parent.ui.calculated_edges_plot.axes.set_ylabel("Mean counts")
        self.parent.ui.calculated_edges_plot.draw()

    def display_all_edge_positions(self):
        self.parent.ui.recap_edges_plot.axes.clear()
        self.parent.ui.recap_edges_plot.draw()

        o_get = Get(parent=self.parent)
        edge_calculation_algorithm = o_get.edge_calculation_algorithms()
        peak_value_array = self.parent.peak_value_arrays[edge_calculation_algorithm]
        if peak_value_array is None:
            return

        file_index_selected = o_get.edge_calculation_file_index_selected()

        self.parent.ui.recap_edges_plot.axes.plot(peak_value_array, '*')
        self.parent.ui.recap_edges_plot.axes.plot(file_index_selected, peak_value_array[file_index_selected], 'r*')
        self.parent.ui.recap_edges_plot.axes.set_xlabel("File index")
        self.parent.ui.recap_edges_plot.axes.set_ylabel("Wave front position (relative pixel position)")
        self.parent.ui.recap_edges_plot.draw()
