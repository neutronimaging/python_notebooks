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


class Timepix3:
    # histogram data
    histo_data = None

    # event data
    event_data = None

    # mode is 'h3' or 'mcp'
    mode = 'h3'

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
                                                       filters={'NeXus': ".h5"},
                                                       multiple=False)
        self.nexus_ui.show()

    def load_nexus(self, nexus_file_name=None):
        logging.info(f"Loading NeXus: {nexus_file_name}")
        with h5py.File(nexus_file_name, 'r') as f:
            try:
                logging.info("Loading a MCP event file!")
                self.x_array = np.array(f['events']['x'])
                self.y_array = np.array(f['events']['y'])
                self.tof_ns_array = np.array(f['events']['tof_ns'])
                self.mode = 'mcp'
            except KeyError:
                logging.info("Nexus file not supported! Only working with MCP data set")
                print("Only works with the MCP data set created by Su-Ann")

    def collect_metadata(self):
        nbr_events = len(self.x_array)
        min_x = np.min(self.x_array)
        max_x = np.max(self.x_array)
        min_y = np.min(self.y_array)
        max_y = np.max(self.y_array)
        min_tof = np.min(self.tof_ns_array)
        max_tof = np.max(self.tof_ns_array)

        self.metadata = {'nbr_events': nbr_events,
                         'x': {'min': min_x,
                               'max': max_x,
                               },
                         'y': {'min': min_y,
                               'max': max_y,
                               },
                         'tof': {'min': min_tof,
                                 'max': max_tof,
                                 },
                         }

    def format_metadata(self):
        metadata = [f"Number of events: {self.metadata['nbr_events']}"]
        metadata.append(f"x array:")
        metadata.append(f"  min: {self.metadata['x']['min']}")
        metadata.append(f"  max: {self.metadata['x']['max']}")
        metadata.append(f"y array:")
        metadata.append(f"  min: {self.metadata['y']['min']}")
        metadata.append(f"  max: {self.metadata['y']['max']}")
        metadata.append(f"tof array:")
        metadata.append(f"  min: {self.metadata['tof']['min']}")
        metadata.append(f"  max: {self.metadata['tof']['max']}")
        return "\n".join(metadata)

    def display_infos(self):

        self.collect_metadata()
        metadata = self.format_metadata()

        vbox = widgets.VBox([widgets.Label("Metadata"),
                             widgets.Textarea(value=metadata,
                                              disabled=True)])
        display(vbox)











    def rebin_and_display_data(self):

        if self.mode == 'h3':
            self.rebin_and_display_h3_data()

        elif self.mode == 'mcp':
            self.rebin_and_display_mcp_data()

        else:
            raise NotImplementedError("detector type not implemented yet!")

    def rebin_and_display_mcp_data(self):
        pass

    def rebin_and_display_h3_data(self):

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
                               dSD_m=19.855,
                               offset_micros=0,
                               element='Ni'
                               ):

            if element == 'Ni':
                _handler = BraggEdgeLibrary(material=[element],
                                            number_of_bragg_edges=5)
            else:  # Ta
                _handler = BraggEdgeLibrary(new_material=[{'name': 'Ta',
                                                           'lattice': 3.3058,
                                                           'crystal_structure': 'BCC'}],
                                            number_of_bragg_edges=5)

            self.bragg_edges = _handler.bragg_edges
            self.hkl = _handler.hkl
            self.handler = _handler

            histo_data, bins_array = np.histogram(self.event_data, nbrs_bins)
            bin_value = bins_array[1] - bins_array[0]

            if x_axis == 'TOF':
                tof_array = bins_array[:-1]  # micros
                x_axis_array = tof_array
                xlabel = "TOF offset (" + MICRO + "s)"
            else:
                _exp = Experiment(tof=bins_array[:-1] * 1e-6,  # to convert to seconds
                                  distance_source_detector_m=dSD_m,
                                  detector_offset_micros=offset_micros)
                lambda_array = _exp.lambda_array[:] * 1e10  # to be in Angstroms
                x_axis_array = lambda_array
                xlabel = LAMBDA + "(" + ANGSTROMS + ")"

            ax.cla()
            ax.plot(x_axis_array, histo_data, '.')
            ax.set_ylabel("Counts")
            ax.set_xlabel(xlabel)
            bin_size.value = f"{bin_value: .2f}"

            max_counts = np.max(histo_data)

            if x_axis == 'lambda':

                logging.info(f"for Ni: {self.hkl[element] =}")
                for _index, _x in enumerate(self.bragg_edges[element]):
                    _hkl_array = self.hkl[element][_index]
                    _str_hkl_array = [str(value) for value in _hkl_array]
                    _hkl = ",".join(_str_hkl_array)

                    # to display _x in the right axis
                    ax.axvline(x=_x, color='r', linestyle='--')

                    ax.text(_x, (max_counts - max_counts / 7),
                            _hkl,
                            ha="center",
                            rotation=45,
                            size=15,
                            )

        v = interactive(plot_rebinned_data,
                        x_axis=widgets.RadioButtons(options=['TOF', 'lambda'],
                                                    value='lambda',
                                                    ),
                        nbrs_bins=widgets.IntSlider(value=10000,
                                                    min=1,
                                                    max=100000,
                                                    continuous_update=False),
                        dSD_m=widgets.FloatSlider(value=19.855,
                                                  min=15,
                                                  max=25,
                                                  step=0.001,
                                                  continuous_update=False,
                                                  readout_format=".3f"),
                        offset_micros=widgets.IntSlider(value=0,
                                                        min=0,
                                                        max=15000,
                                                        continuous_update=False),
                        element=widgets.RadioButtons(options=['Ni', 'Ta'],
                                                     value='Ni'),
                        )
        display(v)
