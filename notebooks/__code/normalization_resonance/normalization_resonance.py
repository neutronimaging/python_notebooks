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

from pleiades.processing.normalization import normalization as normalization_with_pleaides
from pleiades.processing import Roi as PleiadesRoi
from pleiades.processing import Facility

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

        self.select_roi_widget = widgets.Checkbox(
            description="Select ROI on the detector",
            value=True,
            layout=widgets.Layout(width="600px"),
        )

        if len(list(self.dict_sample.keys())) > 1:
            disabled = False
            value = True
        else:
            disabled = True
            value = False

        self.combine_mode_widget = widgets.Checkbox(
            description="Combine all the sample runs into one",
            value=value,
            disabled=disabled,
            layout=widgets.Layout(width="600px"),
        )

        verti_layout = widgets.VBox(
            [
                self.select_roi_widget,
                self.combine_mode_widget,
            ],
            layout=widgets.Layout(padding="10px", 
                                  border="solid 1px",
                                  width="620px"),
        )
        display(verti_layout)

    def normalization(self):
        display(HTML("<span style='font-size: 16px; color:red'>Running normalization ...</span>"))

        sample_folders = list(self.dict_sample.keys())
        ob_folders = list(self.dict_ob.keys())
        facility = Facility.ornl
        nexus_full_path = os.path.join(self.nexus_folder)
            
        if self.roi:
            left = self.roi.left
            top = self.roi.top
            width = self.roi.width
            height = self.roi.height
            roi = PleiadesRoi(x1=left, y1=top, width=width, height=height)

        logging.info(f"normalization:")
        logging.info(f"\tsample_folders: {sample_folders}")
        logging.info(f"\tob_folders: {ob_folders}")
        logging.info(f"\roi: {roi}")

        # transmission = normalization_with_pleaides(list_sample_folders=self.sample_folder,
        #                             list_ob_folders=self.ob_folder,
        #                             nexus_path=nexus_path,
        #                             facility=Facility.ornl,
        #                             combine_mode=self.combine_mode_widget.value,
        #                             roi=self.roi,
        #                             pc_uncertainty=0.005,
        #                             output_folder=self.output_folder,)
    