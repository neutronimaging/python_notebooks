import glob
import os
import shutil
import logging
from PIL.ExifTags import TAGS
import tifffile
import time
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

from IPython.display import HTML, display
from ipywidgets import widgets
from tqdm import tqdm

from __code.ipywe import myfileselector
from __code.mars_sample_cataloging.config import list_metadata_label_to_keep, DEBUG
from __code._utilities.metadata_handler import MetadataHandler

TagNames = {
    '65000': 'Acquisition Time Human Readable Format',
    '65010': 'File Name Str',
    '65015': 'Sample Description Str',
    'JEOL_Header': 'Acquisition Time (s)',
    'number of files in folder': 'Number of Files in Folder',
    'total acquisition time (s)': 'Total Acquisition Time (s)',
    'first file in folder': 'First File in Folder'
}


class MarsSampleCataloging:
       
    metadata_dict = {'raw_radiographs': {}, 'ct_scans': {}}
    
    def initialize(self):
        LOG_PATH = "/SNS/VENUS/shared/log/"
        file_name = "mars_sample_cataloging"
        user_name = os.getlogin()  # add user name to the log file name
        log_file_name = os.path.join(LOG_PATH, f"{user_name}_{file_name}.log")
        logging.basicConfig(
            filename=log_file_name,
            filemode="w",
            format="[%(levelname)s] - %(asctime)s - %(message)s",
            level=logging.INFO,
        )
        logging.info(f"*** Starting a new script {file_name} ***")
    
    def __init__(self, working_dir=""):
        self.initialize()
        self.working_dir = working_dir
        _, _facility, _beamline, ipts = self.working_dir.split("/")
        logging.info(f"Working directory: {self.working_dir}")
        logging.info(f"IPTS: {ipts}")
        logging.info(f"Facility: {_facility}, Beamline: {_beamline}")
        self.ipts = ipts

    def select_output_folder(self):
        self.output_folder_ui = myfileselector.FileSelectorPanelWithJumpFolders(
            instruction="Select Output Folder ...",
            start_dir=self.working_dir,
            multiple=False,
            next=self.create_catalog,
            type="directory",
            newdir_toolbar_button=True,
            ipts_folder=self.working_dir,
        )
        self.output = widgets.Output()
        display(self.output)

    def create_catalog(self, output_folder):
        logging.info(f"Creating catalog in: {output_folder}")
        
        # raw_radiographs
        self.raw_dict_files = self.retrieve_all_tiff_files_from_ipts_raw_radiographs()
        self.extract_metadata_from_filenames(self.raw_dict_files['raw_radiographs'], 'raw_radiographs')
        self.calculate_and_display_raw_radiographs_statistics()

        # ct_scans
        self.ct_dict_folders = self.retrieve_all_folders_from_ipts_ct_scans()
        self.extract_metadata_from_folders(self.ct_dict_folders['ct_scans'], 'ct_scans')
        self.calculate_and_display_ct_scans_statistics()
        
        self.display_global_statistics
        self.export_catalog_to_csv(output_folder)
        
    def export_catalog_to_csv(self, output_folder):

        # raw radiographs
        raw_radiographs_df = pd.DataFrame.from_dict(self.metadata_dict['raw_radiographs'], orient='index')
        output_file = os.path.join(output_folder, f"{self.ipts}_raw_radiographs_folder_sample_catalog.csv")
        raw_radiographs_df.to_csv(output_file, index=False)
        logging.info(f"Raw radiographs catalog exported to: {output_file}")
        display(HTML(f"""<h3>Raw Radiographs catalog exported to: <b>{output_file}</b></h3>"""))
        
        # ct_scans
        ct_scans_df = pd.DataFrame.from_dict(self.metadata_dict['ct_scans'], orient='index')
        output_file = os.path.join(output_folder, f"{self.ipts}_ct_scans_folder_sample_catalog.csv")
        ct_scans_df.to_csv(output_file, index=False)
        logging.info(f"CT scans catalog exported to: {output_file}")
        display(HTML(f"""<h3>CT Scans catalog exported to: <b>{output_file}</b></h3>"""))
        
    def calculate_and_display_raw_radiographs_statistics(self):
        self.calculate_and_plot_statistics_for_category('raw_radiographs')
        
    def calculate_and_display_ct_scans_statistics(self):
        self.calculate_and_plot_statistics_for_category('ct_scans')
        
    def display_global_statistics(self):
        nbr_raw_tiff_files = len(self.raw_dict_files['raw_radiographs'])
        nbr_ct_folders = len(self.ct_dict_folders['ct_scans'])
        
         # present the number of files found to the user as a table
        display(HTML(f"""
        <table>
            <tr>
                <th><b>Category</b></th>
                <th><b>Number of TIFF Files</b></th>
            </tr>
            <tr>
                <td><b>Raw Radiographs</b></td>
                <td>{nbr_raw_tiff_files}</td>
            </tr>
            <tr>
                <td><b>CT Scans</b></td>
                <td>{nbr_ct_folders}</td>
            </tr>
        </table>
        """))
        
    def calculate_and_plot_statistics_for_category(self, category):
        data_frame = pd.DataFrame.from_dict(self.metadata_dict[category], orient='index')       
        logging.info(f"{category} Metadata DataFrame:\n{data_frame.head()}")
        
        # with self.output:
        display(HTML(f"""<h2>Statistics for <b>{category}</b></h2>"""))
    
        if category == 'raw_radiographs':
        
            # display histogram of acquisition times
            data_frame['Acquisition Time (s)'] = pd.to_numeric(data_frame['Acquisition Time (s)'], errors='coerce')
            fig = px.histogram(
                data_frame, 
                x='Acquisition Time (s)', 
                nbins=10,
                title=f"Histogram of Acquisition Times for {category}",
                labels={'count': 'Frequency'}
            )
            fig.update_layout(width=1000, height=600)
            fig.show()

        if category == 'ct_scans':
            # display histogram of number of files in folder for ct_scans category
            data_frame['Number of Files in Folder'] = pd.to_numeric(data_frame['Number of Files in Folder'], errors='coerce')
            fig = px.histogram(
                data_frame, 
                x='Number of Files in Folder', 
                nbins=20,
                title=f"Histogram of Number of Files in {category} folder",
                labels={'count': 'Frequency'}
            )
            fig.update_layout(width=1000, height=600)
            fig.show()
            
            # display histogram of total number of acquisition time in seconds for ct_scans category        
            data_frame['Total Acquisition Time (s)'] = pd.to_numeric(data_frame['Total Acquisition Time (s)'], errors='coerce')
            fig = px.histogram(
                data_frame, 
                x='Total Acquisition Time (s)', 
                nbins=10,
                title=f"Histogram of Total Acquisition Time (s) per folder for {category}",
                labels={'count': 'Frequency'}
            )
            fig.update_layout(width=1000, height=600)
            fig.show()

        # get number of unique samples based on the sample description
        num_unique_samples = data_frame['Sample Description Str'].nunique()
        logging.info(f"Number of unique samples in {category}: {num_unique_samples}")
        # with self.output:
        display(HTML(f"""<p><b>Number of unique samples</b> in <b>{category}</b>: {num_unique_samples}</p>"""))
        
    def _retrive_metadata_from_tiff_file(self, tiff_file):
        logging.info(f"\tRetrieving metadata from file: {tiff_file}")
        metadata = {}
        try:
            with tifffile.TiffFile(tiff_file) as tif:
                page = tif.pages[0]
                for tag in page.tags:
                    try:
                        _metadata_label = tag.name
                        _metadata_value = tag.value
                    except:
                        _metadata_label = tag.code
                        _metadata_value = tag.value
                    
                    if _metadata_label in list_metadata_label_to_keep:
                                
                        if _metadata_label == '65000': # this is the acquisition timestamp in seconds 
                            _metadata_value_formated = MetadataHandler.convert_to_human_readable_format(MetadataHandler._convert_epics_timestamp_to_rfc3339_timestamp(_metadata_value))    
                            metadata[TagNames['65000']] = _metadata_value_formated
                            
                        elif _metadata_label == 'JEOL_Header': # this is a long string, so we only log the first 50 characters
                            _, acquisition_time = _metadata_value.split(":")
                            metadata[TagNames['JEOL_Header']] = acquisition_time.strip()
                        
                        elif _metadata_label == '65010':
                            _, file_name_str = _metadata_value.split(":")
                            metadata[TagNames['65010']] = file_name_str.strip()
                        
                        elif _metadata_label == '65015':
                            _, sample_description_str = _metadata_value.split(":")
                            metadata[TagNames['65015']] = sample_description_str.strip()
        
        except Exception as e:
            logging.error(f"Error reading TIFF file {tiff_file}: {e}")
        
        return metadata
        
    def extract_metadata_from_filenames(self, file_list, category):
        logging.info(f"Extracting metadata from TIFF for category: {category}")
        with self.output:
            display(HTML(f"""Extracting metadata from TIFF for category: <b>{category}</b> ... </h2>"""))
        
        self.metadata_dict[category] = {}   
        local_metadata_dict = {}
        
        with self.output:
            for _file in tqdm(file_list):
                _metadata_dict = self._retrive_metadata_from_tiff_file(_file)
                local_metadata_dict[_file] = _metadata_dict
              
            self.metadata_dict[category] = local_metadata_dict

            self.output.clear_output()
            display(HTML(f"""Metadata extraction for category: <b>{category}</b> completed."""))
        
    def extract_metadata_from_folders(self, folder_list, category):
        logging.info(f"Extracting metadata from folders for category: {category}")
        with self.output:
            display(HTML(f"""Extracting metadata from folders for category: <b>{category}</b> ... </h2>"""))
        
        local_metadata_dict = {}
        with self.output:
            for _folder in tqdm(folder_list):
                logging.info(f"\tProcessing folder: {_folder}")
                list_tiff_files = glob.glob(os.path.join(_folder, "*.tif*"))
                nbr_files = len(list_tiff_files)
                if nbr_files == 0:
                    continue
                
                local_metadata_dict[_folder] = {}
                
                list_tiff_files.sort()
                first_file = list_tiff_files[0]
                _metadata_of_that_folder = self._retrive_metadata_from_tiff_file(first_file)
                local_metadata_dict[_folder].update(_metadata_of_that_folder)
                local_metadata_dict[_folder][TagNames['number of files in folder']] = nbr_files
                local_metadata_dict[_folder][TagNames['total acquisition time (s)']] = nbr_files * float(_metadata_of_that_folder[TagNames['JEOL_Header']])       
                local_metadata_dict[_folder][TagNames['first file in folder']] = first_file
        
            self.output.clear_output()
            display(HTML(f"""Metadata extraction from folders for category: <b>{category}</b> completed."""))
        
        self.metadata_dict[category] = local_metadata_dict
        
    def retrieve_all_tiff_files_from_ipts_raw_radiographs(self) -> dict:
        """
        Docstring for retrieve_all_tiff_files_from_ipts_raw_radiographs
        
        :param self: Description
        :return: Description
        :rtype: dict
        """
        
        # get list of tiff files from all folders in raw/radiographs subfolder
        raw_search_path = os.path.join(
            self.working_dir, "raw", "radiographs", "**", "*.tiff"
        )
        logging.info(f"Searching for tiff files in: {raw_search_path}")
        raw_tiff_files = glob.glob(raw_search_path, recursive=True)
        logging.info(f"\tNumber of tiff files found: {len(raw_tiff_files)}")
        if DEBUG:
            raw_tiff_files = raw_tiff_files[:10]
            logging.info(f"\tDEBUG mode is ON - Limiting number of files to: {len(raw_tiff_files)}")

        return {'raw_radiographs': raw_tiff_files}
    
    def retrieve_all_folders_from_ipts_ct_scans(self) -> dict:
        ct_search_path = os.path.join(
            self.working_dir, "raw", "ct_scans")
        logging.info(f"Searching for all the folders in ct_scans subfolder: {ct_search_path}")
        ct_scan_folders = glob.glob(ct_search_path + '/*', recursive=False)
        logging.info(f"\tNumber of folders found in ct_scans: {len(ct_scan_folders)}")
        
        ct_scans_folders = [folder for folder in ct_scan_folders if os.path.isdir(folder)]
        return {'ct_scans': ct_scans_folders}    
