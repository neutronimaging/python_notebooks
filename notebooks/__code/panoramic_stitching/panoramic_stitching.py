from IPython.core.display import display
from qtpy.QtWidgets import QMainWindow
import os
import inflect

from __code.ipywe import fileselector
from __code._utilities.folder import get_list_of_folders_with_specified_file_type_and_same_number_of_files
from __code._utilities.string import format_html_message
from __code import load_ui

from __code.panoramic_stitching.gui_initialization import GuiInitialization
from __code.panoramic_stitching.data_initialization import DataInitialization
from __code.panoramic_stitching.load_data import LoadData
from __code.panoramic_stitching.image_handler import ImageHandler
from __code.panoramic_stitching.event_handler import EventHandler
from __code.panoramic_stitching.profile import Profile
from __code.panoramic_stitching.automatically_stitch import AutomaticallyStitch
from __code.panoramic_stitching.export import Export
from __code.panoramic_stitching.image_handler import HORIZONTAL_MARGIN, VERTICAL_MARGIN
from __code.panoramic_stitching.remote_control_handler import RemoteControlHandler
from __code.panoramic_stitching.stitching_algorithms import StitchingAlgorithmType

SIMPLE_MANUAL_PIXEL_CHANGE = 1      # pixel
DOUBLE_MANUAL_PIXEL_CHANGE = 5      # pixel


class PanoramicStitching:

    def __init__(self, working_dir=''):
        self.working_dir = working_dir
        self.file_extension = ["tiff", "tif"]

    def select_input_folders(self):
        self.list_folder_widget = fileselector.FileSelectorPanel(instruction='select all the folders of images to '
                                                                             'stitch',
                                                                 start_dir=self.working_dir,
                                                                 type='directory',
                                                                 next=self.folder_selected,
                                                                 multiple=True)
        self.list_folder_widget.show()

    def folder_selected(self, folder_selected):
        final_list_folders, list_folders_rejected = \
            get_list_of_folders_with_specified_file_type_and_same_number_of_files(
                list_of_folders_to_check=folder_selected,
                file_extension=self.file_extension)

        if not final_list_folders:

            str_list_ext = ", ".join(self.file_extension)
            display(format_html_message(pre_message="None of the folder selected contains the file of extension "
                                                    "requested ({})".format(str_list_ext),
                                        spacer=""))
            return

        final_list_folders.sort()
        nbr_folder = len(final_list_folders)
        display(format_html_message(pre_message="Notebook is about to work with {} folders!".format(nbr_folder),
                                    spacer=""))

        # gui initialization
        o_interface = Interface(list_folders=final_list_folders,
                                list_folders_rejected=list_folders_rejected)
        o_interface.show()
        o_interface.load_data()
        o_interface.initialization_after_loading_data()


