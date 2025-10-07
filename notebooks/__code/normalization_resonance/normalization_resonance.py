import glob
import logging
import logging as notebook_logging
import os
from pathlib import Path
import numpy as np

import ipywidgets as widgets
import matplotlib.pyplot as plt
from IPython.display import HTML, display
from ipywidgets import interactive
from PIL import Image

from __code._utilities.list import extract_list_of_runs_from_string
from __code._utilities.nexus import extract_file_path_from_nexus

# from __code.ipywe.myfileselector import MyFileSelectorPanel
from __code.normalization_tof.normalization_tof import NormalizationTof
from __code.ipywe.fileselector import FileSelectorPanel as MyFileSelectorPanel
from __code.normalization_tof import DetectorType, autoreduce_dir, distance_source_detector_m, raw_dir
from __code.normalization_tof.config import DEBUG_DATA, timepix1_config, timepix3_config
from __code.normalization_tof.normalization_for_timepix1_timepix3 import (
    load_data_using_multithreading,
    # normalization,
    normalization_with_list_of_full_path,
    retrieve_list_of_tif,
)

# LOG_PATH = "/SNS/VENUS/shared/log/"
# file_name, ext = os.path.splitext(os.path.basename(__file__))
# user_name = os.getlogin()  # add user name to the log file name
# log_file_name = os.path.join(LOG_PATH, f"{user_name}_{file_name}.log")
# notebook_logging.basicConfig(
#     filename=log_file_name,
#     filemode="w",
#     format="[%(levelname)s] - %(asctime)s - %(message)s",
#     level=notebook_logging.INFO,
# )
# notebook_logging.info(f"*** Starting a new script {file_name} ***")


