import tdcsophiread as tdc
import os
import logging
from IPython.display import display, HTML
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from ipywidgets import interactive
from ipywidgets import widgets

from __code.ipywe import fileselector
from __code._utilities.file import get_full_log_file_name
from __code.timepix3_raw_to_profile_of_roi import config

# Setup plotting
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["font.size"] = 12

LOG_FILE_NAME = "timepix3_raw_to_profile_of_roi.log"


class Timepix3RawToProfileOfRoi:

    apply_sampling = False

    hist2d = None
    x_edges = None
    y_edges = None

    def __init__(self, working_dir=None, debug=False):
        self.working_dir = working_dir
        self.debug = debug

        self.log_file_name = get_full_log_file_name(LOG_FILE_NAME)
        logging.basicConfig(
            filename=self.log_file_name,
            filemode="w",
            format="[%(levelname)s] - %(asctime)s - %(message)s",
            level=logging.INFO,
        )
        logging.info("*** Starting a new session ***")
        logging.info(f"Debug mode is {self.debug}")
        print(f"log file: {self.log_file_name}")
              

    def select_tpx3(self):
        if self.debug:
            self.get_file_infos(file_name=config.default_tpx3_file)
            self.processing_tpx3(file_name=config.default_tpx3_file)
        else:
            self.nexus_ui = fileselector.FileSelectorPanel(
                instruction="Select TPX3 raw file ...",
                start_dir=self.working_dir,
                next=self.after_tpx3_file_selection,
                filters={"TPX3": ".tpx3"},
                multiple=False,
            )
            self.nexus_ui.show()

    def after_tpx3_file_selection(self, file_name):        
        self.get_file_infos(file_name=file_name)
        self.processing_tpx3(file_name=file_name)

    def get_file_infos(self, file_name=None):
        
        if file_name:
            logging.info(f"Getting file info for: {file_name}")
            # Simulate getting file info
            self.file_info = {
                "base name": os.path.basename(file_name),
                "path" : os.path.dirname(file_name),
                "size": f"{os.path.getsize(file_name) / (1024*1024):.2f} MB",
                "modified": os.path.getmtime(file_name),
            }
            logging.info(f"File info:")
            for _key in self.file_info:
                logging.info(f"\t{_key}: {self.file_info[_key]}")
        else:
            logging.info(f"File not found: {file_name}")

    def processing_tpx3(self, file_name=None):

        logging.info(f"Processing TPX3 file: {os.path.basename(file_name)} ... (be patient!)")
        start_time = time.time()
        
        # loading tpx3 file
        hits_view =  tdc.process_tpx3(file_name, parallel=True)
        hits = np.array(hits_view, copy=False)
        self.hits = hits

        end_time = time.time()
        processing_time = end_time - start_time
        logging.info(f"Processing completed in {processing_time:.2f} seconds.")
        display(HTML(f"Processing completed in {processing_time:.2f} seconds."))

        # display result as a table
        from_tof = hits['tof'].min() * 25 / 1e6
        to_tof = hits['tof'].max() * 25 / 1e6
        display(HTML("""
        <h3>TPX3 Processing Results</h3>
        <table border="3px solid black" style="border-collapse:collapse;">
            <tr><th><b>Infos</b></th><th><b>Value</b></th></tr>
            <tr><td>Total hits extracted</td><td>{}</td></tr>
            <tr><td>X range</td><td>{} - {}</td></tr>
            <tr><td>Y range</td><td>{} - {}</td></tr>
            <tr><td>TOF range (ms)</td><td>{:.3f} - {:.3f}</td></tr>
        </table>
        """.format(len(hits), hits['x'].min(), hits['x'].max(), hits['y'].min(), hits['y'].max(),
                   from_tof, to_tof)))

        unique_chips, chip_counts = np.unique(hits["chip_id"], return_counts=True)
        _text =  '<h3>Chips distribution (hits per chips)</h3> ' + \
                '<table border="3px solid black" style="border-collapse:collapse;">'
        for chip, count in zip(unique_chips, chip_counts):
            percentage = 100 * count / len(hits)
            _text += f'<tr><td>Chip {chip}</td><td>{count:,} hits ({percentage:.1f}%)</td></tr>'
        _text += '</table>'
        display(HTML(_text))

    def select_sampling_percentage(self):
        if len(self.hits) > 100_000:
            label = widgets.Label("Select sampling percentage:")
            self.sampling_percentage_ui = widgets.FloatSlider(min=0.01,
                                                         max=100,
                                                         value=0.1,
                                                         step=0.01)
            hori_layout = widgets.HBox([label, self.sampling_percentage_ui])
            self.apply_sampling = True
            display(hori_layout)
        else:
            display(HTML("File has less than 100,000 hits. No sampling is needed."))
            self.apply_sampling = False

    def display_image_with_roi(self):
        self.generate_2d_hit_map()    

    def generate_2d_hit_map(self):
        sample_fraction = self.sampling_percentage_ui.value / 100.
        if self.apply_sampling:
            n_sample = int(len(self.hits) * sample_fraction)
            sample_indices = np.random.choice(len(self.hits), size=n_sample, replace=False)
            hits_for_viz = self.hits[sample_indices]
            display(HTML(f"Using {n_sample:,} sampled hits ({sample_fraction*100:.1f}%) for visualization"))
        else:
            hits_for_viz = self.hits
            display(HTML(f"Using all {len(self.hits):,} hits for visualization"))
       
        # Create 2D histogram (bin by detector pixels)
        x_bins = np.arange(0, 515, 1)  # 0 to 514 pixels
        y_bins = np.arange(0, 515, 1)  # 0 to 514 pixels

        self.hist2d, self.x_edges, self.y_edges = np.histogram2d(
            hits_for_viz["x"], hits_for_viz["y"], bins=[x_bins, y_bins])

    def select_roi(self):
        pass
    
    def generate_histogram_and_select_roi(self):
        self.generate_2d_hit_map()
        self.select_roi()

    

