import logging
import h5py
import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interactive
import ipywidgets as widgets
from IPython.core.display import display, HTML

from neutronbraggedge.experiment_handler import *
from neutronbraggedge.braggedge import BraggEdge as BraggEdgeLibrary

from __code._utilities.file import get_full_home_file_name
from __code._utilities import LAMBDA, MICRO, ANGSTROMS
from __code.ipywe import fileselector

LOG_FILE_NAME = ".timepix3_event_nexus.log"


class Timepix3EventNexus:

    # histogram data
    histo_data = None

    # event data
    event_data = None

    def __init__(self, working_dir=None):
        self.working_dir = working_dir

        self.log_file_name = get_full_home_file_name(LOG_FILE_NAME)
        logging.basicConfig(filename=self.log_file_name,
                            filemode='w',
                            format='[%(levelname)s] - %(asctime)s - %(message)s',
                            level=logging.INFO)
        logging.info("*** Starting a new session ***")


    def select_nexus(self):
        self.nexus_ui = fileselector.FileSelectorPanel(instruction='Select NeXus file ...',
                                                       start_dir=self.working_dir,
                                                       next=self.load_nexus,
                                                       filters={'NeXus': ".nxs.h5"},
                                                       multiple=False)
        self.nexus_ui.show()

    def load_nexus(self, nexus_file_name=None):
        logging.info(f"Loading NeXus: {nexus_file_name}")
        with h5py.File(nexus_file_name, 'r') as f:
            self.event_data = np.array(f['entry']['monitor2']['event_time_offset'])

    def rebin_and_display_data(self):

        hbox = widgets.HBox([widgets.Label("Bin size:",
                                           layout=widgets.Layout(width="100px")),
                             widgets.Label("NaN",
                                           layout=widgets.Layout(width="200px"))])
        display(hbox)

        bin_size = hbox.children[1]

        fig, ax = plt.subplots(figsize=(5, 5),
                               nrows=1,
                               ncols=1,
                               num="Histogram of He3 detector")

        def plot_rebinned_data(x_axis='TOF',
                               nbrs_bins=2,
                               dSD=19.855,
                               det_offset=0,
                               element='Ni'):

            _handler = BraggEdgeLibrary(material=[element],
                                        number_of_bragg_edges=5)
            self.bragg_edges = _handler.bragg_edges
            self.hkl = _handler.hkl
            self.handler = _handler

            histo_data, bins_array = np.histogram(self.event_data, nbrs_bins)
            bin_value = bins_array[1] - bins_array[0]

            if x_axis == 'TOF':
                tof_array = bins_array[:-1]  # micros
                x_axis_array = tof_array
                ax.set_xlabel("TOF offset (" + MICRO + "s)")
            else:
                _exp = Experiment(tof=bins_array[:-1],
                                  distance_source_detector_m=dSD,
                                  detector_offset_micros=det_offset)
                lambda_array = _exp.lambda_array[:] * 1e10  # to be in Angstroms
                x_axis_array = lambda_array
                ax.set_xlabel(LAMBDA + "(" + ANGSTROMS + ")")

            ax.cla()
            ax.plot(x_axis_array, histo_data, '.')
            ax.set_ylabel("Counts")
            bin_size.value = f"{bin_value: .2f}"

            if x_axis == 'lambda':

                logging.info(f"for {element}: {self.hkl[element] =}")
                for _index, _x in enumerate(self.bragg_edges[element]):
                    _hkl_array = self.hkl[element][_index]
                    _str_hkl_array = [str(value) for value in _hkl_array]
                    _hkl = ",".join(_str_hkl_array)
                    print(f"{_x =}")
                    ax.axvline(x=_x, color='b', label=f"{_hkl}")

        v = interactive(plot_rebinned_data,
                        x_axis=widgets.RadioButtons(options=['TOF', 'lambda'],
                                                    ),
                        nbrs_bins=widgets.IntSlider(value=10,
                                                    min=1,
                                                    max=100000,
                                                    continuous_update=False),
                        dSD=widgets.FloatSlider(value=19.855,
                                                min=15,
                                                max=25,
                                                continuous_update=False),
                        det_offset=widgets.IntSlider(value=0,
                                                     min=0,
                                                     max=15000,
                                                     continuous_update=False),
                        element=widgets.Dropdown(options=['Ta', 'He', 'Ni'],
                                                 value='Ni')
                        )
        display(v)
