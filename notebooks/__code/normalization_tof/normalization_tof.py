import os
from IPython.display import display
import ipywidgets as widgets
from IPython.core.display import HTML
import matplotlib.pyplot as plt
import logging as notebook_logging
import numpy as np
import logging
import glob

from ipywidgets import interactive
import ipywidgets as widgets
from IPython.core.display import display, HTML

# from __code.ipywe.myfileselector import MyFileSelectorPanel
from __code.ipywe.fileselector import FileSelectorPanel as MyFileSelectorPanel
from __code.normalization_tof.normalization_for_timepix import (normalization, 
                                                                normalization_with_list_of_runs, 
                                                                load_data_using_multithreading,
                                                                retrieve_list_of_tif)
from __code.normalization_tof.config import DEBUG_DATA
from __code.normalization_tof import autoreduce_dir, distance_source_detector_m

# LOG_PATH = "/SNS/VENUS/shared/log/"
# file_name, ext = os.path.splitext(os.path.basename(__file__))
# user_name = os.getlogin() # add user name to the log file name
# log_file_name = os.path.join(LOG_PATH, f"{user_name}_{file_name}.log")
# notebook_logging.basicConfig(filename=log_file_name,
#                     filemode='w',
#                     format='[%(levelname)s] - %(asctime)s - %(message)s',
#                     level=notebook_logging.INFO)
# notebook_logging.info(f"*** Starting a new script {file_name} ***")



