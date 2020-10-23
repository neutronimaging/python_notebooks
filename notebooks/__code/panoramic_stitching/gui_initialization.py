import pyqtgraph as pg
from qtpy.QtWidgets import QVBoxLayout
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from __code.panoramic_stitching.mplcanvas import MplCanvas


class GuiInitialization:

    def __init__(self, parent=None):
        self.parent = parent

    def run_all(self):
        self.splitter()
        self.pyqtgraph()
        self.matplotlib()

    def splitter(self):
        self.parent.ui.profile_display_splitter.setSizes([500, 500])
        self.parent.ui.display_splitter.setSizes([200, 100])
        self.parent.ui.full_splitter.setSizes([400, 100])

    def pyqtgraph(self):
        self.parent.ui.image_view = pg.ImageView()
        self.parent.ui.image_view.ui.roiBtn.hide()
        self.parent.ui.image_view.ui.menuBtn.hide()
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.parent.ui.image_view)
        self.parent.ui.stitched_widget.setLayout(image_layout)

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

        self.parent.horizontal_profile_plot = _matplotlib(parent=self.parent,
                                                          widget=self.parent.ui.horizontal_profile_plot_widget)
        self.parent.kropff_low_plot = _matplotlib(parent=self.parent,
                                                  widget=self.parent.ui.vertical_profile_plot_widget)
