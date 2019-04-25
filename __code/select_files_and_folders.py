from IPython.display import display
from IPython.core.display import HTML

from __code.file_folder_browser import FileFolderBrowser
from __code.utilities import display_html_message


class SelectFiles(FileFolderBrowser):

    list_of_files = []

    def __init__(self, system=None):
        working_dir = system.System.get_working_dir()

        super(SelectFiles, self).__init__(working_dir=working_dir,
                                          next_function=self.retrieve_list_of_files)

        filters = {"TIFF": "*.tif"}
        default_filter = "TIFF"
        self.select_images(filters=filters,
                           default_filter=default_filter)

    def retrieve_list_of_files(self, list_of_files=''):
        self.list_of_files = list_of_files


class SelectFolder(FileFolderBrowser):

    def __init__(self, system=None, next_function=None):
        working_dir = system.System.get_working_dir()

        super(SelectFolder, self).__init__(working_dir=working_dir,
                                           next_function=next_function)

        self.select_output_folder()


class SelectAsciiFile(FileFolderBrowser):

    ascii_file = ''

    def __init__(self, system=None, instruction=''):
        working_dir = system.System.get_working_dir()

        super(SelectAsciiFile, self).__init__(working_dir=working_dir,
                                              next_function=self.done_message)

        if not instruction:
            instruction = "Select ASCII File!"
        filters = {"Text": "*.txt"}
        default_filter = "Text"

        self.select_images(filters=filters,
                           instruction=instruction,
                           multiple_flag=False,
                           default_filter=default_filter)

    def done_message(self, file_selected):
        self.ascii_file = file_selected
        display_html_message(title_message='Selected Ascii File:',
                             message=file_selected)
