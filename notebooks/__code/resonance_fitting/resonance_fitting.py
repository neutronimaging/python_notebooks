import glob
import logging
import logging as notebook_logging
import os
from pathlib import Path
import numpy as np
import pandas as pd

import ipywidgets as widgets
import matplotlib.pyplot as plt
from IPython.display import HTML, display
from ipywidgets import interactive
from PIL import Image
import periodictable

from pleiades.processing.normalization import normalization as normalization_with_pleaides
from pleiades.processing import Roi as PleiadesRoi
from pleiades.processing import Facility
from pleiades.sammy.io.data_manager import convert_csv_to_sammy_twenty, validate_sammy_twenty_format

from __code._utilities.list import extract_list_of_runs_from_string
from __code._utilities.nexus import extract_file_path_from_nexus

# from __code.ipywe.myfileselector import MyFileSelectorPanel
from __code.resonance_fitting.config import DEBUG_DATA, timepix1_config, timepix3_config


from __code.normalization_tof.normalization_tof import NormalizationTof
from __code.ipywe.fileselector import FileSelectorPanel as FileSelectorPanel
from __code.normalization_tof import DetectorType, autoreduce_dir, distance_source_detector_m, raw_dir
from __code.normalization_tof.config import DEBUG_DATA, timepix1_config, timepix3_config
from __code.normalization_tof.normalization_for_timepix1_timepix3 import (
    load_data_using_multithreading,
    # normalization,
    normalization_with_list_of_full_path,
    retrieve_list_of_tif,
)

FONT_SIZE = 14

class FilesPaths:
    logging = None
    transmission = None

class FolderPaths:
    working = None
    stagging = None
    output = None
    nexus = None
    shared = None
    spectra = None
    twenty = None
    sammy_working = None
    sammy_output = None


