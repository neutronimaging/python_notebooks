import tdcsophiread as tdc
import os
import logging
from IPython.display import display, HTML
import time
import glob
import numpy as np
import logging as notebook_logging
import matplotlib.pyplot as plt
from ipywidgets import interactive
from ipywidgets import widgets
from PIL import Image

from __code.ipywe import fileselector
from __code.timepix3_image_statistics import config

# Setup plotting
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["font.size"] = 12

LOG_FILE_NAME = "timepix3_image_statistics.log"


class Timepix3ImageStatistics:
    def __init__(self, working_dir=None, debug=False):
        self.working_dir = working_dir
        self.debug = debug
        self.initialize()

    def initialize(self):
        LOG_PATH = "/SNS/VENUS/shared/log/"
        file_name, ext = os.path.splitext(os.path.basename(os.path.dirname(__file__)))
        user_name = os.getlogin()  # add user name to the log file name
        self.log_file_name = os.path.join(LOG_PATH, f"{user_name}_{file_name}.log")
        notebook_logging.basicConfig(
            filename=self.log_file_name,
            filemode="w",
            format="[%(levelname)s] - %(asctime)s - %(message)s",
            level=notebook_logging.INFO,
        )
        notebook_logging.info(f"*** Starting a new script {file_name} ***")

    def select_tpx3_folder(self):
        if self.debug:
            self.after_tpx3_file_selection(config.default_tpx3_file)
        else:
            self.nexus_ui = fileselector.FileSelectorPanel(
                instruction="Select TPX3 folder ...",
                start_dir=self.working_dir,
                type="directory",
                next=self.after_tpx3_file_selection,
                multiple=False,
            )
            self.nexus_ui.show()

    def produce_statistics(self):
        self.load_data()
        self.display_integrated_image()
        self.display_chips()
        self.process_chips()
        self.locate_dead_pixels()
        self.locate_high_pixels()

    def load_data(self):
        list_tiff = self.list_of_tiff_files
        self.data = np.array([np.array(Image.open(f)) for f in list_tiff])
        self.integrated_image = np.sum(self.data, axis=0)

    def display_integrated_image(self):
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.imshow(self.integrated_image, cmap="viridis", origin="lower")
        ax.set_title("Integrated Image")
        ax.set_xlabel("X (pixels)")
        ax.set_ylabel("Y (pixels)")
        fig.colorbar(ax.images[0], ax=ax, label="Counts")
        plt.show()

    def display_chips(self):
        self.chip1 = self.integrated_image[0:256, 256:]
        self.chip2 = self.integrated_image[0:256, 0:256]
        self.chip3 = self.integrated_image[256:, 0:256]
        self.chip4 = self.integrated_image[256:, 256:]

        cmap = "viridis"  # 'gray', 'viridis', 'plasma', 'inferno', 'magma', 'cividis'

        fig, axs = plt.subplots(2, 2, figsize=(10, 8))
        im01 = axs[0, 1].imshow(self.chip1, cmap=cmap, vmin=0)
        fig.colorbar(im01, ax=axs[0, 1])
        axs[0, 1].set_title("Chip 1")

        im02 = axs[0, 0].imshow(self.chip2, cmap=cmap, vmin=0)
        fig.colorbar(im02, ax=axs[0, 0])
        axs[0, 0].set_title("Chip 2")

        im03 = axs[1, 0].imshow(self.chip3, cmap=cmap, vmin=0)
        fig.colorbar(im03, ax=axs[1, 0])
        axs[1, 0].set_title("Chip 3")

        im04 = axs[1, 1].imshow(self.chip4, cmap=cmap, vmin=0)
        fig.colorbar(im04, ax=axs[1, 1])
        axs[1, 1].set_title("Chip 4")

        fig.tight_layout()

        # compare histograms of each chips
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(self.chip1.ravel(), bins=256, alpha=0.5, label="Chip 1")
        ax.hist(self.chip2.ravel(), bins=256, alpha=0.5, label="Chip 2")
        ax.hist(self.chip3.ravel(), bins=256, alpha=0.5, label="Chip 3")
        ax.hist(self.chip4.ravel(), bins=256, alpha=0.5, label="Chip 4")
        ax.set_yscale("log")
        ax.set_xlabel("Pixel Value")
        ax.set_ylabel("Frequency")
        ax.legend()
        plt.show()

    def process_chips(self):
        stat = {"min": [], "max": [], "mean": [], "median": [], "std": [], "sum": []}
        Timepix3ImageStatistics.chip_stats(self.chip1, stat)
        Timepix3ImageStatistics.chip_stats(self.chip2, stat)
        Timepix3ImageStatistics.chip_stats(self.chip3, stat)
        Timepix3ImageStatistics.chip_stats(self.chip4, stat)

        fig, axs = plt.subplots(2, 3, figsize=(10, 7))
        axs[0][0].plot(stat["min"], marker="o")
        axs[0][0].set_title("Min")
        axs[0][0].set_xticks([0, 1, 2, 3])
        axs[0][0].set_xticklabels(["Chip 1", "Chip 2", "Chip 3", "Chip 4"])

        axs[0][1].plot(stat["max"], marker="o")
        axs[0][1].set_title("Max")
        axs[0][1].set_xticks([0, 1, 2, 3])
        axs[0][1].set_xticklabels(["Chip 1", "Chip 2", "Chip 3", "Chip 4"])

        axs[0][2].plot(stat["mean"], marker="o")
        axs[0][2].set_title("Mean")
        axs[0][2].set_xticks([0, 1, 2, 3])
        axs[0][2].set_xticklabels(["Chip 1", "Chip 2", "Chip 3", "Chip 4"])

        axs[1][0].plot(stat["median"], marker="o")
        axs[1][0].set_title("Median")
        axs[1][0].set_xticks([0, 1, 2, 3])
        axs[1][0].set_xticklabels(["Chip 1", "Chip 2", "Chip 3", "Chip 4"])

        axs[1][1].plot(stat["std"], marker="o")
        axs[1][1].set_title("Standard Deviation")
        axs[1][1].set_xticks([0, 1, 2, 3])
        axs[1][1].set_xticklabels(["Chip 1", "Chip 2", "Chip 3", "Chip 4"])

        axs[1][2].plot(stat["sum"], marker="o")
        axs[1][2].set_title("Sum")
        axs[1][2].set_xticks([0, 1, 2, 3])
        axs[1][2].set_xticklabels(["Chip 1", "Chip 2", "Chip 3", "Chip 4"])

        fig.tight_layout()

    # let's get the statistics of each chip
    @staticmethod
    def chip_stats(chip, stat):
        stat["min"].append(np.min(chip))
        stat["max"].append(np.max(chip))
        stat["mean"].append(np.mean(chip))
        stat["median"].append(np.median(chip))
        stat["std"].append(np.std(chip))
        stat["sum"].append(np.sum(chip))

    def locate_dead_pixels(self):
        # locate all the dead pixels (value = 0 )
        dead_pixels_chip1 = np.where(self.chip1 == 0)
        dead_pixels_chip2 = np.where(self.chip2 == 0)
        dead_pixels_chip3 = np.where(self.chip3 == 0)
        dead_pixels_chip4 = np.where(self.chip4 == 0)

        display(
            HTML(f"""
        <h3>Dead Pixels Information</h3>
        <table border="3px solid black" style="border-collapse:collapse;">
            <tr><th><b>Chip</b></th><th><b>Number of Dead Pixels</b></th></tr>
            <tr><td>Chip 1</td><td>{len(dead_pixels_chip1[0])}</td></tr>
            <tr><td>Chip 2</td><td>{len(dead_pixels_chip2[0])}</td></tr>
            <tr><td>Chip 3</td><td>{len(dead_pixels_chip3[0])}</td></tr>
            <tr><td>Chip 4</td><td>{len(dead_pixels_chip4[0])}</td></tr>
        </table>
        """)
        )

        # highlight the dead pixels in each chip
        cmap = "viridis"
        fig, axs = plt.subplots(2, 2, figsize=(10, 8))
        im01 = axs[0, 1].imshow(self.chip1, cmap=cmap)
        axs[0, 1].scatter(dead_pixels_chip1[1], dead_pixels_chip1[0], color="y", s=1)
        fig.colorbar(im01, ax=axs[0, 1])
        axs[0, 1].set_title(f"Chip 1 ({len(dead_pixels_chip1[0])} dead pixels)")
        im02 = axs[0, 0].imshow(self.chip2, cmap=cmap)
        axs[0, 0].scatter(dead_pixels_chip2[1], dead_pixels_chip2[0], color="y", s=1)
        fig.colorbar(im02, ax=axs[0, 0])
        axs[0, 0].set_title(f"Chip 2 ({len(dead_pixels_chip2[0])} dead pixels)")
        im03 = axs[1, 0].imshow(self.chip3, cmap=cmap)
        axs[1, 0].scatter(dead_pixels_chip3[1], dead_pixels_chip3[0], color="y", s=1)
        fig.colorbar(im03, ax=axs[1, 0])
        axs[1, 0].set_title(f"Chip 3 ({len(dead_pixels_chip3[0])} dead pixels)")
        im04 = axs[1, 1].imshow(self.chip4, cmap=cmap)
        axs[1, 1].scatter(dead_pixels_chip4[1], dead_pixels_chip4[0], color="y", s=1)
        fig.colorbar(im04, ax=axs[1, 1])
        axs[1, 1].set_title(f"Chip 4 ({len(dead_pixels_chip4[0])} dead pixels)")
        plt.show()

    def locate_high_pixels(self):
        default_threshold = 0.1 * np.max(self.integrated_image)  # 10% of max value

        def display_high_pixels(threshold):
            fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(10, 8))

            im1 = axs[0, 1].imshow(self.chip1, cmap="viridis", origin="lower")
            high_pixels1 = np.where(self.chip1 >= threshold)
            display(
                HTML(
                    f"Number of high pixels in chip1 (>= {threshold}): {len(high_pixels1[0])}"
                )
            )
            axs[0, 1].scatter(high_pixels1[1], high_pixels1[0], color="r", s=1)
            axs[0, 1].set_title(f"High Pixels (>= {threshold})")
            axs[0, 1].set_xlabel("X (pixels)")
            axs[0, 1].set_ylabel("Y (pixels)")
            axs[0, 1].set_title("Chip 1")
            fig.colorbar(im1, ax=axs[0, 1])

            high_pixels2 = np.where(self.chip2 >= threshold)
            display(
                HTML(
                    f"Number of high pixels in chip2 (>= {threshold}): {len(high_pixels2[0])}"
                )
            )
            im2 = axs[0, 0].imshow(self.chip2, cmap="viridis", origin="lower")
            axs[0, 0].scatter(high_pixels2[1], high_pixels2[0], color="r", s=1)
            axs[0, 0].set_title(f"High Pixels (>= {threshold})")
            axs[0, 0].set_xlabel("X (pixels)")
            axs[0, 0].set_ylabel("Y (pixels)")
            axs[0, 0].set_title("Chip 2")
            fig.colorbar(im2, ax=axs[0, 0])

            im3 = axs[1, 0].imshow(self.chip3, cmap="viridis", origin="lower")
            high_pixels3 = np.where(self.chip3 >= threshold)
            display(
                HTML(
                    f"Number of high pixels in chip3 (>= {threshold}): {len(high_pixels3[0])}"
                )
            )
            axs[1, 0].scatter(high_pixels3[1], high_pixels3[0], color="r", s=1)
            axs[1, 0].set_title(f"High Pixels (>= {threshold})")
            axs[1, 0].set_xlabel("X (pixels)")
            axs[1, 0].set_ylabel("Y (pixels)")
            axs[1, 0].set_title("Chip 3")
            fig.colorbar(im3, ax=axs[1, 0])

            im4 = axs[1, 1].imshow(self.chip4, cmap="viridis", origin="lower")
            high_pixels4 = np.where(self.chip4 >= threshold)
            display(
                HTML(
                    f"Number of high pixels in chip4 (>= {threshold}): {len(high_pixels4[0])}"
                )
            )
            axs[1, 1].scatter(high_pixels4[1], high_pixels4[0], color="r", s=1)
            axs[1, 1].set_title(f"High Pixels (>= {threshold})")
            axs[1, 1].set_xlabel("X (pixels)")
            axs[1, 1].set_ylabel("Y (pixels)")
            axs[1, 1].set_title("Chip 4")
            fig.colorbar(im4, ax=axs[1, 1])

            plt.tight_layout()

            plt.show()

        display_plot = interactive(
            display_high_pixels,
            threshold=widgets.IntSlider(
                min=0,
                max=default_threshold,
                value=np.max(self.integrated_image),
            ),
        )
        display(display_plot)

    def after_tpx3_file_selection(self, folder_name):
        logging.info(f"TPX3 folder selected: {folder_name}")
        sub_folder_name = self.make_sure_its_the_correct_folder(folder_name)
        logging.info(
            f"done running make_sure_its_the_correct_folder, Using folder: {sub_folder_name =}"
        )
        if folder_name is not None:
            self.get_file_infos(
                original_folder_name=folder_name, sub_folder_name=sub_folder_name
            )
            # self.processing_tpx3(file_name=file_name)

    def make_sure_its_the_correct_folder(self, folder_name):
        list_of_tif_files = glob.glob(os.path.join(folder_name, "*.tif*"))
        if len(list_of_tif_files) > 0:
            logging.info(
                f"Folder {folder_name} contains .tif files. We are good to go!"
            )
            return folder_name
        else:
            # trying one folder deeper
            list_of_sub_folders = [
                f.path for f in os.scandir(folder_name) if f.is_dir()
            ]
            for sub_folder in list_of_sub_folders:
                list_of_tif_files = glob.glob(os.path.join(sub_folder, "*.tif*"))
                if len(list_of_tif_files) > 0:
                    logging.info(
                        f"Folder {folder_name} does not contain .tif files. Using sub-folder {sub_folder} instead"
                    )
                    display(
                        HTML(
                            f"<span style='color:green'>Folder {folder_name} does not contain .tif files. Using sub-folder {sub_folder} instead</span>"
                        )
                    )
                    return sub_folder
            logging.info(
                f"Folder {folder_name} does not contain .tif files. Please select another folder"
            )
            self.select_tpx3_folder()
            return None

    def get_file_infos(self, original_folder_name=None, sub_folder_name=None):
        if sub_folder_name:
            logging.info(f"Getting folder info for: {sub_folder_name}")

            # Simulate getting file info
            self.file_info = {
                "original_folder_name": original_folder_name,
                "sub_folder_name": sub_folder_name,
                "base name": os.path.basename(sub_folder_name),
                "path": os.path.dirname(sub_folder_name),
                "size": f"{os.path.getsize(sub_folder_name) / (1024*1024):.2f} MB",
            }

            # get modified time in human readable format
            mod_time = time.ctime(os.path.getmtime(sub_folder_name))
            self.file_info["modified"] = mod_time

            # number of images
            list_of_tiff_files = glob.glob(os.path.join(sub_folder_name, "*.tif*"))
            self.list_of_tiff_files = list_of_tiff_files
            self.file_info["number of .tif files"] = len(list_of_tiff_files)
            # size of images
            total_size = sum(os.path.getsize(f) for f in list_of_tiff_files)
            self.file_info["total size of .tif files"] = (
                f"{total_size / (1024*1024):.2f} MB"
            )
            # size of first image
            if len(list_of_tiff_files) > 0:
                self.file_info["size of each .tif file"] = (
                    f"{os.path.getsize(list_of_tiff_files[0]) / (1024*1024):.2f} MB"
                )
            else:
                self.file_info["size of each .tif file"] = "N/A"

            logging.info("File info:")
            for _key in self.file_info:
                logging.info(f"\t{_key}: {self.file_info[_key]}")

            display(
                HTML(
                    """
            <h3>TPX3 Folder Information</h3>
            <table border="3px solid black" style="border-collapse:collapse;">
                <tr><th><b>Property</b></th><th><b>Value</b></th></tr>
                <tr><td>Original folder name</td><td>{}</td></tr>
                <tr><td>Sub-folder name</td><td>{}</td></tr>
                <tr><td>Base name</td><td>{}</td></tr>
                <tr><td>Path</td><td>{}</td></tr>
                <tr><td>Size</td><td>{}</td></tr>
                <tr><td>Last modified</td><td>{}</td></tr>
                <tr><td>Number of .tif files</td><td>{}</td></tr>
                <tr><td>Total size of .tif files</td><td>{}</td></tr>
                <tr><td>Size of each .tif file</td><td>{}</td></tr>
            </table>
            """.format(
                        self.file_info["original_folder_name"],
                        self.file_info["sub_folder_name"],
                        self.file_info["base name"],
                        self.file_info["path"],
                        self.file_info["size"],
                        self.file_info["modified"],
                        self.file_info["number of .tif files"],
                        self.file_info["total size of .tif files"],
                        self.file_info["size of each .tif file"],
                    )
                )
            )

        else:
            logging.info(f"Folder not found: {sub_folder_name}")

    def processing_tpx3(self, file_name=None):
        logging.info(
            f"Processing TPX3 file: {os.path.basename(file_name)} ... (be patient!)"
        )
        start_time = time.time()

        # loading tpx3 file
        hits_view = tdc.process_tpx3(file_name, parallel=True)
        hits = np.array(hits_view, copy=False)
        self.hits = hits

        end_time = time.time()
        processing_time = end_time - start_time
        logging.info(f"Processing completed in {processing_time:.2f} seconds.")
        display(HTML(f"Processing completed in {processing_time:.2f} seconds."))

        # display result as a table
        from_tof = hits["tof"].min() * 25 / 1e6
        to_tof = hits["tof"].max() * 25 / 1e6
        display(
            HTML(
                """
        <h3>TPX3 Processing Results</h3>
        <table border="3px solid black" style="border-collapse:collapse;">
            <tr><th><b>Infos</b></th><th><b>Value</b></th></tr>
            <tr><td>Total hits extracted</td><td>{}</td></tr>
            <tr><td>X range</td><td>{} - {}</td></tr>
            <tr><td>Y range</td><td>{} - {}</td></tr>
            <tr><td>TOF range (ms)</td><td>{:.3f} - {:.3f}</td></tr>
        </table>
        """.format(
                    len(hits),
                    hits["x"].min(),
                    hits["x"].max(),
                    hits["y"].min(),
                    hits["y"].max(),
                    from_tof,
                    to_tof,
                )
            )
        )

        unique_chips, chip_counts = np.unique(hits["chip_id"], return_counts=True)
        _text = (
            "<h3>Chips distribution (hits per chips)</h3> "
            + '<table border="3px solid black" style="border-collapse:collapse;">'
        )
        for chip, count in zip(unique_chips, chip_counts):
            percentage = 100 * count / len(hits)
            _text += f"<tr><td>Chip {chip}</td><td>{count:,} hits ({percentage:.1f}%)</td></tr>"
        _text += "</table>"
        display(HTML(_text))

    def select_sampling_percentage(self):
        if len(self.hits) > 100_000:
            label = widgets.Label("Select sampling percentage:")
            self.sampling_percentage_ui = widgets.FloatSlider(
                min=0.01, max=100, value=0.1, step=0.01
            )
            hori_layout = widgets.HBox([label, self.sampling_percentage_ui])
            self.apply_sampling = True
            display(hori_layout)
        else:
            display(HTML("File has less than 100,000 hits. No sampling is needed."))
            self.apply_sampling = False

    def display_image_with_roi(self):
        self.generate_2d_hit_map()

    def generate_2d_hit_map(self):
        sample_fraction = self.sampling_percentage_ui.value / 100.0
        if self.apply_sampling:
            n_sample = int(len(self.hits) * sample_fraction)
            sample_indices = np.random.choice(
                len(self.hits), size=n_sample, replace=False
            )
            hits_for_viz = self.hits[sample_indices]
            display(
                HTML(
                    f"Using {n_sample:,} sampled hits ({sample_fraction*100:.1f}%) for visualization"
                )
            )
        else:
            hits_for_viz = self.hits
            display(HTML(f"Using all {len(self.hits):,} hits for visualization"))

        # Create 2D histogram (bin by detector pixels)
        x_bins = np.arange(0, 515, 1)  # 0 to 514 pixels
        y_bins = np.arange(0, 515, 1)  # 0 to 514 pixels

        self.hist2d, self.x_edges, self.y_edges = np.histogram2d(
            hits_for_viz["x"], hits_for_viz["y"], bins=[x_bins, y_bins]
        )

    def select_roi(self):
        pass

    def generate_histogram_and_select_roi(self):
        self.generate_2d_hit_map()
        self.select_roi()
