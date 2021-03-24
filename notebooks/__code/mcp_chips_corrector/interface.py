from qtpy.QtWidgets import QMainWindow
from IPython.core.display import HTML
import os
import numpy as np
from IPython.display import display
import pyqtgraph as pg
from qtpy.QtWidgets import QProgressBar, QVBoxLayout

from __code import load_ui
from __code.mcp_chips_corrector.event_handler import EventHandler


class ImageSize:
    height = 0
    width = 0

    def __init__(self, width=0, height=0):
        self.width = width
        self.height = height


class Interface(QMainWindow):

    # pyqtgraph views and profile
    setup_image_view = None
    corrected_image_view = None
    profile_view = None

    # live images
    setup_live_image = None
    corrected_live_image = None

    # data
    integrated_data = None   # [512, 512]
    working_data = None       # [nbr_tof, 512, 512]

    # image size
    image_size = None

    # chip contour
    contour_id = None

    def __init__(self, parent=None, working_dir="", o_corrector=None):
        self.parent = parent
        self.working_dir = working_dir
        self.o_corrector = o_corrector

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that popped up \
            (maybe hidden behind this browser!)</span>'))

        super(Interface, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_mcp_chips_corrector.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("MCP Chips Corrector")

        o_init = Initialization(parent=self)
        o_init.run_all()

        self.display_setup_image()

    # Event handler
    def display_setup_image(self):
        o_event = EventHandler(parent=self)
        o_event.display_setup_image()

    def profile_type_changed(self):
        pass

    def chips_index_changed(self, new_index):
        o_event = EventHandler(parent=self)
        o_event.chips_index_changed()


class Initialization:
    """initialization of all the widgets such as pyqtgraph, progressbar..."""

    def __init__(self, parent=None):
        self.parent = parent

    def run_all(self):
        self.data()
        self.pyqtgraph()
        self.parent.chips_index_changed(0)

    def pyqtgraph(self):
        # setup
        self.parent.setup_image_view = pg.ImageView()
        self.parent.setup_image_view.ui.roiBtn.hide()
        self.parent.setup_image_view.ui.menuBtn.hide()
        setup_layout = QVBoxLayout()
        setup_layout.addWidget(self.parent.setup_image_view)
        self.parent.ui.setup_widget.setLayout(setup_layout)

        # with correction
        self.parent.corrected_image_view = pg.ImageView()
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

    def data(self):
        self.parent.integrated_data = self.parent.o_corrector.integrated_data
        self.parent.working_data = self.parent.o_corrector.working_data

        [height, width] = np.shape(self.parent.integrated_data)
        self.parent.image_size = ImageSize(width=width, height=height)