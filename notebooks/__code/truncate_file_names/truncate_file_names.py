from ipywidgets import widgets
from IPython.core.display import display, HTML
import os
import numpy as np
from __code import utilities
from __code.ipywe import fileselector

from __code.file_handler import ListMostDominantExtension
from __code.ipywe.myfileselector import FileSelectorPanelWithJumpFolders
from __code._utilities.file import get_list_of_files, get_list_file_extensions, get_file_extension


class TruncateFileNames:

    list_of_files = None

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_input_files(self):
        self.input_files_ui = fileselector.FileSelectorPanel(instruction='Select List of Files',
                                                              start_dir=self.working_dir,
                                                              multiple=True)
        self.input_files_ui.show()

    def define_truncate_part(self):

        list_of_files = self.input_files_ui.selected
        if list_of_files:
            self.list_of_files = list_of_files
            self.o_schema = NamingSchemaDefinition(o_truncate=self)
            self.o_schema.show()


class NamingSchemaDefinition:

    list_of_files = None
    ready_to_output = False

    def __init__(self, o_truncate=None):

        if o_truncate:
            self.list_of_files = o_truncate.list_of_files
        else:
            raise ValueError("TruncateFileNames is missing!")

        if self.list_of_files:
            _random_input_list = utilities.get_n_random_element(input_list=self.list_of_files,
                                                                n=10)
            self.random_input_list = [os.path.basename(_file) for _file in _random_input_list]

        self.basename = os.path.basename(self.list_of_files[0])

    def random_input_checkbox_value_changed(self, value):
        self.change_int_range_slider()

    def get_basename_of_current_dropdown_selected_file(self, is_with_ext=False):
        full_file_name = self.random_input_checkbox.value
        if is_with_ext:
            return full_file_name
        else:
            [basename, _] = os.path.splitext(full_file_name)
            return basename

    def change_int_range_slider(self, value=[]):
        if not value:
            [start_index, end_index] = self.int_range_slider.value
        else:
            [start_index, end_index] = value['new']
        basename = self.get_basename_of_current_dropdown_selected_file(is_with_ext=True)
        new_basename = basename[start_index: end_index]
        self.output_label.value = new_basename

        prefix_part_to_remove = basename[0:start_index]
        suffix_part_to_remove = basename[end_index:]

        self.left_part_to_remove_label.value = prefix_part_to_remove
        self.right_part_to_remove_label.value = suffix_part_to_remove

    def show(self):

        self.box1 = widgets.HBox([widgets.Label("Random Input:",
                                                layout=widgets.Layout(width='15%')),
                                  widgets.Dropdown(options=self.random_input_list,
                                                   value=self.random_input_list[0],
                                                   layout=widgets.Layout(width='50%'))
                                  ])
        self.random_input_checkbox = self.box1.children[1]
        self.random_input_checkbox.observe(self.random_input_checkbox_value_changed, 'value')

        self.box2 = widgets.HBox([widgets.IntRangeSlider(value=[0, len(self.basename)],
                                                         min=0,
                                                         max=len(self.basename),
                                                         step=1)])
        self.int_range_slider = self.box2.children[0]
        self.int_range_slider.observe(self.change_int_range_slider, names='value')

        self.box3 = widgets.HBox([widgets.Label("New file name:",
                                                layout=widgets.Layout(width='20%')),
                                  widgets.Label(value="",
                                                layout=widgets.Layout(width='80%'))])
        self.output_label = self.box3.children[1]

        self.box4 = widgets.HBox([widgets.Label("String to remove:",
                                                layout=widgets.Layout(width='30%'))])

        self.box5 = widgets.VBox([widgets.Label("",
                                                layout=widgets.Layout(width='45%'))])
        self.box6 = widgets.HBox([widgets.Label(value="On the left:",
                                                layout=widgets.Layout(width='40%')),
                                  widgets.Label(value="",
                                                layout=widgets.Layout(width='60%'))])
        self.box7 = widgets.HBox([widgets.Label(value="On the right:",
                                                layout=widgets.Layout(width='40%')),
                                  widgets.Label(value="",
                                                layout=widgets.Layout(width='60%'))])
        self.box8 = widgets.VBox([self.box6, self.box7], layout=widgets.Layout(width="50%"))
        self.box9 = widgets.HBox([self.box5, self.box8], layout=widgets.Layout(width="50%"))
        self.left_part_to_remove_label = self.box6.children[1]
        self.right_part_to_remove_label = self.box7.children[1]

        separate_line = widgets.HTML(value="<hr>",
                                     layout=widgets.Layout(width="100%"))

        vbox = widgets.VBox([self.box1, self.box2, self.box3, separate_line, self.box4, self.box9])
        display(vbox)

        self.change_int_range_slider()

    def check_new_names(self):
        dict_old_new_names = self.create_dict_old_new_filenames()
        old_names_new_names = [f"{os.path.basename(_key)} -> {_value}" for _key,_value in dict_old_new_names.items()]
        select_widget = widgets.Select(options=old_names_new_names,
                                       layout=widgets.Layout(width="100%",
                                                             height="400px"))
        display(select_widget)

    def create_dict_old_new_filenames(self):

        [start_index, end_index] = self.int_range_slider.value

        list_base_file_names = [os.path.basename(file) for file in self.list_of_files]

        new_list = {}
        for _file in list_base_file_names:
            new_file_name = _file[start_index: end_index]
            new_list[_file] = new_file_name

        return new_list



    #
    #
    # def current_naming_schema(self):
    #     pre_index_separator = self.box2.children[1].value
    #     schema = "<untouched_part>" + pre_index_separator + '<digit>' + self.str_ext
    #     return schema
    #
    # def new_naming_schema(self):
    #     if not self.use_previous_prefix_widget.value:
    #         prefix = self.new_prefix_text_widget.value
    #     else:
    #         prefix = self.basename_selected_by_user.value
    #
    #     post_index_separator = self.box5.children[1].value
    #     nbr_digits = self.box7.children[1].value
    #
    #     schema = prefix + post_index_separator + nbr_digits * '#' + self.str_ext
    #     return schema
    #
    # def pre_index_text_changed(self, sender):
    #     self.box4.children[1].value = self.current_naming_schema()
    #     self.demo_output_file_name()
    #
    # def post_text_changed(self, sender):
    #     self.box6.children[1].value = self.new_naming_schema()
    #     self.demo_output_file_name()
    #
    # def changed_use_previous_prefix_name(self, value):
    #     self.user_new_prefix_widget.value = not value['new']
    #     self.new_prefix_text_widget.disabled = value['new']
    #     self.post_text_changed(None)
    #
    # def changed_use_new_prefix_name(self, value=[]):
    #     if value == []:
    #         _value = self.user_new_prefix_widget.value
    #     else:
    #         _value = value['new']
    #     self.use_previous_prefix_widget.value = not _value
    #     self.new_prefix_text_widget.disabled = not _value
    #     self.post_text_changed(None)
    #
    #
    #
    #
    # def random_input_checkbox_value_changed(self, value):
    #     self.change_int_range_slider()
    #
    #
    #
    # def demo_output_file_name(self):
    #     input_file = self.get_basename_of_current_dropdown_selected_file(is_with_ext=True)
    #     self.output_ui_2.children[1].value = input_file
    #
    #     old_index_separator = self.get_old_index_separator()
    #     new_prefix_name = self.get_new_prefix_name()
    #     new_index_separator = self.get_new_index_separator()
    #     new_number_of_digits = self.get_new_number_of_digits()
    #     offset = self.box8.children[1].value
    #     [start_index, end_index] = self.int_range_slider.value
    #
    #     try:
    #         display(HTML("""
	# 					  <style>
	# 					  .result_label {
	# 						 font-style: bold;
	# 						 color: black;
	# 						 font-size: 14px;
	# 					  }
	# 					  </style>
	# 					  """))
    #
    #         new_name = self.generate_new_file_name(input_file,
    #                                                start_index,
    #                                                end_index,
    #                                                old_index_separator,
    #                                                new_prefix_name,
    #                                                new_index_separator,
    #                                                new_number_of_digits,
    #                                                offset)
    #
    #         self.ready_to_output = True
    #
    #     except ValueError:
    #
    #         display(HTML("""
	# 					  <style>
	# 					  .result_label {
	# 						 font-style: bold;
	# 						 color: red;
	# 						 font-size: 18px;
	# 					  }
	# 					  </style>
	# 					  """))
    #
    #         new_name = 'ERROR while generating new file name!'
    #
    #         self.ready_to_output = False
    #
    #     self.output_ui_3.children[1].value = new_name
    #
    # def get_old_index_separator(self):
    #     return self.box2.children[1].value
    #
    # def get_new_prefix_name(self):
    #     if self.use_previous_prefix_widget.value == True:
    #         new_prefix_name = self.basename_selected_by_user.value
    #     else:
    #         new_prefix_name = self.new_prefix_text_widget.value
    #     return new_prefix_name
    #
    # def get_new_index_separator(self):
    #     return self.box5.children[1].value
    #
    # def get_new_number_of_digits(self):
    #     return self.box7.children[1].value
    #
    # def generate_new_file_name(self, old_file_name,
    #                            start_index,
    #                            end_index,
    #                            old_index_separator,
    #                            new_prefix_name,
    #                            new_index_separator,
    #                            new_number_of_digits,
    #                            offset):
    #
    #     [_pre_extension, _ext] = os.path.splitext(old_file_name)
    #     _name_separated = _pre_extension.split(old_index_separator)
    #
    #     if self.user_new_prefix_widget.value == True:
    #         prefix = new_prefix_name
    #     else:
    #         prefix = old_file_name[start_index: end_index + 1]
    #
    #     try:
    #         _index = int(_name_separated[-1]) + offset
    #         new_name = prefix + new_index_separator + \
    #                    '{:0{}}'.format(_index, new_number_of_digits) + \
    #                    _ext
    #     except ValueError:
    #         _index = _name_separated[-1]
    #         new_name = prefix + new_index_separator + \
    #             _index + _ext
    #
    #     return new_name
    #
    # def get_dict_old_new_filenames(self):
    #     list_of_input_files = self.list_files
    #
    #     renaming_result = []
    #
    #     old_index_separator = self.get_old_index_separator()
    #     new_prefix_name = self.get_new_prefix_name()
    #
    #     [start_index, end_index] = self.int_range_slider.value
    #
    #     new_index_separator = self.get_new_index_separator()
    #     new_number_of_digits = self.get_new_number_of_digits()
    #     offset = self.box8.children[1].value
    #
    #     list_of_input_basename_files = [os.path.basename(_file) for _file in list_of_input_files]
    #
    #     new_list = {}
    #     for _file_index, _file in enumerate(list_of_input_basename_files):
    #         new_name = self.generate_new_file_name(_file,
    #                                                start_index,
    #                                                end_index,
    #                                                old_index_separator,
    #                                                new_prefix_name,
    #                                                new_index_separator,
    #                                                new_number_of_digits,
    #                                                offset)
    #         new_list[list_of_input_files[_file_index]] = new_name
    #         renaming_result.append("{} \t --> \t {}".format(_file, new_name))
    #
    #     self.renaming_result = renaming_result
    #     return new_list
    #
    # def check_new_names(self):
    #     dict_old_new_names = self.get_dict_old_new_filenames()
    #     old_names_new_names = [f"{os.path.basename(_key)} -> {_value}" for _key,_value in dict_old_new_names.items()]
    #     select_widget = widgets.Select(options=old_names_new_names,
    #                                    layout=widgets.Layout(width="100%",
    #                                                          height="400px"))
    #     display(select_widget)
    #
    # def select_export_folder(self):
    #
    #     if self.ready_to_output:
    #         self.output_folder_ui = FileSelectorPanelWithJumpFolders(instruction='Select Output Folder',
    #                                                                  start_dir=self.working_dir,
    #                                                                  ipts_folder=self.working_dir,
    #                                                                  multiple=False,
    #                                                                  next=self.export,
    #                                                                  newdir_toolbar_button=True,
    #                                                                  type='directory')
    #     else:
    #         display(HTML('<span style="font-size: 20px; color:red">You need to fix the namig convention first!</span>'))
    #
    # def export(self, selected):
    #     input_folder = os.path.abspath(self.input_folder)
    #     input_folder_renamed = os.path.basename(input_folder) + '_renamed'
    #     self.output_folder_ui.shortcut_buttons.close()
    #
    #     dict_old_new_names = self.get_dict_old_new_filenames()
    #     new_output_folder = os.path.join(os.path.abspath(selected), input_folder_renamed)
    #
    #     utilities.copy_files(dict_old_new_names=dict_old_new_names,
    #                          new_output_folder=new_output_folder,
    #                          overwrite=False)
    #
    #     self.new_list_files = dict_old_new_names
    #     self.display_renaming_result(new_output_folder)
    #
    # def display_renaming_result(self, selected):
    #
    #     display(HTML('<span style="font-size: 15px; color:blue">Following files have been created in folder: ' +
    #                  selected + '</span>'))