class ResonanceFitting(NormalizationTof):

    def __init__(self, working_dir=None, debug=False):
        self.folder_paths = FolderPaths()
        self.files_paths = FilesPaths()
        
        self.initialize_logging()
        
        if debug:
            self.folder_paths.working = Path(DEBUG_DATA.working_dir)
            self.folder_paths.output = Path(DEBUG_DATA.output_folder)

        else:
            self.folder_paths.working = Path(working_dir)
            self.folder_paths.output = self.folder_paths.working / "shared"

        self.folder_paths.nexus = self.folder_paths.working / "nexus"
        self.debug = debug

        logging.info(f"{self.folder_paths.working =}")
        logging.info(f"{self.folder_paths.working.parts =}")

        working_dir_splitted = self.folder_paths.working.parts
        _facility = working_dir_splitted[1]
        _beamline = working_dir_splitted[2]
        ipts = working_dir_splitted[3]

        self.ipts = ipts
        self.instrument = _beamline.upper()

        # self.autoreduce_dir = autoreduce_dir[_beamline][0] + str(ipts) + autoreduce_dir[_beamline][1]
        # self.shared_dir = str(Path(shared_dir[self.instrument][0]) / str(ipts) / shared_dir[self.instrument][1])
        self.folder_paths.shared = Path("/") / _facility / self.instrument / str(ipts) / "shared"

        notebook_logging.info(f"Instrument: {self.instrument}")
        notebook_logging.info(f"Working dir: {self.folder_paths.working}")
        notebook_logging.info(f"IPTS: {self.ipts}")
        notebook_logging.info(f"facility: {_facility}")
        notebook_logging.info(f"nexus folder: {self.folder_paths.nexus}")
        notebook_logging.info(f"Shared dir: {self.folder_paths.shared}")

    def initialize_logging(self):
        LOG_PATH = "/SNS/VENUS/shared/log/"
        base_file_name = Path(__file__).name
        file_name_without_extension = Path(base_file_name).stem
        user_name = os.getlogin()  # add user name to the log file name
        log_file_name = LOG_PATH / Path(f"{user_name}_{str(file_name_without_extension)}.log")
        self.files_paths.logging = log_file_name
        notebook_logging.basicConfig(
            filename=log_file_name,
            filemode="w",
            format="[%(levelname)s] - %(asctime)s - %(message)s",
            level=notebook_logging.INFO,
        )
        notebook_logging.info(f"*** Starting a new script {file_name_without_extension} ***")

    def select_normalized_text_file(self):
        self.file_selector = FileSelectorPanel(
            start_dir=str(self.folder_paths.shared),
            type="file",
            instruction="Select normalized ASCII file",
            filters={"transmission txt": "*_transmission.txt"},
            default_filter="transmission txt",
            multiple=False,
            next=self.transmitted_text_file_selected,
        )
        self.file_selector.show()

    def transmitted_text_file_selected(self, file_path):
        file_path = Path(file_path)
        logging.info(f"Transmitted text file selected: {file_path}")
        display(HTML(f"<span style='font-size: {FONT_SIZE}px; color:green'>Transmission file: {file_path.name} ... selected!</span>"))

        self.files_paths.transmission = file_path
       
        self.stagging_folders_setup(file_path)
        self.converting_transmission_to_twenty_format()

    def stagging_folders_setup(self, file_path):

        # set up various stagging folder for SAMMY
        self.folder_paths.stagging = file_path.parent / "hf_analysis"
        self.folder_paths.spectra = self.folder_paths.stagging / "spectra"
        self.folder_paths.twenty = self.folder_paths.stagging / "twenty"
        self.folder_paths.sammy_working = self.folder_paths.stagging / "sammy_working"
        self.folder_paths.sammy_output = self.folder_paths.stagging / "sammy_output"

        # creating thos folders
        Path(self.folder_paths.stagging).mkdir(parents=True, exist_ok=True)
        Path(self.folder_paths.spectra).mkdir(parents=True, exist_ok=True)
        Path(self.folder_paths.twenty).mkdir(parents=True, exist_ok=True)
        Path(self.folder_paths.sammy_working).mkdir(parents=True, exist_ok=True)
        Path(self.folder_paths.sammy_output).mkdir(parents=True, exist_ok=True)

        logging.info(f"Stagging folder: {self.folder_paths.stagging} ... {self.folder_paths.stagging.is_dir()}")
        logging.info(f"Spectra folder: {self.folder_paths.spectra} ... {self.folder_paths.spectra.is_dir()}")
        logging.info(f"Twenty folder: {self.folder_paths.twenty} ... {self.folder_paths.twenty.is_dir()}")
        logging.info(f"SAMMY working folder: {self.folder_paths.sammy_working} ... {self.folder_paths.sammy_working.is_dir()}")
        logging.info(f"SAMMY output folder: {self.folder_paths.sammy_output} ... {self.folder_paths.sammy_output.is_dir()}")

        display(HTML(f"<span style='font-size: {FONT_SIZE}px; color:green'>Stagging folders created!</span>"))

    def converting_transmission_to_twenty_format(self):
        logging.info("Converting transmission data .txt to .twenty format for SAMMY ...")
        twenty_file = self.folder_paths.output / self.files_paths.transmission.name.replace(".txt", ".twenty")
        convert_csv_to_sammy_twenty(self.files_paths.transmission, twenty_file)
        if validate_sammy_twenty_format(twenty_file):
            logging.info(f"Conversion successful! Twenty file created at: {twenty_file}")
            display(HTML(f"<span style='font-size: {FONT_SIZE}px; color:green'>Twenty file created at: {twenty_file}</span>"))
        else:
            logging.error("Conversion failed! The generated .twenty file is not valid.")
            display(HTML(f"<span style='font-size: {FONT_SIZE}px; color:red'>Conversion failed! The generated .twenty file is not valid.</span>"))

    def select_isotope_and_abundance(self):
        list_elements = periodictable.elements
        dict_elements = {}
        for _el in list_elements:
            dict_elements[_el.name.capitalize()] = {'symbol': _el.symbol}
        list_elements_names = list(dict_elements.keys())
        list_elements_names.sort()

        display(HTML(f"<span style='font-size: {FONT_SIZE}px; color:blue'>Select element:</span>"))
        list_elements_widget = widgets.Dropdown(
            options=list_elements_names,
            description="",
            disabled=False,
        )
        display(list_elements_widget)