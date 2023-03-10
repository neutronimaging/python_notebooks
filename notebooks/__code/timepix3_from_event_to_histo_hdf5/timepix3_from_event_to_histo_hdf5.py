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

LOG_FILE_NAME = ".timepix3_from_event_to_histo_hdf5.log"


class Timepix3FromEventToHistoHdf5:
    # histogram data
    histo_data = None

    # event data
    event_data = None

    # mode is 'h3' or 'mcp'
    mode = 'h3'

    # array of tof bins
    bins_tof = None

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
        self.input_nexus_file_name = nexus_file_name
        self.working_dir = os.path.dirname(nexus_file_name)

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
        self.bins_tof = bins_tof
        self.nbr_bins = bin_value

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
        self.cb1 = plt.colorbar(image_id, ax=ax1)
        plt.show()

        def plot_slices(index):

            self.cb1.remove()
            plt.title(f"Slice #{index}")
            image_id = ax1.imshow(self.stack_images[index])
            self.cb1 = plt.colorbar(image_id, ax=ax1)

            plt.show()

        print(np.shape(self.stack_images))

        v = interactive(plot_slices,
                        index=widgets.IntSlider(min=0,
                                                max=len(self.stack_images)-1,
                                                value=0),
                        )
        display(v)

    def define_output_filename(self):
        input_nexus_filename = os.path.basename(self.input_nexus_file_name)
        export_id = widgets.HBox([widgets.Label("Output file name:",
                                                layout=widgets.Layout(width="150px")),
                                  widgets.Text(value=input_nexus_filename,
                                               layout=widgets.Layout(width="300px")),
                                  ])
        display(export_id)
        self.output_file_name_id = export_id.children[1]

    def select_output_location(self):
        o_output_folder = FileFolderBrowser(working_dir=self.working_dir,
                                            next_function=self.export_h5)
        o_output_folder.select_output_folder(instruction="Select output folder ...")

    def export_h5(self, output_folder):
        logging.info(f"Export h5 to {output_folder}")
        output_filename = self.output_file_name_id.value
        logging.info(f"\t output file name: {output_filename}")

        full_output_filename = os.path.join(output_folder, output_filename)

        display(HTML(f"Writing HDF5 file .... in progress"))

        with h5py.File(full_output_filename, mode='w') as f:
            f.create_group('entry/histo')
            f.create_dataset('entry/histo/stack', data=self.stack_images)
            f.create_dataset('entry/histo/number_of_bins', data=self.nbr_bins)
            f.create_dataset('entry/histo/tof_ns', data=self.bins_tof)
            f.create_group('entry/infos')
            f.create_dataset('entry/infos/input_nexus_filename', data=self.input_nexus_file_name)

        display(HTML(f"Writing HDF5 file .... Done!"))
        display(HTML(f"hdf5 file created: {full_output_filename}"))
        logging.info(f"hdf5 file created: {full_output_filename}")