class Interface(QMainWindow):

    save_as_table_file_name = ""
    remote_control_id = None
    stitching_algorithm = StitchingAlgorithmType.minimum

    list_folders = None  # list of folders to work on

    # data_dictionary = {'folder_name1': {'file_name1': MetadataData},
    #                                     'file_name2': MetadataData,
    #                                     'file_name3': MetadataData,
    #                                    },
    #                    'folder_name2': {...},
    #                     ...,
    #                    }
    data_dictionary = None

    # offset_dictionary =  {'folder_name1': {'file_name1': {'xoffset': 0, 'yoffset': 0, 'visible': True},
    #                                        'file_name2': {'xoffset': 0, 'yoffset': 0, 'visible': True},
    #                                        'file_name3': {'xoffset': 0, 'yoffset': 0, 'visible', True},
    #                                       },
    #                       'folder_name2': {...},
    #                       ...,
    #                       }
    offset_dictionary = None
    offset_dictionary_for_reset = None

    # panoramic_images = {'folder_name1': [],
    #                     'folder_name2': [],
    #                     ... }
    panoramic_images = {}

    horizontal_profile_plot = None
    vertical_profile_plot = None

    histogram_level = None
    current_live_image = None

    image_width = None
    image_height = None
    contour_image_roi_id = None
    # from_to_roi_id = None
    from_label_id = None
    to_label_id = None
    from_to_roi = {'x0': 2000 + HORIZONTAL_MARGIN, 'y0': 50 + VERTICAL_MARGIN,
                   'x1': 50 + HORIZONTAL_MARGIN, 'y1': 50 + VERTICAL_MARGIN}

    # new implementation
    from_roi_id = None
    from_roi_cross_id = None
    to_roi_id = None
    to_roi_cross_id = None
    from_roi = {'x': 2000 + HORIZONTAL_MARGIN, 'y': 100 + VERTICAL_MARGIN}
    to_roi = {'x': 100 + HORIZONTAL_MARGIN, 'y': 50 + VERTICAL_MARGIN}

    width_profile = {'min': 1,
                     'max': 300,
                     'default': 10}

    horizontal_profile = {'id': None,
                          'x0': 500 + HORIZONTAL_MARGIN,
                          'y': 200 + VERTICAL_MARGIN,
                          'x1': 2500 + HORIZONTAL_MARGIN,
                          'width': width_profile['default']}
    vertical_profile = {'id': None,
                        'x': 300 + HORIZONTAL_MARGIN,
                        'y0': 70 + VERTICAL_MARGIN,
                        'y1': 2000 + VERTICAL_MARGIN,
                        'width': width_profile['default']}

    def __init__(self, parent=None, list_folders=None, list_folders_rejected=None):

        self.list_folders = list_folders

        display(format_html_message(pre_message="Check UI that popped up \
                    (maybe hidden behind this browser!)",
                                    spacer=""))
        super(Interface, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_panoramic_stitching_manual.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Semi-Automatic Panoramic Stitching")

        # gui initialization
        o_init = GuiInitialization(parent=self)
        o_init.before_loading_data()

        if list_folders_rejected:

            nbr_folders_rejected = len(list_folders_rejected)
            if nbr_folders_rejected == 1:
                have_string = " has"
            else:
                have_string = " have"
            p = inflect.engine()
            self.ui.statusbar.showMessage("{} ".format(nbr_folders_rejected) + p.plural("folder",
                                          nbr_folders_rejected) + have_string + " been rejected and not loaded!", 10000)
            self.ui.statusbar.setStyleSheet("color: red")

    def load_data(self):
        # load data and metadata

        self.ui.setEnabled(False)
        o_load = LoadData(parent=self,
                          list_folders=self.list_folders)
        o_load.run()

    def initialization_after_loading_data(self):
        o_init = DataInitialization(parent=self)
        o_init.offset_table()

        o_init = GuiInitialization(parent=self)
        o_init.after_loading_data()

        o_event = EventHandler(parent=self)
        o_event.check_status_of_from_to_checkbox()

        o_image = ImageHandler(parent=self)
        o_image.update_current_panoramic_image()
        o_image.update_contour_plot()

        self.ui.setEnabled(True)

    # event handler
    def remote_control_widget_pressed(self):
        EventHandler.button_pressed(ui=self.ui.remote_control_widget, name='remote_control')
        RemoteControlHandler(parent=self)

    def remote_control_widget_released(self):
        EventHandler.button_released(ui=self.ui.remote_control_widget, name='remote_control')

    def list_folder_combobox_value_changed(self, new_folder_selected=None):
        o_event = EventHandler(parent=self)
        o_event.list_folder_combobox_value_changed(new_folder_selected=new_folder_selected)

    def visibility_checkbox_changed(self, state=None, row=-1):
        o_event = EventHandler(parent=self)
        o_event.save_table_offset_of_this_cell(row=row, column=3, state=state)

        o_pano = ImageHandler(parent=self)
        o_pano.update_current_panoramic_image()

        self.horizontal_profile_changed()
        self.vertical_profile_changed()

    def table_of_offset_cell_changed(self, row, column):
        o_event = EventHandler(parent=self)
        o_event.save_table_offset_of_this_cell(row=row, column=column)
        o_event.update_remote_ui()

        o_pano = ImageHandler(parent=self)
        o_pano.update_current_panoramic_image()
        o_pano.update_contour_plot()

        self.horizontal_profile_changed()
        self.vertical_profile_changed()

    def table_of_offset_selection_changed(self):
        o_pano = ImageHandler(parent=self)
        o_pano.update_contour_plot()
        o_event = EventHandler(parent=self)
        o_event.check_status_of_from_to_checkbox()
        o_event.update_remote_ui()

    def from_to_checkbox_checked(self, state):
        o_event = EventHandler(parent=self)
        o_event.check_status_of_from_to_checkbox()

    def from_roi_box_changed(self):
        o_event = EventHandler(parent=self)
        o_event.from_roi_box_changed()

    def to_roi_box_changed(self):
        o_event = EventHandler(parent=self)
        o_event.to_roi_box_changed()

    def from_to_button_pushed(self):
        o_event = EventHandler(parent=self)
        o_event.from_to_button_pushed()
        self.horizontal_profile_changed()
        self.vertical_profile_changed()

    def enable_horizontal_profile_checked(self, state):
        o_event = EventHandler(parent=self)
        o_event.horizontal_profile(enabled=state)

    def horizontal_profile_changed(self):
        o_profile = Profile(parent=self)
        o_profile.horizontal_profile_changed()

    def horizontal_profile_slider_changed(self, new_value):
        o_event = EventHandler(parent=self)
        o_event.horizontal_slider_width_changed(width=new_value)

    def vertical_profile_slider_changed(self, new_value):
        o_event = EventHandler(parent=self)
        o_event.vertical_slider_width_changed(width=new_value)

    def vertical_profile_changed(self):
        o_profile = Profile(parent=self)
        o_profile.vertical_profile_changed()

    def enable_vertical_profile_checked(self, state):
        o_event = EventHandler(parent=self)
        o_event.vertical_profile(enabled=state)

    def left_left_button_pressed(self):
        EventHandler.button_pressed(ui=self.ui.left_left_button, name='left_left')
        o_event = EventHandler(parent=self)
        o_event.manual_offset_changed(direction='horizontal', nbr_pixel=-DOUBLE_MANUAL_PIXEL_CHANGE)
        self.horizontal_profile_changed()

    def left_left_button_released(self):
        EventHandler.button_released(ui=self.ui.left_left_button, name='left_left')

    def left_button_pressed(self):
        EventHandler.button_pressed(ui=self.ui.left_button, name='left')
        o_event = EventHandler(parent=self)
        o_event.manual_offset_changed(direction='horizontal', nbr_pixel=-SIMPLE_MANUAL_PIXEL_CHANGE)
        self.horizontal_profile_changed()

    def left_button_released(self):
        EventHandler.button_released(ui=self.ui.left_button, name='left')

    def right_right_button_pressed(self):
        EventHandler.button_pressed(ui=self.ui.right_right_button, name='right_right')
        o_event = EventHandler(parent=self)
        o_event.manual_offset_changed(direction='horizontal', nbr_pixel=DOUBLE_MANUAL_PIXEL_CHANGE)
        self.horizontal_profile_changed()

    def right_right_button_released(self):
        EventHandler.button_released(ui=self.ui.right_right_button, name='right_right')

    def right_button_pressed(self):
        EventHandler.button_pressed(ui=self.ui.right_button, name='right')
        o_event = EventHandler(parent=self)
        o_event.manual_offset_changed(direction='horizontal', nbr_pixel=SIMPLE_MANUAL_PIXEL_CHANGE)
        self.horizontal_profile_changed()

    def right_button_released(self):
        EventHandler.button_released(ui=self.ui.right_button, name='right')

    def up_up_button_pressed(self):
        EventHandler.button_pressed(ui=self.ui.up_up_button, name='up_up')
        o_event = EventHandler(parent=self)
        o_event.manual_offset_changed(direction='vertical', nbr_pixel=-DOUBLE_MANUAL_PIXEL_CHANGE)
        self.vertical_profile_changed()

    def up_up_button_released(self):
        EventHandler.button_released(ui=self.ui.up_up_button, name='up_up')

    def up_button_pressed(self):
        EventHandler.button_pressed(ui=self.ui.up_button, name='up')
        o_event = EventHandler(parent=self)
        o_event.manual_offset_changed(direction='vertical', nbr_pixel=-SIMPLE_MANUAL_PIXEL_CHANGE)
        self.vertical_profile_changed()

    def up_button_released(self):
        EventHandler.button_released(ui=self.ui.up_button, name='up')

    def down_down_button_pressed(self):
        EventHandler.button_pressed(ui=self.ui.down_down_button, name='down_down')
        o_event = EventHandler(parent=self)
        o_event.manual_offset_changed(direction='vertical', nbr_pixel=DOUBLE_MANUAL_PIXEL_CHANGE)
        self.vertical_profile_changed()

    def down_down_button_released(self):
        EventHandler.button_released(ui=self.ui.down_down_button, name='down_down')

    def down_button_pressed(self):
        EventHandler.button_pressed(ui=self.ui.down_button, name='down')
        o_event = EventHandler(parent=self)
        o_event.manual_offset_changed(direction='vertical', nbr_pixel=SIMPLE_MANUAL_PIXEL_CHANGE)
        self.vertical_profile_changed()

    def down_button_released(self):
        EventHandler.button_released(ui=self.ui.down_button, name='down')

    def table_right_clicked(self, position):
        o_event = EventHandler(parent=self)
        o_event.table_right_click()

    def automatically_stitch_all_other_images_button_clicked(self):
        o_auto = AutomaticallyStitch(parent=self)
        o_auto.run()

    def export_panoramic_images_button_clicked(self):
        o_export = Export(parent=self)
        o_export.run()

    def closeEvent(self, c):
        if self.remote_control_id:
            self.remote_control_id.close()

