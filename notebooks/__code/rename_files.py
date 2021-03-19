from ipywidgets import widgets
from IPython.core.display import display, HTML
import os
import numpy as np
from __code import utilities
from __code.ipywe import fileselector

from __code.file_handler import ListMostDominantExtension
from __code.ipywe.myfileselector import FileSelectorPanelWithJumpFolders


class FormatFileNameIndex(object):

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_input_folder(self):
        self.input_folder_ui = fileselector.FileSelectorPanel(instruction='Select Input Folder',
                                                              type='directory',
                                                              start_dir=self.working_dir,
                                                              next=self.next,
                                                              multiple=False)
        self.input_folder_ui.show()

    def calculate_most_dominant_files(self):
        self.o_list_dominant = ListMostDominantExtension(working_dir=self.input_folder)
        self.o_list_dominant.calculate()

    def get_most_dominant_files(self):
        _result = self.o_list_dominant.get_files_of_selected_ext()
        self.list_files = _result.list_files
        self.ext = _result.ext

    def next(self, input_folder):
        self.input_folder = input_folder
        self.calculate_most_dominant_files()
        self.get_most_dominant_files()

        self.o_schema = NamingSchemaDefinition(o_format=self)
        self.o_schema.show()


class NamingSchemaDefinition(object):
    ext = ''
    list_files = []
    working_dir = ''

    ready_to_output = False

    def __init__(self, o_format=None):
        if o_format:
            self.list_files = o_format.list_files
            self.ext = o_format.ext
            self.working_dir = o_format.working_dir

        if self.list_files:
            _random_input_list = utilities.get_n_random_element(input_list=self.list_files,
                                                                n=10)
            self.random_input_list = [os.path.basename(_file) for _file in _random_input_list]

        self.basename = os.path.basename(self.list_files[0])

    def current_naming_schema(self):
        pre_index_separator = self.box2.children[1].value
        schema = "<untouched_part>" + pre_index_separator + '<digit>' + self.ext
        return schema

    def new_naming_schema(self):
        if not self.use_previous_prefix_widget.value:
            prefix = self.new_prefix_text_widget.value
        else:
            prefix = self.basename_selected_by_user.value

        post_index_separator = self.box5.children[1].value
        nbr_digits = self.box7.children[1].value

        schema = prefix + post_index_separator + nbr_digits * '#' + self.ext
        return schema

    def pre_index_text_changed(self, sender):
        self.box4.children[1].value = self.current_naming_schema()
        self.demo_output_file_name()

    def post_text_changed(self, sender):
        self.box6.children[1].value = self.new_naming_schema()
        self.demo_output_file_name()

    def changed_use_previous_prefix_name(self, value):
        self.user_new_prefix_widget.value = not value['new']
        self.new_prefix_text_widget.disabled = value['new']
        self.post_text_changed(None)

    def changed_use_new_prefix_name(self, value=[]):
        if value == []:
            _value = self.user_new_prefix_widget.value
        else:
            _value = value['new']
        self.use_previous_prefix_widget.value = not _value
        self.new_prefix_text_widget.disabled = not _value
        self.post_text_changed(None)

    def get_basename_of_current_dropdown_selected_file(self, is_with_ext=False):
        full_file_name = self.random_input_checkbox.value
        if is_with_ext:
            return full_file_name
        else:
            [basename, _] = os.path.splitext(full_file_name)
            return basename

    def change_int_range_slider(self, value=[]):
        if value == []:
            [start_index, end_index] = self.int_range_slider.value
        else:
            [start_index, end_index] = value['new']
        basename = self.get_basename_of_current_dropdown_selected_file()
        new_basename = basename[start_index: end_index + 1]
        self.basename_selected_by_user.value = new_basename

        # update in the second ui
        if self.use_previous_prefix_widget.value:
            self.changed_use_new_prefix_name()

    def random_input_checkbox_value_changed(self, value):
        self.change_int_range_slider()

    def show(self):

        # current schema name
        self.box2 = widgets.HBox([widgets.Label("Pre. Index Separator",
                                                layout=widgets.Layout(width='15%')),
                                  widgets.Text(value='_',
                                               layout=widgets.Layout(width='5%'))])

        self.box2b = widgets.HBox([widgets.Label("Untouched filename part:",
                                                 layout=widgets.Layout(width="20%")),
                                   widgets.Label("",
                                                 layout=widgets.Layout(width='40%')),
                                   widgets.IntRangeSlider(value=[0, 2],
                                                          min=0,
                                                          max=len(self.basename),
                                                          step=1)])
        self.int_range_slider = self.box2b.children[2]
        self.int_range_slider.observe(self.change_int_range_slider, names='value')
        self.basename_selected_by_user = self.box2b.children[1]

        self.box4 = widgets.HBox([widgets.Label("Current Name Schema: ",
                                                layout=widgets.Layout(width='20%')),
                                  widgets.Label(self.current_naming_schema(),
                                                layout=widgets.Layout(width='30%')),
                                  widgets.Label("Random Input:",
                                                layout=widgets.Layout(width='15%')),
                                  widgets.Dropdown(options=self.random_input_list,
                                                   value=self.random_input_list[0],
                                                   layout=widgets.Layout(width='50%'))
                                  ])

        self.box2.children[1].on_trait_change(self.pre_index_text_changed, 'value')
        before = widgets.VBox([self.box2, self.box2b, self.box4])
        self.random_input_checkbox = self.box4.children[3]
        self.random_input_checkbox.observe(self.random_input_checkbox_value_changed, 'value')

        # new naming schema
        box_text_width = '10%'
        self.box1 = widgets.HBox([widgets.Label("New prefix File Name",
                                                layout=widgets.Layout(width='10%')),
                                  widgets.Checkbox(value=True,
                                                   description='Use previous prefix name',
                                                   layout=widgets.Layout(width='30%'))])
        self.use_previous_prefix_widget = self.box1.children[1]
        self.box1.children[1].observe(self.changed_use_previous_prefix_name, names='value')

        self.box1b = widgets.HBox([widgets.Label("",
                                                 layout=widgets.Layout(width='10%')),
                                   widgets.Checkbox(value=False,
                                                    description='Use new prefix',
                                                    layout=widgets.Layout(width='20%')),
                                   widgets.Text(value='image',
                                                disabled=True,
                                                layout=widgets.Layout(width='25%'))])
        self.box1b.children[2].observe(self.changed_use_new_prefix_name, names='value')
        self.new_prefix_text_widget = self.box1b.children[2]
        self.user_new_prefix_widget = self.box1b.children[1]
        self.user_new_prefix_widget.observe(self.changed_use_new_prefix_name, names='value')

        self.box5 = widgets.HBox([widgets.Label("New Index Separator",
                                                layout=widgets.Layout(width='15%')),
                                  widgets.Text(value='_',
                                               layout=widgets.Layout(width=box_text_width))])

        self.box7 = widgets.HBox([widgets.Label("Number of digits",
                                                layout=widgets.Layout(width='15%')),
                                  widgets.IntText(value=4,
                                                  layout=widgets.Layout(width=box_text_width))])

        self.box8 = widgets.HBox([widgets.Label("Offset",
                                                layout=widgets.Layout(width='15%')),
                                  widgets.IntText(value=0,
                                                  layout=widgets.Layout(width=box_text_width))])

        self.box6 = widgets.HBox([widgets.Label("New Name Schema: ",
                                                layout=widgets.Layout(width='20%')),
                                  widgets.Label(self.new_naming_schema(),
                                                layout=widgets.Layout(width='40%'))])

        self.box1.children[1].on_trait_change(self.post_text_changed, 'value')
        self.box5.children[1].on_trait_change(self.post_text_changed, 'value')
        self.box7.children[1].on_trait_change(self.post_text_changed, 'value')
        self.box8.children[1].on_trait_change(self.post_text_changed, 'value')

        after = widgets.VBox([self.box1, self.box1b, self.box5, self.box7, self.box8, self.box6])

        accordion = widgets.Accordion(children=[before, after])
        accordion.set_title(0, 'Current Schema Name')
        accordion.set_title(1, 'New Naming Schema')

        output_ui_1 = widgets.HBox([widgets.Label("Example of naming: ",
                                                  layout=widgets.Layout(width='20%'))])

        self.output_ui_2 = widgets.HBox([widgets.Label("Old name: ",
                                                       layout=widgets.Layout(width='40%')),
                                         widgets.Label("",
                                                       layout=widgets.Layout(width='60%'))])

        self.output_ui_3 = widgets.HBox([widgets.Label("New name: ",
                                                       layout=widgets.Layout(width='40%')),
                                         widgets.Label("",
                                                       layout=widgets.Layout(width='60%'))])

        self.output_ui_3.children[1].add_class("result_label")
        vbox = widgets.VBox([accordion, output_ui_1, self.output_ui_2, self.output_ui_3])
        display(vbox)

        self.demo_output_file_name()
        self.change_int_range_slider()
        self.changed_use_new_prefix_name()

    def demo_output_file_name(self):
        input_file = self.get_basename_of_current_dropdown_selected_file(is_with_ext=True)
        self.output_ui_2.children[1].value = input_file

        old_index_separator = self.get_old_index_separator()
        new_prefix_name = self.get_new_prefix_name()
        new_index_separator = self.get_new_index_separator()
        new_number_of_digits = self.get_new_number_of_digits()
        offset = self.box8.children[1].value
        [start_index, end_index] = self.int_range_slider.value

        try:
            display(HTML("""
						  <style>
						  .result_label {
							 font-style: bold;
							 color: black;
							 font-size: 14px;
						  }
						  </style>
						  """))

            new_name = self.generate_new_file_name(input_file,
                                                   start_index,
                                                   end_index,
                                                   old_index_separator,
                                                   new_prefix_name,
                                                   new_index_separator,
                                                   new_number_of_digits,
                                                   offset)

            self.ready_to_output = True

        except ValueError:

            display(HTML("""
						  <style>
						  .result_label {
							 font-style: bold;
							 color: red;
							 font-size: 18px;
						  }
						  </style>
						  """))

            new_name = 'ERROR while generating new file name!'

            self.ready_to_output = False

        self.output_ui_3.children[1].value = new_name

    def get_old_index_separator(self):
        return self.box2.children[1].value

    def get_new_prefix_name(self):
        if self.use_previous_prefix_widget.value == True:
            new_prefix_name = self.basename_selected_by_user.value
        else:
            new_prefix_name = self.new_prefix_text_widget.value
        return new_prefix_name

    def get_new_index_separator(self):
        return self.box5.children[1].value

    def get_new_number_of_digits(self):
        return self.box7.children[1].value

    def generate_new_file_name(self, old_file_name,
                               start_index,
                               end_index,
                               old_index_separator,
                               new_prefix_name,
                               new_index_separator,
                               new_number_of_digits,
                               offset):

        [_pre_extension, _ext] = os.path.splitext(old_file_name)
        _name_separated = _pre_extension.split(old_index_separator)

        if self.user_new_prefix_widget.value == True:
            prefix = new_prefix_name
        else:
            prefix = old_file_name[start_index: end_index + 1]

        try:
            _index = np.float(_name_separated[-1]) + offset
            new_name = prefix + new_index_separator + \
                       '{:0{}}'.format(_index, new_number_of_digits) + \
                       self.ext
        except ValueError:
            _index = _name_separated[-1]
            new_name = prefix + new_index_separator + \
                _index + self.ext

        return new_name

    def get_dict_old_new_filenames(self):
        list_of_input_files = self.list_files

        renaming_result = []

        old_index_separator = self.get_old_index_separator()
        new_prefix_name = self.get_new_prefix_name()

        [start_index, end_index] = self.int_range_slider.value

        new_index_separator = self.get_new_index_separator()
        new_number_of_digits = self.get_new_number_of_digits()
        offset = self.box8.children[1].value

        list_of_input_basename_files = [os.path.basename(_file) for _file in list_of_input_files]

        new_list = {}
        for _file_index, _file in enumerate(list_of_input_basename_files):
            new_name = self.generate_new_file_name(_file,
                                                   start_index,
                                                   end_index,
                                                   old_index_separator,
                                                   new_prefix_name,
                                                   new_index_separator,
                                                   new_number_of_digits,
                                                   offset)
            new_list[list_of_input_files[_file_index]] = new_name
            renaming_result.append("{} \t --> \t {}".format(_file, new_name))

        self.renaming_result = renaming_result
        return new_list

    def select_export_folder(self):

        if self.ready_to_output:
            self.output_folder_ui = FileSelectorPanelWithJumpFolders(instruction='Select Output Folder',
                                                                     start_dir=self.working_dir,
                                                                     multiple=False,
                                                                     next=self.export,
                                                                     newdir_toolbar_button=True,
                                                                     type='directory')
        else:
            display(HTML('<span style="font-size: 20px; color:red">You need to fix the namig convention first!</span>'))

    def export(self, selected):

        self.output_folder_ui.shortcut_buttons.close()

        dict_old_new_names = self.get_dict_old_new_filenames()
        new_output_folder = os.path.abspath(selected)

        utilities.copy_files(dict_old_new_names=dict_old_new_names,
                             new_output_folder=new_output_folder,
                             overwrite=False)

        self.new_list_files = dict_old_new_names
        self.display_renaming_result(selected)

    def display_renaming_result(self, selected):

        display(HTML('<span style="font-size: 15px; color:blue">Following files have been created in folder: ' +
                     selected + '</span>'))

        result = widgets.HBox([widgets.Label("Renmaing results: ",
                                             layout=widgets.Layout(width='20%')),
                               widgets.Dropdown(options=self.renaming_result,
                                                value=self.renaming_result[0],
                                                layout=widgets.Layout(width='80%'))
                               ])
        display(result)
