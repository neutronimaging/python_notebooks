from qtpy.QtWidgets import QVBoxLayout
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from __code.panoramic_stitching.mplcanvas import MplCanvas


class Initialization:

    def __init__(self, parent=None):
        self.parent = parent

    def matplotlib(self):
        def _matplotlib(parent=None, widget=None):
            sc = MplCanvas(parent, width=5, height=4, dpi=100)
            # sc.axes.plot([0,1,2,3,4,5], [10, 1, 20 ,3, 40, 50])
            toolbar = NavigationToolbar(sc, parent)
            layout = QVBoxLayout()
            layout.addWidget(toolbar)
            layout.addWidget(sc)
            widget.setLayout(layout)
            return sc

        self.parent.top_plot = _matplotlib(parent=self.parent,
                                           widget=self.parent.ui.top_widget)

        self.parent.bottom_plot = _matplotlib(parent=self.parent,
                                              widget=self.parent.ui.bottom_widget)
