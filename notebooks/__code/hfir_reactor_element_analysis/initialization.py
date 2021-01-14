from qtpy.QtWidgets import QVBoxLayout, QProgressBar
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np

from __code.panoramic_stitching.mplcanvas import MplCanvas
from __code._utilities.array import get_n_random_int_of_max_value_m


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
        list_of_images = self.parent.o_selection.column_labels[1:]
        list_n_random_int = get_n_random_int_of_max_value_m(n=10, max=len(list_of_images))
        pandas_obj = self.parent.o_pandas
        list_max = []
        list_min = []
        for _file_index in list_n_random_int:
            _file = list_of_images[_file_index]
            _y_axis = np.array(pandas_obj[_file])
            list_max.append(np.nanmax(_y_axis))
            list_min.append(np.nanmin(_y_axis))

        global_max = np.int(np.nanmax(list_max))
        global_min = np.int(np.nanmin(list_min))

        self.parent.ui.high_threshold_slider.setMaximum(global_max)
        self.parent.ui.high_threshold_slider.setMinimum(global_min)
        self.parent.ui.low_threshold_slider.setMaximum(global_max)
        self.parent.ui.low_threshold_slider.setMinimum(global_min)

        delta_global = (global_max - global_min)/3
        self.parent.ui.high_threshold_slider.setValue(np.int(2*delta_global))
        self.parent.ui.low_threshold_slider.setValue(np.int(delta_global))

        self.parent.ui.listWidget.addItems(list_of_images)
        self.parent.ui.listWidget.setCurrentRow(0)

        self.parent.ui.splitter.setSizes([200, 500])

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)
