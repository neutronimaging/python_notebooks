import numpy as np
import pyqtgraph as pg
from qtpy.QtWidgets import QProgressBar, QVBoxLayout


class ImageSize:
    height = 0
    width = 0
    gap_index = 0

    def __init__(self, width=0, height=0):
        gap_index = np.int(height/2)
        self.gap_index = gap_index
        self.width = width
        self.height = height


class Initialization:
    """initialization of all the widgets such as pyqtgraph, progressbar..."""

    def __init__(self, parent=None):
        self.parent = parent

    def run_all(self):
        self.data()
        self.pyqtgraph()
        self.parent.chips_index_changed()
        self.splitter()
        self.parent.profile_type_changed()
        self.parent.profile_changed()
        self.widgets()
        self.statusbar()

    def pyqtgraph(self):
        # setup
        self.parent.setup_image_view = pg.ImageView()
        self.parent.setup_image_view.ui.roiBtn.hide()
        self.parent.setup_image_view.ui.menuBtn.hide()
        setup_layout = QVBoxLayout()
        setup_layout.addWidget(self.parent.setup_image_view)
        self.parent.ui.setup_widget.setLayout(setup_layout)

        # with correction
        self.parent.corrected_image_view = pg.ImageView(view=pg.PlotItem())
        self.parent.corrected_image_view.ui.roiBtn.hide()
        self.parent.corrected_image_view.ui.menuBtn.hide()
        correction_layout = QVBoxLayout()
        correction_layout.addWidget(self.parent.corrected_image_view)
        self.parent.ui.with_correction_widget.setLayout(correction_layout)

        # profile
        self.parent.profile_view = pg.PlotWidget(title="Profile")
        profile_layout = QVBoxLayout()
        profile_layout.addWidget(self.parent.profile_view)
        self.parent.ui.profile_widget.setLayout(profile_layout)

        # Alignment
        self.parent.alignment_before_view = pg.ImageView()
        self.parent.alignment_before_view.ui.roiBtn.hide()
        self.parent.alignment_before_view.ui.menuBtn.hide()
        setup_layout = QVBoxLayout()
        setup_layout.addWidget(self.parent.alignment_before_view)
        self.parent.ui.alignment_before_widget.setLayout(setup_layout)

        self.parent.alignment_after_view = pg.ImageView()
        self.parent.alignment_after_view.ui.roiBtn.hide()
        self.parent.alignment_after_view.ui.menuBtn.hide()
        setup_layout = QVBoxLayout()
        setup_layout.addWidget(self.parent.alignment_after_view)
        self.parent.ui.alignment_after_widget.setLayout(setup_layout)

    def data(self):
        self.parent.integrated_data = self.parent.o_corrector.integrated_data
        self.parent.working_data = self.parent.o_corrector.working_data
        self.parent.working_list_files = self.parent.o_corrector.working_list_files

        [height, width] = np.shape(self.parent.integrated_data)
        self.parent.image_size = ImageSize(width=width, height=height)

    def splitter(self):
        self.parent.ui.splitter.setSizes([1, 1])
        self.parent.ui.splitter_2.setSizes([200, 1])

    def widgets(self):
        self.parent.ui.reset_pushButton.setVisible(False)

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)
