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
from __code._utilities import LAMBDA, MICRO, ANGSTROMS
from __code.ipywe import fileselector
from __code.file_folder_browser import FileFolderBrowser

LOG_FILE_NAME = ".venus_monitor_hdf5.log"

ENERGY_CONVERSION_FACTOR = 81.787


class VenusChopTCeroMonitorCounts:

    list_nexus_with_missing_key = []

    def __init__(self, working_dir=None):
        self.working_dir = working_dir

        self.log_file_name = get_full_home_file_name(LOG_FILE_NAME)
        logging.basicConfig(filename=self.log_file_name,
                            filemode='w',
                            format='[%(levelname)s] - %(asctime)s - %(message)s',
                            level=logging.INFO)
        logging.info("*** Starting a new session ***")

    def select_list_nexus(self):

        start_dir = os.path.join(self.working_dir, 'nexus')

        self.nexus_ui = fileselector.FileSelectorPanel(instruction='Select NeXus files ...',
                                                       start_dir=start_dir,
                                                       next=self.load_data,
                                                       filters={'NeXus': ".h5"},
                                                       multiple=True,
                                                       sort_by_time=True,
                                                       sort_in_reverse=True)
        self.nexus_ui.show()



    def load_data(self, list_nexus_file_name):

        list_nexus_file_name.sort(reverse=True)
        self.list_nexus_file_name = list_nexus_file_name

        phase_delay_array = []
        monitor_counts_array = []

        for _nexus in list_nexus_file_name:

            with h5py.File(_nexus, 'r') as nxs:
                try:
                    _average_phase_delay = nxs['entry']['DASlogs']['BL10:CHOP:TCERO:PhaseDelaySP']['average_value'][()][0]
                    _monitor_counts = nxs['entry']['monitor1']['total_counts'][()][0]
                except KeyError:
                    self.list_nexus_with_missing_key.append(_nexus)
                    _average_phase_delay = np.nan
                    _monitor_counts = np.NaN

                phase_delay_array.append(_average_phase_delay)
                monitor_counts_array.append(_monitor_counts)

        self.phase_delay_array = phase_delay_array
        self.monitor_counts_array = monitor_counts_array

        self.display()
   
    def display(self):

        minimum_counts = np.nanmin(self.monitor_counts_array)
        index_of_minimum = int(np.where(self.monitor_counts_array == minimum_counts)[0][0])

        value_of_phase_delay_at_that_minimum = self.phase_delay_array[index_of_minimum]

        plt.rcParams['figure.constrained_layout.use'] = True
        fig, ax1 = plt.subplots(nrows=1, ncols=1, num=f"",
                               figsize=(8, 8),
                               )
        ax2 = ax1.twinx()

        ax1.plot(self.phase_delay_array, 'r+')
        ax2.plot(self.monitor_counts_array, 'b.')
        ax1.axvline(index_of_minimum, linestyle='--')
        ax1.axhline(value_of_phase_delay_at_that_minimum)

        ax1.set_xlabel("Nexus index")
        ax1.set_ylabel("Phase Delay", color='r')
        ax2.set_ylabel("Monitor Counts", color='b')

        display(HTML("<b>Report:</b>"))
        print(f"Phase delay at minimum: {value_of_phase_delay_at_that_minimum}")
        print(f"Index of NeXus at minimum: {index_of_minimum}")

        nexus_file_of_minimum = self.list_nexus_file_name[index_of_minimum]
        print(f"NeXus at minimum: {nexus_file_of_minimum}")

        start_time = 0
        with h5py.File(nexus_file_of_minimum, 'r') as nxs:
            start_time = nxs['entry']['start_time'][()]

        print(f"Start acquisition time: {start_time[0].decode('utf-8')}")
        print(f"")
        _list_nexus_with_missing_key = [os.path.basename(_file) for _file in self.list_nexus_with_missing_key]
        print(f"List of nexus that had missing key: {_list_nexus_with_missing_key}")
