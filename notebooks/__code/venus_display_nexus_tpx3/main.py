import os

import h5py
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import HTML, display
from ipywidgets import widgets

from __code.ipywe import fileselector


class VenusDisplayNexusTpx3:
    def __init__(self, working_dir=None):
        self.working_dir = working_dir
        self.output = widgets.Output()

    def define_settings(self):
        bin_size_label = widgets.Label(value="Bin Size (micros)")
        self.bin_size = widgets.IntSlider(
            value=1000,
            min=10,
            max=100000,
            step=10,
            description="",
        )
        hori1 = widgets.HBox([bin_size_label, self.bin_size])
        max_time_label = widgets.Label(value="Max time (micros)")
        self.max_time = widgets.FloatText(value=16667)
        hori2 = widgets.HBox([max_time_label, self.max_time])

        vbox = widgets.VBox([hori1, hori2])
        display(vbox)

    def select_event_nexus(self):
        start_dir = os.path.join(self.working_dir, "nexus")
        self.nexus_ui = fileselector.FileSelectorPanel(
            instruction="Select NeXus file ...",
            start_dir=start_dir,
            next=self.load_data,
            filters={"NeXus": ".nxs.h5"},
            multiple=False,
            stay_alive=False,
            sort_in_reverse=True,
            sort_by_alphabetical=True,
        )
        self.nexus_ui.show()

        # Display the output widget where plots will appear
        display(self.output)

    def load_data(self, nexus_full_path):
        list_banks = [100, 200, 300]
        self.output.clear_output()

        for _bank in list_banks:
            self._load_data_single_bank(nexus_full_path, bank=_bank)
            display(HTML("<hr>"))

    def _load_data_single_bank(self, nexus_full_path, bank=100):

        # Use the output widget context to capture all output
        with self.output:
            with h5py.File(nexus_full_path, "r") as hdf5_data:
                event_time_offset_original = hdf5_data["entry"][f"bank{bank}_events"]["event_time_offset"][:]
                event_id_original = hdf5_data["entry"][f"bank{bank}_events"]["event_id"][:]

            offset_value = 1000000  # Offset value
            event_id_original -= offset_value

            event_id = event_id_original

            hist, bin_edges = np.histogram(
                event_time_offset_original, bins=self.bin_size.value, range=(0, self.max_time.value)
            )

            # First plot - histogram
            fig1, ax1 = plt.subplots(figsize=(10, 5))
            ax1.bar(bin_edges[:-1], hist, width=np.diff(bin_edges), edgecolor="black")
            ax1.set_xlabel("Event Time Offset (micros)")
            ax1.set_ylabel("Counts")
            ax1.set_title(f"Event Time Offset Histogram from bank:{bank}")
            plt.tight_layout()
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

            # Second plot - 2D image
            fig2, ax2 = plt.subplots(figsize=(10, 10))
            im = ax2.imshow(full_image, cmap="viridis", interpolation="nearest")
            plt.colorbar(im, ax=ax2)
            ax2.set_title(f"{os.path.basename(nexus_full_path)} - bank:{bank}")
            plt.tight_layout()
            plt.show()

            display(HTML(f"Statistics for bank:{bank}:"))
            display(HTML(f"<br>Total Events: {len(event_id)}"))
            display(HTML(f"<br>Unique Pixels Hit: {len(np.unique(event_id))}"))
