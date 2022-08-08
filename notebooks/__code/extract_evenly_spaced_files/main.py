import os
from ipywidgets import widgets
from IPython.core.display import display, HTML
import numpy as np

from __code import file_handler
from __code.ipywe.myfileselector import FileSelectorPanelWithJumpFolders
from __code.ipywe.fileselector import FileSelectorPanel
from __code.extract_evenly_spaced_files.get import Get
from __code._utilities.file import retrieve_time_stamp


class ExtractEvenlySpacedFiles(object):
    working_dir = ''
    extract_message = "You are about to extract {} files!"

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_folder(self):
        self.folder_widget = FileSelectorPanel(instruction='select folder with images to combine',
                                               start_dir=self.working_dir,
                                               type='directory',
                                               next=self.retrieve_list_of_files,
                                               multiple=False)
        self.folder_widget.show()

    def retrieve_list_of_files(self, folder_selected):
        [self.list_files, _] = file_handler.retrieve_list_of_most_dominant_extension_from_folder(folder=folder_selected)
        self.folder_of_files_to_extract = folder_selected

        sorting_algorithm = self.sorting_ui.value
        if sorting_algorithm == "File Name":
            self.list_files.sort()
        else:
            retrieve_time_stamp_dict = retrieve_time_stamp(list_images=self.list_files)
            list_time_stamp = retrieve_time_stamp_dict['list_time_stamp']
            index_sorted = np.argsort(list_time_stamp)
            list_files = np.array(self.list_files)
            self.list_files = list_files[index_sorted]

        self.list_of_files_to_extract = self.list_files
        self.basename_list_files = [os.path.basename(_file) for _file in self.list_files]
        self.basename_list_of_files_that_will_be_extracted = [os.path.basename(_file) for _file in self.list_files]
        self.number_of_files = len(self.list_files)
        display(HTML('<span style="font-size: 15px; color:blue">' + str(self.number_of_files) +
                 ' files will be used in the extraction.</span>'))

    def sorting_method(self):
        self.sorting_ui = widgets.RadioButtons(options=["Time", "File Name"],
                                               value="File Name")
        display(self.sorting_ui)

    def how_to_extract(self):
        o_get = Get(parent=self)

        # how to extract
        hori_layout_1 = widgets.HBox([widgets.Label("Extract 1 over ",
                                                    layout=widgets.Layout(width="100px")),
                                      widgets.Dropdown(options=np.arange(1, self.number_of_files),
                                                       value=2,
                                                       layout=widgets.Layout(width="60px")),
                                      widgets.Label("files",
                                                    layout=widgets.Layout(width="20px"))])
        self.extracting_ui = hori_layout_1.children[1]

        # number of files that will be extracted
        hori_layout_2 = widgets.HBox([widgets.Label(self.extract_message.format(
                o_get.number_of_files_to_extract()),
                                                  layout=widgets.Layout(width="40%"))])
        self.extracting_label_ui = hori_layout_2.children[0]

        # list of files that will be extracted
        hori_layout_3 = widgets.HBox([widgets.Label("List of files extracted",
                                                    layout=widgets.Layout(width='20%')),
                                      widgets.Select(options=self.basename_list_files,
                                                     layout=widgets.Layout(width='80%',
                                                                           height='400px'))])
        self.list_of_files_that_will_be_extracted_ui = hori_layout_3.children[1]

        verti_layout = widgets.VBox([hori_layout_1, hori_layout_2, hori_layout_3])
        display(verti_layout)

        self.extracting_ui = hori_layout_1.children[1]
        self.extracting_ui.observe(self.update_extracting_value, names='value')

        self.update_extracting_value(-1)

    def update_extracting_value(self, _):
        o_get = Get(parent=self)
        nbr_files_extracted = o_get.number_of_files_to_extract()
        self.extracting_label_ui.value = self.extract_message.format(nbr_files_extracted)

        list_of_files_that_will_be_extracted = o_get.list_of_files_to_extract()
        self.list_of_files_to_extract = list_of_files_that_will_be_extracted

        basename_list_of_files_that_will_be_extracted = [os.path.basename(_file) for _file in list_of_files_that_will_be_extracted]
        self.list_of_files_that_will_be_extracted_ui.options = basename_list_of_files_that_will_be_extracted
        self.basename_list_of_files_that_will_be_extracted = basename_list_of_files_that_will_be_extracted

    def renaming_checkbox_changed(self, value):
        if value['new']:
            visibility = 'visible'
        else:
            visibility = 'hidden'
        self.left_vertical_layout.layout.visibility = visibility
        self.right_vertical_layout.layout.visibility = visibility

    def prefix_changed(self, new_value):
        o_get = Get(parent=self)
        new_prefix = new_value['new']
        self.renamed_basename_list_of_files = o_get.renamed_basename_list_of_files(prefix=new_prefix)
        self.new_file_name_ui.options = self.renamed_basename_list_of_files

    def renamed_files(self):
        o_get = Get(parent=self)
        self.basename_list_of_files_that_will_be_extracted = self.basename_list_of_files_that_will_be_extracted
        question_widget = widgets.Checkbox(value=True,
                                           description="Rename files?")
        question_widget.observe(self.renaming_checkbox_changed, names='value')
        self.renaming_files_widget = question_widget

        self.prefix_file_name = widgets.Text(value="",
                                             placeholder="Type prefix here",
                                             description="Prefix:")
        self.prefix_file_name.observe(self.prefix_changed, names='value')
        self.renamed_basename_list_of_files = o_get.renamed_basename_list_of_files(prefix=self.prefix_file_name.value)

        self.left_vertical_layout = widgets.VBox([widgets.Label("Before renaming",
                                                                layout=widgets.Layout(width='100%')),
                                                  widgets.Select(
                                                          options=self.basename_list_of_files_that_will_be_extracted,
                                                                 layout=widgets.Layout(width='90%',
                                                                                  height='400px'))],
                                                  layout=widgets.Layout(width='40%'))
        self.right_vertical_layout = widgets.VBox([widgets.Label("After renaming",
                                                                 layout=widgets.Layout(width='100%')),
                                                   widgets.Select(options=self.renamed_basename_list_of_files,
                                                                  layout=widgets.Layout(width='90%',
                                                                                   height='400px'))],
                                                   layout=widgets.Layout(width='40%'))
        self.new_file_name_ui = self.right_vertical_layout.children[1]
        horizontal_layout = widgets.HBox([self.left_vertical_layout,
                                          self.right_vertical_layout])
        full_vertical_layout = widgets.VBox([question_widget,
                                             self.prefix_file_name,
                                             horizontal_layout])
        display(full_vertical_layout)

    def select_output_folder(self):
        self.output_folder_ui = FileSelectorPanelWithJumpFolders(instruction='select where to extract the files',
                                                                 start_dir=self.working_dir,
                                                                 next=self.extract,
                                                                 type='directory',
                                                                 ipts_folder=self.working_dir,
                                                                 newdir_toolbar_button=True)

    def extract(self, output_folder):
        self.output_folder_ui.shortcut_buttons.close()  # hack to hide the buttons

        list_of_files_to_extract = self.list_of_files_to_extract
        full_path_to_file = os.path.dirname(list_of_files_to_extract[0])
        name_of_parent_folder = os.path.basename(full_path_to_file)
        basename_list_of_files_that_will_be_extracted = self.basename_list_of_files_that_will_be_extracted
        fullname_list_of_files_that_will_be_extracted = [os.path.join(full_path_to_file,
                                                                      _file) for _file in basename_list_of_files_that_will_be_extracted]

        extracting_value = self.extracting_ui.value

        new_folder = name_of_parent_folder + "_extracted_1_every_{}_files".format(extracting_value)
        full_output_folder_name = os.path.abspath(os.path.join(output_folder, new_folder))

        file_handler.make_or_reset_folder(full_output_folder_name)
        if self.renaming_files_widget.value:
            list_files_new_name = self.renamed_basename_list_of_files
            display(HTML('<span style="font-size: 15px; color:green">Copying and renaming ' +
                         str(len(list_of_files_to_extract)) +
                         ' files into ' + full_output_folder_name + '... IN PROGRESS!</span>'))

            file_handler.copy_and_rename_files_to_folder(list_files=fullname_list_of_files_that_will_be_extracted,
                                                         new_list_files_names=list_files_new_name,
                                                         output_folder=full_output_folder_name)
            display(HTML('<span style="font-size: 15px; color:blue">' + str(len(list_of_files_to_extract)) +
                         ' files have been copied and renamed into ' + full_output_folder_name + '... DONE!</span>'))
        else:
            display(HTML('<span style="font-size: 15px; color:green">Copying ' + str(len(list_of_files_to_extract)) +
                         ' files into ' + full_output_folder_name + '... IN PROGRESS!</span>'))
            file_handler.copy_files_to_folder(list_files=fullname_list_of_files_that_will_be_extracted,
                                              output_folder=full_output_folder_name)
            display(HTML('<span style="font-size: 15px; color:blue">' + str(len(list_of_files_to_extract)) +
                     ' files have been copied into ' + full_output_folder_name + '</span>'))
