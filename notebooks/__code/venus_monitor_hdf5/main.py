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
from __code._utilities.file import make_ascii_file
from __code._utilities import LAMBDA, MICRO, ANGSTROMS
from __code.ipywe import fileselector
from __code.file_folder_browser import FileFolderBrowser
from __code.ipywe.myfileselector import FileSelectorPanelWithJumpFolders

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

        self.record_settings()

        start_dir = os.path.join(self.working_dir, 'nexus')

        self.nexus_ui = fileselector.FileSelectorPanel(instruction='Select NeXus file ...',
                                                       start_dir=start_dir,
                                                       next=self.load_data,
                                                       filters={'NeXus': ".h5"},
                                                       multiple=True,
                                                       sort_in_reverse=True,
                                                       sort_by_alphabetical=True)
        self.nexus_ui.show()

    def load_data(self, list_nexus_file_name):

        list_data = {}

        for _nexus in list_nexus_file_name:

            try:

                with h5py.File(_nexus, 'r') as nxs:
                    _index = np.array(nxs['entry']['monitor1']['event_index'])
                    _time_offset = np.array(nxs['entry']['monitor1']['event_time_offset'])
                    _time_zero = np.array(nxs['entry']['monitor1']['event_time_zero'])
                    _total_counts = nxs['entry']['monitor1']['total_counts'][()]

                list_data[_nexus] = {'event_index': _index,
                                     'event_time_offset': _time_offset,
                                     'event_time_zero': _time_zero,
                                     'total_counts': _total_counts}

            except KeyError:
                display(HTML("<font color='red'>Error loading the monitor data!<br>Entry is missing!</font>"))
                list_data[_nexus] = None

        self.list_data = list_data
        self.display_all_at_once()

    def define_settings(self):

        # bins
        bins_label = widgets.Label(u"Bins size (\u00B5s)")
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
                                                   layout=widgets.Layout(width="100px"),
                                                   disabled=True,
                                                   )
        monitor_units = widgets.Label(u"\u00B5s")
        monitor_layout = widgets.HBox([monitor_label,
                                       self.monitor_offset_ui,
                                       monitor_units],
                                       )

        # full layout
        full_layout = widgets.VBox([bins_layout,
                                    distance_layout,
                                    monitor_layout])

        display(full_layout)

    def record_settings(self):
        self.bins_size = self.bins_ui.value
        self.distance_source_detector_m = self.distance_source_detector_ui.value
        self.detector_offset_micros = self.monitor_offset_ui.value

    def calculate_data_tof(self, time_offset=None, max_bin=2*16666):
        bins_size = self.bins_size
        histo_tof, bins_tof = np.histogram(time_offset, bins=np.arange(0, max_bin, bins_size))
        detector_offset_micros = self.detector_offset_micros
        _bins_tof = np.empty_like(bins_tof)
        for _index, _bin in enumerate(bins_tof):
            _bins_tof[_index] = _bin - detector_offset_micros
        return _bins_tof, histo_tof

    def calculate_data_lambda(self, bins_tof=None):
        tof_axis = bins_tof[:-1]
        # detector_offset_micros = self.detector_offset_micros
        distance_source_detector_cm = self.distance_source_detector_m * 100.

        lambda_axis_angstroms = VenusMonitorHdf5.from_micros_to_lambda(tof_axis_micros=tof_axis,
                                                                        distance_source_detector_cm=distance_source_detector_cm)
        return lambda_axis_angstroms

    def calculate_data_energy(self):
        lambda_axis_angstroms = self.lambda_axis_angstroms
        self.energy_axis_ev = 1000 * (ENERGY_CONVERSION_FACTOR / (lambda_axis_angstroms*lambda_axis_angstroms))

    @staticmethod
    def from_micros_to_lambda(tof_axis_micros, distance_source_detector_cm=2372.6):
        return 0.3954 * (tof_axis_micros) / distance_source_detector_cm

    def display_all_at_once(self):

        list_data = self.list_data
        
        plt.rcParams['figure.constrained_layout.use'] = True
        # fig, ax = plt.subplots(nrows=1, ncols=2, num=f"Nexus Monitors",
        #                        figsize=(10, 5),
        #                        )

        # ax[0].set_xlabel(u"TOF (\u00B5s)")
        # ax[0].set_ylabel("Counts")
        # ax[0].set_title(u"Counts vs TOF(\u00B5s)")

        # ax[1].set_xlabel(u"Lambda (\u212B)")
        # ax[1].set_ylabel("Total counts")
        # ax[1].set_title(u"Counts vs lambda (\u212B)")

        def plot_data(max_bin):
            fig, ax = plt.subplots(nrows=2, ncols=1, num=f"Nexus Monitors",
                               figsize=(10, 10),
                               )

            ax[0].set_xlabel(u"TOF (\u00B5s)")
            ax[0].set_ylabel("Counts")
            ax[0].set_title(u"Counts vs TOF(\u00B5s)")

            ax[1].set_xlabel(u"Lambda (\u212B)")
            ax[1].set_ylabel("Total counts")
            ax[1].set_title(u"Counts vs lambda (\u212B)")


            for _key in list_data.keys():

                if list_data[_key] is None:
                    continue

                time_offset = list_data[_key]['event_time_offset']
                bins_tof, histo_tof = self.calculate_data_tof(time_offset=time_offset,
                                                              max_bin=max_bin)
                self.list_data[_key]['bins_tof'] = bins_tof
                self.list_data[_key]['histo_tof'] = histo_tof
                lambda_axis_angstroms = self.calculate_data_lambda(bins_tof=bins_tof)
                self.list_data[_key]['lambda_axis_angstroms'] = lambda_axis_angstroms

                # self.calculate_data_energy()

                nexus = os.path.basename(_key)
                #ax[0].plot(bins_tof[:-1], histo_tof, label=nexus)
                ax[0].semilogy(bins_tof[:-1], histo_tof, label=nexus)
                ax[1].plot(lambda_axis_angstroms, histo_tof, 'r', label=nexus)

            ax[0].legend()
            ax[1].legend()
            plt.show()

            # ax[2].plot(self.energy_axis_ev, self.histo_tof, '*g')
            # ax[2].set_xlabel("Energy (eV)")
            # ax[2].set_ylabel("Total counts")
            # ax[2].set_title("Counts vs Energy (eV)")

            display(HTML("<h2>Total counts:</h2>"))
            for _key in list_data.keys():
                print(f"{os.path.basename(_key)}: {self.list_data[_key]['total_counts'][0]}")

        display_all = interactive(plot_data,
                                  max_bin=widgets.IntSlider(min=16666,
                                                            max=5*16666,
                                                            value=3*16666))
        display(display_all)

