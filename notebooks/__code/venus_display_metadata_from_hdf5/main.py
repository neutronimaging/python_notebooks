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
from __code.venus_display_metadata_from_hdf5 import list_pvs
from __code._utilities.file import make_ascii_file
from __code._utilities import LAMBDA, MICRO, ANGSTROMS
from __code.ipywe import fileselector
from __code.file_folder_browser import FileFolderBrowser
from __code.ipywe.myfileselector import FileSelectorPanelWithJumpFolders


LOG_PATH = "/SNS/VENUS/shared/log/"
file_name, ext = os.path.splitext(os.path.basename(__file__))
LOG_FILE_NAME = os.path.join(LOG_PATH, f"{file_name}.log")

ENERGY_CONVERSION_FACTOR = 81.787


class VenusDisplayMetadataFromHdf5:

    def __init__(self, working_dir=None):
        self.working_dir = working_dir

        logging.basicConfig(filename=LOG_FILE_NAME,
                            filemode='w',
                            format='[%(levelname)s] - %(asctime)s - %(message)s',
                            level=logging.INFO)
        logging.info("*** Starting a new session ***")

    def select_event_nexus(self):

        start_dir = os.path.join(self.working_dir, 'nexus')

        self.nexus_ui = fileselector.FileSelectorPanel(instruction='Select NeXus file ...',
                                                       start_dir=start_dir,
                                                       next=self.load_metadata,
                                                       filters={'NeXus': ".h5"},
                                                       multiple=True,
                                                       stay_alive=False,
                                                       sort_in_reverse=True,
                                                       sort_by_alphabetical=True)
        self.nexus_ui.show()

    def value_of_pv_path(h5file, list_pv_path):
    
        with h5py.File(h5file, 'r') as nxs:
            for _path_entry in list_pv_path:
                nxs = nxs[_path_entry]
            return nxs['value'][:]

    def mean_value_of_pv_path(h5file, list_pv_path):
        with h5py.File(h5file, 'r') as nxs:
            for _path_entry in list_pv_path:
                nxs = nxs[_path_entry]
            return np.mean(np.array(nxs['value'][:]))

    def load_metadata(self, list_nexus_file_name):
        
        list_nexus_file_name.sort()

        logging.info(f"working with {list_nexus_file_name}")
     
        list_nexus = []
        list_mean_data = {_key: [] for _key in list_pvs.keys()}
        dict_data = {_nexus: {} for _nexus in list_nexus_file_name}

        for _nexus in list_nexus_file_name:
            
            dict_data[_nexus] = {}
            list_nexus.append(os.path.basename(_nexus))
            
            for _pv_key in list_pvs.keys():
                _pv_path = list_pvs[_pv_key]['path']
                _pv_label = list_pvs[_pv_key]['label']
                try:
                    _value = VenusDisplayMetadataFromHdf5.value_of_pv_path(_nexus, _pv_path)
                    _mean_value = VenusDisplayMetadataFromHdf5.mean_value_of_pv_path(_nexus, _pv_path)
                    list_mean_data[_pv_key].append(_mean_value)
                    dict_data[_nexus][_pv_key] = _value
                    logging.info(f"{_pv_label}: {_mean_value}")
                except KeyError:
                    logging.error(f"Error loading {_pv_label} from {_nexus}")
                    _value = None
                    list_mean_data[_pv_key].append(None)        
                    dict_data[_nexus][_pv_key] = None  

        self.dict_data = dict_data
        self.list_mean_data = list_mean_data
        self.display_metadata()

    def display_metadata(self):

        fig, axs = plt.subplots(nrows=len(list_pvs.keys()), ncols=2, num="Venus Metadata",
                                figsize=(8, 4*len(list_pvs.keys())),
                                )
        
        for _index, _pv_key in enumerate(self.list_mean_data.keys()):
            
            axs[_index, 0].plot(self.list_mean_data[_pv_key], 'o-', label=_pv_key)
            axs[_index, 0].set_title(f"{list_pvs[_pv_key]['label']}")
            axs[_index, 0].set_ylabel(list_pvs[_pv_key]['label'])
            axs[_index, 0].set_xlabel("Nexus file index")
            axs[_index, 0].legend()
       
            axs[_index, 1].plot(self.)

        plt.tight_layout()
        plt.show()


 