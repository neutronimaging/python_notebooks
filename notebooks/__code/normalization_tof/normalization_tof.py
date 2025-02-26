import os
from IPython.display import display
import ipywidgets as widgets
from IPython.core.display import HTML

from __code.ipywe.myfileselector import MyFileSelectorPanel
import __code.ipywe.myfileselector as myfileselector
from __code.normalization_tof.normalization_for_timepix import normalization


class NormalizationTof:

    def __init__(self, working_dir=None):
        self.working_dir = working_dir

    def select_sample_folder(self):
        self.select_folder(instruction="Select sample top folder",
                           next_function=self.sample_folder_selected)

    def select_ob_folder(self):
        self.select_folder(instruction="Select ob top folder",
                           next_function=self.ob_folder_selected)

    def select_output_folder(self):
        self.select_folder(instruction="Select output folder",
                           next_function=self.output_folder_selected)

    def run_normalization(self):
        sample_folder = self.sample_folder
        ob_folder = self.ob_folder
        output_folder = self.output_folder
        normalization(sample_folder=sample_folder,
                       ob_folder=ob_folder,
                       output_folder=output_folder,
                       verbose=True)
        display(HTML("<span style='color:blue'>Normalization completed</span>"))
        display(HTML(f"Log file: /SNS/VENUS/shared/logs/normalization_for_timepix.log"))

    # helper functions

    def sample_folder_selected(self, folder_selected):
        self.sample_folder = folder_selected
        display(HTML(f"Sample folder selected: <span style='color:blue'>{folder_selected}</span>"))

    def ob_folder_selected(self, folder_selected):
        self.ob_folder = folder_selected
        display(HTML(f"OB folder selected: <span style='color:blue'>{folder_selected}</span>"))

    def output_folder_selected(self, folder_selected):
        self.output_folder = folder_selected
        display(HTML(f"Output folder selected: <span style='color:blue'>{folder_selected}</span>"))

    def select_folder(self, instruction="Select a folder", next_function=None):

        # go straight to autoreduce/mcp folder
        start_dir = os.path.join(self.working_dir, 'shared', 'autoreduce', 'mcp')
        if not os.path.exists(start_dir):
            start_dir = self.working_dir

        self.list_input_folders_ui = MyFileSelectorPanel(instruction=instruction,
                                                        start_dir=start_dir,
                                                        type='directory',
                                                        multiple=False,
                                                        next=next_function)
        self.list_input_folders_ui.show()
