import glob
from dotenv import load_dotenv
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
import ipysheet
from ipysheet import sheet, cell, row, column, from_dataframe, to_array, calculation

# from pleiades.processing.normalization import normalization as normalization_with_pleaides
# from pleiades.processing import Roi as PleiadesRoi
# from pleiades.processing import Facility
from pleiades.sammy.io.data_manager import convert_csv_to_sammy_twenty, validate_sammy_twenty_format
from pleiades.sammy.io.json_manager import JsonManager
from pleiades.sammy.io.inp_manager import InpManager
from pleiades.sammy.backends.local import LocalSammyRunner
from pleiades.sammy.config import LocalSammyConfig
from pleiades.sammy.interface import SammyFilesMultiMode


from __code.resonance_fitting import VENUS_RES_FUNC, SAMMY_EXE_PATH
from __code._utilities.list import extract_list_of_runs_from_string
from __code._utilities.nexus import extract_file_path_from_nexus

# from __code.ipywe.myfileselector import MyFileSelectorPanel
from __code.resonance_fitting.config import DEBUG_DATA, timepix1_config, timepix3_config
from __code.resonance_fitting.get import Get

from __code.normalization_tof.normalization_tof import NormalizationTof
from __code.ipywe.fileselector import FileSelectorPanel as FileSelectorPanel
from __code.normalization_tof import DetectorType, autoreduce_dir, distance_source_detector_m, raw_dir
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
    inp_file = None
    json_path = None
    sammy_files_multi_mode = None

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

    df_to_use = None
    horizontal_box = None # total abundance display box

    def __init__(self, working_dir=None, debug=False):
        self.folder_paths = FolderPaths()
        self.files_paths = FilesPaths()
        
        self.initialize_logging()

        load_dotenv(".envrc")
        
        if debug:
            self.folder_paths.working = Path(DEBUG_DATA.working_dir)
            self.folder_paths.output = Path(DEBUG_DATA.output_folder)

        else:
            self.folder_paths.working = Path(working_dir)
            self.folder_paths.output = self.folder_paths.working / "shared"

        self.folder_paths.nexus = self.folder_paths.working / "nexus"
        self.debug = debug

        notebook_logging.info(f"{self.folder_paths.working =}")
        notebook_logging.info(f"{self.folder_paths.working.parts =}")

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
        display(HTML(f"<span style='font-size: {FONT_SIZE}px; color:blue'>Log file: {log_file_name}</span>"))

    def select_normalized_text_file(self):
        self.file_selector = FileSelectorPanel(
            start_dir=str(self.folder_paths.shared),
            type="file",
            instruction="Select normalized ASCII file",
            filters={"transmission txt": "*_transmission.txt"},
            default_filter="transmission txt",
            multiple=False,
            next=self._transmitted_text_file_selected,
        )
        self.file_selector.show()

    def select_output_folder(self):
        self.folder_selector = FileSelectorPanel(
            start_dir=str(self.folder_paths.shared),
            type="directory",
            instruction="Select output folder",
            multiple=False,
            next=self._output_folder_selected,
        )
        self.folder_selector.show()

    def _output_folder_selected(self, folder_path):
        self._stagging_folders_setup(Path(folder_path))
        self._converting_transmission_to_twenty_format()

    def select_isotope_and_abundance(self):
        list_elements = periodictable.elements
        dict_elements = {}
        for _el in list_elements:
            dict_elements[_el.name.capitalize()] = {'symbol': _el.symbol}
        list_elements_names = list(dict_elements.keys())
        list_elements_names.sort()
        self.dict_elements = dict_elements

        if self.debug:
            default_symbol_selected = DEBUG_DATA.isotope_element
            for _el_name in dict_elements.keys():
                if dict_elements[_el_name]['symbol'] == default_symbol_selected:
                    default_element_selected = _el_name
                    break
        else:
            default_symbol_selected = "Hydrogen"

        display(HTML(f"<span style='font-size: {FONT_SIZE}px; color:blue'>Select element/isotopes to use:</span>"))
        self.list_elements_widget = widgets.Dropdown(
            options=list_elements_names,
            value=default_element_selected,
            description="",
            disabled=False,
        )
        display(self.list_elements_widget)
        self.list_elements_widget.observe(self._on_element_change, names='value')
        
        self._display_tables_and_buttons()

        # empty stylesheet table for now
        _df = pd.DataFrame({'Isotope': [None], 'Abundance (%)': [0]})
        self.isotope_to_use_sheet = from_dataframe(_df)
        self.df_to_use = _df
        display(self.isotope_to_use_sheet)

    def _transmitted_text_file_selected(self, file_path):
        file_path = Path(file_path)
        notebook_logging.info(f"Transmitted text file selected: {file_path}")
        display(HTML(f"<span style='font-size: {FONT_SIZE}px; color:green'>Transmission file: {file_path.name} ... selected!</span>"))

        self.files_paths.transmission = file_path

    def _stagging_folders_setup(self, file_path):

        # set up various stagging folder for SAMMY
        self.folder_paths.output = Path(file_path)
        self.folder_paths.stagging = self.folder_paths.output / "hf_analysis"
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

        notebook_logging.info("Stagging folders setup:")    
        notebook_logging.info(f"output folder: {self.folder_paths.output} ... {self.folder_paths.output.is_dir()}   ")
        notebook_logging.info(f"Stagging folder: {self.folder_paths.stagging} ... {self.folder_paths.stagging.is_dir()}")
        notebook_logging.info(f"Spectra folder: {self.folder_paths.spectra} ... {self.folder_paths.spectra.is_dir()}")
        notebook_logging.info(f"Twenty folder: {self.folder_paths.twenty} ... {self.folder_paths.twenty.is_dir()}")
        notebook_logging.info(f"SAMMY working folder: {self.folder_paths.sammy_working} ... {self.folder_paths.sammy_working.is_dir()}")
        notebook_logging.info(f"SAMMY output folder: {self.folder_paths.sammy_output} ... {self.folder_paths.sammy_output.is_dir()}")
        display(HTML(f"<span style='font-size: {FONT_SIZE}px; color:green'>Stagging folders created!</span>"))

    def _converting_transmission_to_twenty_format(self):
        notebook_logging.info("Converting transmission data .txt to .twenty format for SAMMY ...")
        twenty_file = self.folder_paths.twenty / self.files_paths.transmission.name.replace(".txt", ".twenty")
        convert_csv_to_sammy_twenty(self.files_paths.transmission, twenty_file)
        if validate_sammy_twenty_format(twenty_file):
            notebook_logging.info(f"Conversion successful! Twenty file created at: {twenty_file}")
            display(HTML(f"<span style='font-size: {FONT_SIZE}px; color:green'>Twenty file created at: {twenty_file}</span>"))
        else:
            notebook_logging.error("Conversion failed! The generated .twenty file is not valid.")
            display(HTML(f"<span style='font-size: {FONT_SIZE}px; color:red'>Conversion failed! The generated .twenty file is not valid.</span>"))

    def _on_element_change(self, change):
        notebook_logging.info(f"Element selected: {change['new']}")
        self.isotope_sheet.close()
        element_symbol = self.dict_elements[change['new']]['symbol']
        self._create_and_display_isotope_table(element_symbol=element_symbol)

        self.isotope_to_use_sheet.close()
        self.validate_isotope_button.close()
        self.isotope_sheet.close()
        self.horizontal_box.close()

        self.isotope_to_use_sheet = from_dataframe(self.df_to_use)

        self._display_tables_and_buttons()
        display(self.isotope_to_use_sheet)
        self._update_total_abundance_of_isotopes_to_use()

    def _get_dict_isotopes(self, element_symbol):
        """
        Get a dictionary of isotopes and their abundances for a given element.
        
        dict = {[isotope_name]: {'abundance': None, 'mass': None}}
        
        return dict
        """
        # element = periodictable.elements.symbol(element_name)
        _dict = {}
        for _el in getattr(periodictable, element_symbol):
            _dict[str(_el)] = {'abundance': _el.abundance, 
                          'mass': _el.mass}

        notebook_logging.info(f"in get_dict_isotopes: {element_symbol = }, {_dict = }")
        return _dict

    def _create_and_display_isotope_table(self, element_symbol):

        dict_isotopes = self._get_dict_isotopes(element_symbol)

        list_isotopes_for_this_element = dict_isotopes.keys()
        notebook_logging.info(f"{list_isotopes_for_this_element}")
        # list_mass_isotopes = [dict_isotopes[iso]['mass'] for iso in list_isotopes_for_this_element]
        list_abundance_isotopes = [dict_isotopes[iso]['abundance'] for iso in list_isotopes_for_this_element]
        
        # create a boolean array of the same length as list_isotopes_for_this_element

        list_use_it = np.array([False for _ in list_isotopes_for_this_element])
        for _index, value in enumerate(list_abundance_isotopes):
            if value > 0:
                list_use_it[_index] = True

        temp_dict = {'Isotope': np.array(list_isotopes_for_this_element), 
                    'Abundance (%)': np.array(list_abundance_isotopes),
                    'use it': list_use_it}
        
        df = pd.DataFrame(temp_dict)

        self.isotope_sheet = from_dataframe(df)
        # self.isotope_sheet.column_width = 50
        display(self.isotope_sheet)

    def on_validate_isotope_selection(self, b):
        """Reached when the user clicks the ADD TO LIST OF ELEMENTS/ISOTOPES TO CONSIDER button"""

        notebook_logging.info("Adding to list of elements/isotopes to consider ...")
        df = ipysheet.to_dataframe(self.isotope_sheet)
        notebook_logging.info(f"Isotope selection:\n{df}")

        array = to_array(self.isotope_sheet)
        notebook_logging.info(f"Isotope selection as array:\n{array}")
        
        for _index, row in enumerate(array):
            notebook_logging.info(f"at {_index =}, {row[0] = }, {row[1] = }, {row[2] = }")

        # retrieve the content of the isotope_to_use_sheet
        df_to_use = ipysheet.to_dataframe(self.isotope_to_use_sheet)
        # remove any row with 'Isotope' = None
        df_to_use = df_to_use[df_to_use['Isotope'].notna()]
        notebook_logging.info(f"Current isotopes to use:\n{df_to_use}")

        # add it the new isotopes selected with 'use it' = True
        for _index, row in enumerate(array):
            notebook_logging.info(f"Processing row {_index}: {row}, {row[2] =}")
            if str(row[2]) == 'True':  # 'use it' is True
                isotope_name = row[0]
                abundance = f"{float(str(row[1])):.4f}"
                notebook_logging.info(f"Adding isotope: {isotope_name} with abundance: {abundance}")
                df_to_use = pd.concat([df_to_use, pd.DataFrame({'Isotope': [isotope_name], 'Abundance (%)': [abundance]})], ignore_index=True)

         # remove duplicates
        self.df_to_use = df_to_use.drop_duplicates(subset='Isotope')

        self.isotope_to_use_sheet.close()
        self.validate_isotope_button.close()
        self.isotope_sheet.close()

        self.isotope_to_use_sheet = from_dataframe(self.df_to_use)

        # listen to all events in this table
        for cell in self.isotope_to_use_sheet.cells:
            cell.observe(self._on_isotope_to_use_table_change, names='value')

        self._display_tables_and_buttons()
        display(self.isotope_to_use_sheet)
        
        self._update_total_abundance_of_isotopes_to_use()

        # disable button (to make sure only 1 element is added at a time)
        # self.validate_isotope_button.disabled = True        

    def _on_isotope_to_use_table_change(self, change):
        self._update_total_abundance_of_isotopes_to_use()

    def _update_total_abundance_of_isotopes_to_use(self):

        if self.horizontal_box:
            self.horizontal_box.close()

        df_to_use = ipysheet.to_dataframe(self.isotope_to_use_sheet)
        list_abundances = df_to_use['Abundance (%)'].tolist()
        list_abundances_float = [float(_value) for _value in list_abundances]
        total_abundance = sum(list_abundances_float)
        notebook_logging.info(f"Total abundance of isotopes to use: {total_abundance} %")

        if total_abundance > 100.0:
            color = "red"
        else:
            color = "blue"

        self.total_abundance_label = widgets.HTML(
            value=f"<span style='font-size: {FONT_SIZE}px; color:{color}'>Total abundance of isotopes to use: <b>{total_abundance:.2f} %</b></span>"
        )
        self.horizontal_box = widgets.HBox([self.total_abundance_label])
        display(self.horizontal_box)

    def _display_tables_and_buttons(self):
        """display the isotope table. the button to validate the selection as well as the table of isotopes to use
        """
        
        dict_elements = self.dict_elements

        full_name_of_element = self.list_elements_widget.value
        element_symbol = dict_elements[full_name_of_element]['symbol']

        self._create_and_display_isotope_table(element_symbol=element_symbol)
        
        self.validate_isotope_button = widgets.Button(
            description="Add to list of elements/isotopes to consider",
            layout=widgets.Layout(width="100%"),
            disabled=False,
            button_style="success",  # 'success', 'info', 'warning', 'danger' or ''
            tooltip="Click to validate isotope selection",
            icon="plus-circle",  # (FontAwesome names without the `fa-` prefix)
        )
        self.validate_isotope_button.on_click(self.on_validate_isotope_selection)
        display(self.validate_isotope_button)

    def _reformat_list_isotopes(self, list_isotopes):
        """
        to go from "155-Hf" to "Hf-155"
        """
        list_reformatted = []
        for _iso in list_isotopes:
            parts = _iso.split('-')
            if len(parts) == 2:
                reformatted = f"{parts[1]}-{parts[0]}"
                list_reformatted.append(reformatted)
            else:
                notebook_logging.warning(f"Unexpected isotope format: {_iso}")
        return list_reformatted
    

    def define_configuration(self):
        self._create_json_manager()
        self._setup_element_manager()

    def _create_json_manager(self):
        """
        forceRMoore: this should always be yes when we are using it for fitting number density
        purgeSpinGropus: this has to be yes to avoid including irrelevant resonance entries, this is the new feature we ask Doro to added to Sammy this past summer
        fudge: fudge factor, this determines the step size used in fitting, users should not need to worry about it
        """
        notebook_logging.info("Creating configuration file for resonance fitting ...")

        # retrieve isotopes and abundances to use
        df_to_use = ipysheet.to_dataframe(self.isotope_to_use_sheet)
        list_isotopes = df_to_use['Isotope'].tolist()
        list_isotopes_reformatted = self._reformat_list_isotopes(list_isotopes)
        list_abundances = df_to_use['Abundance (%)'].tolist()
        list_abundances_float = [float(_value)*0.01 for _value in list_abundances]

        notebook_logging.info(f"\t{list_isotopes = }")
        notebook_logging.info(f"\t{list_isotopes_reformatted =}")
        notebook_logging.info(f"\t{list_abundances = }")
        notebook_logging.info(f"\t{list_abundances_float = }")
        notebook_logging.info(f"\t{self.folder_paths.stagging = }")
        self.json_manager = JsonManager()
        json_path = self.json_manager.create_json_config(
            isotopes=list_isotopes_reformatted,
            abundances=list_abundances_float,
            working_dir=self.folder_paths.stagging,
            custom_global_settings={"forceRMoore": "yes",
                                    "purgeSpinGroups": "yes",
                                    "fudge": "0.7"}
        )

        self.files_paths.json_path = json_path

        notebook_logging.info(f"Configuration file created at: {json_path}")
        endf_files = [f for f in os.listdir(self.folder_paths.stagging) if f.endswith('.par')]
        notebook_logging.info(f"ENDf files found in working directory: {len(endf_files)} files")
        for f in sorted(endf_files):
            notebook_logging.info(f"\t- {f}")
        display(HTML(f"<span style='font-size: {FONT_SIZE}px; color:green'>Configuration file created at: {json_path}</span>"))

    def _setup_element_manager(self):

        # from all the elements selected, let's find out the one with the most abundant isotope
        table_array = to_array(self.isotope_to_use_sheet)
        max_abundance = 0.0
        for _element, _abundance in table_array:
            _float_abundance = float(str(_abundance))
            if _float_abundance > max_abundance:
                max_abundance = _float_abundance
                most_abundant_isotope = _element
           
        notebook_logging.info(f"Most abundant isotope selected: {most_abundant_isotope}")

        mass_number_str, element_symbol = most_abundant_isotope.split('-')
        my_periodic_table_element = getattr(periodictable, element_symbol)

        self.most_abundant_element_symbol = element_symbol
        display(HTML(f"<span style='font-size: {FONT_SIZE}px; color:blue'>Most Abundant Element Selected: <b>{element_symbol}</b></span>"))

        label_width = "160px"
        text_width = "50px"
        # mass number of the element selected
        _label_left = widgets.HTML("<div style='text-align: right'>Mass number:</div>",
                                   layout=widgets.Layout(width=label_width))
        self.mass_number_widget = widgets.IntText(value=int(mass_number_str), 
                                       disabled=False,
                                       layout=widgets.Layout(width=text_width))
        _hori_layout_1 = widgets.HBox([_label_left, 
                                       self.mass_number_widget])
        display(_hori_layout_1)

        # density (g/cm^3)
        
        _label_left = widgets.HTML("<div style='text-align: right'>Density (g/cm<sup>3</sup>):</div>",
                                   layout=widgets.Layout(width=label_width))
        self.density_widget = widgets.FloatText(value=my_periodic_table_element.density, 
                                     disabled=False,
                                     layout=widgets.Layout(width=text_width))
        _hori_layout_2 = widgets.HBox([_label_left, self.density_widget])
        display(_hori_layout_2)

        # thickness (mm)
        _label_left = widgets.HTML("<div style='text-align: right'>Thickness (mm):</div>",
                                   layout=widgets.Layout(width=label_width))
        self.thickness_widget = widgets.FloatText(value=0.05, 
                                       disabled=False,
                                       layout=widgets.Layout(width=text_width))
        _hori_layout_3 = widgets.HBox([_label_left, self.thickness_widget])
        display(_hori_layout_3)

        # atomic mass amu
        _label_left = widgets.HTML("<div style='text-align: right'>Atomic mass (amu):</div>",
                                   layout=widgets.Layout(width=label_width))
        self.atomic_mass_widget = widgets.FloatText(value=my_periodic_table_element.mass, 
                                         disabled=False,
                                         layout=widgets.Layout(width=text_width))
        _hori_layout_4 = widgets.HBox([_label_left, self.atomic_mass_widget])
        display(_hori_layout_4) 

        # abundance (%)
        _label_left = widgets.HTML("<div style='text-align: right'>Abundance (%):</div>",
                                   layout=widgets.Layout(width=label_width))
        self.abundance_widget = widgets.FloatSlider(value=100.0, min=0, max=100, step=0.1, disabled=False)
        _hori_layout_5 = widgets.HBox([_label_left, self.abundance_widget])
        display(_hori_layout_5)

        # energy range (ev)
        _label_left = widgets.HTML("<div style='text-align: right'>Energy range (eV):</div>",
                                   layout=widgets.Layout(width=label_width))
        self.energy_range_widget = widgets.FloatRangeSlider(value=[1.0, 200.0], min=0, max=2000, step=0.1, disabled=False)
        _hori_layout_6 = widgets.HBox([_label_left, self.energy_range_widget])
        display(_hori_layout_6)

        # temperature (K)
        _label_left = widgets.HTML("<div style='text-align: right'>Temperature (K):</div>",
                                   layout=widgets.Layout(width=label_width))
        self.temperature_widget = widgets.FloatSlider(value=293.6, min=0, max=1000, step=0.1, disabled=False)
        _hori_layout_7 = widgets.HBox([_label_left, self.temperature_widget])
        display(_hori_layout_7)

        # title
        _label_left = widgets.HTML("<div style='text-align: right'>Title:</div>",
                                   layout=widgets.Layout(width=label_width))
        o_get = Get(parent=self)
        _element_name = o_get.full_name_of_element_from_abreviation(self.most_abundant_element_symbol)
        _ipts = self.ipts
        _instrument = self.instrument
        _title = f"{_element_name} multip-isotope transmission analysis - {_instrument} {_ipts}"
        self.title_widget = widgets.Text(value=_title, 
                                        disabled=False,
                                        layout=widgets.Layout(width="100%"))
        _hori_layout_8 = widgets.HBox([_label_left, self.title_widget], layout=widgets.Layout(width="100%"))
        display(_hori_layout_8)

    def create_configurations(self):
        self._create_multi_isotope_inp()
        self._sammy_files_multi_mode()
        self._local_sammy_config()


        display(HTML(f"<span style='font-size: {FONT_SIZE}px; color:green'>SAMMY input files created in: {self.folder_paths.sammy_working}!</span>") )

    def _create_multi_isotope_inp(self):

        notebook_logging.info("Creating SAMMY input file for resonance fitting ...")
        _element = self.most_abundant_element_symbol
        mass_number = self.mass_number_widget.value
        density = self.density_widget.value
        thickness = self.thickness_widget.value
        atomic_mass = self.atomic_mass_widget.value
        abundance = self.abundance_widget.value * 0.01  # convert to fraction
        energy_range = self.energy_range_widget.value
        min_energy = energy_range[0]
        max_energy = energy_range[1]
        temperature = self.temperature_widget.value
        title = self.title_widget.value

        material_props = {
            'element': _element,
            'mass_number': mass_number,
            'density_g_cm3': density,
            'thickness_mm': thickness,
            'atomic_mass_amu': atomic_mass,
            'abundance': abundance,
            'min_energy': min_energy,
            'max_energy_ev': max_energy,
            'temperature_K': temperature}
        notebook_logging.info(f"{material_props = }")

        inp_file = self.folder_paths.sammy_working / "hf_fitting.inp"
        self.files_paths.inp_file = inp_file
        notebook_logging.info(f"{inp_file = }")

        notebook_logging.info(f"{title =}")
        notebook_logging.info(f"{VENUS_RES_FUNC =}")

        notebook_logging.info(f"calling InpManager.create_multi_isotope_inp ...")
        InpManager.create_multi_isotope_inp(
            inp_file,
            title=title,
            material_properties=material_props,
            resolution_file_path=VENUS_RES_FUNC,
        )
        notebook_logging.info(f"SAMMY input file created at: {inp_file}")

    def _sammy_files_multi_mode(self):
        notebook_logging.info("Creating SAMMY files for multi-isotope resonance fitting ...")
        transmission_file_path = self.files_paths.transmission.name
        notebook_logging.info(f"{transmission_file_path = }")
        data_file = self.folder_paths.twenty / f"{transmission_file_path.replace('.txt', '.twenty')}"
        notebook_logging.info(f"{data_file = }")

        files = SammyFilesMultiMode(
            input_file=self.files_paths.inp_file,
            json_config_file=self.files_paths.json_path,
            data_file=data_file,
            endf_directory=self.folder_paths.working
        )
        self.files_paths.sammy_files_multi_mode = files
        notebook_logging.info("SAMMY files for multi-isotope resonance fitting created.")

    def _local_sammy_config(self):
        notebook_logging.info("Setting up local SAMMY configuration ...")
        sammy_executable = SAMMY_EXE_PATH
        working_directory = self.folder_paths.sammy_working
        output_directory = self.folder_paths.sammy_output

        config = LocalSammyConfig(sammy_executable=sammy_executable,
                                  working_dir=working_directory,
                                  output_dir=output_directory)

        runner = LocalSammyRunner(config=config)
        notebook_logging.info("Done running LocalSammyConfig and LocalSammyRunner!")