from ipywidgets import widgets
from IPython.core.display import display, HTML
import os

from __code import utilities
from __code.ipywe import fileselector

from __code.ipywe.myfileselector import FileSelectorPanelWithJumpFolders


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
        self.working_dir = os.path.dirname(os.path.dirname(self.list_of_files[0]))
        self.input_folder = os.path.dirname(self.list_of_files[0])

    def random_input_checkbox_value_changed(self, value):
        self.update_new_file_name()

    def get_basename_of_current_dropdown_selected_file(self, is_with_ext=False):
        full_file_name = self.random_input_checkbox.value
        if is_with_ext:
            return full_file_name
        else:
            [basename, _] = os.path.splitext(full_file_name)
            return basename

    def show(self):

        self.box1 = widgets.HBox([widgets.Label("Random Input:",
                                                layout=widgets.Layout(width='15%')),
                                  widgets.Dropdown(options=self.random_input_list,
                                                   value=self.random_input_list[0],
                                                   layout=widgets.Layout(width='50%'))
                                  ])
        self.random_input_checkbox = self.box1.children[1]
        self.random_input_checkbox.observe(self.random_input_checkbox_value_changed, 'value')

        self.box2 = widgets.HBox([widgets.Label("String to remove:",
                                                layout=widgets.Layout(width='30%'))])

        self.box6 = widgets.HBox([widgets.Label(value="    On the left:",
                                                layout=widgets.Layout(width='40%')),
                                  widgets.Text(value="",
                                                layout=widgets.Layout(width='60%'))])
        self.box7 = widgets.HBox([widgets.Label(value="    On the right:",
                                                layout=widgets.Layout(width='40%')),
                                  widgets.Text(value="",
                                                layout=widgets.Layout(width='60%'))])
        self.box8 = widgets.VBox([self.box6, self.box7], layout=widgets.Layout(width="50%"))
        self.left_part_to_remove_text = self.box6.children[1]
        self.right_part_to_remove_text = self.box7.children[1]
        self.left_part_to_remove_text.observe(self.left_part_text_changed, 'value')
        self.right_part_to_remove_text.observe(self.right_part_text_changed, 'value')

        self.box9= widgets.HBox([widgets.Label("New file name:",
                                                layout=widgets.Layout(width='20%')),
                                  widgets.Label(value="",
                                                layout=widgets.Layout(width='80%'))])
        self.output_label = self.box9.children[1]

        separate_line = widgets.HTML(value="<hr>",
                                     layout=widgets.Layout(width="100%"))

        vbox = widgets.VBox([self.box1, separate_line, self.box2, self.box8, separate_line, self.box9])
        display(vbox)

        self.update_new_file_name()

    def left_part_text_changed(self, text):
        self.update_new_file_name()

    def right_part_text_changed(self, text):
        self.update_new_file_name()

    def update_new_file_name(self):
        basename = self.get_basename_of_current_dropdown_selected_file(is_with_ext=True)
        new_file_name = ""

        start_text = self.left_part_to_remove_text.value
        end_text = self.right_part_to_remove_text.value

        if basename[:len(start_text)] == start_text[:]:
            new_file_name = basename[len(start_text):]

        if basename[-len(end_text):] == end_text[:]:
            new_file_name = basename[:-len(end_text)]

        self.output_label.value = new_file_name

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

        new_dict = {}
        for _file in list_base_file_names:
            new_file_name = _file[start_index: end_index]
            new_dict[_file] = new_file_name

        return new_dict

    def select_export_folder(self):

        self.output_folder_ui = FileSelectorPanelWithJumpFolders(instruction='Select Output Folder',
                                                                 start_dir=self.working_dir,
                                                                 ipts_folder=self.working_dir,
                                                                 multiple=False,
                                                                 # next=self.rename_and_export_files,
                                                                 newdir_toolbar_button=True,
                                                                 type='directory')


    def rename_and_export_files(self, output_folder=None):

        output_folder = self.output_folder_ui.output_folder_ui.selected
        input_folder = os.path.abspath(self.input_folder)
        input_folder_renamed = os.path.basename(input_folder) + '_renamed'
        self.output_folder_ui.shortcut_buttons.close()
        new_output_folder = os.path.join(os.path.abspath(output_folder), input_folder_renamed)
        dict_old_new_names = self.create_dict_old_new_filenames()

        utilities.copy_files(dict_old_new_names=dict_old_new_names,
                             input_folder_name=input_folder,
                             new_output_folder=new_output_folder,
                             overwrite=False)

        self.new_list_files = dict_old_new_names
        self.display_renaming_result(new_output_folder)

    def display_renaming_result(self, selected):
        display(HTML('<span style="font-size: 15px; color:blue">Following files have been created in folder: ' +
                     selected + '</span>'))
