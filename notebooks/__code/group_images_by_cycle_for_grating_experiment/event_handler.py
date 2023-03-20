import numpy as np
import os

from __code.group_images_by_cycle_for_grating_experiment.get import Get
from __code.file_folder_browser import FileFolderBrowser
from __code.group_images_by_cycle_for_grating_experiment.excel_handler import ExcelHandler


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def search_metadata_outer_edited(self, name):
        search_string = name['new'].lower()
        selection_of_search_string = []
        for _metadata in self.parent.list_metadata:
            if search_string in _metadata.lower():
                selection_of_search_string.append(_metadata)
        if selection_of_search_string:
            self.parent.list_metadata_outer.options = selection_of_search_string
            self.parent.list_metadata_outer.value = selection_of_search_string[0]
            self.parent.save_key_metadata()
        else:
            self.parent.list_metadata_outer.options = ["No Metadata found!"]

    def reset_search_metadata_outer(self, value):
        self.parent.search_outer_field.value = ""
        self.search_metadata_outer_edited({'new': ""})
        o_get = Get(parent=self.parent)
        _, metadata_outer_value = o_get.default_metadata_selected()
        self.parent.list_metadata_outer.value = metadata_outer_value
        self.parent.save_key_metadata()

    def metadata_outer_selection_changed(self, name):
        new_value = name['new']
        self.parent.metadata_outer_selected_label.value = new_value
        self.parent.save_key_metadata()

    def metadata_inner_selection_changed(self, name):
        new_value = name['new']
        self.parent.metadata_inner_selected_label.value = new_value
        self.parent.save_key_metadata()

    def search_metadata_inner_edited(self, name):
        search_string = name['new'].lower()
        selection_of_search_string = []
        for _metadata in self.parent.list_metadata:
            if search_string in _metadata.lower():
                selection_of_search_string.append(_metadata)
        if selection_of_search_string:
            self.parent.list_metadata_inner.options = selection_of_search_string
            self.parent.list_metadata_inner.value = selection_of_search_string[0]
            self.parent.save_key_metadata()
        else:
            self.parent.list_metadata_inner.options = ["No Metadata found!"]

    def reset_search_metadata_inner(self, value):
        self.parent.search_inner_field.value = ""
        self.search_metadata_inner_edited({'new': ""})
        o_get = Get(parent=self.parent)
        metadata_inner_value, _ = o_get.default_metadata_selected()
        self.parent.list_metadata_inner.value = metadata_inner_value

    def group_index_changed(self, value):
        new_group_selected = value['new']
        _, new_group_index = new_group_selected.split(" # ")
        o_get = Get(parent=self.parent)
        short_list_files = o_get.list_of_files_basename_only(int(new_group_index))
        self.parent.list_of_files_ui.options = short_list_files
        short_list_new_files = o_get.list_of_new_files_basename_only(np.int(new_group_index))
        self.parent.list_of_new_files_ui.options = short_list_new_files
        self.parent.list_of_new_files_ui.value = short_list_new_files[0]
        self.parent.list_of_files_ui.value = short_list_files[0]

    def list_of_files_changed(self, value):
        dictionary_file_vs_metadata = self.parent.dictionary_file_vs_metadata
        file_selected = value['new']

        # make sure only first file name is used to retrieve key
        list_file_selected = file_selected.split(", ")
        if len(list_file_selected) > 1:
            file_selected = list_file_selected[0]

        full_file_name_selected = os.path.join(self.parent.data_path, file_selected)

        string_to_display = ""
        for _key, _value in dictionary_file_vs_metadata[full_file_name_selected].items():
            string_to_display += "{}: {}\n".format(_key, _value)
        self.parent.metadata_ui.value = string_to_display
        
    def list_of_new_files_changed(self, value):
        new_file_selected = value['new']
        list_of_files_names = self.parent.list_of_files_ui.options
        list_of_new_files_names = self.parent.list_of_new_files_ui.options
        index = list_of_new_files_names.index(new_file_selected)
        file_selected = list_of_files_names[index]
        self.parent.list_of_files_ui.value = file_selected

    def use_excel_file_clicked(self, state):
        # self.parent.output_folder = "/Volumes/G-DRIVE/IPTS/IPTS-28730-gratting-CT"  #REMOVE_ME

        o_file = FileFolderBrowser(working_dir=self.parent.output_folder,
                                   next_function=self.load_excel_file)
        o_file.select_images(instruction="Select Excel file ...",
                             multiple_flag=False,
                             filters={"excel": "*.xls"},
                             default_filter="excel")

    def load_excel_file(self, file_name):
        o_excel = ExcelHandler(parent=self.parent)
        o_excel.load_excel(excel_file=file_name)

    def create_new_excel_clicked(self, state):
        o_excel = ExcelHandler(parent=self.parent)
        o_excel.new_excel()

    def switch_inner_outer_metadata(self, state):
        outer_metadata_selected = self.parent.list_metadata_outer.value
        inner_metadata_selected = self.parent.list_metadata_inner.value

        self.parent.list_metadata_outer.value = inner_metadata_selected
        self.parent.list_metadata_inner.value = outer_metadata_selected
