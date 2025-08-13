import os
from IPython.display import display
import ipywidgets as widgets
from IPython.core.display import HTML
import matplotlib.pyplot as plt
import logging as notebook_logging
import numpy as np
import logging
import glob
from pathlib import Path
import warnings

from ipywidgets import interactive
import ipywidgets as widgets
from IPython.core.display import display, HTML

from __code._utilities.list import extract_list_of_runs_from_string
from __code._utilities.nexus import extract_file_path_from_nexus

# from __code.ipywe.myfileselector import MyFileSelectorPanel
from __code.ipywe.fileselector import FileSelectorPanel as MyFileSelectorPanel
from __code.normalization_tof.normalization_for_timepix import (normalization, 
                                                                normalization_with_list_of_runs, 
                                                                load_data_using_multithreading,
                                                                retrieve_list_of_tif)
from __code.normalization_tof.config import DEBUG_DATA
from __code.normalization_tof import autoreduce_dir, distance_source_detector_m
from __code.normalization_tof import DetectorType, raw_dir, autoreduce_dir


LOG_PATH = "/SNS/VENUS/shared/log/"
file_name, ext = os.path.splitext(os.path.basename(__file__))
user_name = os.getlogin() # add user name to the log file name
log_file_name = os.path.join(LOG_PATH, f"{user_name}_{file_name}.log")
notebook_logging.basicConfig(filename=log_file_name,
                    filemode='w',
                    format='[%(levelname)s] - %(asctime)s - %(message)s',
                    level=notebook_logging.INFO)
