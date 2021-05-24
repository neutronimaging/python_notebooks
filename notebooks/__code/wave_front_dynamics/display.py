from __code._utilities.parent import Parent
from __code.wave_front_dynamics.get import Get


class Display(Parent):

    def display_edge_position(self):
        o_get = Get(parent=self.parent)
        edge_calculation_algorithm = o_get.edge_calculation_algorithms()
        park_value_array = self.parent.peak_value_arrays[edge_calculation_algorithm]

        self.parent.ui.recap_edges_plot.axes.clear()
        self.parent.ui.recap_edges_plot.axes.plot(park_value_array, '*')
        self.parent.ui.recap_edges_plot.axes.set_xlabel("File index")
        self.parent.ui.recap_edges_plot.axes.set_ylabel("Wave front position (relative pixel position)")
        self.parent.ui.recap_edges_plot.draw()
