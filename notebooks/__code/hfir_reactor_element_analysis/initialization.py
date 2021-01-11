from qtpy.QtWidgets import QVBoxLayout
from qtpy.QtCore import Slot as pyqtSlot
from PyQt5 import QtCore
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from __code.panoramic_stitching.mplcanvas import MplCanvas
from __code.widgets.qrangeslider import QRangeSlider


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

    def widgets(self):
        pandas_obj = self.parent.o_pandas
        nbr_angles = len(pandas_obj.index)
        self.parent.ui.to_angle_slider.setMaximum(nbr_angles-1)
        self.parent.ui.from_angle_slider.setMaximum(nbr_angles-20)
        self.parent.ui.to_angle_slider.setMinimum(20)
        self.parent.ui.to_angle_slider.setValue(nbr_angles-1)
        self.parent.ui.from_angle_slider.setValue(0)

        list_of_images = self.parent.o_selection.column_labels[1:]
        self.parent.ui.listWidget.addItems(list_of_images)
        self.parent.ui.listWidget.setCurrentRow(0)

        self.parent.ui.splitter.setSizes([500, 0])

        from_angle = self.parent.ui.from_angle_slider.value()
        self.parent.from_angle_slider_moved(from_angle)

        to_angle = self.parent.ui.to_angle_slider.value()
        self.parent.to_angle_slider_moved(to_angle)

    def fitting(self):
        self.parent.automatic_a_value_estimate()
        self.parent.automatic_b_value_estimate()
        self.parent.check_status_of_automatic_fit()

    # @QtCore.pyqtSlot(int)
    # def max_value_changed(self, value):
    #     print(f"value changed and is now {value}")