import glob
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
from __code.ipywe.fileselector import FileSelectorPanel as MyFileSelectorPanel
from __code.normalization_tof import (
    DetectorType,
    autoreduce_dir,
    distance_source_detector_m,
    raw_dir,
)
from __code.normalization_tof.config import DEBUG_DATA, timepix1_config, timepix3_config
from __code.normalization_tof.normalization_for_timepix1_timepix3 import (
    load_data_using_multithreading,
    # normalization,
    normalization_with_list_of_full_path,
    retrieve_list_of_tif,
)

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


class NormalizationTof:
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

    def __init__(self, working_dir=None, debug=False):
        if debug:
            self.working_dir = DEBUG_DATA.working_dir
            self.output_dir = DEBUG_DATA.output_folder
        else:
            self.working_dir = working_dir
            self.output_dir = os.path.join(self.working_dir, "shared")

        self.nexus_folder = os.path.join(self.working_dir, "nexus")
        self.debug = debug
        _, _facility, _beamline, ipts = self.working_dir.split("/")

        self.ipts = ipts
        self.instrument = _beamline.upper()

        # self.autoreduce_dir = autoreduce_dir[_beamline][0] + str(ipts) + autoreduce_dir[_beamline][1]
        # self.shared_dir = str(Path(shared_dir[self.instrument][0]) / str(ipts) / shared_dir[self.instrument][1])
        self.shared_dir = Path("/") / _facility / self.instrument / str(ipts) / "shared"

        notebook_logging.info(f"Instrument: {self.instrument}")
        notebook_logging.info(f"Working dir: {self.working_dir}")
        notebook_logging.info(f"IPTS: {self.ipts}")
        notebook_logging.info(f"facility: {_facility}")
        notebook_logging.info(f"nexus folder: {self.nexus_folder}")
        notebook_logging.info(f"Shared dir: {self.shared_dir}")

        display(
            HTML("<span style='color:blue; font-size:16px'>Select detector type</span>")
        )
        self.detector_type_widget = widgets.Dropdown(
            options=[DetectorType.tpx1_legacy, DetectorType.tpx1, DetectorType.tpx3],
            value=DetectorType.tpx1,
            layout=widgets.Layout(width="400px"),
            disabled=False,
        )
        display(self.detector_type_widget)

    def reset_sample_dicts(self):
        self.dict_sample = {}
        self.dict_short_name_full_path["sample"] = {}

    def reset_ob_dicts(self):
        self.dict_short_name_full_path["ob"] = {}
        self.dict_ob = {}
        self.dict_ob_runs = None
        self.dict_ob_data = None

    def reset_dc_dicts(self):
        self.dict_short_name_full_path["dc"] = {}
        self.dict_dc = {}
        self.dict_dc_runs = None
        self.dict_dc_data = None

    def setup_default_paths(self):
        notebook_logging.info("Setting up default paths...")
        self.detector_type = self.detector_type_widget.value
        self.raw_dir = Path(raw_dir[self.instrument][self.detector_type][0]) / str(
            self.ipts
        )
        self.autoreduce_dir = (
            Path(autoreduce_dir[self.instrument][self.detector_type][0])
            / str(self.ipts)
            / Path(autoreduce_dir[self.instrument][self.detector_type][1])
        )
        notebook_logging.info(f"\tAutoreduce dir: {self.autoreduce_dir}")
        notebook_logging.info(f"\tDetector type: {self.detector_type}")
        notebook_logging.info(f"\tRaw dir: {self.raw_dir}")
        # self.select_folder(instruction="Select sample top folder", next_function=self.sample_folder_selected)

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
                _, number = _run.split("_")
                sample_run_numbers_list.append(number)
            str_sample_run_numbers = ", ".join(sample_run_numbers_list)
        else:
            str_sample_run_numbers = ""

        sample_label = widgets.HTML(
            value="<b><font color='green'>List of sample run numbers (ex: 8702, 8704-8706)</font></b>"
        )

        self.sample_run_numbers_widget = widgets.Textarea(
            value=str_sample_run_numbers,
            placeholder="",
            layout=widgets.Layout(width="400px"),
        )
        vertical_layout = widgets.VBox(
            [
                sample_label,
                self.sample_run_numbers_widget,
            ]
        )
        display(vertical_layout)

        display(HTML("<span style='font-size: 16px; color:red'>OR</span>"))
        # give focus to the widgets self.sample_run_numbers_widget
        # self.sample_run_numbers_widget.focus()

        self.select_folder(
            instruction="Browse sample runs to normalize",
            next_function=self.save_sample_run_numbers_selected,
            multiple=True,
            newdir_toolbar_button=False,
        )

    def save_sample_run_numbers_selected(self, runs_selected):
        self.sample_run_numbers_selected = runs_selected

    def retrieve_file_path_from_nexus(self, run_number):
        """
        Retrieve the full path to the NeXus file for the given run number.
        This function should be implemented to read the NeXus file and extract the path.
        """
        notebook_logging.info(
            f"Retrieving file path from NeXus for run number: {run_number}"
        )
        # Placeholder implementation, replace with actual logic to read NeXus file
        nexus_file_path = (
            Path(self.nexus_folder) / f"{self.instrument.upper()}_{run_number}.nxs.h5"
        )
        notebook_logging.info(f"\tNeXus file path: {nexus_file_path}")
        if nexus_file_path.exists():
            return extract_file_path_from_nexus(nexus_file_path)
        else:
            return None

    def extract_full_path(self, run_number=None):
        """
        Extract the full path to the run number based on the detector type.
        """
        notebook_logging.info(
            f"Extracting full path for run number: {run_number} with detector type: {self.detector_type}"
        )

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

    def display_infos(self, input_full_path=None):
        if input_full_path is None:
            return

        # retrieve the list of tiff files
        list_tiff = retrieve_list_of_tif(input_full_path)
        nbr_tiff = len(list_tiff)

        # load the first tiff file to get the shape and dtype
        data = Image.open(list_tiff[0])
        shape = data.size  # (width, height)
        dtype = np.array(data).dtype  # e.g. 'I;16' for 16-bit unsigned integer

        # present result in a table
        display(
            HTML(f"""
                        <h3>Information for run: {os.path.basename(input_full_path)}</h3>
                    <table border="3px solid black" style="border-collapse:collapse;">
                        <tr><th>Nbr TIFF</th><th>Images height</th><th>Images width</th><th>Data Type</th></tr>
                        <tr><td>{nbr_tiff}</td><td>{shape[0]}</td><td>{shape[1]}</td><td>{dtype}</td></tr>
                    </table>
        """)
        )

    def check_sample(self):
        """
        Check if the sample folder and runs are valid.
        """
        self.reset_sample_dicts()

        notebook_logging.info("Checking sample inputs...")
        display(HTML("Sample run numbers selected:"))

        if self.sample_run_numbers_widget.value.strip() != "":
            list_of_runs = extract_list_of_runs_from_string(
                self.sample_run_numbers_widget.value
            )
            notebook_logging.info(f"\t{list_of_runs = }")

            list_of_sample_full_path = []
            for _run in list_of_runs:
                _full_path = self.extract_full_path(run_number=_run)
                list_of_sample_full_path.append(_full_path)

            for _file_full_path in list_of_sample_full_path:
                if os.path.exists(_file_full_path):
                    notebook_logging.info(
                        f"\tSample run number {_file_full_path} - FOUND"
                    )
                    is_valid_run, report_dict = self.check_folder_is_valid(
                        _file_full_path
                    )
                    if is_valid_run:
                        nbr_tiff = report_dict["nbr_tiff"]
                        notebook_logging.info(
                            f"\tSample run number {_file_full_path} - FOUND with {nbr_tiff} tif* files"
                        )
                        display(
                            HTML(
                                f"<span style='color:green'>{_file_full_path}</span> - OK"
                            )
                        )
                        self.dict_sample[_file_full_path] = {}
                        self.dict_short_name_full_path["sample"][
                            os.path.basename(_file_full_path)
                        ] = _file_full_path
                        self.display_infos(input_full_path=_file_full_path)
                    else:
                        display(
                            HTML(
                                f"<span style='color:red'>{_file_full_path} - EMPTY!</span>"
                            )
                        )

                else:
                    notebook_logging.info(
                        f"\tSample run number {_file_full_path} - NOT FOUND"
                    )
                    display(
                        HTML(
                            f"<span style='color:red'>{_file_full_path} - NOT FOUND!</span>"
                        )
                    )

        else:
            notebook_logging.info(
                f"Sample run numbers selected: {self.sample_run_numbers_selected}"
            )
            if self.sample_run_numbers_selected is None:
                display(HTML("<span style='color:red'>No sample runs selected!</span>"))
                return

            for _run in self.sample_run_numbers_selected:
                _run = os.path.abspath(_run)
                if os.path.exists(_run):
                    notebook_logging.info(f"\tSample run number {_run} - FOUND")
                    # check here that the folder is not empty (contains tiff)
                    is_valid_run, report_dict = self.check_folder_is_valid(_run)
                    if is_valid_run:
                        nbr_tiff = report_dict["nbr_tiff"]
                        display(HTML(f"<span style='color:green'>{_run}</span> - OK"))
                        notebook_logging.info(
                            f"\tfolder seems to be a valid folder containing {nbr_tiff} tif* files"
                        )
                        self.dict_sample[_run] = {}
                        self.dict_short_name_full_path["sample"][
                            os.path.basename(_run)
                        ] = _run
                        self.display_infos(input_full_path=_run)
                    else:
                        display(HTML(f"<span style='color:red'>{_run} - EMPTY!</span>"))
                else:
                    display(
                        HTML(
                            f"<span style='color:red'>{_run} - NOT FOUND!</span> - ERROR!"
                        )
                    )
                    notebook_logging.info(f"\tSample run number {_run} - NOT FOUND!")

            self.sample_run_numbers_selected = None

    def select_ob_folder(self):
        self.select_folder(
            instruction="Browse ob top folder", next_function=self.ob_folder_selected
        )

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
                _, number = _run.split("_")
                ob_run_numbers_list.append(number)
            str_ob_run_numbers = ", ".join(ob_run_numbers_list)

            output_folder = DEBUG_DATA.output_folder

        else:
            str_ob_run_numbers = ""

        ob_label = widgets.HTML(
            value="<b><font color='green'>List of ob run numbers (ex: 8705, 8707)</font></b>"
        )

        self.ob_run_numbers_widget = widgets.Textarea(
            value=str_ob_run_numbers,
            placeholder="",
            layout=widgets.Layout(width="400px"),
        )
        vertical_layout = widgets.VBox(
            [
                ob_label,
                self.ob_run_numbers_widget,
            ]
        )
        display(vertical_layout)

        display(HTML("<span style='font-size: 16px; color:red'>OR</span>"))

        self.select_folder(
            instruction="Browse ob run number folders",
            next_function=self.save_ob_run_numbers_selected,
            start_dir=self.ob_folder,
            multiple=True,
        )

    def check_ob(self):
        """
        Check if the ob folder and runs are valid.
        """
        notebook_logging.info("Checking ob inputs...")
        display(HTML("OB run numbers selected:"))

        self.reset_ob_dicts()

        if self.ob_run_numbers_widget.value.strip() != "":
            list_of_runs = extract_list_of_runs_from_string(
                self.ob_run_numbers_widget.value
            )
            notebook_logging.info(f"\t{list_of_runs = }")

            list_of_ob_full_path = []
            for _run in list_of_runs:
                _full_path = self.extract_full_path(run_number=_run)
                list_of_ob_full_path.append(_full_path)

            for _file_full_path in list_of_ob_full_path:
                if os.path.exists(_file_full_path):
                    notebook_logging.info(f"\tOB run number {_file_full_path} - FOUND")
                    is_valid_run, report_dict = self.check_folder_is_valid(
                        _file_full_path
                    )
                    if is_valid_run:
                        nbr_tiff = report_dict["nbr_tiff"]
                        notebook_logging.info(
                            f"\tOB run number {_file_full_path} - FOUND with {nbr_tiff} tif* files"
                        )
                        display(
                            HTML(
                                f"<span style='color:green'>{_file_full_path}</span> - OK"
                            )
                        )
                        self.dict_ob[_file_full_path] = {}
                        self.dict_short_name_full_path["ob"][
                            os.path.basename(_file_full_path)
                        ] = _file_full_path
                        self.display_infos(input_full_path=_file_full_path)
                    else:
                        display(
                            HTML(
                                f"<span style='color:red'>{_file_full_path} - EMPTY!</span>"
                            )
                        )
                else:
                    notebook_logging.info(
                        f"\tOB run number {_file_full_path} - NOT FOUND"
                    )
                    display(
                        HTML(
                            f"<span style='color:red'>{_file_full_path} - NOT FOUND!</span>"
                        )
                    )

        else:
            notebook_logging.info(
                f"OB run numbers selected: {self.ob_run_numbers_selected}"
            )
            if self.ob_run_numbers_selected is None:
                display(HTML("<span style='color:red'>No OB runs selected!</span>"))
                return

            for _run in self.ob_run_numbers_selected:
                _run = os.path.abspath(_run)
                if os.path.exists(_run):
                    notebook_logging.info(f"\tOB run number {_run} - FOUND")
                    # check here that the folder is not empty (contains tiff)
                    is_valid_run, report_dict = self.check_folder_is_valid(_run)
                    if is_valid_run:
                        nbr_tiff = report_dict["nbr_tiff"]
                        display(HTML(f"<span style='color:green'>{_run}</span> - OK"))
                        notebook_logging.info(
                            f"\tfolder seems to be a valid folder containing {nbr_tiff} tif* files"
                        )
                        self.dict_short_name_full_path["ob"][os.path.basename(_run)] = (
                            _run
                        )
                        self.dict_ob[_run] = {}
                        self.display_infos(input_full_path=_run)
                    else:
                        display(HTML(f"<span style='color:red'>{_run} - EMPTY!</span>"))
                else:
                    display(
                        HTML(
                            f"<span style='color:red'>{_run} - NOT FOUND!</span> - ERROR!"
                        )
                    )
                    notebook_logging.info(f"\tOB run number {_run} - NOT FOUND!")
            self.ob_run_numbers_selected = None

    def select_dc_run_numbers(self):
        self.select_folder(
            instruction="Browse dc top folder", next_function=self.dc_folder_selected
        )

    def select_dc_run_numbers(self):
        if self.debug:
            dc_runs = DEBUG_DATA.dc_runs_selected
            dc_run_numbers_list = []
            for _run in dc_runs:
                _, number = _run.split("_")
                dc_run_numbers_list.append(number)
            str_dc_run_numbers = ", ".join(dc_run_numbers_list)

            output_folder = DEBUG_DATA.output_folder

        else:
            str_dc_run_numbers = ""

        dc_label = widgets.HTML(
            value="<b><font color='green'>List of dc run numbers (ex: 8705, 8707)</font></b>"
        )

        self.dc_run_numbers_widget = widgets.Textarea(
            value=str_dc_run_numbers,
            placeholder="",
            layout=widgets.Layout(width="400px"),
        )
        vertical_layout = widgets.VBox(
            [
                dc_label,
                self.dc_run_numbers_widget,
            ]
        )
        display(vertical_layout)

        display(HTML("<span style='font-size: 16px; color:red'>OR</span>"))

        self.select_folder(
            instruction="Browse dc run number folders",
            next_function=self.save_dc_run_numbers_selected,
            start_dir=self.dc_folder,
            multiple=True,
        )

    def check_dc(self):
        """
        Check if the dc folder and runs are valid.
        """
        notebook_logging.info("Checking dc inputs...")
        display(HTML("DC run numbers selected:"))

        self.reset_dc_dicts()

        if self.dc_run_numbers_widget.value.strip() != "":
            list_of_runs = extract_list_of_runs_from_string(
                self.dc_run_numbers_widget.value
            )
            notebook_logging.info(f"\t{list_of_runs = }")

            list_of_dc_full_path = []
            for _run in list_of_runs:
                _full_path = self.extract_full_path(run_number=_run)
                list_of_dc_full_path.append(_full_path)

            for _file_full_path in list_of_dc_full_path:
                if os.path.exists(_file_full_path):
                    notebook_logging.info(f"\tDC run number {_file_full_path} - FOUND")
                    is_valid_run, report_dict = self.check_folder_is_valid(
                        _file_full_path
                    )
                    if is_valid_run:
                        nbr_tiff = report_dict["nbr_tiff"]
                        notebook_logging.info(
                            f"\tDC run number {_file_full_path} - FOUND with {nbr_tiff} tif* files"
                        )
                        display(
                            HTML(
                                f"<span style='color:green'>{_file_full_path}</span> - OK"
                            )
                        )
                        self.dict_dc[_file_full_path] = {}
                        self.dict_short_name_full_path["dc"][
                            os.path.basename(_file_full_path)
                        ] = _file_full_path
                        self.display_infos(input_full_path=_file_full_path)
                    else:
                        display(
                            HTML(
                                f"<span style='color:red'>{_file_full_path} - EMPTY!</span>"
                            )
                        )
                else:
                    notebook_logging.info(
                        f"\tDC run number {_file_full_path} - NOT FOUND"
                    )
                    display(
                        HTML(
                            f"<span style='color:red'>{_file_full_path} - NOT FOUND!</span>"
                        )
                    )

        else:
            notebook_logging.info(
                f"DC run numbers selected: {self.dc_run_numbers_selected}"
            )
            if self.dc_run_numbers_selected is None:
                display(HTML("<span style='color:red'>No DC runs selected!</span>"))
                return

            for _run in self.dc_run_numbers_selected:
                _run = os.path.abspath(_run)
                if os.path.exists(_run):
                    notebook_logging.info(f"\tDC run number {_run} - FOUND")
                    # check here that the folder is not empty (contains tiff)
                    is_valid_run, report_dict = self.check_folder_is_valid(_run)
                    if is_valid_run:
                        nbr_tiff = report_dict["nbr_tiff"]
                        display(HTML(f"<span style='color:green'>{_run}</span> - OK"))
                        notebook_logging.info(
                            f"\tfolder seems to be a valid folder containing {nbr_tiff} tif* files"
                        )
                        self.dict_short_name_full_path["dc"][os.path.basename(_run)] = (
                            _run
                        )
                        self.dict_dc[_run] = {}
                        self.display_infos(input_full_path=_run)
                    else:
                        display(HTML(f"<span style='color:red'>{_run} - EMPTY!</span>"))
                else:
                    display(
                        HTML(
                            f"<span style='color:red'>{_run} - NOT FOUND!</span> - ERROR!"
                        )
                    )
                    notebook_logging.info(f"\tDC run number {_run} - NOT FOUND!")
            self.dc_run_numbers_selected = None

    def _load_and_get_integrated_ob(self, full_path):
        """
        Load the integrated open beam data from the given OB run path.
        This function is a placeholder and should be implemented to load the actual data.
        """
        notebook_logging.info(f"Loading integrated OB data for {full_path}")
        # Here you would load the integrated OB data, for example using a specific library
        # For now, we will just return a dummy value
        if self.dict_ob[full_path].get("data") is None:
            notebook_logging.info("No data found for this OB run, loading it now...")
            # load the data from the OB run
            notebook_logging.info(
                f"\tFull path to OB run: {os.path.basename(full_path)}"
            )
            list_tiff = retrieve_list_of_tif(full_path)
            notebook_logging.info(f"\tNumber of TIFF files found: {len(list_tiff)}")
            if len(list_tiff) == 0:
                display(
                    HTML(
                        f"<span style='color:red'>No TIFF files found in {full_path}!</span>"
                    )
                )
                notebook_logging.error(f"No TIFF files found in {full_path}!")
                return None
            data = load_data_using_multithreading(list_tiff, combine_tof=True)
            self.dict_ob[full_path]["data"] = data

        return self.dict_ob[full_path]["data"]

    def preview_ob_runs(self):
        if self.dict_ob is None:
            display(HTML("<span style='color:red'>No OB runs selected!</span>"))
            return

        notebook_logging.info("Previewing OB runs")

        # list_ob_short_runs = [os.path.basename(_run) for _run in self.ob_run_numbers]
        # self.dict_ob_runs = {_short_name: _full_name for _short_name, _full_name in zip(list_ob_short_runs, self.ob_run_numbers)}
        # self.dict_ob_data = {_short_name: None for _short_name in list_ob_short_runs}

        list_ob_key = list(self.dict_ob.keys())
        list_ob_short_runs = [os.path.basename(_run) for _run in list_ob_key]
        if len(list_ob_key) == 1:
            notebook_logging.info("Only one OB run")
            full_path = list_ob_key[0]
            notebook_logging.info(f"\tFull path to OB run: {full_path}")
            integrated_ob = self._load_and_get_integrated_ob(full_path)
            if integrated_ob is None:
                display(
                    HTML(
                        f"<span style='color:red'>Failed to load integrated OB data for {list_ob_short_runs[0]}!</span>"
                    )
                )
                return
            fig, ax = plt.subplots(figsize=(10, 6))
            im = ax.imshow(integrated_ob, cmap="viridis", aspect="auto")
            ax.set_title(f"Integrated OB run: {list_ob_short_runs[0]}")
            fig.colorbar(im, ax=ax, orientation="vertical", label="Intensity")
            plt.show()

        else:
            notebook_logging.info(f"Multiple OB runs to display: {len(list_ob_key)}")

            def display_ob_run(short_name):
                """
                Display the integrated OB run data.
                """
                full_path = self.dict_short_name_full_path["ob"][short_name]
                integrated_ob = self._load_and_get_integrated_ob(full_path)
                if integrated_ob is None:
                    display(
                        HTML(
                            f"<span style='color:red'>Failed to load integrated OB data for {os.path.basename(full_path)}!</span>"
                        )
                    )
                    return
                fig, ax = plt.subplots(figsize=(10, 6))
                im = ax.imshow(integrated_ob, cmap="viridis", aspect="auto")
                ax.set_title(f"Integrated OB run: {os.path.basename(full_path)}")
                fig.colorbar(im, ax=ax, orientation="vertical", label="Intensity")
                plt.show()

            list_ob_key = list(self.dict_short_name_full_path["ob"].keys())
            _display = interactive(
                display_ob_run,
                short_name=widgets.Dropdown(
                    options=list_ob_key,
                    description="OB run:",
                    layout=widgets.Layout(width="100%"),
                    disabled=False,
                ),
            )
            display(_display)

    def select_output_folder(self):
        self.select_folder(
            instruction="Select output folder",
            start_dir=self.working_dir,
            next_function=self.output_folder_selected,
            newdir_toolbar_button=True,
        )

    def retrieve_nexus_file_path(self):
        """
        Retrieve the NeXus file paths for sample and OB runs.

        This function assumes that the NeXus files are named in a specific format"""

        all_nexus_files_found = True
        notebook_logging.info("Retrieving NeXus file paths for sample and OB runs...")

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
            _disabled = False
        else:
            _value = False
            _disabled = True
        self.proton_charge_flag = widgets.Checkbox(
            description="Proton charge", value=_value, disabled=_disabled
        )

        self.shutter_counts_flag = widgets.Checkbox(
            description="Shutter counts",
            value=not tpx3_disabled_flag,
            disabled=tpx3_disabled_flag,
        )
        self.correct_chips_alignment_flag = widgets.Checkbox(
            description="Correct chips alignment", disabled=False, value=True
        )

        vertical_layout = widgets.VBox(
            [
                self.proton_charge_flag,
                self.shutter_counts_flag,
                self.correct_chips_alignment_flag,
            ]
        )
        display(vertical_layout)

        display(HTML("<hr>"))

        self.replace_ob_zeros_by_local_median_flag = widgets.Checkbox(
            description="Replace OB zeros by local median (will take much more time!)",
            value=False,
            layout=widgets.Layout(width="400px"),
        )
        self.replace_ob_zeros_by_local_median_flag.observe(
            self._on_replace_ob_zeros_by_local_median_flag_change, names="value"
        )
        self.correct_chips_alignment_flag = widgets.Checkbox(
            description="Correct chips alignment", disabled=False, value=True
        )
        display(self.replace_ob_zeros_by_local_median_flag)

        kernel_size_label = widgets.Label(
            value="Kernel size for local median (odd number))",
            layout=widgets.Layout(width="300"),
        )
        self.kernel_size_for_local_median_y = widgets.BoundedIntText(
            description="y axis:",
            value=3,
            min=1,
            max=99,
            step=2,
            layout=widgets.Layout(width="150px"),
        )
        self.kernel_size_for_local_median_x = widgets.BoundedIntText(
            description="x axis:",
            value=3,
            min=1,
            max=99,
            step=2,
            layout=widgets.Layout(width="150px"),
        )
        self.kernel_size_for_local_median_tof = widgets.BoundedIntText(
            description="tof axis:",
            value=3,
            min=1,
            max=99,
            step=2,
            layout=widgets.Layout(width="150px"),
        )
        hori_layout = widgets.HBox(
            [
                kernel_size_label,
                self.kernel_size_for_local_median_y,
                self.kernel_size_for_local_median_x,
                self.kernel_size_for_local_median_tof,
            ],
            hori_layout=widgets.Layout(align_items="center", width="100%"),
        )
        display(hori_layout)

        _label = widgets.Label(
            value="Maximum number of iterations:", layout=widgets.Layout(width="300px")
        )
        self.maximum_iterations_ui = widgets.BoundedIntText(
            value=10,
            min=1,
            max=20,
            step=1,
            layout=widgets.Layout(width="200px"),
        )
        hori_layout = widgets.HBox(
            [_label, self.maximum_iterations_ui],
            hori_layout=widgets.Layout(align_items="center", width="100%"),
        )
        display(hori_layout)

        display(HTML("<hr>"))

        label = widgets.Label(
            value="Distance source detector (m)", layout=widgets.Layout(width="200px")
        )
        self.distance_source_detector = widgets.FloatText(
            value=distance_source_detector_m[self.instrument],
            disabled=False,
            layout=widgets.Layout(width="50px"),
        )
        hori_layout = widgets.HBox([label, self.distance_source_detector])
        display(hori_layout)

        if self.instrument == "SNAP":
            label = widgets.Label(
                value="Detector offset (us)", layout=widgets.Layout(width="200px")
            )
            self.detector_offset_us = widgets.FloatText(
                value=0.0, disabled=False, layout=widgets.Layout(width="50px")
            )
            hori_layout = widgets.HBox([label, self.detector_offset_us])
            display(hori_layout)

    def _on_replace_ob_zeros_by_local_median_flag_change(self, change):
        if change["new"]:
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
            description="Export corrected stack of sample data",
            layout=widgets.Layout(width="100%"),
            value=False,
        )
        self.export_corrected_stack_of_ob_data = widgets.Checkbox(
            description="Export corrected stack of ob data",
            layout=widgets.Layout(width="100%"),
            value=False,
        )
        self.export_corrected_stack_of_normalized_data = widgets.Checkbox(
            description="Export corrected stack of normalized data",
            layout=widgets.Layout(width="100%"),
            value=True,
            disabled=True,
        )
        label = widgets.Label(
            value="Note: Any of the stacks exported will also contain the original spectra file"
        )
        vertical_layout = widgets.VBox(
            [
                self.export_corrected_stack_of_sample_data,
                self.export_corrected_stack_of_ob_data,
                self.export_corrected_stack_of_normalized_data,
                label,
            ]
        )
        display(vertical_layout)
        display(
            HTML("<span style='font-size: 16px; color:red'>Integrated images</span>")
        )
        self.export_corrected_integrated_sample_data = widgets.Checkbox(
            description="Export corrected integrated sample data",
            layout=widgets.Layout(width="100%"),
            value=False,
        )
        self.export_corrected_integrated_ob_data = widgets.Checkbox(
            description="Export corrected integrated ob data",
            layout=widgets.Layout(width="100%"),
            value=False,
        )
        self.export_corrected_integrated_normalized_data = widgets.Checkbox(
            description="Export corrected integrated normalized data",
            layout=widgets.Layout(width="100%"),
            value=False,
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
        display(
            HTML(
                f"Sample folder selected: <span style='color:blue'>{folder_selected}</span>"
            )
        )

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
        display(
            HTML(
                f"Open beam folder selected: <span style='color:blue'>{folder_selected}</span>"
            )
        )

    def dc_folder_selected(self, folder_selected):
        self.dc_folder = folder_selected
        display(
            HTML(
                f"Dark current folder selected: <span style='color:blue'>{folder_selected}</span>"
            )
        )

    def save_ob_run_numbers_selected(self, folder_selected):
        self.ob_run_numbers_selected = folder_selected

    def save_dc_run_numbers_selected(self, folder_selected):
        self.dc_run_numbers_selected = folder_selected

    def output_folder_selected(self, folder_selected):
        self.output_folder = folder_selected
        display(HTML("Output folder selected:"))
        if os.path.exists(folder_selected):
            display(
                HTML(f"<span style='color:green'>{folder_selected} - FOUND!</span>")
            )
            notebook_logging.info(f"Output folder selected: {folder_selected} - FOUND")
        else:
            display(
                HTML(
                    f"<span style='color:blue'>{folder_selected} - DOES NOT EXIST and will be CREATED!</span>"
                )
            )
            notebook_logging.info(
                f"Output folder selected: {folder_selected} - NOT FOUND and will be CREATED!"
            )

    def select_folder(
        self,
        instruction="Select a folder",
        next_function=None,
        start_dir=None,
        multiple=False,
        newdir_toolbar_button=False,
    ):
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
        sample_run_numbers = self.sample_run_numbers
        ob_run_numbers = self.ob_run_numbers
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
            shutter_counts_flag=self.shutter_counts_flag.value,
            # replace_ob_zeros_by_nan_flag=self.replace_ob_zeros_by_nan_flag.value,
            replace_ob_zeros_by_local_median_flag=self.replace_ob_zeros_by_local_median_flag.value,
            kernel_size_for_local_median=(
                self.kernel_size_for_local_median_y.value,
                self.kernel_size_for_local_median_x.value,
                self.kernel_size_for_local_median_tof.value,
            ),
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
