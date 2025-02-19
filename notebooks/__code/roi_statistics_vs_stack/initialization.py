import pyqtgraph as pg
from qtpy.QtWidgets import QProgressBar
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout
import numpy as np
import os
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from __code._utilities.table_handler import TableHandler
from __code.roi_statistics_vs_stack import StatisticsColumnIndex
from __code.__all.mplcanvas import MplCanvas


class Initialization:

    def __init__(self, parent=None):
        self.parent = parent

    def all(self):
        self.pyqtgraph()
        self.splitter()
        self.widgets()
        self.statusbar()
        self.matplotlib()

    def pyqtgraph(self):
        # image view
        self.parent.ui.image_view = pg.ImageView(view=pg.PlotItem())
        self.parent.ui.image_view.ui.menuBtn.hide()
        self.parent.ui.image_view.ui.roiBtn.hide()

        # default ROI
        roi = self.parent.roi_dict
        x0 = roi['x0']
        y0 = roi['y0']
        width = roi['width']
        height = roi['height']
        self.parent.ui.roi = pg.ROI(
            [x0, y0], [width, height], pen=(62, 13, 244), scaleSnap=True)  # blue
        self.parent.ui.roi.addScaleHandle([1, 1], [0, 0])
        self.parent.ui.image_view.addItem(self.parent.ui.roi)
        self.parent.ui.roi.sigRegionChanged.connect(self.parent.roi_changed)

        hori_layout = QHBoxLayout()
        hori_layout.addWidget(self.parent.ui.image_view)
        self.parent.ui.widget.setLayout(hori_layout)

    def splitter(self):
        self.parent.ui.splitter.setSizes([500, 500])

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(540, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)

    def widgets(self):
        self.parent.ui.horizontalSlider.setMaximum(len(self.parent.list_of_images)-1)

    def table(self):
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        for _row in np.arange(len(self.parent.list_of_images)):
            o_table.insert_empty_row(_row)
            short_file_name = os.path.basename(self.parent.list_of_images[_row])
            o_table.insert_item(row=_row,
                                column=StatisticsColumnIndex.file_name,
                                value=short_file_name,
                                editable=False)
            o_table.insert_item(row=_row,
                                column=StatisticsColumnIndex.time_offset,
                                value=self.parent.data_dict[_row]['time_offset'],
                                format_str="{:.2f}",
                                editable=False)

            list_column_index = [StatisticsColumnIndex.min, StatisticsColumnIndex.max,
                                 StatisticsColumnIndex.mean, StatisticsColumnIndex.median,
                                 StatisticsColumnIndex.std]
            for _col in list_column_index:
                o_table.insert_item(row=_row,
                                    column=_col,
                                    value="N/A",
                                    editable=False)

        o_table.set_column_width(column_width=[350, 100, 70, 70, 70, 70, 70])

    def matplotlib(self):
        def _matplotlib(parent=None, widget=None):
            sc = MplCanvas(parent, width=5, height=2, dpi=100)
            # sc.axes.plot([0,1,2,3,4,5], [10, 1, 20 ,3, 40, 50])
            toolbar = NavigationToolbar(sc, parent)
            layout = QVBoxLayout()
            layout.addWidget(toolbar)
            layout.addWidget(sc)
            widget.setLayout(layout)
            return sc

        self.parent.statistics_plot = _matplotlib(parent=self.parent,
                                                  widget=self.parent.ui.plot_widget)
