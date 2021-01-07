from qtpy.QtWidgets import QVBoxLayout
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
        file_range_slider = QRangeSlider()
        file_range_slider.setWindowTitle('example 1')
        file_range_slider.setRange(0, 10)
        file_range_slider.setMin(0)
        file_range_slider.setMax(len(self.parent.o_selection.column_labels))
        file_range_slider.setBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);')
        # file_range_slider.handle.setStyleSheet('background: url(data/sin.png) repeat-x; border: 0px;')
        file_range_slider.setSpanStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #282, stop:1 #393);')
        layout = QVBoxLayout()
        layout.addWidget(file_range_slider)
        self.parent.ui.file_range_widget.setLayout(layout)
        
        angle_range_slider = QRangeSlider()
        angle_range_slider.setWindowTitle('example 1')
        angle_range_slider.setRange(0, 10)
        angle_range_slider.setMin(0)
        angle_range_slider.setMax(100)
        angle_range_slider.setBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);')
        angle_range_slider.setSpanStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #282, stop:1 #393);')
        layout = QVBoxLayout()
        layout.addWidget(angle_range_slider)
        self.parent.ui.angle_range_widget.setLayout(layout)

        list_of_images = self.parent.o_selection.column_labels[1:]
        self.parent.ui.listWidget.addItems(list_of_images)
        self.parent.ui.listWidget.setCurrentRow(0)

        self.parent.ui.splitter.setSizes([500, 0])
