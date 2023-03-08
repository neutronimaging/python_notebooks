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

LOG_FILE_NAME = ".timepix3_event_nexus.log"


class Timepix3FromEventToHistoNexus:
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

    def select_event_nexus(self):
        self.nexus_ui = fileselector.FileSelectorPanel(instruction='Select NeXus file ...',
                                                       start_dir=self.working_dir,
                                                       next=self.display_tree_structure,
                                                       filters={'NeXus': ".h5"},
                                                       multiple=False)
        self.nexus_ui.show()

    def display_tree_structure(self, nexus_file_name=None):
        logging.info(f"Display tree structure of {nexus_file_name}")
        losa.get_hdf_tree(nexus_file_name)

    def collect_metadata(self):
        nbr_events = len(self.x_array)
        min_x = np.min(self.x_array)
        max_x = np.max(self.x_array)
        min_y = np.min(self.y_array)
        max_y = np.max(self.y_array)
        min_tof = np.min(self.tof_array)
        max_tof = np.max(self.tof_array)

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
                                              disabled=True,
                                              layout=widgets.Layout(height='200px'))])
        display(vbox)

    def define_detector(self):
        self.width_ui = widgets.IntText(value=1024,
                                        description="Width")
        self.height_ui = widgets.IntText(value=1024,
                                         description="Height")
        vbox = widgets.VBox([widgets.Label("MCP detector size:"),
                             self.height_ui,
                             self.width_ui])
        display(vbox)

    def select_binning_parameter(self):

        self.nbr_bin_ui = widgets.IntText(value=1000,
                                  description="Nbr of bins:")
        display(self.nbr_bin_ui)

        self.range_to_use = widgets.IntSlider(value=50,
                                              max=100,
                                              min=1,
                                              description="% to use")
        display(self.range_to_use)

    def bins(self):
        logging.info("Binning the data:")
        bin_value = self.nbr_bin_ui.value
        percentage_to_use = self.range_to_use.value

        nbr_point = len(self.tof_array)
        max_index_to_use = int(nbr_point * (percentage_to_use / 100))

        mcp_height = self.height_ui.value
        mcp_width = self.width_ui.value

        logging.info(f"\tbin_value: {bin_value}")
        logging.info(f"\tpercentage to use: {percentage_to_use}")
        logging.info(f"\tnbr point: {nbr_point}")
        logging.info(f"\tmax_index_to_use: {max_index_to_use}")
        logging.info(f"\tMCP height: {mcp_height}")
        logging.info(f"\tMCP width: {mcp_width}")

        logging.info(f"Narrowing down the arrays to the range specified!")
        tof_array = self.tof_array[0:max_index_to_use]
        x_array = self.x_array[0:max_index_to_use]
        y_array = self.y_array[0:max_index_to_use]

        # indexes with NaN
        logging.info(f"Removing NaNs!")
        index_nan = np.where(np.isnan(tof_array))
        # remove those x, y and tof_nx
        self.tof_array_cleaned = np.delete(tof_array, index_nan)
        self.x_array_cleaned = np.delete(x_array, index_nan)
        self.y_array_cleaned = np.delete(y_array, index_nan)

        # binning
        logging.info(f"Binning of tof array ... started")
        histo_tof, bins_tof = np.histogram(self.tof_array_cleaned, bin_value)
        logging.info(f"Binning of tof array ...  Done!")

        stack_images = np.zeros((bin_value, mcp_height, mcp_width))
        np.shape(stack_images)

        for _index, _tof in enumerate(tof_array):
            _array_location = np.where((bins_tof - _tof) < 0)
            try:
                _location = _array_location[0][-1]
            except IndexError:
                _location = 0
            x = round(x_array[_index])
            y = round(y_array[_index])
            if (x < 0) or (y < 0) or (x > 1023) or (y > 1023):
                continue

            stack_images[_location, y, x] += 1

        self.stack_images = stack_images

    def display_integrated_stack(self):

        self.integrated_stack = self.stack_images.sum(axis=0)
        fig, ax = plt.subplots(figsize=(7, 7),
                               nrows=1, ncols=1)
        image = ax.imshow(self.integrated_stack)
        self.cb = plt.colorbar(image, ax=ax)
        plt.show()

        max_counts = np.max(self.integrated_stack)

        def plot_integrated(vmin, vmax):
            self.cb.remove()
            plt.title("Integrated slices (sum)")
            image = ax.imshow(self.integrated_stack, vmin=vmin, vmax=vmax)
            self.cb = plt.colorbar(image, ax=ax)
            plt.show()

        v = interactive(plot_integrated,
                        vmin=widgets.IntSlider(min=0,
                                                 max=max_counts,
                                                 value=0),
                        vmax=widgets.IntSlider(min=0,
                                               max=max_counts,
                                               value=max_counts),
                        )

        display(v)

    def display_slices(self):

        fig1, ax1 = plt.subplots(figsize=(7, 7),
                                 nrows=1, ncols=1)
        first_image = self.stack_images[0]
        image_id = ax1.imshow(first_image)
        self.cb1 =  plt.colorbar(image_id, ax=ax1)
        plt.show()

        def plot_slices(index):

            self.cb1.remove()
            plt.title(f"Slice #{index}")
            image_id = ax1.imshow(self.stack_images[index])
            self.cb1 = plt.colorbar(image_id, ax=ax1)

            plt.show()

        v = interactive(plot_slices,
                        index=widgets.IntSlider(min=0,
                                                max=len(self.integrated_stack)-1,
                                                value=0),
                        )
        display(v)






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
