import pyqtgraph as pg
from pyqtgraph.dockarea import *
from qtpy.QtWidgets import QVBoxLayout, QTableWidgetItem, QLabel, QSpacerItem, QWidget, QHBoxLayout, QSizePolicy
import os
import numpy as np

from __code._utilities.table_handler import TableHandler


class Initialization:

    def __init__(self, parent=None):
        self.parent = parent

    def pyqtgraph(self):
        area = DockArea()
        area.setVisible(True)
        d1 = Dock("Raw", size=(200, 200))
        d1h = Dock("Raw Histogram", size=(200, 200))
        d2 = Dock("Gamma Filtered", size=(200, 200))
        d2h = Dock("Gamma Filtered Histogram", size=(200, 200))

        area.addDock(d1, 'left')
        area.addDock(d1h, 'left')
        area.moveDock(d1, 'above', d1h)
        area.addDock(d2, 'right', d1)
        area.addDock(d2h, 'right')
        area.moveDock(d2, 'above', d2h)

        # raw image
        self.parent.ui.raw_image_view = pg.ImageView(view=pg.PlotItem(), name='raw_image')
        self.parent.ui.raw_image_view.ui.roiBtn.hide()
        self.parent.ui.raw_image_view.ui.menuBtn.hide()
        self.parent.ui.raw_image_view.view.setAutoVisible(y=True)
        self.parent.raw_vLine = pg.InfiniteLine(angle=90, movable=False)
        self.parent.raw_hLine = pg.InfiniteLine(angle=0, movable=False)
        self.parent.ui.raw_image_view.addItem(self.parent.raw_vLine, ignoreBounds=True)
        self.parent.ui.raw_image_view.addItem(self.parent.raw_hLine, ignoreBounds=True)
        self.parent.raw_vLine.setPos([1000, 1000])
        self.parent.raw_hLine.setPos([1000, 1000])
        self.parent.raw_proxy = pg.SignalProxy(self.parent.ui.raw_image_view.view.scene().sigMouseMoved,
                                               rateLimit=60,
                                               slot=self.parent.mouse_moved_in_raw_image)
        d1.addWidget(self.parent.ui.raw_image_view)

        # raw histogram plot
        self.parent.ui.raw_histogram_plot = pg.PlotWidget()
        d1h.addWidget(self.parent.ui.raw_histogram_plot)

        # filtered image
        self.parent.ui.filtered_image_view = pg.ImageView(view=pg.PlotItem(), name='filtered_image')
        self.parent.ui.filtered_image_view.ui.roiBtn.hide()
        self.parent.ui.filtered_image_view.ui.menuBtn.hide()
        self.parent.filtered_vLine = pg.InfiniteLine(angle=90, movable=False)
        self.parent.filtered_hLine = pg.InfiniteLine(angle=0, movable=False)
        self.parent.ui.filtered_image_view.addItem(self.parent.filtered_vLine, ignoreBounds=True)
        self.parent.ui.filtered_image_view.addItem(self.parent.filtered_hLine, ignoreBounds=True)
        self.parent.filtered_vLine.setPos([1000, 1000])
        self.parent.filtered_hLine.setPos([1000, 1000])
        self.parent.filtered_proxy = pg.SignalProxy(self.parent.ui.filtered_image_view.view.scene().sigMouseMoved,
                                                    rateLimit=60,
                                                    slot=self.parent.mouse_moved_in_filtered_image)
        d2.addWidget(self.parent.ui.filtered_image_view)

        # filtered histogram plot
        self.parent.ui.filtered_histogram_plot = pg.PlotWidget()
        d2h.addWidget(self.parent.ui.filtered_histogram_plot)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(area)
        self.parent.ui.image_widget.setLayout(vertical_layout)

        # self.parent.ui.raw_image_view.view.getViewBox().setXLink('filtered_image')
        # self.parent.ui.raw_image_view.view.getViewBox().setYLink('filtered_image')

    def table(self):
        list_file = []
        for _row, _file in enumerate(self.parent.list_files):
            self.parent.ui.tableWidget.insertRow(_row)

            _short_file = os.path.basename(_file)
            list_file.append(_short_file)
            _item = QTableWidgetItem(_short_file)
            self.parent.ui.tableWidget.setItem(_row, 0, _item)

        # select first row
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        o_table.select_rows(list_of_rows=[0])

        self.parent.list_short_file_name = list_file

    def widgets(self):
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        o_table.set_column_width(column_width=self.parent.table_columns_size)

    def statusbar(self):
        _width_labels = 60
        _height_labels = 30

        # x0, y0, width and height of selection
        _x_label = QLabel("X:")
        self.parent.x_value = QLabel("N/A")
        self.parent.x_value.setFixedSize(_width_labels, _height_labels)
        _y_label = QLabel("Y:")
        self.parent.y_value = QLabel("N/A")
        self.parent.y_value.setFixedSize(_width_labels, _height_labels)
        raw_label = QLabel("  Counts Raw:")
        self.parent.raw_value = QLabel("N/A")
        self.parent.raw_value.setFixedSize(_width_labels, _height_labels)
        filtered_label = QLabel("  Counts Filtered:")
        self.parent.filtered_value = QLabel("N/A")
        self.parent.filtered_value.setFixedSize(_width_labels, _height_labels)

        hori_layout = QHBoxLayout()
        hori_layout.addWidget(_x_label)
        hori_layout.addWidget(self.parent.x_value)
        hori_layout.addWidget(_y_label)
        hori_layout.addWidget(self.parent.y_value)
        hori_layout.addWidget(raw_label)
        hori_layout.addWidget(self.parent.raw_value)
        hori_layout.addWidget(filtered_label)
        hori_layout.addWidget(self.parent.filtered_value)

        # spacer
        spacerItem = QSpacerItem(22520, 40, QSizePolicy.Expanding, QSizePolicy.Expanding)
        hori_layout.addItem(spacerItem)

        # add status bar in main ui
        bottom_widget = QWidget()
        bottom_widget.setLayout(hori_layout)
        self.parent.ui.statusbar.addPermanentWidget(bottom_widget)
