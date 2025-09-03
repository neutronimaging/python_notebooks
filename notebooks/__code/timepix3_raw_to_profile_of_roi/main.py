# import tdcsophiread as tdc
import os
import logging
from IPython.display import display, HTML
import time
import numpy as np

from __code.ipywe import fileselector
from __code._utilities.file import get_full_log_file_name
from __code.timepix3_raw_to_profile_of_roi import config

LOG_FILE_NAME = "timepix3_raw_to_profile_of_roi.log"


class Timepix3RawToProfileOfRoi:

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
        display(HTML("Processing TPX3 file ... be patient!"))
        start_time = time.time()
        
        ## loading tpx3 file
        # hits_view =  tdc.process_tpx3(file_name, parallel=True)
        # hits = np.array(hits_view, copy=False)

        # DEBUG ONLY
        hits = np.arange(10)

        end_time = time.time()
        processing_time = end_time - start_time
        logging.info(f"Processing completed in {processing_time:.2f} seconds.")
        display(HTML(f"Processing completed in {processing_time:.2f} seconds."))

        # display result as a table
        display(HTML("<h3>TPX3 Processing Results</h3>"))
        display(HTML("<table>"))
        display(HTML(f"<tr><th>Infos</th><th>Value</th></tr>"))
        display(HTML(f"<tr><td>Total hits extracted</td><td>{len(hits)}</td></tr>"))
        display(HTML(f"<tr><td>X range</td><td>{hits['x'].min()} - {hits['x'].max()}</td></tr>"))
        display(HTML(f"<tr><td>Y range</td><td>{hits['y'].min()} - {hits['y'].max()}</td></tr>"))
        
        from_tof = hits['tof'].min() * 25 / 1e6
        to_tof = hits['tof'].max() * 25 / 1e6
        display(HTML(f"<tr><td>TOF range</td><td>{from_tof:.3f} - {to_tof:.3f} ms</td></tr>"))
        display(HTML("</table>"))
        
        # chips distribution
        display(HTML("<h3>Chips distribution (hits per chip)</h3>"))
        display(HTML("<table>"))
        unique_chips, chip_counts = np.unique(hits["chip_id"], return_counts=True)
        for chip, count in zip(unique_chips, chip_counts):
            percentage = 100 * count / len(hits)
            display(HTML(f"<tr><td>Chip {chip}</td><td>{count:,} hits ({percentage:.1f}%)</td></tr>"))
            display(HTML(f"<tr><td>Chip {chip}</td><td>{count} ({percentage:.1f}%)</td></tr>"))
        display(HTML("</table>"))
        