class NormalizationTof:

    sample_folder = None
    sample_run_numbers = None
    ob_folder = None
    ob_run_numbers = None
    output_folder = None

    dict_ob_runs = None 
    dict_ob_data = None

    LOG_PATH = "/SNS/VENUS/shared/log/"
    file_name, ext = os.path.splitext(os.path.basename(__file__))
    user_name = os.getlogin() # add user name to the log file name
    log_file_name = os.path.join(LOG_PATH, f"{user_name}_{file_name}.log")
    print(f"Log file name: {log_file_name}")
    notebook_logging.basicConfig(filename=log_file_name,
                        filemode='w',
                        format='[%(levelname)s] - %(asctime)s - %(message)s',
                        level=notebook_logging.INFO)
    notebook_logging.info(f"*** Starting a new script {file_name} ***")

    def __init__(self, working_dir=None, debug=False):

        print(f"Working dir: {working_dir}")

        if debug:
            self.working_dir = DEBUG_DATA.working_dir
            self.output_dir = DEBUG_DATA.output_folder
        else:
            self.working_dir = working_dir
            self.output_dir = os.path.join(self.working_dir, 'shared')
        
        self.nexus_folder = os.path.join(self.working_dir, 'nexus')
        self.debug = debug
        _, _facility, _beamline, ipts = self.working_dir.split('/')


        self.ipts = ipts
        self.instrument = _beamline.upper()
        self.autoreduce_dir = autoreduce_dir[_beamline][0] + str(ipts) + autoreduce_dir[_beamline][1]
        if os.path.exists(self.autoreduce_dir):
            display(HTML(f"Autoreduce folder found: <span style='color:green'>{self.autoreduce_dir}</span>"))
            notebook_logging.info(f"Autoreduce folder found: {self.autoreduce_dir}")
        else:
            display(HTML(f"<span style='color:red'>Autoreduce folder {self.autoreduce_dir} DOES NOT EXIST!</span>"))
            notebook_logging.info(f"Autoreduce folder {self.autoreduce_dir} DOES NOT EXIST!")
            display(HTML(f"<span style='color:red'>Make sure you selected the right INSTRUMENT and IPTS!</span>"))
            
    def manually_set_runs(self):
       
        if self.debug:
            sample_runs = DEBUG_DATA.sample_runs_selected
            sample_run_numbers_list = []
            for _run in sample_runs:
                _, number = _run.split('_')
                sample_run_numbers_list.append(number)
            str_sample_run_numbers = ', '.join(sample_run_numbers_list)

            ob_runs = DEBUG_DATA.ob_runs_selected
            ob_run_numbers_list = []
            for _run in ob_runs:
                _, number = _run.split('_')
                ob_run_numbers_list.append(number)
            str_ob_run_numbers = ', '.join(ob_run_numbers_list)
        
            output_folder = DEBUG_DATA.output_folder

        else:
            str_sample_run_numbers = ""
            str_ob_run_numbers = ""
            # output_folder = os.path.join(self.working_dir, 'shared')
            output_folder = ""

        sample_label = widgets.Label(value="List of sample run numbers (ex: 8702, 8704)")
        self.sample_run_numbers_widget = widgets.Textarea(value=str_sample_run_numbers,
                                                    placeholder="",
                                                    layout=widgets.Layout(width='400px'))
        ob_label = widgets.Label(value="List of ob run numbers (ex: 8703, 8705)")
        self.ob_run_numbers_widget = widgets.Textarea(value=str_ob_run_numbers,
                                                placeholder="",
                                                layout=widgets.Layout(width='400px'))
        output_label = widgets.Label(value="Output folder")
        self.output_folder_widget = widgets.Text(value=output_folder,
                                          placeholder="",
                                          layout=widgets.Layout(width='400px'))
        vertical_layout = widgets.VBox([sample_label, self.sample_run_numbers_widget,
                                        ob_label, self.ob_run_numbers_widget,
                                        output_label, self.output_folder_widget,])
        display(vertical_layout)
        
        # if self.instrument != "SNAP":
        #     display(HTML("<span style='font-size: 16px; color:red'>You have the option here to enter the runs manually or just use the widgets (following cells) to define them!</span>"))
        #     display(vertical_layout)

        # else:
        #     display(HTML("<span style='font-size: 16px; color:red'>Manual entry of runs is not available for SNAP instrument!</span>"))

    def select_sample_folder(self):
        self.select_folder(instruction="Select sample top folder",
                           next_function=self.sample_folder_selected)

    def select_sample_run_numbers(self):
        if self.sample_run_numbers_widget.value.strip() != "":
            sample_run_numbers = self.sample_run_numbers_widget.value.split(',')
            list_sample_run_numbers = [f"Run_{_run.strip()}" for _run in sample_run_numbers]
            list_sample_runs_full_path = [os.path.join(self.autoreduce_dir, _sample) for _sample in list_sample_run_numbers]
            self.sample_run_numbers_selected(list_sample_runs_full_path)
        else:
            self.select_folder(instruction="Select sample run number folder",
                               next_function=self.sample_run_numbers_selected,
                               multiple=True,)

    def select_ob_folder(self):
            self.select_folder(instruction="Select ob top folder",
                            next_function=self.ob_folder_selected)

    def select_ob_run_numbers(self):
        if self.ob_run_numbers_widget.value.strip() != "":
            ob_run_numbers = self.ob_run_numbers_widget.value.split(',')
            list_ob_run_numbers = [f"Run_{_run.strip()}" for _run in ob_run_numbers]
            list_ob_runs_full_path = [os.path.join(self.autoreduce_dir, _ob) for _ob in list_ob_run_numbers]
            self.ob_run_numbers_selected(list_ob_runs_full_path)
        else:    
            self.select_folder(instruction="Select ob run number folders",
                               next_function=self.ob_run_numbers_selected,
                               start_dir=self.ob_folder,
                               multiple=True)

    def _load_and_get_integrated_ob(self, ob_run):
        """
        Load the integrated open beam data from the given OB run path.
        This function is a placeholder and should be implemented to load the actual data.
        """
        logging.info(f"Loading integrated OB data for {ob_run}")
        # Here you would load the integrated OB data, for example using a specific library
        # For now, we will just return a dummy value
        if self.dict_ob_data.get(ob_run, None) is None:
            logging.info("No data found for this OB run, loading it now...")
            # load the data from the OB run
            logging.info(f"\tFull path to OB run: {ob_run}")
            full_path = self.dict_ob_runs.get(ob_run)
            list_tiff = retrieve_list_of_tif(full_path)
            logging.info(f"\tNumber of TIFF files found: {len(list_tiff)}")
            if len(list_tiff) == 0:
                display(HTML(f"<span style='color:red'>No TIFF files found in {full_path}!</span>"))
                notebook_logging.error(f"No TIFF files found in {full_path}!")
                return None
            data = load_data_using_multithreading(list_tiff, combine_tof=True)
            self.dict_ob_data[ob_run] = data
      
        return self.dict_ob_data[ob_run]

    def preview_ob_runs(self):
        if self.ob_run_numbers is None or len(self.ob_run_numbers) == 0:
            display(HTML("<span style='color:red'>No OB runs selected!</span>"))
            return

        logging.info(f"Previewing OB runs: {self.ob_run_numbers}")
        
        nbr_ob_runs = len(self.ob_run_numbers)
        list_ob_short_runs = [os.path.basename(_run) for _run in self.ob_run_numbers]
        self.dict_ob_runs = {_short_name: _full_name for _short_name, _full_name in zip(list_ob_short_runs, self.ob_run_numbers)}
        self.dict_ob_data = {_short_name: None for _short_name in list_ob_short_runs}

        if nbr_ob_runs == 1:
        
            logging.info(f"Only one OB run")
            full_path = self.dict_ob_runs.get(list_ob_short_runs[0])
            logging.info(f"\tFull path to OB run: {full_path}")
            integrated_ob = self._load_and_get_integrated_ob(list_ob_short_runs[0])
            if integrated_ob is None:
                display(HTML(f"<span style='color:red'>Failed to load integrated OB data for {list_ob_short_runs[0]}!</span>"))
                return
            fig, ax = plt.subplots(figsize=(10, 6))
            im = ax.imshow(integrated_ob, cmap='viridis', aspect='auto')
            ax.set_title(f"Integrated OB run: {list_ob_short_runs[0]}")
            fig.colorbar(im, ax=ax, orientation='vertical', label='Intensity')
            plt.show()
        
        else:

            logging.info(f"Multiple OB runs to display: {nbr_ob_runs}")
            def display_ob_run(ob_run):
                """
                Display the integrated OB run data.
                """
                full_path = self.dict_ob_runs.get(ob_run)
                integrated_ob = self._load_and_get_integrated_ob(ob_run)
                if integrated_ob is None:
                    display(HTML(f"<span style='color:red'>Failed to load integrated OB data for {ob_run}!</span>"))
                    return
                fig, ax = plt.subplots(figsize=(10, 6))
                im = ax.imshow(integrated_ob, cmap='viridis', aspect='auto')
                ax.set_title(f"Integrated OB run: {ob_run}")
                fig.colorbar(im, ax=ax, orientation='vertical', label='Intensity')
                plt.show()

            _display = interactive(display_ob_run,
                                   ob_run=widgets.Dropdown(
                                       options=list_ob_short_runs,
                                       description='OB run:',
                                       disabled=False,)
            )
            display(_display)
      
    def select_output_folder(self):
        if self.instrument == "SNAP":
            self.select_folder(instruction="Select output folder",
                            start_dir=self.working_dir,
                            next_function=self.output_folder_selected)

        else:
            if self.output_folder_widget.value.strip() != "":
                self.output_folder = self.output_folder_widget.value
                self.output_folder_selected(self.output_folder)
            else:
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
                                                  value=True)

        vertical_layout = widgets.VBox([self.proton_charge_flag, 
                                        self.shutter_counts_flag, 
                                        self.replace_ob_zeros_by_nan_flag, 
                                        ])
        display(vertical_layout)

        display(HTML("<hr>"))

        label = widgets.Label(value="Distance source detector (m)", 
                              layout=widgets.Layout(width='200px'))
        self.distance_source_detector = widgets.FloatText(value=distance_source_detector_m[self.instrument],
                                                          disabled=False,
                                                          layout=widgets.Layout(width='50px'))
        hori_layout = widgets.HBox([label, self.distance_source_detector])
        display(hori_layout)        

        if self.instrument == "SNAP":
            label = widgets.Label(value="Detector offset (us)",
                                layout=widgets.Layout(width='200px'))
            self.detector_offset_us = widgets.FloatText(value=0.0,
                                                        disabled=False,
                                                        layout=widgets.Layout(width='50px'))
            hori_layout = widgets.HBox([label, self.detector_offset_us])
            display(hori_layout)
        
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

    def check_folder_is_valid(self, full_path):
        list_tiff = glob.glob(os.path.join(full_path, "*.tif*"))
        if list_tiff:
            return True, {'nbr_tiff': len(list_tiff)}
        else:
            return False, {'nbr_tiff': 0}

    def sample_folder_selected(self, folder_selected):
        self.sample_folder = folder_selected
        display(HTML(f"Sample folder selected: <span style='color:blue'>{folder_selected}</span>"))

    def sample_run_numbers_selected(self, runs_selected):
        self.sample_run_numbers = runs_selected
        display(HTML(f"Sample run numbers selected:"))
        notebook_logging.info(f"Sample run numbers selected: {runs_selected}")
        for _run in runs_selected:
            if os.path.exists(_run):
                notebook_logging.info(f"\tSample run number {_run} - FOUND")
                # check here that the folder is not empty (contains tiff)
                is_valid_run, report_dict = self.check_folder_is_valid(_run)
                if is_valid_run:
                    nbr_tiff = report_dict['nbr_tiff']
                    display(HTML(f"<span style='color:green'>{_run}</span>"))
                    notebook_logging.info(f"\tfolder seems to be a valid folder containing {nbr_tiff} tif* files")
                else:
                    display(HTML(f"<span style='color:red'>{_run} - EMPTY!</span>"))
            else:
                display(HTML(f"<span style='color:red'>{_run} - NOT FOUND!</span>"))
                notebook_logging.info(f"\tSample run number {_run} - NOT FOUND!")

    def ob_folder_selected(self, folder_selected):
        self.ob_folder = folder_selected
        display(HTML(f"Open beam folder selected: <span style='color:blue'>{folder_selected}</span>"))

    def ob_run_numbers_selected(self, folder_selected):
        self.ob_run_numbers = folder_selected
        display(HTML(f"OB folder selected:"))
        notebook_logging.info(f"OB folder selected: {folder_selected}")
        for _run in folder_selected:
            if os.path.exists(_run):
                notebook_logging.info(f"\tOB run number {_run} - FOUND")
                is_valid_run, report_dict = self.check_folder_is_valid(_run)
                if is_valid_run:
                    nbr_tiff = report_dict['nbr_tiff']
                    display(HTML(f"<span style='color:green'>{_run}</span>"))
                    notebook_logging.info(f"\tfolder seems to be a valid folder containing {nbr_tiff} tif* files")
                else:
                    display(HTML(f"<span style='color:red'>{_run} - EMPTY!</span>"))
            else:
                display(HTML(f"<span style='color:red'>{_run} - NOT FOUND!</span>"))
                notebook_logging.info(f"\tOB run number {_run} - NOT FOUND!")

    def output_folder_selected(self, folder_selected):
        self.output_folder = folder_selected
        display(HTML(f"Output folder selected:"))
        if os.path.exists(folder_selected):
            display(HTML(f"<span style='color:green'>{folder_selected} - FOUND!</span>"))
            notebook_logging.info(f"Output folder selected: {folder_selected} - FOUND")
        else:
            display(HTML(f"<span style='color:blue'>{folder_selected} - DOES NOT EXIST and will be CREATED!</span>"))
            notebook_logging.info(f"Output folder selected: {folder_selected} - NOT FOUND and will be CREATED!")

    def select_folder(self, instruction="Select a folder", next_function=None, start_dir=None, multiple=False):

        # go straight to autoreduce/mcp folder
        if start_dir is None:
            start_dir = self.autoreduce_dir

        self.list_input_folders_ui = MyFileSelectorPanel(instruction=instruction,
                                                        start_dir=start_dir,
                                                        type='directory',
                                                        multiple=multiple,
                                                        sort_in_reverse=True,
                                                        # sort_increasing=False,
                                                        next=next_function)
        self.list_input_folders_ui.show()

    # calling main code
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
        
        detecor_delay_us = None
        if self.instrument == "SNAP":
            detecor_delay_us = self.detector_offset_us.value
     
        normalization_with_list_of_runs(sample_run_numbers=sample_run_numbers,
                                        ob_run_numbers=ob_run_numbers,
                                        output_folder=output_folder,
                                        nexus_path=self.nexus_folder,
                                        proton_charge_flag=self.proton_charge_flag.value,
                                        shutter_counts_flag=self.shutter_counts_flag.value,
                                        replace_ob_zeros_by_nan_flag=self.replace_ob_zeros_by_nan_flag.value,
                                        verbose=True,
                                        instrument=self.instrument,
                                        detector_delay_us=detecor_delay_us,
                                        preview=preview,
                                        distance_source_detector_m=self.distance_source_detector.value,
                                        export_mode=export_mode)
        display(HTML("<span style='color:blue'>Normalization completed</span>"))
        display(HTML(f"Log file: /SNS/VENUS/shared/logs/normalization_for_timepix.log"))
