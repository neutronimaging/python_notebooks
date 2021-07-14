import webbrowser
from ipywidgets import widgets
from IPython.core.display import display
from __code.ipywe import fileselector

from NeuNorm.normalization import Normalization


class FileSelection:

    def __init__(self, working_dir='./'):
        self.working_dir = working_dir

    def select_file_help(self, value):
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/file_selector/#select_profile")

    def load_files(self, files):
        o_norm = Normalization()
        o_norm.load(file=files, notebook=True)
        self.data_dict = o_norm.data

    def select_data(self):
        help_ui = widgets.Button(description="HELP",
                                 button_style='info')
        help_ui.on_click(self.select_file_help)
        display(help_ui)

        self.files_ui = fileselector.FileSelectorPanel(instruction='Select Images ...',
                                                       start_dir=self.working_dir,
                                                       next=self.load_files,
                                                       multiple=True)

        self.files_ui.show()

    def close(self):
        self.parent.registration_tool_ui = None