notebook_logging.info(f"*** Starting a new script {file_name} ***")


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
       
        # self.autoreduce_dir = autoreduce_dir[_beamline][0] + str(ipts) + autoreduce_dir[_beamline][1]
        # self.shared_dir = str(Path(shared_dir[self.instrument][0]) / str(ipts) / shared_dir[self.instrument][1])
        self.shared_dir = Path("/") / _facility / self.instrument / str(ipts) / "shared"

        logging.info(f"Instrument: {self.instrument}")
        logging.info(f"Working dir: {self.working_dir}")
        logging.info(f"IPTS: {self.ipts}")
        logging.info(f"facility: {_facility}")
        logging.info(f"nexus folder: {self.nexus_folder}")
        logging.info(f"Shared dir: {self.shared_dir}")

        display(HTML(f"<span style='color:blue; font-size:16px'>Select detector type</span>"))
        self.detector_type_widget = widgets.Dropdown(
            options=[DetectorType.tpx1_legacy, DetectorType.tpx1, DetectorType.tpx3],
            value=DetectorType.tpx1,
            layout=widgets.Layout(width='400px'),
            disabled=False,
        )
        display(self.detector_type_widget)

    def setup_default_paths(self):
        logging.info("Setting up default paths...")
        self.detector_type = self.detector_type_widget.value
        self.raw_dir = Path(raw_dir[self.instrument][self.detector_type][0]) / str(self.ipts) / Path(raw_dir[self.instrument][self.detector_type][1])
        self.autoreduce_dir = Path(autoreduce_dir[self.instrument][self.detector_type][0]) / str(self.ipts) / Path(autoreduce_dir[self.instrument][self.detector_type][1])
        logging.info(f"\tAutoreduce dir: {self.autoreduce_dir}")
        logging.info(f"\tDetector type: {self.detector_type}")
        logging.info(f"\tRaw dir: {self.raw_dir}")

    # def manually_set_runs(self):
       
    #     if self.debug:
    #         sample_runs = DEBUG_DATA.sample_runs_selected
    #         sample_run_numbers_list = []
    #         for _run in sample_runs:
    #             _, number = _run.split('_')
    #             sample_run_numbers_list.append(number)
    #         str_sample_run_numbers = ', '.join(sample_run_numbers_list)

    #         ob_runs = DEBUG_DATA.ob_runs_selected
    #         ob_run_numbers_list = []
    #         for _run in ob_runs:
    #             _, number = _run.split('_')
    #             ob_run_numbers_list.append(number)
    #         str_ob_run_numbers = ', '.join(ob_run_numbers_list)
        
    #         output_folder = DEBUG_DATA.output_folder

    #     else:
    #         str_sample_run_numbers = ""
    #         str_ob_run_numbers = ""
    #         # output_folder = os.path.join(self.working_dir, 'shared')
    #         output_folder = ""

    #     sample_label = widgets.Label(value="List of sample run numbers (ex: 8702, 8704)")
    #     self.sample_run_numbers_widget = widgets.Textarea(value=str_sample_run_numbers,
    #                                                 placeholder="",
    #                                                 layout=widgets.Layout(width='400px'))
    #     ob_label = widgets.Label(value="List of ob run numbers (ex: 8703, 8705)")
    #     self.ob_run_numbers_widget = widgets.Textarea(value=str_ob_run_numbers,
    #                                             placeholder="",
    #                                             layout=widgets.Layout(width='400px'))
    #     output_label = widgets.Label(value=f"Full output folder path")
    #     self.output_folder_widget = widgets.Text(value=output_folder,
    #                                       placeholder="",
    #                                       layout=widgets.Layout(width='400px'))
    #     vertical_layout = widgets.VBox([sample_label, self.sample_run_numbers_widget,
    #                                     ob_label, self.ob_run_numbers_widget,
    #                                     output_label, self.output_folder_widget,])
    #     display(vertical_layout)
        
        # if self.instrument != "SNAP":
        #     display(HTML("<span style='font-size: 16px; color:red'>You have the option here to enter the runs manually or just use the widgets (following cells) to define them!</span>"))
        #     display(vertical_layout)

        # else:
        #     display(HTML("<span style='font-size: 16px; color:red'>Manual entry of runs is not available for SNAP instrument!</span>"))

    def select_sample_folder(self):
        self.select_folder(instruction="Select sample top folder",
                           next_function=self.sample_folder_selected)

    def select_sample_run_numbers(self):
        # if self.sample_run_numbers_widget.value.strip() != "":
        #     sample_run_numbers = self.sample_run_numbers_widget.value.split(',')
        #     list_sample_run_numbers = [f"Run_{_run.strip()}" for _run in sample_run_numbers]
        #     list_sample_runs_full_path = [os.path.join(self.autoreduce_dir, _sample) for _sample in list_sample_run_numbers]
        #     self.sample_run_numbers_selected(list_sample_runs_full_path)
        # else:
        
        self.setup_default_paths()

        if self.debug:
            sample_runs = DEBUG_DATA.sample_runs_selected
            sample_run_numbers_list = []
            for _run in sample_runs:
                _, number = _run.split('_')
                sample_run_numbers_list.append(number)
            str_sample_run_numbers = ', '.join(sample_run_numbers_list)
        else:
            str_sample_run_numbers = ""

        sample_label = widgets.HTML(value=f"<b><font color='green'>List of sample run numbers (ex: 8702, 8704-8706)</font></b>")

        self.sample_run_numbers_widget = widgets.Textarea(value=str_sample_run_numbers,
                                                    placeholder="",
                                                    layout=widgets.Layout(width='400px'))
        vertical_layout = widgets.VBox([sample_label, self.sample_run_numbers_widget,
                                        ])
        display(vertical_layout)

        display(HTML("<span style='font-size: 16px; color:red'>OR</span>"))

        self.select_folder(instruction="Browse sample runs to normalize",
                            next_function=self.sample_run_numbers_selected,
                            multiple=True,)

    def sample_run_numbers_selected(self, runs_selected):
        self.sample_run_numbers_selected = runs_selected

    def retrieve_file_path_from_nexus(self, run_number):
        """
        Retrieve the full path to the NeXus file for the given run number.
        This function should be implemented to read the NeXus file and extract the path.
        """
        logging.info(f"Retrieving file path from NeXus for run number: {run_number}")
        # Placeholder implementation, replace with actual logic to read NeXus file
        nexus_file_path = Path(self.nexus_folder) / f"{self.instrument.upper()}_{run_number}.nxs.h5"
        logging.info(f"\tNeXus file path: {nexus_file_path}")
        if nexus_file_path.exists():
            return extract_file_path_from_nexus(nexus_file_path)
        else:
            return None

    def extract_full_path(self, run_number=None):
        """
        Extract the full path to the run number based on the detector type.
        """
        logging.info(f"Extracting full path for run number: {run_number} with detector type: {self.detector_type}")

        if run_number is None:
            raise ValueError("Run number must be provided")
        
        if self.detector_type == DetectorType.tpx1_legacy:
            return Path(self.autoreduce_dir) / f"Run_{run_number}" 

        elif self.detector_type in [DetectorType.tpx1, DetectorType.tpx3]:
            # retrieve the path from the NeXus file
            file_path = self.retrieve_file_path_from_nexus(run_number)
            if self.detector_type == DetectorType.tpx1:
                file_path = Path(self.autoreduce_dir) / file_path
            elif self.detector_type == DetectorType.tpx3:
                file_path = Path(self.raw_dir) / file_path
            if file_path is None:
                raise ValueError(f"No NeXus file found for run number {run_number}")
            return str(file_path)

        else:
            raise ValueError(f"Unknown detector type: {self.detector_type}")

    def check_sample(self):
        """
        Check if the sample folder and runs are valid.
        """

        logging.info("Checking sample inputs...")
        display(HTML(f"Sample run numbers selected:"))

        if self.sample_run_numbers_widget.value.strip() != "":

            list_of_runs = extract_list_of_runs_from_string(self.sample_run_numbers_widget.value)
            logging.info(f"\t{list_of_runs = }")

            list_of_sample_full_path = []
            for _run in list_of_runs:
                _full_path = self.extract_full_path(run_number=_run)
                list_of_sample_full_path.append(_full_path)

            for _file_full_path in list_of_sample_full_path:
                if os.path.exists(_file_full_path):
                    logging.info(f"\tSample run number {_file_full_path} - FOUND")
                    display(HTML(f"<span style='color:green'>{_file_full_path} - OK!</span>"))
                else:
                    logging.info(f"\tSample run number {_file_full_path} - NOT FOUND")
                    display(HTML(f"<span style='color:red'>{_file_full_path} - NOT FOUND!</span>"))

        else:
            notebook_logging.info(f"Sample run numbers selected: {self.sample_run_numbers_selected}")
            for _run in self.sample_run_numbers_selected:
                if os.path.exists(_run):
                    notebook_logging.info(f"\tSample run number {_run} - FOUND")
                    # check here that the folder is not empty (contains tiff)
                    is_valid_run, report_dict = self.check_folder_is_valid(_run)
                    if is_valid_run:
                        nbr_tiff = report_dict['nbr_tiff']
                        display(HTML(f"<span style='color:green'>{_run}</span> - OK"))
                        notebook_logging.info(f"\tfolder seems to be a valid folder containing {nbr_tiff} tif* files")
                    else:
                        display(HTML(f"<span style='color:red'>{_run} - EMPTY!</span>"))
                else:
                    display(HTML(f"<span style='color:red'>{_run} - NOT FOUND!</span> - ERROR!"))
                    notebook_logging.info(f"\tSample run number {_run} - NOT FOUND!")


    def select_ob_folder(self):
            self.select_folder(instruction="Browse ob top folder",
                            next_function=self.ob_folder_selected)

    def select_ob_run_numbers(self):
        # if self.ob_run_numbers_widget.value.strip() != "":
        #     ob_run_numbers = self.ob_run_numbers_widget.value.split(',')
        #     list_ob_run_numbers = [f"Run_{_run.strip()}" for _run in ob_run_numbers]
        #     list_ob_runs_full_path = [os.path.join(self.autoreduce_dir, _ob) for _ob in list_ob_run_numbers]
        #     self.ob_run_numbers_selected(list_ob_runs_full_path)
        # else:    
        
        if self.debug:
        
            ob_runs = DEBUG_DATA.ob_runs_selected
            ob_run_numbers_list = []
            for _run in ob_runs:
                _, number = _run.split('_')
                ob_run_numbers_list.append(number)
            str_ob_run_numbers = ', '.join(ob_run_numbers_list)
        
            output_folder = DEBUG_DATA.output_folder

        else:
            str_ob_run_numbers = ""

        ob_label = widgets.HTML(value=f"<b><font color='green'>List of ob run numbers (ex: 8705, 8707)</font></b>")

        self.ob_run_numbers_widget = widgets.Textarea(value=str_ob_run_numbers,
                                                    placeholder="",
                                                    layout=widgets.Layout(width='400px'))
        vertical_layout = widgets.VBox([ob_label, self.ob_run_numbers_widget,
                                        ])
        display(vertical_layout)

        display(HTML("<span style='font-size: 16px; color:red'>OR</span>"))

        self.select_folder(instruction="Browse ob run number folders",
                            next_function=self.ob_run_numbers_selected,
                            start_dir=self.ob_folder,
                            multiple=True)

    def check_ob(self):
        """
        Check if the ob folder and runs are valid.
        """
        logging.info("Checking ob inputs...")
        display(HTML(f"OB run numbers selected:"))

        if self.ob_run_numbers_widget.value.strip() != "":

            list_of_runs = extract_list_of_runs_from_string(self.ob_run_numbers_widget.value)
            logging.info(f"\t{list_of_runs = }")

            list_of_ob_full_path = []
            for _run in list_of_runs:
                _full_path = self.extract_full_path(run_number=_run)
                list_of_ob_full_path.append(_full_path)

            for _file_full_path in list_of_ob_full_path:
                if os.path.exists(_file_full_path):
                    logging.info(f"\tOB run number {_file_full_path} - FOUND")
                    display(HTML(f"<span style='color:green'>{_file_full_path} - OK!</span>"))
                else:
                    logging.info(f"\tOB run number {_file_full_path} - NOT FOUND")
                    display(HTML(f"<span style='color:red'>{_file_full_path} - NOT FOUND!</span>"))

        else:
            notebook_logging.info(f"OB run numbers selected: {self.ob_run_numbers_selected}")
            for _run in self.ob_run_numbers_selected:
                if os.path.exists(_run):
                    notebook_logging.info(f"\tOB run number {_run} - FOUND")
                    # check here that the folder is not empty (contains tiff)
                    is_valid_run, report_dict = self.check_folder_is_valid(_run)
                    if is_valid_run:
                        nbr_tiff = report_dict['nbr_tiff']
                        display(HTML(f"<span style='color:green'>{_run}</span> - OK"))
                        notebook_logging.info(f"\tfolder seems to be a valid folder containing {nbr_tiff} tif* files")
                    else:
                        display(HTML(f"<span style='color:red'>{_run} - EMPTY!</span>"))
                else:
                    display(HTML(f"<span style='color:red'>{_run} - NOT FOUND!</span> - ERROR!"))
                    notebook_logging.info(f"\tOB run number {_run} - NOT FOUND!")




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
                                  start_dir=self.shared_dir,
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
        self.correct_chips_alignment_flag = widgets.Checkbox(description='Correct chips alignment',
                                                  value=True)

        vertical_layout = widgets.VBox([self.proton_charge_flag, 
                                        self.shutter_counts_flag, 
                                        self.replace_ob_zeros_by_nan_flag, 
                                        self.correct_chips_alignment_flag
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
        label = widgets.Label(value="Note: Any of the stacks exported will also contain the original spectra file")
        vertical_layout = widgets.VBox([self.export_corrected_stack_of_sample_data,
                                        self.export_corrected_stack_of_ob_data,
                                        self.export_corrected_stack_of_normalized_data,
                                        label
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

    # def sample_run_numbers_selected(self, runs_selected):
    #     self.sample_run_numbers = runs_selected
    #     display(HTML(f"Sample run numbers selected:"))
    #     notebook_logging.info(f"Sample run numbers selected: {runs_selected}")
    #     for _run in runs_selected:
    #         if os.path.exists(_run):
    #             notebook_logging.info(f"\tSample run number {_run} - FOUND")
    #             # check here that the folder is not empty (contains tiff)
    #             is_valid_run, report_dict = self.check_folder_is_valid(_run)
    #             if is_valid_run:
    #                 nbr_tiff = report_dict['nbr_tiff']
    #                 display(HTML(f"<span style='color:green'>{_run}</span>"))
    #                 notebook_logging.info(f"\tfolder seems to be a valid folder containing {nbr_tiff} tif* files")
    #             else:
    #                 display(HTML(f"<span style='color:red'>{_run} - EMPTY!</span>"))
    #         else:
    #             display(HTML(f"<span style='color:red'>{_run} - NOT FOUND!</span>"))
    #             notebook_logging.info(f"\tSample run number {_run} - NOT FOUND!")

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
                                                        newdir_toolbar_button=True,
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
                       'normalized_integrated': self.export_corrected_integrated_normalized_data.value,
                       'x_axis': True,  # always export x axis
                       }

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
                                        correct_chips_alignment_flag=self.correct_chips_alignment_flag.value,
                                        verbose=True,
                                        instrument=self.instrument,
                                        detector_delay_us=detecor_delay_us,
                                        preview=preview,
                                        distance_source_detector_m=self.distance_source_detector.value,
                                        export_mode=export_mode)
        display(HTML("<span style='color:blue'>Normalization completed</span>"))
        display(HTML(f"Log file: /SNS/VENUS/shared/logs/normalization_for_timepix.log"))

