from IPython.display import HTML
from IPython.display import display
from ipywidgets import widgets
from ipywidgets.widgets import interact
import os
import h5py
import numpy as np
import matplotlib.pyplot as plt

from __code.ipywe import fileselector


class VenusDisplayNexusTpx3:
    def __init__(self, working_dir=None):
        self.working_dir = working_dir
    
    def define_settings(self):
        bin_size_label = widgets.Label(value='Bin Size (micros)')
        self.bin_size = widgets.IntSlider(value=1000, min=10, max=100000, step=10, 
                                     description='',
        )
        hori1 = widgets.HBox([bin_size_label, self.bin_size])
        max_time_label = widgets.Label(value='Max time (micros)')
        self.max_time = widgets.FloatText(value=16667)
        hori2 = widgets.HBox([max_time_label, self.max_time])

        vbox = widgets.VBox([hori1, hori2])
        display(vbox)

    def select_event_nexus(self):

        start_dir = os.path.join(self.working_dir, 'nexus')
        self.nexus_ui = fileselector.FileSelectorPanel(instruction='Select NeXus file ...',
                                                       start_dir=start_dir,
                                                       next=self.load_data,
                                                       filters={'NeXus': ".nxs.h5"},
                                                       multiple=False,
                                                       stay_alive=False,
                                                       sort_in_reverse=True,
                                                       sort_by_alphabetical=True)
        self.nexus_ui.show()

    def load_data(self, nexus_full_path):

        with h5py.File(nexus_full_path, 'r') as hdf5_data:
            event_time_offset_original = hdf5_data['entry']['bank100_events']['event_time_offset'][:]
            event_id_original = hdf5_data['entry']['bank100_events']['event_id'][:]

        offset_value = 1000000  # Offset value
        event_id_original -= offset_value

        event_id = event_id_original

        hist, bin_edges = np.histogram(event_time_offset_original, bins=self.bin_size.value, 
                                       range=(0, self.max_time.value))
        plt.figure(figsize=(10, 5))
        plt.bar(bin_edges[:-1], hist, width=np.diff(bin_edges), edgecolor='black')
        plt.xlabel('Event Time Offset (micros)')
        plt.ylabel('Counts')
        plt.title('Event Time Offset Histogram')
        plt.show()

        # Vectorized mapping function
        def map_pixels_to_coordinates(pixel_ids):
            rows = pixel_ids % 512
            cols = pixel_ids // 512
            return rows, cols

        # Initialize the full image
        full_image = np.zeros((512, 512), dtype=np.int32)

        # Vectorized processing
        rows, cols = map_pixels_to_coordinates(event_id)
        np.add.at(full_image, (cols, rows), 1)

        # Plot the result
        fig, ax = plt.subplots(figsize=(10, 10))
        im = ax.imshow(full_image, cmap='viridis', interpolation='nearest')
        plt.colorbar(im, ax=ax)
        ax.set_title(os.path.basename(nexus_full_path))
        plt.show()



        display(HTML(f"Statistics:"))
        display(HTML(f"<br>Total Events: {len(event_id)}"))
        display(HTML(f"<br>Unique Pixels Hit: {len(np.unique(event_id))}"))

