from qtpy.QtWidgets import QMainWindow
from IPython.core.display import HTML
import os
from IPython.display import display
import logging

from __code import load_ui
from __code.mcp_chips_corrector.event_handler import EventHandler
from __code.mcp_chips_corrector.initialization import Initialization
from __code.mcp_chips_corrector.get import Get
from __code.mcp_chips_corrector.export import Export


class Interface(QMainWindow):

    # pyqtgraph views and profile
    setup_image_view = None
    corrected_image_view = None
    profile_view = None
    alignment_view = None

    # histogram
    alignment_view_histogram_level = None

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

        o_get = Get(parent=self)
        log_file_name = o_get.log_file_name()
        logging.basicConfig(filename=log_file_name,
                            filemode='w',
                            format='[%(levelname)s] - %(asctime)s - %(message)s',
                            level=logging.INFO)   # logging.INFO, logging.DEBUG
        logging.info("*** Starting new session ***")

        o_init = Initialization(parent=self)
        o_init.run_all()

        self.display_setup_image()

    # Event handler

    # contrast
    def apply_contrast_correction_clicked(self):
        self.check_export_button_status()

    def display_setup_image(self):
        o_event = EventHandler(parent=self)
        o_event.display_setup_image()
        o_event.mcp_alignment_correction()

    def profile_type_changed(self):
        o_event = EventHandler(parent=self)
        o_event.profile_type_changed()
        o_event.plot_profile()
        o_event.calculate_coefficient_corrector()
        o_event.with_correction_tab()
        o_event.plot_mean()
        self.check_export_button_status()

    def chips_index_changed(self):
        o_event = EventHandler(parent=self)
        o_event.chips_index_changed()
        o_event.plot_profile()
        o_event.calculate_coefficient_corrector()
        o_event.with_correction_tab()
        o_event.plot_mean()
        self.check_export_button_status()

    def profile_changed(self):
        o_event = EventHandler(parent=self)
        o_event.profile_changed()
        o_event.plot_profile()
        o_event.calculate_coefficient_corrector()
        o_event.with_correction_tab()
        o_event.plot_mean()
        self.check_export_button_status()

    def coefficient_corrector_manually_changed(self):
        self.ui.reset_pushButton.setVisible(True)
        o_event = EventHandler(parent=self)
        o_event.with_correction_tab()
        self.check_export_button_status()

    def reset_button_pushed(self):
        self.ui.reset_pushButton.setVisible(False)
        o_event = EventHandler(parent=self)
        o_event.profile_changed()
        o_event.plot_profile()
        o_event.calculate_coefficient_corrector()
        o_event.with_correction_tab()
        o_event.plot_mean()
        self.check_export_button_status()

    # Alignment
    def chips_alignment_clicked(self):
        o_event = EventHandler(parent=self)
        o_event.mcp_alignment_correction()
        o_event.check_auto_fill_checkBox_widget()

    # result
    def main_tab_changed(self, tab_index):
        if tab_index == 2:
            o_event = EventHandler(parent=self)
            o_event.update_result_tab()

    # general
    def check_export_button_status(self):
        o_event = EventHandler(parent=self)
        o_event.check_export_button_status()

    def correct_all_images_pushed(self):
        o_export = Export(parent=self)
        o_export.correct_all_images()
