import os
from IPython.display import display
from ipywidgets import widgets
from IPython.core.display import HTML
import ipywe.fileselector

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


class SelectFolderWithDefaultPaths(FileFolderBrowser):

    def __init__(self, system=None, next_function=None):
        working_dir = system.System.get_working_dir()

        super(SelectFolderWithDefaultPaths, self).__init__(working_dir=working_dir,
                                                           next_function=next_function)

        ipts = os.path.basename(self.working_dir)

        button_layout = widgets.Layout(width='30%',
                                       border='1px solid gray')

        hbox = widgets.HBox([widgets.Button(description="Jump to {} Shared Folder".format(ipts),
                                            button_style='success',
                                            layout=button_layout),
                             widgets.Button(description="Jump to My Home Folder",
                                            button_style='success',
                                            layout=button_layout)])
        go_to_shared_button_ui = hbox.children[0]
        go_to_home_button_ui = hbox.children[1]

        go_to_shared_button_ui.on_click(self.display_file_selector_from_shared)
        go_to_home_button_ui.on_click(self.display_file_selector_from_home)

        display(hbox)

        self.display_file_selector()

    def display_file_selector_from_shared(self, ev):
        start_dir = os.path.join(self.working_dir, 'shared')
        self.output_folder_ui.remove()
        self.display_file_selector(start_dir=start_dir)

    def display_file_selector_from_home(self, ev):
        import getpass
        _user = getpass.getuser()
        start_dir = os.path.join('/SNS/users', _user)
        self.output_folder_ui.remove()
        self.display_file_selector(start_dir=start_dir)

    def display_file_selector(self, start_dir=''):
        self.output_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Output Folder',
                                                                start_dir=start_dir,
                                                                multiple=False,
                                                                next=self.next_function,
                                                                type='directory')
        self.output_folder_ui.show()


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