# def display_all_at_once(self):

#         list_data = self.list_data
        
#         plt.rcParams['figure.constrained_layout.use'] = True
#         fig, ax = plt.subplots(nrows=1, ncols=2, num=f"Nexus Monitors",
#                                figsize=(10, 5),
#                                )

#         ax[0].set_xlabel(u"TOF (\u00B5s)")
#         ax[0].set_ylabel("Counts")
#         ax[0].set_title(u"Counts vs TOF(\u00B5s)")

#         ax[1].set_xlabel(u"Lambda (\u212B)")
#         ax[1].set_ylabel("Total counts")
#         ax[1].set_title(u"Counts vs lambda (\u212B)")

#         for _key in list_data.keys():

#             if list_data[_key] is None:
#                 continue

#             time_offset = list_data[_key]['event_time_offset']
#             bins_tof, histo_tof = self.calculate_data_tof(time_offset=time_offset)
#             self.list_data[_key]['bins_tof'] = bins_tof
#             self.list_data[_key]['histo_tof'] = histo_tof
#             lambda_axis_angstroms = self.calculate_data_lambda(bins_tof=bins_tof)
#             self.list_data[_key]['lambda_axis_angstroms'] = lambda_axis_angstroms

#             # self.calculate_data_energy()

#             nexus = os.path.basename(_key)
#             ax[0].plot(bins_tof[:-1], histo_tof, label=nexus)
#             ax[1].plot(lambda_axis_angstroms, histo_tof, 'r', label=nexus)

#         ax[0].legend()
#         ax[1].legend()

#         # ax[2].plot(self.energy_axis_ev, self.histo_tof, '*g')
#         # ax[2].set_xlabel("Energy (eV)")
#         # ax[2].set_ylabel("Total counts")
#         # ax[2].set_title("Counts vs Energy (eV)")

#         display(HTML("<h2>Total counts:</h2>"))
#         for _key in list_data.keys():
#             print(f"{os.path.basename(_key)}: {self.list_data[_key]['total_counts'][0]}")

    def export_data(self):

        start_dir = os.path.join(self.working_dir, 'shared')
        my_folder_selector = FileSelectorPanelWithJumpFolders(start_dir=start_dir,
                                                              type='directory',
                                                              next=self.export,
                                                              ipts_folder=self.working_dir,
                                                              newdir_toolbar_button=True,
                                                              )
        
    def export(self, output_folder=None):

        for _nexus in self.list_data.keys():

            base_nexus_file_name = os.path.basename(_nexus)
            split_nexus_file_name = base_nexus_file_name.split(".")
            output_file_name = f"{split_nexus_file_name[0]}_monitor_data.txt"
            full_output_file_name = os.path.join(output_folder, output_file_name)

            tof_axis = self.list_data[_nexus]['bins_tof']
            lambda_axis = self.list_data[_nexus]['lambda_axis_angstroms']
            y_axis = self.list_data[_nexus]['histo_tof']

            metadata_array = [f"# tof (\u00B5s), \u03BB (\u212B), Counts",
                            f"# nexus: {base_nexus_file_name}",
                            f"# IPTS: {self.working_dir}"]
            output_array = []
            for _t, _l, _y in zip(tof_axis, lambda_axis, y_axis):
                output_array.append([_t, _l, _y])

            make_ascii_file(data=output_array,
                            metadata=metadata_array,
                            dim='2d',
                            sep=',',
                            output_file_name=full_output_file_name,
            )

            display(HTML(f"Data have been exported in {full_output_file_name}"))
