from IPython.core.display import display
from qtpy.QtWidgets import QMainWindow, QHBoxLayout, QCheckBox, QSpacerItem, QSizePolicy, QWidget
from qtpy import QtCore
import os

from __code.ipywe import fileselector
from __code._utilities.folder import get_list_of_folders_with_specified_file_type
from __code._utilities.string import format_html_message
from __code._utilities.table_handler import TableHandler
from __code import load_ui

from __code.panoramic_stitching.gui_initialization import GuiInitialization
from __code.panoramic_stitching.data_initialization import DataInitialization
from __code.panoramic_stitching.load_data import LoadData
from __code.panoramic_stitching.image_handler import ImageHandler
from __code.panoramic_stitching.event_handler import EventHandler


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
        final_list_folders = get_list_of_folders_with_specified_file_type(list_of_folders_to_check=folder_selected,
                                                                          file_extension=self.file_extension)
        if not final_list_folders:

            str_list_ext = ", ".join(self.file_extension)
            display(format_html_message(pre_message="None of the folder selected contains the file of extension "
                                                    "requested ({}}".format(str_list_ext),
                                        spacer=""))
            return

        final_list_folders.sort()
        nbr_folder = len(final_list_folders)
        display(format_html_message(pre_message="Notebook is about to work with {} folders!".format(nbr_folder),
                                    spacer=""))

        # gui initialization
        o_interface = Interface(working_dir=self.working_dir, list_folders=final_list_folders)
        o_interface.show()
        o_interface.load_data()


class Interface(QMainWindow):

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
    from_to_roi_id = None
    from_label_id = None
    to_label_id = None
    from_to_roi = {'x0': 2000, 'y0': 50, 'x1': 50, 'y1': 50}

    # new implementation
    from_roi_id = None
    from_roi_cross_id = None
    to_roi_id = None
    to_roi_cross_id = None
    from_roi = {'x': 2000, 'y': 100}
    to_roi = {'x': 100, 'y': 50}

    def __init__(self, parent=None, working_dir=None, list_folders=None):

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

    def load_data(self):
        # load data and metadata
        o_load = LoadData(parent=self,
                          list_folders=self.list_folders)
        o_load.run()

    def initialization_after_loading_data(self):
        o_init = DataInitialization(parent=self)
        o_init.offset_table()

        o_init = GuiInitialization(parent=self)
        o_init.after_loading_data()

        o_image = ImageHandler(parent=self)
        o_image.update_current_panoramic_image()

    # event handler
    def list_folder_combobox_value_changed(self, new_folder_selected=None):
        o_event = EventHandler(parent=self)
        o_event.list_folder_combobox_value_changed(new_folder_selected=new_folder_selected)

    def visibility_checkbox_changed(self, state=None, row=-1):
        o_event = EventHandler(parent=self)
        o_event.save_table_offset_of_this_cell(row=row, column=3, state=state)

        o_pano = ImageHandler(parent=self)
        o_pano.update_current_panoramic_image()

    def table_of_offset_cell_changed(self, row, column):
        o_event = EventHandler(parent=self)
        o_event.save_table_offset_of_this_cell(row=row, column=column)

        o_pano = ImageHandler(parent=self)
        o_pano.update_current_panoramic_image()
        o_pano.update_contour_plot()

    def table_of_offset_selection_changed(self):
        o_pano = ImageHandler(parent=self)
        o_pano.update_contour_plot()

    def from_to_checkbox_checked(self, state):
        o_event = EventHandler(parent=self)
        o_event.from_to_checkbox_changed(state=state)

    def from_roi_box_changed(self):
        o_event = EventHandler(parent=self)
        o_event.from_roi_box_changed()

    def to_roi_box_changed(self):
        o_event = EventHandler(parent=self)
        o_event.to_roi_box_changed()
