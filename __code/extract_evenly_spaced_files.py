import os
from ipywidgets import widgets
from IPython.core.display import display, HTML
import numpy as np

import ipywe.fileselector

from __code import file_handler
from __code import fileselector


class ExtractEvenlySpacedFiles(object):
    working_dir = ''
    extract_message = "You are about to extract {} files!"

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_folder(self):
        self.folder_widget = ipywe.fileselector.FileSelectorPanel(instruction='select folder with images to combine',
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
        [self.list_files, _] = file_handler.retrieve_list_of_most_dominand_extension_from_folder(folder=folder_selected)
        self.number_of_files = len(self.list_files)
        display(HTML('<span style="font-size: 15px; color:blue">' + str(self.number_of_files) +
                 ' files will be used in the extraction.</span>'))


    def how_to_extract(self):
        # how to extract
        hori_layout_1 = widgets.HBox([widgets.Label("Extract 1 over ",
                                                    layout=widgets.Layout(width="10%")),
                                      widgets.Dropdown(options=np.arange(1, self.number_of_files),
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
                                                    layout=widgets.Layout(width='10%')),
                                      widgets.Select(options=self.list_files,
                                                     layout=widgets.Layout(width='50%',
                                                                           height='200px'))])
        self.list_of_files_that_will_be_extracted_ui = hori_layout_3.children[1]

        verti_layout = widgets.VBox([hori_layout_1, hori_layout_2, hori_layout_3])
        display(verti_layout)

        self.extracting_ui = hori_layout_1.children[1]
        self.extracting_ui.observe(self.update_extracting_value, names='value')

    def update_extracting_value(self, _):
        nbr_files_extracted = self.get_number_of_files_to_extract()
        self.extracting_label_ui.value = self.extract_message.format(nbr_files_extracted)

        list_of_files_that_will_be_extracted = self.get_list_of_files_to_extract()
        self.list_of_files_that_will_be_extracted_ui.options = list_of_files_that_will_be_extracted
        self.list_of_files_to_extract = list_of_files_that_will_be_extracted

    def select_output_folder(self):
        self.output_folder_ui = fileselector.FileSelectorPanelWithJumpFolders(instruction='select where to extract the files',
                                                                              start_dir=self.working_dir,
                                                                              next=self.extract,
                                                                              type='directory',
                                                                              newdir_toolbar_button=True)

    def extract(self, output_folder):
        list_of_files_to_extract = self.list_of_files_to_extract
        name_of_parent_folder = os.path.basename(os.path.dirname(list_of_files_to_extract[0]))
        extracting_value = self.extracting_ui.value

        new_folder = name_of_parent_folder + "_extracted_1_every_{}_files".format(extracting_value)
        full_output_folder_name = os.path.abspath(os.path.join(output_folder, new_folder))


