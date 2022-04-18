import os
from ipywidgets import widgets
from IPython.core.display import display, HTML
import numpy as np
import json
from collections import OrderedDict
import shutil

from __code.ipywe import fileselector
from __code import file_handler
from __code._utilities.string import format_html_message
from __code.group_images_by_cycle_for_grating_experiment.group_images_by_cycle import GroupImagesByCycle
from __code.group_images_by_cycle_for_grating_experiment.sort_images_within_each_cycle import SortImagesWithinEachCycle
from __code.file_handler import make_or_reset_folder, copy_and_rename_files_to_folder, get_file_extension
from __code._utilities.metadata_handler import MetadataHandler

METADATA_ERROR = 1  # range +/- for which a metadata will be considered identical
THIS_FILE_PATH = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(THIS_FILE_PATH, 'config.json')
NEW_FILE_NAME_PREFIX = "image_"


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
                                                     'tif': r"^\w*_(?P<run>run\d+)_\w*.tif$"}
        self.load_config()

    def load_config(self):
        with open(CONFIG_FILE) as f:
            config = json.load(f)
        self.config = config

        # self.metadata_key_to_select = []
        # self.metadata_name_to_select = []
        # for key in config.keys():
        #     self.metadata_key_to_select.append(config[key]['key'])
        #     self.metadata_name_to_select.append(config[key]['name'])

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

    def get_default_metadata_selected(self):
        config = self.config
        list_metadata = self.list_metadata

        value_inner, value2 = "", ""

        metadata_inner = config['metadata_inner']
        for _entry in list_metadata:
            if f"{metadata_inner['key']} -> {metadata_inner['name']}:" in _entry:
                value_inner = _entry

        metadata_outer = config['metadata_outer']
        for _entry in list_metadata:
            if f"{metadata_outer['key']} -> {metadata_outer['name']}:" in _entry:
                value_outer = _entry

        return value_inner, value_outer

    def select_metadata_to_use_for_sorting(self):
        # retrieving list of metadata
        list_metadata = MetadataHandler.get_list_of_metadata(self.list_images[0])
        self.list_metadata = list_metadata

        metadata_inner_value, metadata_outer_value = self.get_default_metadata_selected()

        select_width = "550px"
        select_height = "300px"

        # metadata_outer
        search_outer = widgets.HBox([widgets.Label("Search:"),
                                     widgets.Text("",
                                                  layout=widgets.Layout(width="150px")),
                                     widgets.Button(description="X",
                                                    button_style='',
                                                    layout=widgets.Layout(width="10px"))
                                     ])
        self.search_outer_field = search_outer.children[1]
        self.search_outer_field.observe(self.search_metadata_outer_edited, names='value')
        search_outer.children[2].on_click(self.reset_search_metadata_outer)

        result2 = widgets.HBox([widgets.HTML("<u>Metadata Selected</u>:",
                                             layout=widgets.Layout(width="200px")),
                                widgets.Label(metadata_outer_value,
                                              layout=widgets.Layout(width="100%"))])
        self.metadata_outer_selected_label = result2.children[1]

        metadata_outer = widgets.VBox([widgets.HTML("<b>Outer Loop Metadata</b>"),
                                  search_outer,
                                  widgets.Select(options=list_metadata,
                                                 value=metadata_outer_value,
                                                 layout=widgets.Layout(width=select_width,
                                                                       height=select_height)),
                                  result2])
        self.list_metadata_outer = metadata_outer.children[2]
        self.list_metadata_outer.observe(self.metadata_outer_selection_changed, names='value')

        # metadata_inner
        search_inner = widgets.HBox([widgets.Label("Search:",
                                                   ),
                                     widgets.Text("",
                                                  layout=widgets.Layout(width="150px")),
                                     widgets.Button(description="X",
                                                    button_style='',
                                                    layout=widgets.Layout(width="10px")
                                                    )])
        self.search_inner_field = search_inner.children[1]
        self.search_inner_field.observe(self.search_metadata_inner_edited, names='value')
        search_inner.children[2].on_click(self.reset_search_metadata_inner)

        result1 = widgets.HBox([widgets.HTML("<u>Metadata Selected</u>:",
                                             layout=widgets.Layout(width="200px")),
                                widgets.Label(metadata_inner_value,
                                              layout=widgets.Layout(width="100%"))])
        self.metadata_inner_selected_label = result1.children[1]

        metadata_inner = widgets.VBox([widgets.HTML("<b>Inner Loop Metadata</b>"),
                                  search_inner,
                                  widgets.Select(options=list_metadata,
                                                 value=metadata_inner_value,
                                                 layout=widgets.Layout(width=select_width,
                                                                       height=select_height)),
                                  result1])
        self.list_metadata_inner = metadata_inner.children[2]
        self.list_metadata_inner.observe(self.metadata_inner_selection_changed, names='value')

        metadata = widgets.HBox([metadata_outer, widgets.Label(" "), metadata_inner])
        display(metadata)

        self.save_key_metadata()

    def metadata_inner_selection_changed(self, name):
        new_value = name['new']
        self.metadata_inner_selected_label.value = new_value
        self.save_key_metadata()

    def search_metadata_inner_edited(self, name):
        search_string = name['new']
        selection_of_search_string = []
        for _metadata in self.list_metadata:
            if search_string in _metadata.lower():
                selection_of_search_string.append(_metadata)
        if selection_of_search_string:
            self.list_metadata_inner.options = selection_of_search_string
            self.list_metadata_inner.value = selection_of_search_string[0]
            self.save_key_metadata()
        else:
            self.list_metadata_inner.options = ["No Metadata found!"]

    def reset_search_metadata_inner(self, value):
        self.search_inner_field.value = ""
        self.search_metadata_inner_edited({'new': ""})
        metadata_inner_value, _ = self.get_default_metadata_selected()
        self.list_metadata_inner.value = metadata_inner_value

    def metadata_outer_selection_changed(self, name):
        new_value = name['new']
        self.metadata_outer_selected_label.value = new_value
        self.save_key_metadata()

    def search_metadata_outer_edited(self, name):
        search_string = name['new']
        selection_of_search_string = []
        for _metadata in self.list_metadata:
            if search_string in _metadata.lower():
                selection_of_search_string.append(_metadata)
        if selection_of_search_string:
            self.list_metadata_outer.options = selection_of_search_string
            self.list_metadata_outer.value = selection_of_search_string[0]
            self.save_key_metadata()
        else:
            self.list_metadata_outer.options = ["No Metadata found!"]

    def reset_search_metadata_outer(self, value):
        self.search_outer_field.value = ""
        self.search_metadata_outer_edited({'new': ""})
        _, metadata_outer_value = self.get_default_metadata_selected()
        self.list_metadata_outer.value = metadata_outer_value
        self.save_key_metadata()

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

        self.dictionary_of_groups_sorted = o_group.master_grouped_dictionary
        # self.dictionary_of_groups_unsorted = o_group.dictionary_of_groups
        # dict_new_names = GroupImages.make_dictionary_of_groups_new_names(self.dictionary_of_groups_unsorted)
        # self.dictionary_of_groups_new_names = dict_new_names
        # self.dictionary_file_vs_metadata = o_group.master_dictionary

    @staticmethod
    def make_dictionary_of_groups_new_names(dictionary_of_group_unsorted):
        dict_new_names = OrderedDict()
        for _group_index in dictionary_of_group_unsorted.keys():
            nbr_files = len(dictionary_of_group_unsorted[_group_index])
            list_new_names = [f"group{_group_index:02d}_{_index:04d}.tiff"
                              for _index
                              in np.arange(nbr_files)]
            dict_new_names[_group_index] = list_new_names
        return dict_new_names

    def display_groups(self):
        self.group_images()



        return

        nbr_groups = len(self.dictionary_of_groups_unsorted)

        # column 1
        group_label = ["Group # {}".format(_index) for _index in np.arange(nbr_groups)]
        self.list_group_label = group_label
        vbox_left = widgets.VBox([widgets.HTML("<b>Select Group</b>:"),
                                  widgets.Select(options=group_label,
                                                 layout=widgets.Layout(width="150px",
                                                                       height="300px"))])
        select_group_ui = vbox_left.children[1]
        select_group_ui.observe(self.group_index_changed, 'value')

        # column 2
        vbox_center = widgets.VBox([widgets.HTML("<b>Original file names</b>:"),
                                    widgets.Select(options=self.get_list_of_files_basename_only(0),
                                                   layout=widgets.Layout(width="450px",
                                                                         height="300px"))])
        list_of_files_ui = vbox_center.children[1]
        list_of_files_ui.observe(self.list_of_files_changed, 'value')
        self.list_of_files_ui = list_of_files_ui

        # column 3
        vbox_3 = widgets.VBox([widgets.HTML("<b>New Name</b>"),
                               widgets.Select(options=self.get_list_of_new_files_basename_only(0),
                                              layout=widgets.Layout(width="450px",
                                                                    height="300px"))])
        list_of_new_files_ui = vbox_3.children[1]
        list_of_new_files_ui.observe(self.list_of_new_files_changed, 'value')
        self.list_of_new_files_ui = list_of_new_files_ui

        # column 4
        vbox_right = widgets.VBox([widgets.Label("Metadata:"),
                                   widgets.Textarea(value="",
                                                    layout=widgets.Layout(width="200px",
                                                                          height="300px"))])
        self.metadata_ui = vbox_right.children[1]
        self.list_of_files_changed(value={'new': self.get_list_of_files_basename_only(0)[0]})

        hbox = widgets.HBox([vbox_left, vbox_center, vbox_3, vbox_right])
        display(hbox)

        bottom_hbox = widgets.HBox([widgets.Label("Images are in:",
                                                  layout=widgets.Layout(width="150px")),
                                    widgets.Label(self.data_path,
                                                  layout=widgets.Layout(width="90%"))])
        self.path_ui = bottom_hbox.children[1]
        display(bottom_hbox)

    def get_list_of_files_basename_only(self, index):
        list_files = self.dictionary_of_groups_unsorted[index]
        short_list_files = [os.path.basename(_file) for _file in list_files]
        return short_list_files

    def get_list_of_new_files_basename_only(self, index):
        list_files = self.dictionary_of_groups_new_names[index]
        short_list_files = [os.path.basename(_file) for _file in list_files]
        return short_list_files

    def group_index_changed(self, value):
        new_group_selected = value['new']
        _, new_group_index = new_group_selected.split(" # ")
        short_list_files = self.get_list_of_files_basename_only(np.int(new_group_index))
        self.list_of_files_ui.options = short_list_files
        short_list_new_files = self.get_list_of_new_files_basename_only(np.int(new_group_index))
        self.list_of_new_files_ui.options = short_list_new_files
        self.list_of_new_files_ui.value = short_list_new_files[0]
        self.list_of_files_ui.value = short_list_files[0]

    def list_of_new_files_changed(self, value):
        new_file_selected = value['new']
        list_of_files_names = self.list_of_files_ui.options
        list_of_new_files_names = self.list_of_new_files_ui.options
        index = list_of_new_files_names.index(new_file_selected)
        file_selected = list_of_files_names[index]
        self.list_of_files_ui.value = file_selected

    def list_of_files_changed(self, value):
        dictionary_file_vs_metadata = self.dictionary_file_vs_metadata
        file_selected = value['new']
        full_file_name_selected = os.path.join(self.data_path, file_selected)
        string_to_display = ""
        for _key, _value in dictionary_file_vs_metadata[full_file_name_selected].items():
            string_to_display += "{}: {}\n".format(_key, _value)
        self.metadata_ui.value = string_to_display

        list_new_names = list(self.list_of_new_files_ui.options)
        list_of_names = list(self.list_of_files_ui.options)
        index = list_of_names.index(file_selected)
        self.list_of_new_files_ui.value = list_new_names[index]

    # def update_old_name_order(self):
    #     how_to_sort_within_cycle = self.how_to_sort_within_cycle
    #     o_sort = SortImagesWithinEachCycle(dict_groups_filename=self.dictionary_of_groups_unsorted,
    #                                        dict_filename_metadata=self.dictionary_file_vs_metadata)
    #     o_sort.sort(dict_how_to_sort=how_to_sort_within_cycle)
    #     self.dictionary_of_groups_sorted = o_sort.dict_groups_filename_sorted
    #
    #     group_number_selected = self._get_group_number_selected()
    #     list_files_sorted = self.dictionary_of_groups_sorted[group_number_selected]
    #     short_list_files_sorted = [os.path.basename(_file) for _file in list_files_sorted]
    #     self.old_name_ui.options = short_list_files_sorted

    def _get_group_number_selected(self):
        group_string = self.select_group_ui.value
        _, group_number = group_string.split(" # ")
        return np.int(group_number)

    # def sorting_algorithm_variable1_changed(self, value):
    #     new_value = value['new']
    #     is_ascending = True if new_value == 'Ascending' else False
    #     self.how_to_sort_within_cycle['1st_variable']['is_ascending'] = is_ascending
    #     self.update_old_name_order()
    #
    # def sorting_algorithm_variable2_changed(self, value):
    #     new_value = value['new']
    #     is_ascending = True if new_value == 'Ascending' else False
    #     self.how_to_sort_within_cycle['2nd_variable']['is_ascending'] = is_ascending
    #     self.update_old_name_order()

    # def name_of_first_metadata_changed(self, value):
    #     old_value = value['old']
    #     new_value = value['new']
    #     self.how_to_sort_within_cycle['1st_variable']['name'] = new_value
    #     self.name_of_second_metadata_ui.value = old_value
    #     self.update_old_name_order()
    #
    # def name_of_second_metadata_changed(self, value):
    #     old_value = value['old']
    #     new_value = value['new']
    #     self.how_to_sort_within_cycle['2nd_variable']['name'] = new_value
    #     self.name_of_first_metadata_ui.value = old_value
    #     self.update_old_name_order()
    #
    # def selection_of_group_changed(self, value=None):
    #     self.update_old_name_order()
    #     group_index = self._get_group_number_selected()
    #     dict_new_names = self.dictionary_of_groups_new_names
    #     list_new_names = dict_new_names[group_index]
    #     self.new_name_ui.options = list_new_names

    def select_output_folder(self):
        output_folder_widget = fileselector.FileSelectorPanel(instruction='select output folder',
                                                              start_dir=os.path.dirname(self.data_path),
                                                              type='directory',
                                                              next=self.move_and_rename_files,
                                                              multiple=False)
        output_folder_widget.show()

    def move_and_rename_files(self, output_folder):
        if not output_folder:
            return

        output_folder_basename = os.path.basename(self.folder_selected) + "_sorted_for_grating_reconstruction"
        output_folder = os.path.join(output_folder, output_folder_basename)
        output_folder = os.path.abspath(output_folder)
        make_or_reset_folder(output_folder)

        dict_old_files = self.dictionary_of_groups_unsorted
        dict_new_files = self.dictionary_of_groups_new_names

        list_keys = list(dict_old_files.keys())
        size_outer_loop = len(list_keys)
        size_inner_loop = len(dict_old_files[list_keys[0]])

        hbox1 = widgets.HBox([widgets.HTML("Groups",
                                           layout=widgets.Layout(width="100px")),
                              widgets.IntProgress(min=0,
                                                  max=size_outer_loop - 1,
                                                  value=0,
                                                  layout=widgets.Layout(width="300px"))])
        outer_progress_ui = hbox1.children[1]
        hbox2 = widgets.HBox([widgets.HTML("Files",
                                           layout=widgets.Layout(width="100px")),
                              widgets.IntProgress(min=0,
                                                  max=size_inner_loop - 1,
                                                  value=0,
                                                  layout=widgets.Layout(width="300px"))])
        inner_progress_ui = hbox2.children[1]

        vbox = widgets.VBox([hbox1, hbox2])
        display(vbox)

        for _outer_index, _key in enumerate(dict_old_files.keys()):
            _old_name_list = dict_old_files[_key]
            _new_name_list = dict_new_files[_key]
            inner_progress_ui.value = 0
            outer_progress_ui.value = _outer_index
            for _inner_index, (_old, _new) in enumerate(zip(_old_name_list, _new_name_list)):
                new_full_file_name = os.path.join(output_folder, _new)
                old_full_file_name = _old
                shutil.copy(old_full_file_name, new_full_file_name)
                inner_progress_ui.value = _inner_index

        vbox.close()

        message = f"Folder {output_folder} have been created!"
        display(HTML('<span style="font-size: 15px">' + message + '</span>'))
