from __code import utilities, gui_widgets, file_handler
import ipywe.fileselector
from IPython.core.display import display, HTML
import pandas as pd
import numpy as np
from pprint import pprint

from ipywidgets import widgets
from IPython.core.display import display, HTML

import matplotlib.pyplot as plt

from IPython import display as display_ipython

from plotly.offline import plot, init_notebook_mode, iplot
init_notebook_mode()
import plotly.plotly as py
import plotly.graph_objs as go

import os
import sys
import time, datetime


class FileNameMetadataTimeStamp(object):

    def __init__(self, working_dir, verbose=False):
        self.working_dir = working_dir
        self.verbose = verbose

        if sys.platform == 'darwin':
            self.my_system = 'mac'
        else:
            self.my_system = 'not_mac'

        # sample images
        self.timestamp_array = []
        self.list_base_file_name = []
        self.time_stamp_vs_file_name = []

        # metadata
        final_time_stamp_metadata = []

    def select_image_folder(self):
        self.folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Raw Image Folder ...',
                                                         start_dir=self.working_dir,
                                                         type='directory')
        self.folder_ui.show()

        display(HTML(
            '<span style="font-size: 20px; color:blue">Make sure you select the Raw untouched (not copied) sample folder!</span>'))

    def select_metadata_file(self):
        self.sample_environment_file_ui = ipywe.fileselector.FileSelectorPanel(
            instruction='Select Sample Environment File ...',
            start_dir=self.working_dir)
        self.sample_environment_file_ui.show()

    def format_files(self, metadata_header=[]):
        self.format_image_infos()
        self.format_metadata_infos(header=metadata_header)

    def merging_formated_files(self):
        file_name_array = self.time_stamp_vs_file_name
        metadata_array = self.final_time_stamp_metadata

        if self.verbose:
            file_name_array.head()
            metadata_array.head()

        # set the first column as the index
        file_name_array = file_name_array.set_index('index')
        metadata_array = metadata_array.set_index('index')

        time_stamp_metadata_file_name_merged = pd.merge(file_name_array,
                                                        metadata_array,
                                                        left_index=True,
                                                        right_index=True,
                                                        how='outer')

        if self.verbose:
            pprint(time_stamp_metadata_file_name_merged)

        # extract file name vs temperature
        time_stamp_array = np.array(time_stamp_metadata_file_name_merged.index)
        file_name_array = np.array(
            time_stamp_metadata_file_name_merged[time_stamp_metadata_file_name_merged.columns[0]])
        metadata_array = np.array(
            time_stamp_metadata_file_name_merged[time_stamp_metadata_file_name_merged.columns[1]])

        # calculate equivalent metadata for each file
        file_name_vs_metadata_array = []  # 'file_name, metadata, time_stamp

        # w1 = widgets.IntProgress(description='Calculating')
        # w1.max = len(file_name_array)
        # display(w1)

        for _index, _file in enumerate(file_name_array):
            if _file is np.NaN:
                continue

            if np.isnan(metadata_array[_index]):
                _metadata = self.__extract_metadata(index=_index,
                                                    metadata_array=metadata_array,
                                                    time_stamp_array=time_stamp_array)
            else:
                _metadata = metadata_array[_index]

            _new_entry = [_file, _metadata, time_stamp_array[_index]]
            file_name_vs_metadata_array.append(_new_entry)

        # w1.value = _index+1

        if self.verbose:
            pprint(file_name_vs_metadata_array)


    def __calculate_file_metadata(self, left_meta=-1, right_meta=-1, left_time=-1, right_time=-1, file_time=-1):
        coeff = (float(right_meta) - float(left_meta)) / (float(right_time) - float(left_time))
        part1 = coeff * (float(file_time) - float(left_time))
        return part1 + float(left_meta)

    def __get_first_metadata_and_index_value(self, index=-1, data_array=[], direction='left'):
        if direction == 'left':
            coeff = -1
        else:
            coeff = 1

        while (np.isnan(data_array[index])):
            index += coeff
        return [data_array[index], index]

    def __extract_metadata(self, index=-1, metadata_array=[], time_stamp_array=[]):

        [left_meta, left_index] = self.__get_first_metadata_and_index_value(index=index, data_array=metadata_array,
                                                                     direction='left')
        [right_meta, right_index] = self.__get_first_metadata_and_index_value(index=index, data_array=metadata_array,
                                                                       direction='right')

        left_time = time_stamp_array[left_index]
        right_time = time_stamp_array[right_index]

        file_time = time_stamp_array[index]

        file_metadata = self.__calculate_file_metadata(left_meta=left_meta,
                                                right_meta=right_meta,
                                                left_time=left_time,
                                                right_time=right_time,
                                                file_time=file_time)

        return file_metadata

    def format_metadata_infos(self, header=[]):
        box = widgets.VBox([widgets.Label("Formatting metadata file .......... IN PROGRESS")])
        display(box)
        progress_label = box.children[0]

        # retrieve time and metadata from file
        sample_environment_file = self.sample_environment_file_ui.selected

        df = pd.read_csv(sample_environment_file, sep='\t', names=header)
        df = df.reset_index()

        try:
            del df[None]  # removing empty columns
        except:
            pass

        # removing useless columns
        if self.my_system == 'mac':
            time_stamp_metadata = df.drop(df.columns[[1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18]],
                                          axis=1)
        else:
            time_stamp_metadata = df[['time_stamp', 'OT\ Temp']]

        if self.verbose:
            pprint("")
            pprint(time_stamp_metadata.head())
            fig = plt.figure()
            if self.my_system == 'mac':
                df['OT Temp'].plot()
            else:
                df['OT\ Temp'].plot()

        # convert to pandas time format
        time_stamp_metadata['index'] = pd.to_datetime(time_stamp_metadata['index'])
        if self.verbose:
            pprint("")
            pprint(time_stamp_metadata.head())

        # convert to time stamp
        new_df_2 = time_stamp_metadata
        new_df_2['index'] = time_stamp_metadata['index'].apply(self.conv)

        self.final_time_stamp_metadata = new_df_2

        if self.verbose:
            pprint("")
            pprint(new_df_2.head())

        progress_label.value = 'Formatting metadata file .......... DONE!'

    def conv(self, x):
            return time.mktime(datetime.datetime.strptime(str(x), "%Y-%m-%d %H:%M:%S").timetuple())

    def format_image_infos(self):
        folder = self.folder_ui.selected

        list_files = file_handler.retrieve_list_of_most_dominand_extension_from_folder(folder=folder)
        list_files = list_files[0]

        box = widgets.VBox([widgets.Label("Retrieving Time Stamp .......... IN PROGRESS")])

        display(box)
        progress_label = box.children[0]
        timestamp_array = []
        list_base_file_name = []
        for _index, _file in enumerate(list_files):
            time_stamp = os.path.getmtime(_file)
            timestamp_array.append(time_stamp)
            list_base_file_name.append(os.path.basename(_file))

        progress_label.value = 'Retrieving Time Stamp .......... DONE!'

        data = list(zip(timestamp_array, list_base_file_name))
        self.time_stamp_vs_file_name = pd.DataFrame(data, columns=['index', 'file_name'])

        self.timestamp_array = timestamp_array
        self.list_base_file_name = list_base_file_name
