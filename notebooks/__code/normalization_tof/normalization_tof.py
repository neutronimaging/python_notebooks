import os
from IPython.display import display
import ipywidgets as widgets
from IPython.core.display import HTML
import matplotlib.pyplot as plt

from __code.ipywe.myfileselector import MyFileSelectorPanel
from __code.normalization_tof.normalization_for_timepix import normalization, normalization_with_list_of_runs


class NormalizationTof:

    sample_folder = None
    sample_run_numbers = None
    ob_folder = None
    ob_run_numbers = None
    output_folder = None

    def __init__(self, working_dir=None):
        self.working_dir = working_dir
        self.nexus_folder = os.path.join(self.working_dir, 'nexus')

    def select_sample_folder(self):
        self.select_folder(instruction="Select sample top folder",
                           next_function=self.sample_folder_selected)

    def select_sample_run_numbers(self):
        self.select_folder(instruction="Select sample run number folder",
                           next_function=self.sample_run_numbers_selected,
                           multiple=True,)

    def select_ob_folder(self):
        self.select_folder(instruction="Select ob top folder",
                           next_function=self.ob_folder_selected)

    def select_ob_run_numbers(self):
        self.select_folder(instruction="Select ob run number folders",
                           next_function=self.ob_run_numbers_selected,
                           start_dir=self.ob_folder,
                           multiple=True)

    def select_output_folder(self):
        self.select_folder(instruction="Select output folder",
                           start_dir=self.working_dir,
                           next_function=self.output_folder_selected)

    def settings(self):
        label = widgets.Label(value="What to take into account for normalization?")
        display(label)
        self.proton_charge_flag = widgets.Checkbox(description='Proton charge',
                                              value=True)
        self.shutter_counts_flag = widgets.Checkbox(description='Shutter counts',
                                               value=True)
        self.replace_ob_zeros_by_nan_flag = widgets.Checkbox(description='Replace OB zeros by NaN',
                                                  value=False)
        # self.replace_ob_zeros_by_median_flag = widgets.Checkbox(description='Replace OB zeros by median of neighboring pixels',
        #                                                         layout=widgets.Layout(width='100%'))
        vertical_layout = widgets.VBox([self.proton_charge_flag, 
                                        self.shutter_counts_flag, 
                                        self.replace_ob_zeros_by_nan_flag, 
                                        ])
        display(vertical_layout)

    def what_to_export(self):
        display(HTML("<span style='font-size: 16px; color:red'>Stack of images</span>"))
        self.export_corrected_stack_of_sample_data = widgets.Checkbox(description='Export corrected stack of sample data',
                                                                        layout=widgets.Layout(width='100%'),
                                                                    value=False)
        self.export_corrected_stack_of_ob_data = widgets.Checkbox(description='Export corrected stack of ob data',
                                                                        layout=widgets.Layout(width='100%'),
                                             value=False)
        self.export_corrected_stack_of_normalized_data = widgets.Checkbox(description='Export corrected stack of normalized data',
                                                                        layout=widgets.Layout(width='100%'),
                                             value=True,
                                             disabled=True)
        vertical_layout = widgets.VBox([self.export_corrected_stack_of_sample_data,
                                        self.export_corrected_stack_of_ob_data,
                                        self.export_corrected_stack_of_normalized_data,
                                        ])
        display(vertical_layout)
        display(HTML("<span style='font-size: 16px; color:red'>Integrated images</span>"))
        self.export_corrected_integrated_sample_data = widgets.Checkbox(description='Export corrected integrated sample data',
                                                                        layout=widgets.Layout(width='100%'),
                                              value=False)
        self.export_corrected_integrated_ob_data = widgets.Checkbox(description='Export corrected integrated ob data',
                                                                 layout=widgets.Layout(width='100%'),
                                               value=False)
        self.export_corrected_integrated_normalized_data = widgets.Checkbox(description='Export corrected integrated normalized data',
                                                                        layout=widgets.Layout(width='100%'),
                                               value=False)
        vertical_layout = widgets.VBox([self.export_corrected_integrated_sample_data,
                                        self.export_corrected_integrated_ob_data,
                                        self.export_corrected_integrated_normalized_data,
                                        ])
        
        display(vertical_layout)

    def run_normalization_with_list_of_runs(self, preview=False):
        sample_run_numbers = self.sample_run_numbers
        ob_run_numbers = self.ob_run_numbers
        output_folder = self.output_folder
        export_mode = {'sample_stack': self.export_corrected_stack_of_sample_data.value,
                       'ob_stack': self.export_corrected_stack_of_ob_data.value,
                       'normalized_stack': self.export_corrected_stack_of_normalized_data.value,
                       'sample_integrated': self.export_corrected_integrated_sample_data.value,
                       'ob_integrated': self.export_corrected_integrated_ob_data.value,
                       'normalized_integrated': self.export_corrected_integrated_normalized_data.value,}
        normalization_with_list_of_runs(sample_run_numbers=sample_run_numbers,
                                        ob_run_numbers=ob_run_numbers,
                                        output_folder=output_folder,
                                        nexus_path=self.nexus_folder,
                                        proton_charge_flag=self.proton_charge_flag.value,
                                        shutter_counts_flag=self.shutter_counts_flag.value,
                                        replace_ob_zeros_by_nan_flag=self.replace_ob_zeros_by_nan_flag.value,
                                        verbose=True,
                                        preview=preview,
                                        export_mode=export_mode)
        display(HTML("<span style='color:blue'>Normalization completed</span>"))
        display(HTML(f"Log file: /SNS/VENUS/shared/logs/normalization_for_timepix.log"))

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

    def sample_run_numbers_selected(self, runs_selected):
        self.sample_run_numbers = runs_selected
        display(HTML(f"Sample run numbers selected: <span style='color:blue'>{', '.join(runs_selected)}</span>"))

    def ob_folder_selected(self, folder_selected):
        self.ob_folder = folder_selected
        display(HTML(f"OB folder selected: <span style='color:blue'>{folder_selected}</span>"))

    def ob_run_numbers_selected(self, folder_selected):
        self.ob_run_numbers = folder_selected
        display(HTML(f"OB run numbers selected: <span style='color:blue'>{', '.join(folder_selected)}</span>"))

    def output_folder_selected(self, folder_selected):
        self.output_folder = folder_selected
        display(HTML(f"Output folder selected: <span style='color:blue'>{folder_selected}</span>"))

    def select_folder(self, instruction="Select a folder", next_function=None, start_dir=None, multiple=False):

        # go straight to autoreduce/mcp folder
        if start_dir is None:
            start_dir = os.path.join(self.working_dir, 'shared', 'autoreduce', 'mcp', 'images')
        
        self.list_input_folders_ui = MyFileSelectorPanel(instruction=instruction,
                                                        start_dir=start_dir,
                                                        type='directory',
                                                        multiple=multiple,
                                                        sort_increasing=False,
                                                        next=next_function)
        self.list_input_folders_ui.show()
