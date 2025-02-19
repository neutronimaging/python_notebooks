import os
import logging
import h5py
import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interactive
import ipywidgets as widgets
from IPython.core.display import display, HTML
import algotom.io.loadersaver as losa

from neutronbraggedge.experiment_handler import *
from neutronbraggedge.braggedge import BraggEdge as BraggEdgeLibrary

from __code._utilities.file import get_full_home_file_name
from __code._utilities.json import save_json
from __code._utilities import LAMBDA, MICRO, ANGSTROMS
from __code.ipywe import fileselector
from __code.file_folder_browser import FileFolderBrowser

LOG_FILE_NAME = ".venus_monitor_hdf5.log"

ENERGY_CONVERSION_FACTOR = 81.787


class VenusNexusListPCAboveThreshold:

    list_nexus_with_missing_key = []

    def __init__(self, working_dir=None):
        self.working_dir = working_dir

        self.log_file_name = get_full_home_file_name(LOG_FILE_NAME)
        logging.basicConfig(filename=self.log_file_name,
                            filemode='w',
                            format='[%(levelname)s] - %(asctime)s - %(message)s',
                            level=logging.INFO)
        logging.info("*** Starting a new session ***")

    def proton_charge_threshold(self):
        pc_ui = widgets.VBox([
            widgets.Label("Proton charge threshold (C):",
                          layout=widgets.Layout(width='50%')),
            widgets.FloatText(1,
                              layout=widgets.Layout(width='200px')),              
        ])
        display(pc_ui)
        self.proton_charge_threshold_ui = pc_ui.children[1]

    def select_list_nexus(self):

        start_dir = os.path.join(self.working_dir, 'nexus')

        self.nexus_ui = fileselector.FileSelectorPanel(instruction='Select NeXus files ...',
                                                       start_dir=start_dir,
                                                       next=self.check_proton_charge_value,
                                                       filters={'NeXus': ".h5"},
                                                       multiple=True,
                                                       sort_by_time=True,
                                                       sort_in_reverse=True)
        self.nexus_ui.show()

    def check_proton_charge_value(self, list_nexus_files):
        self.retrieve_proton_charge_value(list_nexus_files)
        self.list_good_nexus()    
    
    def retrieve_proton_charge_value(self, list_nexus_files):

        print("Retrieving proton charge value ...", end="")
        # key is the nexus file name
        # value is the proton charge
        file_name_proton_charge_dict = {}
        list_nexus_with_missing_key = []

        for _nexus in list_nexus_files:

            with h5py.File(_nexus, 'r') as nxs:
                
                try:
                    _proton_charge = nxs['entry']['proton_charge'][()][0]
                    _proton_charge *= 1e-12  # go to Coulomb
                except KeyError:
                    self.list_nexus_with_missing_key.append(_nexus)
                    _proton_charge = np.nan
              
            file_name_proton_charge_dict[_nexus] = _proton_charge

        self.file_name_proton_charge_dict = file_name_proton_charge_dict
        print(" done!")

    def list_good_nexus(self):
        
        self.list_good_nexus = []
        print("Listing good nexus:")
        _threshold = self.proton_charge_threshold_ui.value
        _dict = self.file_name_proton_charge_dict
        for _nexus in _dict.keys():
            
            if _dict[_nexus] >= _threshold:
                self.list_good_nexus.append(_nexus)
                print(f"{_nexus}: {_dict[_nexus]}")
        print("Done!")    

    def export_good_nexus(self):
        shared_folder = os.path.join(self.working_dir, 'shared', 'processed_data')
        threshold = f"{self.proton_charge_threshold_ui.value:.2f}"
        threshold = threshold.replace(".", "_")
        file_name = os.path.join(shared_folder, f"nexus_above_{threshold}.json")
        save_json(file_name, self.list_good_nexus)
        print(f"Json file created with name: {file_name}")
