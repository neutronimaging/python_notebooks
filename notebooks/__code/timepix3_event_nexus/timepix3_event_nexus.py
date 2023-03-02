import logging
import h5py
import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interactive
import ipywidgets as widgets
from IPython.core.display import display, HTML

from __code._utilities.file import get_full_home_file_name
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

        fig, ax = plt.subplots(figsize=(7, 7),
                               nrows=1,
                               ncols=1,
                               num="Histogram of He3 detector")

        def plot_rebinned_data(nbrs_bins=2):
            histo_data, bins_array = np.histogram(self.event_data, nbrs_bins)
            bin_value = bins_array[1] - bins_array[0]
            ax.cla()
            ax.plot(bins_array[:-1], histo_data, '.')
            ax.set_xlabel(u"TOF offset (\u03bcs)")
            ax.set_ylabel("Counts")

            bin_size.value = f"{bin_value: .2f}"

        v = interactive(plot_rebinned_data,
                        nbrs_bins=widgets.IntSlider(value=10,
                                                    min=1,
                                                    max=100000),
                        )
        display(v)

