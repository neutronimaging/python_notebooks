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

        start_dir = os.path.join(self.working_dir, 'nexus')

        self.nexus_ui = fileselector.FileSelectorPanel(instruction='Select NeXus file ...',
                                                       start_dir=start_dir,
                                                       next=self.load_data,
                                                       filters={'NeXus': ".h5"},
                                                       multiple=False)
        self.nexus_ui.show()

    def load_data(self, nexus_file_name):

        with h5py.File(nexus_file_name, 'r') as nxs:
            self.index = np.array(nxs['entry']['monitor1']['event_index'])
            self.time_offset = np.array(nxs['entry']['monitor1']['event_time_offset'])
            self.time_zero = np.array(nxs['entry']['monitor1']['event_time_zero'])

    def define_settings(self):

        # bins
        bins_label = widgets.Label("Nbr bins")
        self.bins_ui = widgets.IntSlider(min=1,
                                    max=10000,
                                    value=100)
        bins_layout = widgets.HBox([bins_label,
                                    self.bins_ui])

        # distance
        distance_lock = widgets.Checkbox(False,
                                         layout=widgets.Layout(width="150px"))
        distance_label = widgets.Label("Distance source_monitor",
                                       layout=widgets.Layout(width="200px"),
                                       disabled=True)
        self.distance_source_detector_ui = widgets.FloatText(value=23.726,
                                                        layout=widgets.Layout(width="100px"),
                                                        disabled=True)
        distance_units_label = widgets.Label("m")

        distance_layout = widgets.HBox([distance_lock,
                                        distance_label,
                                        self.distance_source_detector_ui,
                                        distance_units_label])

        def lock_changed(changes):
            new_value = changes['new']
            self.distance_source_detector_ui.disabled = not new_value

        distance_lock.observe(lock_changed, names='value')


        # monitor offset
        monitor_label = widgets.Label("Monitor offset",
                                      layout=widgets.Layout(width='100px'))
        self.monitor_offset_ui = widgets.FloatText(value=0,
                                              layout=widgets.Layout(width="100px"))
        monitor_units = widgets.Label(u"\u00B5s")
        monitor_layout = widgets.HBox([monitor_label,
                                       self.monitor_offset_ui,
                                       monitor_units])

        # full layout
        full_layout = widgets.VBox([bins_layout,
                                    distance_layout,
                                    monitor_layout])

        display(full_layout)

    def record_settings(self):
        self.nbr_bins = self.bins_ui.value
        self.distance_source_detector_m = self.distance_source_detector_ui.value
        self.detector_offset_micros = self.monitor_offset_ui.value

    def calculate_data_tof(self):

        nbr_bins = self.nbr_bins
        self.histo_tof, self.bins_tof = np.histogram(self.time_offset, bins=np.arange(0, 16666, nbr_bins))


    def calculate_data_lambda(self):

        tof_axis = self.bins_tof[:-1]
        detector_offset_micros = self.detector_offset_micros
        distance_source_detector_cm = self.distance_source_detector_m * 100.

        self.lambda_axis_angstroms = VenusMonitorHdf5.from_micros_to_lambda(tof_axis_micros=tof_axis,
                                                                            distance_source_detector_cm=distance_source_detector_cm,
                                                            detector_offset_micros=detector_offset_micros)

    def calculate_data_energy(self):
        lambda_axis_angstroms = self.lambda_axis_angstroms
        self.energy_axis_ev = 1000 * (ENERGY_CONVERSION_FACTOR / (lambda_axis_angstroms*lambda_axis_angstroms))

    @staticmethod
    def from_micros_to_lambda(tof_axis_micros, detector_offset_micros=0, distance_source_detector_cm=2372.6):
        return 0.3954 * (tof_axis_micros + detector_offset_micros) / distance_source_detector_cm

    def display_all_at_once(self):

        self.calculate_data_tof()
        self.calculate_data_lambda()
        self.calculate_data_energy()

        plt.rcParams['figure.constrained_layout.use'] = True
        fig, ax = plt.subplots(nrows=3, ncols=1, num='Monitor',
                               figsize=(10, 15),
                               )

        ax[0].plot(self.bins_tof[:-1], self.histo_tof)
        ax[0].set_xlabel(u"TOF (\u00B5s)")
        ax[0].set_ylabel("Counts")
        ax[0].set_title(u"Counts vs TOF(\u00B5s)")

        ax[1].plot(self.lambda_axis_angstroms, self.histo_tof, 'r')
        ax[1].set_xlabel(u"Lambda (\u212B)")
        ax[1].set_ylabel("Total counts")
        ax[1].set_title(u"Counts vs lambda (\u212B)")

        ax[2].plot(self.energy_axis_ev, self.histo_tof, '*g')
        ax[2].set_xlabel("Energy (eV)")
        ax[2].set_ylabel("Total counts")
        ax[2].set_title("Counts vs Energy (eV)")
