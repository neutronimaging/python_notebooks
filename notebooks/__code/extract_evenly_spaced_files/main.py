import os
from ipywidgets import widgets
from IPython.core.display import display, HTML
import numpy as np

from __code import file_handler
from __code.ipywe import fileselector


class ExtractEvenlySpacedFiles(object):
    working_dir = ''
    extract_message = "You are about to extract {} files!"

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_folder(self):
        self.folder_widget = fileselector.FileSelectorPanel(instruction='select folder with images to combine',
                                                            start_dir=self.working_dir,
                                                            type='directory',
                                                            next=self._retrieve_list_of_files,
                                                            multiple=False)
        self.folder_widget.show()

    def get_number_of_files_to_extract(self):
        extracting_value = self.extracting_ui.value
        nbr_files = self.number_of_files
        return np.int(nbr_files / extracting_value)

    def get_list_of_files_to_extract(self):
        extracting_value = self.extracting_ui.value
        list_of_files = self.list_files
        nbr_files = self.number_of_files
        array_of_indexes = np.arange(1,nbr_files, extracting_value)

        list_of_files_to_extract = []
        for _index in array_of_indexes:
            list_of_files_to_extract.append(list_of_files[_index])

        return list_of_files_to_extract

    def _retrieve_list_of_files(self, folder_selected):
        [self.list_files, _] = file_handler.retrieve_list_of_most_dominant_extension_from_folder(folder=folder_selected)
        self.list_of_files_to_extract = self.list_files
        self.basename_list_files = [os.path.basename(_file) for _file in self.list_files]
        self.basename_list_of_files_that_will_be_extracted = [os.path.basename(_file) for _file in self.list_files]
        self.number_of_files = len(self.list_files)
        display(HTML('<span style="font-size: 15px; color:blue">' + str(self.number_of_files) +
                 ' files will be used in the extraction.</span>'))

    def how_to_extract(self):
        # how to extract
        hori_layout_1 = widgets.HBox([widgets.Label("Extract 1 over ",
                                                    layout=widgets.Layout(width="10%")),
                                      widgets.Dropdown(options=np.arange(1, self.number_of_files),
                                                       value=2,
                                                       layout=widgets.Layout(width="5%")),
                                      widgets.Label("files",
                                                    layout=widgets.Layout(width="10%"))])
        self.extracting_ui = hori_layout_1.children[1]

        # number of files that will be extracted
        hori_layout_2 = widgets.HBox([widgets.Label(self.extract_message.format(self.get_number_of_files_to_extract()),
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

    def update_extracting_value(self, _):
        nbr_files_extracted = self.get_number_of_files_to_extract()
        self.extracting_label_ui.value = self.extract_message.format(nbr_files_extracted)

        list_of_files_that_will_be_extracted = self.get_list_of_files_to_extract()
        self.list_of_files_to_extract = list_of_files_that_will_be_extracted

        basename_list_of_files_that_will_be_extracted = [os.path.basename(_file) for _file in list_of_files_that_will_be_extracted]
        self.list_of_files_that_will_be_extracted_ui.options = basename_list_of_files_that_will_be_extracted
        self.basename_list_of_files_that_will_be_extracted = basename_list_of_files_that_will_be_extracted

    def get_renamed_basename_list_of_files(self):
        list_of_files_to_extract = self.basename_list_of_files_that_will_be_extracted

        renamed_list_of_files_to_extract = []
        for _counter, _file in enumerate(list_of_files_to_extract):
            [_name, ext] = os.path.splitext(_file)
            _name_split = _name.split('_')
            new_name = "_".join(_name_split[:-1]) + "_{:04d}{}".format(_counter, ext)
            renamed_list_of_files_to_extract.append(new_name)
        return renamed_list_of_files_to_extract

    def renaming_checkbox_changed(self, value):
        if value['new']:
            visibility = 'visible'
        else:
            visibility = 'hidden'
        self.left_vertical_layout.layout.visibility = visibility
        self.right_vertical_layout.layout.visibility = visibility

    def renamed_files(self):
        self.renamed_basename_list_of_files = self.get_renamed_basename_list_of_files()
        basename_list_of_files_that_will_be_extracted = self.basename_list_of_files_that_will_be_extracted
        question_widget = widgets.Checkbox(value=True,
                                           description="Rename files?")
        question_widget.observe(self.renaming_checkbox_changed, names='value')
        self.renaming_files_widget = question_widget

        self.left_vertical_layout = widgets.VBox([widgets.Label("Before renaming",
                                                                layout=widgets.Layout(width='100%')),
                                                  widgets.Select(options=basename_list_of_files_that_will_be_extracted,
                                                                 layout=widgets.Layout(width='90%',
                                                                                  height='400px'))],
                                                  layout=widgets.Layout(width='40%'))
        self.right_vertical_layout = widgets.VBox([widgets.Label("After renaming",
                                                                 layout=widgets.Layout(width='100%')),
                                                   widgets.Select(options=self.renamed_basename_list_of_files,
                                                                  layout=widgets.Layout(width='90%',
                                                                                   height='400px'))],
                                                   layout=widgets.Layout(width='40%'))
        horizontal_layout = widgets.HBox([self.left_vertical_layout, self.right_vertical_layout])
        full_vertical_layout = widgets.VBox([question_widget, horizontal_layout])
        display(full_vertical_layout)

    def select_output_folder(self):
        self.output_folder_ui = fileselector.FileSelectorPanelWithJumpFolders(instruction='select where to extract the files',
                                                                              start_dir=self.working_dir,
                                                                              next=self.extract,
                                                                              type='directory',
                                                                              ipts_folder=self.working_dir,
                                                                              newdir_toolbar_button=True)

    def extract(self, output_folder):

        self.output_folder_ui.shortcut_buttons.close()  # hack to hide the buttons

        list_of_files_to_extract = self.list_of_files_to_extract
        name_of_parent_folder = os.path.basename(os.path.dirname(list_of_files_to_extract[0]))
        extracting_value = self.extracting_ui.value

        new_folder = name_of_parent_folder + "_extracted_1_every_{}_files".format(extracting_value)
        full_output_folder_name = os.path.abspath(os.path.join(output_folder, new_folder))

        file_handler.make_or_reset_folder(full_output_folder_name)
        if self.renaming_files_widget.value:
            list_files_new_name = self.renamed_basename_list_of_files
            display(HTML('<span style="font-size: 15px; color:green">Copying and renaming ' + str(len(list_of_files_to_extract)) +
                         ' files into ' + full_output_folder_name + '... IN PROGRESS!</span>'))
            file_handler.copy_and_rename_files_to_folder(list_files=list_of_files_to_extract,
                                                         new_list_files_names=list_files_new_name,
                                                         output_folder=full_output_folder_name)
            display(HTML('<span style="font-size: 15px; color:blue">' + str(len(list_of_files_to_extract)) +
                         ' files have been copied and renamed into ' + full_output_folder_name + '... DONE!</span>'))
        else:
            display(HTML('<span style="font-size: 15px; color:green">Copying ' + str(len(list_of_files_to_extract)) +
                         ' files into ' + full_output_folder_name + '... IN PROGRESS!</span>'))
            file_handler.copy_files_to_folder(list_files=list_of_files_to_extract,
                                              output_folder=full_output_folder_name)
            display(HTML('<span style="font-size: 15px; color:blue">' + str(len(list_of_files_to_extract)) +
                     ' files have been copied into ' + full_output_folder_name + '</span>'))
