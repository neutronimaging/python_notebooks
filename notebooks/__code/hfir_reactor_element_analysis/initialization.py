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

        self.parent.profiles_plot = _matplotlib(parent=self.parent,
                                           widget=self.parent.ui.profiles_widget)

        self.parent.elements_position = _matplotlib(parent=self.parent,
                                                   widget=self.parent.ui.elements_position_widget)

    def widgets(self):
        pandas_obj = self.parent.o_pandas

        list_of_images = self.parent.o_selection.column_labels[1:]
        self.parent.ui.listWidget.addItems(list_of_images)
        self.parent.ui.listWidget.setCurrentRow(0)

        self.parent.ui.splitter.setSizes([200, 500])