class NormalizationResonance(NormalizationTof):
    
    sample_folder = None
    sample_run_numbers = None
    sample_run_numbers_selected = None
    
    ob_folder = None
    ob_run_numbers = None
    ob_run_numbers_selected = None

    dc_folder = None
    dc_run_numbers = None
    dc_run_numbers_selected = None

    output_folder = None
    
    # {'full_path_data': {'data': None, 'nexus': None}}
    dict_sample = {}
    dict_ob = {}
    dict_dc = {}

    # {'short_name': 'full_path_data'}
    dict_short_name_full_path = {"sample": {}, "ob": {}, "dc": {}}

    dict_ob_runs = None
    dict_ob_data = None
    dict_dc_data = None

    # LOG_PATH = "/SNS/VENUS/shared/log/"
    # file_name, ext = os.path.splitext(os.path.basename(__file__))
    # user_name = os.getlogin()  # add user name to the log file name
    # log_file_name = os.path.join(LOG_PATH, f"{user_name}_{file_name}.log")
    # print(f"Log file name: {log_file_name}")
    # notebook_logging.basicConfig(
    #     filename=log_file_name,
    #     filemode="w",
    #     format="[%(levelname)s] - %(asctime)s - %(message)s",
    #     level=notebook_logging.INFO,
    # )
    # notebook_logging.info(f"*** Starting a new script {file_name} ***")

    def initialize(self):
        LOG_PATH = "/SNS/VENUS/shared/log/"
        file_name, ext = os.path.splitext(os.path.basename(__file__))
        user_name = os.getlogin()  # add user name to the log file name
        log_file_name = os.path.join(LOG_PATH, f"{user_name}_{file_name}.log")
        notebook_logging.basicConfig(
            filename=log_file_name,
            filemode="w",
            format="[%(levelname)s] - %(asctime)s - %(message)s",
            level=notebook_logging.INFO,
        )
        notebook_logging.info(f"*** Starting a new script {file_name} ***")

    def retrieve_nexus_file_path(self):
        """
        Retrieve the NeXus file paths for sample, OB and DC.
        
        This function assumes that the NeXus files are named in a specific format"""

        all_nexus_files_found = True
        notebook_logging.info("Retrieving NeXus file paths for sample, OB and DC runs...")

        notebook_logging.info("\tworking with sample runs:")
        for full_path in self.dict_sample.keys():
            if self.detector_type == DetectorType.tpx1_legacy:
                run_number = os.path.basename(full_path).split("_")[1]
            elif self.detector_type in [DetectorType.tpx1, DetectorType.tpx3]:
                file_name_split = os.path.basename(full_path).split("_")
                run_number = file_name_split[2]

            nexus_full_path = os.path.join(
                self.nexus_folder, f"{self.instrument.upper()}_{run_number}.nxs.h5"
            )
            if os.path.exists(nexus_full_path):
                notebook_logging.info(f"\tNeXus file found: {nexus_full_path}")
                self.dict_sample[full_path]["nexus"] = nexus_full_path
            else:
                notebook_logging.warning(f"\tNeXus file NOT found: {nexus_full_path}")
                all_nexus_files_found = False
                self.dict_sample[full_path]["nexus"] = None

        notebook_logging.info("\tworking with ob runs:")
        for full_path in self.dict_ob.keys():
            if self.detector_type == DetectorType.tpx1_legacy:
                run_number = os.path.basename(full_path).split("_")[1]
            elif self.detector_type in [DetectorType.tpx1, DetectorType.tpx3]:
                file_name_split = os.path.basename(full_path).split("_")
                run_number = file_name_split[2]

            nexus_full_path = os.path.join(
                self.nexus_folder, f"{self.instrument.upper()}_{run_number}.nxs.h5"
            )
            if os.path.exists(nexus_full_path):
                notebook_logging.info(f"\tNeXus file found: {nexus_full_path}")
                self.dict_ob[full_path]["nexus"] = nexus_full_path
            else:
                notebook_logging.warning(f"\tNeXus file NOT found: {nexus_full_path}")
                all_nexus_files_found = False
                self.dict_ob[full_path]["nexus"] = None

        notebook_logging.info("\tworking with dc runs:")
        for full_path in self.dict_dc.keys():
            if self.detector_type == DetectorType.tpx1_legacy:
                run_number = os.path.basename(full_path).split("_")[1]
            elif self.detector_type in [DetectorType.tpx1, DetectorType.tpx3]:
                file_name_split = os.path.basename(full_path).split("_")
                run_number = file_name_split[2]

            nexus_full_path = os.path.join(
                self.nexus_folder, f"{self.instrument.upper()}_{run_number}.nxs.h5"
            )
            if os.path.exists(nexus_full_path):
                notebook_logging.info(f"\tNeXus file found: {nexus_full_path}")
                self.dict_dc[full_path]["nexus"] = nexus_full_path
            else:
                notebook_logging.warning(f"\tNeXus file NOT found: {nexus_full_path}")
                all_nexus_files_found = False
                self.dict_dc[full_path]["nexus"] = None

        notebook_logging.info("Done retrieving NeXus file paths.")

        return all_nexus_files_found

    def settings(self):
        all_nexus_found = self.retrieve_nexus_file_path()
        notebook_logging.info(f"All NeXus files found: {all_nexus_found}")

        tpx3_disabled_flag = True if self.detector_type == DetectorType.tpx3 else False

        label = widgets.Label(value="What to take into account for normalization?")
        display(label)

        if all_nexus_found:
            _value = True
            _disabled=False
        else:
            _value = False
            _disabled = True
        self.proton_charge_flag = widgets.Checkbox(description="Proton charge", 
                                                   value=_value,
                                                   disabled=_disabled)
        
        self.monitor_counts_flag = widgets.Checkbox(description="Monitor counts", 
                                                   value=False,
                                                   disabled=_disabled)

        self.shutter_counts_flag = widgets.Checkbox(
            description="Shutter counts", value=not tpx3_disabled_flag, disabled=tpx3_disabled_flag
        )
        self.correct_chips_alignment_flag = widgets.Checkbox(
            description="Correct chips alignment", disabled=False, value=True
        )

        vertical_layout = widgets.VBox(
            [
                self.proton_charge_flag,
                # self.monitor_counts_flag,
                self.shutter_counts_flag,
            ]
        )
        display(vertical_layout)

        display(HTML("<hr>"))

        display(HTML("<span style='font-size: 16px; color:red'>Handling OB zeros - <i>May take much more time!</i></span>"))
        self.replace_ob_zeros_by_local_median_flag = widgets.Checkbox(description="Replace zeros by local median", 
                                                                      value=False,
                                                                      layout=widgets.Layout(width="500px"))
        self.replace_ob_zeros_by_local_median_flag.observe(self._on_replace_ob_zeros_by_local_median_flag_change, 
                                                           names='value')
      
        display(HTML("<hr>"))

        label = widgets.Label(value="Distance source detector (m)", layout=widgets.Layout(width="200px"))
        self.distance_source_detector = widgets.FloatText(
            value=distance_source_detector_m[self.instrument], disabled=False, layout=widgets.Layout(width="50px")
        )
        hori_layout = widgets.HBox([label, self.distance_source_detector])
        display(hori_layout)

        if self.instrument == "SNAP":
            label = widgets.Label(value="Detector offset (us)", layout=widgets.Layout(width="200px"))
            self.detector_offset_us = widgets.FloatText(value=0.0, disabled=False, layout=widgets.Layout(width="50px"))
            hori_layout = widgets.HBox([label, self.detector_offset_us])
            display(hori_layout)

    def _on_replace_ob_zeros_by_local_median_flag_change(self, change):
        if change['new']:
            self.kernel_size_for_local_median_y.disabled = False
            self.kernel_size_for_local_median_x.disabled = False
            self.kernel_size_for_local_median_tof.disabled = False
            self.maximum_iterations_ui.disabled = False
        else:
            self.kernel_size_for_local_median_y.disabled = True
            self.kernel_size_for_local_median_x.disabled = True
            self.kernel_size_for_local_median_tof.disabled = True
            self.maximum_iterations_ui.disabled = True

    def what_to_export(self):
        display(HTML("<span style='font-size: 16px; color:red'>Stack of images</span>"))
        self.export_corrected_stack_of_sample_data = widgets.Checkbox(
            description="Export corrected stack of sample data", layout=widgets.Layout(width="100%"), value=False
        )
        self.export_corrected_stack_of_ob_data = widgets.Checkbox(
            description="Export corrected stack of ob data", layout=widgets.Layout(width="100%"), value=False
        )
        self.export_corrected_stack_of_normalized_data = widgets.Checkbox(
            description="Export corrected stack of normalized data",
            layout=widgets.Layout(width="100%"),
            value=True,
            disabled=True,
        )
        label = widgets.Label(value="Note: Any of the stacks exported will also contain the original spectra file")
        vertical_layout = widgets.VBox(
            [
                self.export_corrected_stack_of_sample_data,
                self.export_corrected_stack_of_ob_data,
                self.export_corrected_stack_of_normalized_data,
                label,
            ]
        )
        display(vertical_layout)
        display(HTML("<span style='font-size: 16px; color:red'>Integrated images</span>"))
        self.export_corrected_integrated_sample_data = widgets.Checkbox(
            description="Export corrected integrated sample data", layout=widgets.Layout(width="100%"), value=False
        )
        self.export_corrected_integrated_ob_data = widgets.Checkbox(
            description="Export corrected integrated ob data", layout=widgets.Layout(width="100%"), value=False
        )
        self.export_corrected_integrated_normalized_data = widgets.Checkbox(
            description="Export corrected integrated normalized data", layout=widgets.Layout(width="100%"), value=False
        )
        vertical_layout = widgets.VBox(
            [
                self.export_corrected_integrated_sample_data,
                self.export_corrected_integrated_ob_data,
                self.export_corrected_integrated_normalized_data,
            ]
        )

        display(vertical_layout)

    def check_folder_is_valid(self, full_path):
        list_tiff = glob.glob(os.path.join(full_path, "*.tif*"))
        if list_tiff:
            return True, {"nbr_tiff": len(list_tiff)}
        else:
            return False, {"nbr_tiff": 0}

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

    def dc_folder_selected(self, folder_selected):
        self.dc_folder = folder_selected
        display(HTML(f"Dark current folder selected: <span style='color:blue'>{folder_selected}</span>"))

    def save_ob_run_numbers_selected(self, folder_selected):
        self.ob_run_numbers_selected = folder_selected
     
    def save_dc_run_numbers_selected(self, folder_selected):
        self.dc_run_numbers_selected = folder_selected
        
    def output_folder_selected(self, folder_selected):
        self.output_folder = folder_selected
        display(HTML("Output folder selected:"))
        if os.path.exists(folder_selected):
            display(HTML(f"<span style='color:green'>{folder_selected} - FOUND!</span>"))
            notebook_logging.info(f"Output folder selected: {folder_selected} - FOUND")
        else:
            display(HTML(f"<span style='color:blue'>{folder_selected} - DOES NOT EXIST and will be CREATED!</span>"))
            notebook_logging.info(f"Output folder selected: {folder_selected} - NOT FOUND and will be CREATED!")

    def select_folder(self, instruction="Select a folder",
                       next_function=None, 
                       start_dir=None, 
                       multiple=False,
                       newdir_toolbar_button=False):
        # go straight to autoreduce/mcp folder
        if start_dir is None:
            start_dir = self.autoreduce_dir

        self.list_input_folders_ui = MyFileSelectorPanel(
            instruction=instruction,
            start_dir=start_dir,
            type="directory",
            newdir_toolbar_button=newdir_toolbar_button,
            multiple=multiple,
            sort_in_reverse=True,
            # sort_increasing=False,
            next=next_function,
        )
        self.list_input_folders_ui.show()

    # calling main code
    def run_normalization_with_list_of_runs(self, preview=False):
        # sample_run_numbers = self.sample_run_numbers
        # ob_run_numbers = self.ob_run_numbers
        output_folder = self.output_folder
        export_mode = {
            "sample_stack": self.export_corrected_stack_of_sample_data.value,
            "ob_stack": self.export_corrected_stack_of_ob_data.value,
            "normalized_stack": self.export_corrected_stack_of_normalized_data.value,
            "sample_integrated": self.export_corrected_integrated_sample_data.value,
            "ob_integrated": self.export_corrected_integrated_ob_data.value,
            "normalized_integrated": self.export_corrected_integrated_normalized_data.value,
            "x_axis": True,  # always export x axis
        }

        detector_delay_us = None
        if self.instrument == "SNAP":
            detector_delay_us = self.detector_offset_us.value

        sample_dict = {}
        for _full_path in self.dict_sample.keys():
            sample_dict[os.path.basename(_full_path)] = {
                "full_path": _full_path,
                "nexus": self.dict_sample[_full_path]["nexus"],
            }

        ob_dict = {}
        for _full_path in self.dict_ob.keys():
            ob_dict[os.path.basename(_full_path)] = {
                "full_path": _full_path,
                "nexus": self.dict_ob[_full_path]["nexus"],
            }

        dc_dict = {}
        if self.dict_dc:
            logging.info("Dark current runs provided")
            for _full_path in self.dict_dc.keys():
                dc_dict[os.path.basename(_full_path)] = {
                    "full_path": _full_path,
                    "nexus": self.dict_dc[_full_path]["nexus"],
                }

        if self.correct_chips_alignment_flag.value:
            if self.detector_type in [DetectorType.tpx1_legacy, DetectorType.tpx1]:
                correct_chips_alignment_config = timepix1_config
            elif self.detector_type == DetectorType.tpx3:
                correct_chips_alignment_config = timepix3_config
            else:
                correct_chips_alignment_config = None

        normalization_with_list_of_full_path(
            sample_dict=sample_dict,
            ob_dict=ob_dict,
            dc_dict=dc_dict,
            output_folder=output_folder,
            proton_charge_flag=self.proton_charge_flag.value,
            monitor_counts_flag=self.monitor_counts_flag.value,
            shutter_counts_flag=self.shutter_counts_flag.value,
            # replace_ob_zeros_by_nan_flag=self.replace_ob_zeros_by_nan_flag.value,
            replace_ob_zeros_by_local_median_flag=self.replace_ob_zeros_by_local_median_flag.value,
            kernel_size_for_local_median=(self.kernel_size_for_local_median_y.value,
                                          self.kernel_size_for_local_median_x.value,
                                          self.kernel_size_for_local_median_tof.value),
            max_iterations=self.maximum_iterations_ui.value,
            correct_chips_alignment_flag=self.correct_chips_alignment_flag.value,
            correct_chips_alignment_config=correct_chips_alignment_config,
            verbose=True,
            instrument=self.instrument,
            detector_delay_us=detector_delay_us,
            preview=preview,
            distance_source_detector_m=self.distance_source_detector.value,
            export_mode=export_mode,
        )
        display(HTML("<span style='color:blue'>Normalization completed</span>"))
        display(HTML("Log file: /SNS/VENUS/shared/logs/normalization_for_timepix.log"))
