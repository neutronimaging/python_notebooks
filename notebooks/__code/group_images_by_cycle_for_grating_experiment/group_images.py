import os
from IPython.core.display import display
import numpy as np
import json
from collections import OrderedDict


from __code.ipywe import fileselector
from __code import file_handler
from __code._utilities.string import format_html_message
from __code.group_images_by_cycle_for_grating_experiment.group_images_by_cycle import GroupImagesByCycle
from __code.group_images_by_cycle_for_grating_experiment.get import Get
from .utilities import make_dictionary_of_groups_new_names
from __code.group_images_by_cycle_for_grating_experiment.notebook_widgets import NotebookWidgets
from __code.group_images_by_cycle_for_grating_experiment.combine_and_move_files import CombineAndMoveFiles

METADATA_ERROR = 1  # range +/- for which a metadata will be considered identical
THIS_FILE_PATH = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(THIS_FILE_PATH, 'config.json')
NEW_FILE_NAME_PREFIX = "image_"

DEBUG = False


class GroupImages:
    working_dir = ''
    data_path = ''
    metadata_key_to_select = None
    metadata_name_to_select = None

    # how_to_sort_within_cycle = {'1st_variable': {'name'        : '',
    #                                              'is_ascending': True},
    #                             '2nd_variable': {'name'        : '',
    #                                              'is_ascending': True},
    #                             }
    dictionary_of_groups_sorted = None

    def __init__(self, working_dir=''):
        self.working_dir = working_dir
        self.folder_selected = ''
        self.list_images = []
        self.file_extension = 'N/A'
        self.dict_of_metadata = {}  # key is 'tag->value' and value is 'tag'
        self.list_images_to_combine = None
        self.extension_to_regular_expression_dict = {'tiff': r"^\w*_(?P<run>run\d+)_\w*.tiff$",
                                                     'tif' : r"^\w*_(?P<run>run\d+)_\w*.tif$"}
        self.load_config()

    def load_config(self):
        with open(CONFIG_FILE) as f:
            config = json.load(f)
        self.config = config

    def select_input_folder(self):
        self.files_list_widget = fileselector.FileSelectorPanel(instruction='select images to sort ...',
                                                                start_dir=self.working_dir,
                                                                next=self.info_files_selected,
                                                                multiple=True)
        self.files_list_widget.show()

    def info_files_selected(self, selected):
        if not selected:
            return

        self.list_images = selected
        self.folder_selected = os.path.dirname(selected[0])
        self.data_path = os.path.dirname(self.list_images[0])
        self.record_file_extension(filename=self.list_images[0])

        selected = os.path.abspath(self.folder_selected)
        display(format_html_message('Input folder ', selected))
        display(format_html_message('Nbr files ', str(len(self.list_images))))
        if not ('tif' in self.file_extension):
            display(format_html_message('This notebook only works with TIFF images!', is_error=True))
            return

    def select_metadata_to_use_for_sorting(self):
        o_widgets = NotebookWidgets(parent=self)
        o_widgets.select_metadata_to_use_for_sorting()

    def record_file_extension(self, filename=''):
        self.file_extension = file_handler.get_file_extension(filename)

    def save_key_metadata(self):
        key_name_inner, key_name_outer = self.get_metadata_name_to_select()
        if (key_name_inner is None) or (key_name_outer is None):
            return

        key_inner, name_inner = key_name_inner.split(' -> ')
        key_outer, name_outer = key_name_outer.split(' -> ')

        self.metadata_name_to_select = [name_outer, name_inner]
        self.metadata_key_to_select = [int(key_outer), int(key_inner)]

    def get_metadata_name_to_select(self):
        metadata_inner = self.metadata_inner_selected_label.value
        metadata_outer = self.metadata_outer_selected_label.value

        try:
            key_name_inner, _ = metadata_inner.split(':')
            key_name_outer, _ = metadata_outer.split(':')
        except ValueError:
            return None, None

        return key_name_inner, key_name_outer

    def group_images(self):
        o_group = GroupImagesByCycle(list_of_files=self.list_images,
                                     list_of_metadata_key=self.metadata_key_to_select,
                                     tolerance_value=METADATA_ERROR)
        o_group.run()

        self.master_outer_inner_dictionary = o_group.master_outer_inner_dictionary
        self.dictionary_of_groups_sorted = self.format_into_dictionary_of_groups(self.master_outer_inner_dictionary)
        dict_new_names = make_dictionary_of_groups_new_names(self.dictionary_of_groups_sorted,
                                                             self.dict_group_outer_value)
        self.dictionary_of_groups_new_names = dict_new_names
        self.dictionary_file_vs_metadata = o_group.master_dictionary

    def format_into_dictionary_of_groups(self, master_outer_inner_dictionary):
        """
        format the dictionary
        dict = OrderedDict('value_outer_loop_1': {'value_inner_loop_1': ['file1'],
                                                  'value_inner_loop_2': ['file2', 'file3'],
                                                  'value_inner_loop_3': ['file4']},
                            'value_outer_loop_2': {'value_inner_loop_1': ['file5'],
                                                   'value_inner_loop_2': ['file6'],
                                                   ...,
                                                   },
                            )
        into

        dict = OrderedDict('0': {'value_inner_loop_1': ['file1'],
                                 'value_inner_loop_2': ['file2', 'file3'],
                                 'value_inner_loop_3': ['file4']},
                            '1': {'value_inner_loop_1': ['file5'],
                                  'value_inner_loop_2': ['file6'],
                                   ...,
                                 },
                            )

        this also creates a dictionary {'0': 'value_outer_loop_1',
                                        '1': 'value_outer_loop_2',
                                        }

        """
        list_key = master_outer_inner_dictionary.keys()
        groups_inner_dictionary = OrderedDict()

        dict_group_outer_value = OrderedDict()

        for _index, _key in enumerate(list_key):
            groups_inner_dictionary[_index] = master_outer_inner_dictionary[_key]
            dict_group_outer_value[_index] = _key

        self.dict_group_outer_value = dict_group_outer_value
        return groups_inner_dictionary

    def display_groups(self):
        o_widgets = NotebookWidgets(parent=self)
        o_widgets.display_groups()

    def _get_group_number_selected(self):
        group_string = self.select_group_ui.value
        _, group_number = group_string.split(" # ")
        return np.int(group_number)

    def select_output_folder(self):
        output_folder_widget = fileselector.FileSelectorPanel(instruction='select output folder',
                                                              start_dir=os.path.dirname(self.data_path),
                                                              type='directory',
                                                              next=self.copy_combine_and_rename_files,
                                                              multiple=False)
        output_folder_widget.show()

    def make_dictionary_of_groups_old_names(self):
        """
        this create and returns a dictionary that will look like
        {0: [[old_file1, old_file2], [old_file3], [old_file4]],
         1: [[old_file5], [old_file6], [old_file7], [old_file8]],
        ...
        }
        """
        dictionary_of_groups_old_names = OrderedDict()
        o_get = Get(parent=self)
        for _key in self.dictionary_of_groups_new_names.keys():
            list_files = o_get.list_of_old_files_fullname(index=_key)
            dictionary_of_groups_old_names[_key] = list_files

        return dictionary_of_groups_old_names

    def copy_combine_and_rename_files(self, output_folder):

        o_combine_and_move_files = CombineAndMoveFiles(parent=self,
                                                       output_folder=output_folder,
                                                       debug=DEBUG)
        o_combine_and_move_files.run()
