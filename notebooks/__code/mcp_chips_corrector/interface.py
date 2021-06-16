from qtpy.QtWidgets import QMainWindow
from IPython.core.display import HTML
import os
from IPython.display import display

from __code import load_ui
from __code.mcp_chips_corrector.event_handler import EventHandler
from __code.mcp_chips_corrector.initialization import Initialization


class Interface(QMainWindow):

    # pyqtgraph views and profile
    setup_image_view = None
    corrected_image_view = None
    profile_view = None
    alignment_before_view = None
    alignment_after_view = None

    # live images
    setup_live_image = None
    corrected_live_image = None
    corrected_histogram_level = None

    # data
    integrated_data = None   # [512, 512]
    working_data = None       # [nbr_tof, 512, 512]

    # image size
    image_size = None

    # chip contour
    contour_id = None

    # profile ROI
    profile = {'horizontal': {'x0': 150, 'y0': 150, 'width': 100, 'height': 10},
               'vertical': {'x0': 150, 'y0': 150, 'width': 10, 'height': 100},
               }
    profile_id = None

    nbr_pixels_to_exclude_on_each_side_of_chips_gap = 3

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
        o_event = EventHandler(parent=self)
        o_event.profile_type_changed()
        o_event.plot_profile()
        o_event.calculate_coefficient_corrector()
        o_event.with_correction_tab()
        o_event.plot_mean()

    def chips_index_changed(self):
        o_event = EventHandler(parent=self)
        o_event.chips_index_changed()
        o_event.plot_profile()
        o_event.calculate_coefficient_corrector()
        o_event.with_correction_tab()
        o_event.plot_mean()

    def profile_changed(self):
        o_event = EventHandler(parent=self)
        o_event.profile_changed()
        o_event.plot_profile()
        o_event.calculate_coefficient_corrector()
        o_event.with_correction_tab()
        o_event.plot_mean()

    def coefficient_corrector_manually_changed(self):
        self.ui.reset_pushButton.setVisible(True)
        o_event = EventHandler(parent=self)
        o_event.with_correction_tab()

    def reset_button_pushed(self):
        self.ui.reset_pushButton.setVisible(False)
        o_event = EventHandler(parent=self)
        o_event.profile_changed()
        o_event.plot_profile()
        o_event.calculate_coefficient_corrector()
        o_event.with_correction_tab()
        o_event.plot_mean()

    def correct_all_images_pushed(self):
        o_event = EventHandler(parent=self)
        o_event.correct_all_images()
