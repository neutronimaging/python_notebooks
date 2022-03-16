import pyqtgraph as pg
from qtpy.QtWidgets import QHBoxLayout


class Initialization:

    def __init__(self, parent=None):
        self.parent = parent

    def pyqtgraph(self):
        # image view
        self.parent.ui.image_view = pg.ImageView()
        self.parent.ui.image_view.ui.menuBtn.hide()
        self.parent.ui.image_view.ui.roiBtn.hide()

        # default ROI
        self.parent.ui.roi = pg.ROI(
            [0, 0], [20, 20], pen=(62, 13, 244), scaleSnap=True)  # blue
        self.parent.ui.roi.addScaleHandle([1, 1], [0, 0])
        self.parent.ui.image_view.addItem(self.parent.ui.roi)
        self.parent.ui.roi.sigRegionChanged.connect(self.parent.roi_changed)

        hori_layout = QHBoxLayout()
        hori_layout.addWidget(self.parent.ui.image_view)
        self.parent.ui.widget.setLayout(hori_layout)

    def splitter(self):
        self.parent.ui.splitter.setSizes([500, 500])
