from IPython.core.display import display
from qtpy.QtWidgets import QMainWindow
import os
from collections import OrderedDict
import copy

from __code.ipywe import fileselector
from __code._utilities.folder import get_list_of_folders_with_specified_file_type
from __code._utilities.string import format_html_message
from __code._utilities.table_handler import TableHandler
from __code import load_ui

from __code.panoramic_stitching.gui_initialization import GuiInitialization
from __code.panoramic_stitching.data_initialization import DataInitialization
from __code.panoramic_stitching.load_data import LoadData
from __code.panoramic_stitching.panoramic_image import PanoramicImage
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

    # offset_dictionary =  {'folder_name1': {'file_name1': {'xoffset': 0, 'yoffset': 0},
    #                                        'file_name2': {'xoffset': 0, 'yoffset': 0},
    #                                        'file_name3': {'xoffset': 0, 'yoffset': 0},
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

        o_image = PanoramicImage(parent=self)
        o_image.update_current_panoramic_image()

    # event handler
    def list_folder_combobox_value_changed(self, new_folder_selected=None):
        if new_folder_selected is None:
            new_folder_selected = self.ui.list_folders_combobox.currentText()

        group_name = os.path.basename(new_folder_selected)
        group_offset_dictionary = self.offset_dictionary[group_name]

        list_files = list(self.data_dictionary[group_name].keys())
        list_files.sort()

        list_items = []
        for _file in list_files:
            offset_file_entry = group_offset_dictionary[_file]
            list_items.append([_file, offset_file_entry['xoffset'], offset_file_entry['yoffset']])

        o_table = TableHandler(table_ui=self.ui.tableWidget)
        o_table.fill_table_with(list_items=list_items,
                                editable_columns_boolean=[False, True, True],
                                block_signal=True)

    def table_of_offset_cell_changed(self, row, column):
        o_event = EventHandler(parent=self)
        o_event.save_table_offset_of_this_cell(row=row, column=column)

        o_pano = PanoramicImage(parent=self)
        o_pano.update_current_panoramic_image()
