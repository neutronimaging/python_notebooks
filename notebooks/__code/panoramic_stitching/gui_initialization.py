import pyqtgraph as pg
from qtpy.QtWidgets import QVBoxLayout


class GuiInitialization:

    def __init__(self, parent=None):
        self.parent = parent

    def run_all(self):
        self.splitter()
        self.pyqtgraph()

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
