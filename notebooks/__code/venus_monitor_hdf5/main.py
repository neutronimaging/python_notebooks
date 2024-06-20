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


class VenusMonitorHdf5:

    def __init__(self, working_dir=None):
        self.working_dir = working_dir

        self.log_file_name = get_full_home_file_name(LOG_FILE_NAME)
        logging.basicConfig(filename=self.log_file_name,
                            filemode='w',
                            format='[%(levelname)s] - %(asctime)s - %(message)s',
                            level=logging.INFO)
        logging.info("*** Starting a new session ***")

    def select_event_nexus(self):
        self.nexus_ui = fileselector.FileSelectorPanel(instruction='Select NeXus file ...',
                                                       start_dir=self.working_dir,
                                                       next=self.load_data,
                                                       filters={'NeXus': ".h5"},
                                                       multiple=False)
        self.nexus_ui.show()

    def load_data(self, nexus_file_name):

        print(f"{nexus_file_name}")

        with h5py.File(nexus_file_name, 'r') as nxs:
            self.index = np.array(nxs['entry']['monitor1']['event_index'])
            self.time_offset = np.array(nxs['entry']['monitor1']['event_time_offset'])
            self.time_zero = np.array(nxs['entry']['monitor1']['event_time_zero'])

    def display_data_tof(self, nbr_bins=10):

        self.histo_tof, self.bins_tof = np.histogram(self.time_offset, bins=np.arange(0, 16666, nbr_bins))

        fig, ax = plt.subplots(num='histogram2')
        plt.plot(self.bins_tof[:-1], self.histo_tof)
        ax.set_xlabel("TOF (micros)")
        ax.set_ylabel("Counts")

    def display_data_lambda(self, distance_source_detector_m=23.726, detector_offset_micros=0):

        distance_source_detector_cm = distance_source_detector_m / 100
        tof_axis = self.bins_tof[:-1]

        lambda_axis = VenusMonitorHdf5.from_micros_to_lambda(tof_axis_micros=tof_axis,
                                                             detector_offset_micros=detector_offset_micros)

        fig, ax = plt.subplots(num='histogram3')
        plt.plot(lambda_axis, self.histo_tof)
        ax.set_xlabel("Lambgda (Angstroms)")
        ax.set_ylabel("Total counts")

    @staticmethod
    def from_micros_to_lambda(tof_axis_micros, detector_offset_micros=0, distance_source_detector_cm=2372.6):
        return 0.3954 * (tof_axis_micros + detector_offset_micros) / distance_source_detector_cm
