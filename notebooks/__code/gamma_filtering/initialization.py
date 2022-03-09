import pyqtgraph as pg
from pyqtgraph.dockarea import *
from qtpy import QtGui


class Initialization:

    def __init__(self, parent=None):
        self.parent = parent

    def init_pyqtgraph(self):
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

        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(area)
        self.parent.ui.image_widget.setLayout(vertical_layout)

        self.parent.ui.raw_image_view.view.getViewBox().setXLink('filtered_image')
        self.parent.ui.raw_image_view.view.getViewBox().setYLink('filtered_image')

        