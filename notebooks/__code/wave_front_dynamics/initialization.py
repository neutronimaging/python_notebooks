import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from qtpy.QtWidgets import QVBoxLayout

from __code.panoramic_stitching.mplcanvas import MplCanvas
from __code._utilities.parent import Parent


class Initialization(Parent):

    def widgets(self):
        pass

    def matplotlib(self):

        def _matplotlib(parent=None, widget=None):
            sc = MplCanvas(parent, width=5, height=4, dpi=100)
            toolbar = NavigationToolbar(sc, parent)
            layout = QVBoxLayout()
            layout.addWidget(toolbar)
            layout.addWidget(sc)
            widget.setLayout(layout)
            return sc

        self.parent.prepare_data_plot = _matplotlib(parent=self.parent,
                                                    widget=self.parent.ui.prepare_data_widget)
        self.parent.recap_edges_plot = _matplotlib(parent=self.parent,
                                                   widget=self.parent.ui.recap_edges_widget)
        self.parent.calculated_edges_plot = _matplotlib(parent=self.parent,
                                                        widget=self.parent.ui.calculated_edges_widget)
