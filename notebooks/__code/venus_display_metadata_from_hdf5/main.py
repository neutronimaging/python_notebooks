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

    display_average_metadata = False
    list_mean_data = {}
    list_mean_data_second_set = {}
    
    def __init__(self, working_dir=None):
        self.working_dir = working_dir

        logging.basicConfig(filename=LOG_FILE_NAME,
                            filemode='w',
                            format='[%(levelname)s] - %(asctime)s - %(message)s',
                            level=logging.INFO)
        logging.info("*** Starting a new session ***")

    def select_event_nexus(self, display_average_metadata=False):
        self.display_average_metadata = display_average_metadata

        self.legend_ui = widgets.Text(value="", placeholder='Type your legend here', description='Legend:', disabled=False)
        display(self.legend_ui)

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
        dict_data, list_mean_data, list_nexus = self._load_metadata(list_nexus_file_name)
        self.dict_data = dict_data
        self.list_mean_data = list_mean_data
        self.list_nexus = list_nexus       
        if self.display_average_metadata:
            self.display_average_metadata()
        else:
            self.display_metadata()

    def display_metadata(self):

        fig, axs = plt.subplots(nrows=len(list_pvs.keys()), ncols=2, num="Venus Metadata",
                                figsize=(12, 4*len(list_pvs.keys())),
                                )
        
        for _index, _pv_key in enumerate(self.list_mean_data.keys()):
            
            axs[_index, 0].plot(self.list_mean_data[_pv_key], 'o-', label=self.legend_ui.value)
            axs[_index, 0].set_title(f"Mean {list_pvs[_pv_key]['label']}")
            axs[_index, 0].set_ylabel(list_pvs[_pv_key]['label'])
            axs[_index, 0].set_xlabel("Nexus file index")
            axs[_index, 0].set_xticks(range(len(self.list_mean_data[_pv_key])), labels=self.list_nexus, rotation=90)
            axs[_index, 0].legend()
       
            for _nexus in self.dict_data.keys():
                _data = self.dict_data[_nexus][_pv_key]
                if _data is not None:
                    axs[_index, 1].plot(_data, '.-', label=os.path.basename(_nexus))
                    axs[_index, 1].set_xlabel("value index")
                    axs[_index, 1].set_ylabel(list_pvs[_pv_key]['label'])
                    axs[_index, 1].set_title(f"full {list_pvs[_pv_key]['label']} ")
                    axs[_index, 1].legend()
            # axs[_index, 1].set_title(f"{list_pvs[_pv_key]['label']} vs. time")

        plt.tight_layout()
        plt.show()

    def display_first_and_second_set(self):

        fig, axs = plt.subplots(nrows=len(list_pvs.keys()), ncols=2, num="Venus Metadata",
                                        figsize=(12, 4*len(list_pvs.keys())),
                                        )
                
        for _index, _pv_key in enumerate(self.list_mean_data.keys()):
            
            axs[_index, 0].plot(self.list_mean_data[_pv_key], 'o-', label=self.legend_ui.value)
            axs[_index, 0].set_title(f"Mean {list_pvs[_pv_key]['label']}")
            axs[_index, 0].set_ylabel(list_pvs[_pv_key]['label'])
            axs[_index, 0].set_xlabel("Nexus file index")
            axs[_index, 0].set_xticks(range(len(self.list_mean_data[_pv_key])), labels=self.list_nexus, rotation=90)
            axs[_index, 0].legend()
    
            axs[_index, 1].plot(self.list_mean_data_second_set[_pv_key], 'o-', color='red', label=self.legend_second_set_ui.value)
            axs[_index, 1].set_title(f"Mean {list_pvs[_pv_key]['label']}")
            axs[_index, 1].set_ylabel(list_pvs[_pv_key]['label'])
            axs[_index, 1].set_xlabel("Nexus file index")
            axs[_index, 1].set_xticks(range(len(self.list_mean_data_second_set[_pv_key])), 
                                      labels=self.list_nexus_second_set,
                                        rotation=90)
            axs[_index, 1].legend()
           
        plt.tight_layout()
        plt.show()

    def display_average_metadata(self):

            fig, axs = plt.subplots(nrows=len(list_pvs.keys()), ncols=1, num="Venus Metadata",
                                    figsize=(10, 4*len(list_pvs.keys())),
                                    )
            
            for _index, _pv_key in enumerate(self.list_mean_data.keys()):
                
                axs[_index].plot(self.list_mean_data[_pv_key], 'o-', label=self.legend_ui.value)
                axs[_index].set_title(f"Mean {list_pvs[_pv_key]['label']}")
                axs[_index].set_ylabel(list_pvs[_pv_key]['label'])
                axs[_index].set_xlabel("Nexus file index")
                axs[_index].set_xticks(range(len(self.list_mean_data[_pv_key])), labels=self.list_nexus, rotation=90)
                axs[_index].legend()
              
            plt.tight_layout()
            plt.show()

    def select_event_nexus_second_set(self, display_average_metadata=False):
        self.display_average_metadata = display_average_metadata

        self.legend_second_set_ui = widgets.Text(value="", 
                                                 placeholder='Type your legend here', 
                                                 description='Legend:', 
                                                 disabled=False)
        display(self.legend_second_set_ui)

        start_dir = os.path.join(self.working_dir, 'nexus')

        self.nexus_ui = fileselector.FileSelectorPanel(instruction='Select NeXus file ...',
                                                       start_dir=start_dir,
                                                       next=self.load_metadata_second_set,
                                                       filters={'NeXus': ".h5"},
                                                       multiple=True,
                                                       stay_alive=False,
                                                       sort_in_reverse=True,
                                                       sort_by_alphabetical=True)
        self.nexus_ui.show()

    def load_metadata_second_set(self, list_nexus_file_name):       
        dict_data, list_mean_data, list_nexus = self._load_metadata(list_nexus_file_name)
        self.dict_data_second_set = dict_data
        self.list_mean_data_second_set = list_mean_data
        self.list_nexus_second_set = list_nexus
        self.display_first_and_second_set()

    def _load_metadata(self, list_nexus_file_name):
        list_nexus_file_name.sort()

        logging.info(f"working with {list_nexus_file_name}")
     
        list_nexus = []
        list_mean_data = {_key: [] for _key in list_pvs.keys()}
      
        dict_data = {os.path.basename(_nexus).split(".")[0]: {} for _nexus in list_nexus_file_name}

        for _nexus in list_nexus_file_name:
                      
            _base_nexus = os.path.basename(_nexus)
            _split_base_nexus = _base_nexus.split(".")
            _short_name_nexus = _split_base_nexus[0]
            list_nexus.append(os.path.basename(_short_name_nexus))
            
            for _pv_key in list_pvs.keys():
                _pv_path = list_pvs[_pv_key]['path']
                _pv_label = list_pvs[_pv_key]['label']
                try:
                    _value = VenusDisplayMetadataFromHdf5.value_of_pv_path(_nexus, _pv_path)
                    _mean_value = VenusDisplayMetadataFromHdf5.mean_value_of_pv_path(_nexus, _pv_path)
                    list_mean_data[_pv_key].append(_mean_value)
                    dict_data[_short_name_nexus][_pv_key] = _value
                    logging.info(f"{_pv_label}: {_mean_value}")
                except KeyError:
                    logging.error(f"Error loading {_pv_label} from {_short_name_nexus}")
                    _value = None
                    list_mean_data[_pv_key].append(None)        
                    dict_data[_short_name_nexus][_pv_key] = None  

        return dict_data, list_mean_data, list_nexus
