import ipywe.fileselector
from NeuNorm.normalization import Normalization

from IPython.core.display import HTML
from IPython.core.display import display

from ipywidgets.widgets import interact
from ipywidgets import widgets

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
import pandas as pd
import datetime
import shutil

from __code.file_handler import make_ascii_file


class ProfileVsFileIndex(object):

    o_load = None
    folder_ui = None
    roi = []

    list_data_files = [] # filename
    list_data = [] # data

    height = -1
    width = -1
    image_dimension = None
    integrated_data = None
    rebin_range = None

    def __init__(self, working_dir='./'):
        self.working_dir = working_dir


    def select_images(self):
        self.folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Input Images ...',
                                                              start_dir=self.working_dir,
                                                              multiple=True)

        self.folder_ui.show()

    def load_images(self):

        try:
            self.list_data_files = self.folder_ui.selected
        except:
            display(HTML('<span style="font-size: 20px; color:red">Please Select a set of Images First!</span>'))
            return

        self.o_load = Normalization()
        self.o_load.load(file=self.list_data_files, notebook=True)

        self.list_data = self.o_load.data['sample']['data']

    def __calculate_integrated_data(self):

        _data = self.list_data
        if len(_data) > 1:
            integrated_array = np.array([_array for _array in _data])
            return integrated_array.mean(axis=0)
        else:
            return np.squeeze(_data)

    def select_profile(self, roi_left=0, roi_top=0, roi_height=-1, roi_width=-1):

        self.integrated_data = self.__calculate_integrated_data()

        self.image_dimension = np.shape(self.integrated_data)
        [self.height, self.width] = self.image_dimension

        if roi_height == -1:
            roi_height = self.height - 1

        if roi_width == -1:
            roi_width = self.width - 1

        def plot_images_with_roi(x_left, y_top, width, height):

            plt.figure(figsize=(5, 5))
            ax_img = plt.subplot(111)

            ax_img.imshow(self.integrated_data, cmap='rainbow',
                          interpolation=None)
            #                   vmin = min_intensity,
            #                   vmax = max_intensity)

            ax_img.add_patch(patches.Rectangle((x_left, y_top), width, height, fill=False))

            return [x_left, y_top, width, height]

        self.profile = interact(plot_images_with_roi,
                               x_left=widgets.IntSlider(min=0,
                                                        max=self.width - 1,
                                                        step=1,
                                                        value=roi_left,
                                                        continuous_update=False),
                               y_top=widgets.IntSlider(min=0,
                                                       max=self.height - 1,
                                                       step=1,
                                                       value=roi_top,
                                                       continuous_update=False),
                               width=widgets.IntSlider(min=0,
                                                       max=self.width - 1,
                                                       step=1,
                                                       value=roi_width,
                                                       continuous_update=False),
                               height=widgets.IntSlider(min=0,
                                                        max=self.height - 1,
                                                        step=1,
                                                        value=roi_height,
                                                        continuous_update=False))

    def calculate_integrated_profile(self):
        [roi_left, roi_top, roi_width, roi_height] = self.profile.widget.result

        self.roi = [roi_left, roi_top, roi_width, roi_height]

        sample_data = self.o_load.data['sample']['data']
        self.sample_data = sample_data

        w = widgets.IntProgress()
        w.max = len(sample_data) - 1
        display(w)
        index = 0

        profile_array = []
        for _image in sample_data:
            _profile_image = _image[roi_top:roi_top + roi_height, roi_left:roi_left + roi_width]
            _value = np.sum(_profile_image)
            profile_array.append(_value)
            w.value = index
            index += 1

        w.close()

    def calculate_profile(self):

        self.rebin = 1

        sample_data = self.sample_data
        [roi_left, roi_top, roi_width, roi_height] = self.roi

        w = widgets.IntProgress()
        w.max = len(sample_data) - 1
        display(w)

        self.rebin_range = np.arange(0, roi_height - roi_top, self.rebin)

        profile_1d = []
        for _index, _array in enumerate(sample_data):
            _roi_array = _array[roi_top:roi_top + roi_height, roi_left:roi_left + roi_width]
            _width_profile = np.sum(_roi_array, 1)
            rebin_width_profile = [sum(_width_profile[x:x + self.rebin]) for x in self.rebin_range]
            profile_1d.append(rebin_width_profile)
            _index += 1
            w.value = _index

        self.profile_1d = profile_1d

    def display_profile(self):

        [roi_left, roi_top, roi_width, roi_height] = self.roi

        def plot_profile(file_index):
            data_1d = self.profile_1d[file_index]
            data_2d = self.sample_data[file_index]

            fig = plt.figure(figsize=(5, 5))

            ax_plt = plt.subplot(211)
            ax_plt.plot(data_1d)
            ax_plt.set_title(os.path.basename(self.list_data_files[file_index]))

            ax_img = plt.subplot(212)
            ax_img.imshow(data_2d, cmap='rainbow',
                          interpolation=None)
            ax_img.add_patch(patches.Rectangle((roi_left, roi_top), roi_width, roi_height, fill=False))

        number_of_files = len(self.sample_data)
        _ = interact(plot_profile,
                     file_index=widgets.IntSlider(min=0,
                     max=number_of_files - 1,
                     value=0,
                     step=1,
                     description="Image Index",
                     continuous_update=False))

    def select_file_name_vs_time_stamp(self):

        self.file_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select file_name_vs_time_stamp File ...',
                                                            start_dir=self.working_dir,
                                                            multiple=False)

        self.file_ui.show()

    def load_file_name_vs_time_stamp_file(self):
        file_vs_timestamp_file = self.file_ui.selected
        if file_vs_timestamp_file:
            if type(file_vs_timestamp_file) == list:
                file_vs_timestamp_file = file_vs_timestamp_file[0]

            self.df = pd.read_csv(file_vs_timestamp_file)

        self.df.head()

        self.list_file_name = self.df['#filename'].values
        list_column = self.df.columns.values
        self.list_time_stamp = self.df[list_column[1]].values

    def select_output_folder(self):
        self.output_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Output Folder ...',
                                                                     start_dir=self.working_dir,
                                                                     type='directory')
        self.output_folder_ui.show()

    def __get_time_stamp(self, file_name):
        _index_time_stamp = self.list_data_files_short.index(os.path.basename(file_name))
        return self.list_time_stamp[_index_time_stamp]

    def output_profiles(self):

        # make name of output folder
        output_folder = os.path.join(os.path.abspath(self.output_folder_ui.selected),
                                     os.path.basename(os.path.dirname(self.list_file_name[0]) + '_profiles'))
        output_folder = os.path.abspath(output_folder)
        if os.path.isdir(output_folder):
            shutil.rmtree(output_folder)
        os.mkdir(output_folder)

        [roi_left, roi_top, roi_width, roi_height] = self.roi

        self.list_data_files_short = [os.path.basename(_file) for _file in self.df['#filename']]
        time_0 = self.__get_time_stamp(self.list_data_files[0])

        w = widgets.IntProgress()
        w.max = len(self.profile_1d)
        display(w)

        for _index, _profile in enumerate(self.profile_1d):
            _file_name = self.list_data_files[_index]
            _time_stamp = self.__get_time_stamp(_file_name)

            metadata = []
            metadata.append("#Image: {}".format(_file_name))
            metadata.append(
                "#ROI selected (y0, x0, height, width): ({}, {}, {}, {})".format(roi_top,
                                                                                 roi_left,
                                                                                 roi_height,
                                                                                 roi_width))
            metadata.append("#Rebin in y direction: {}".format(self.rebin))

            _time_stamp_str = datetime.datetime.fromtimestamp(_time_stamp).strftime("%Y-%m-%d %H:%M:%S")
            metadata.append("#Time Stamp: {}".format(_time_stamp_str))

            _delta_time = _time_stamp - time_0
            metadata.append("#Delta Time (s): {}".format(_delta_time))
            metadata.append("#")

            metadata.append("#Label: pixel_index, counts")

            data = []
            for _index_data, value in enumerate(self.profile_1d[_index]):
                data.append("{}, {}".format(self.rebin_range[_index_data], value))

            _base_file_name = os.path.basename(_file_name)
            [base, _] = os.path.splitext(_base_file_name)

            output_file_name = os.path.join(output_folder, base + '.txt')
            make_ascii_file(metadata=metadata,
                            data=data,
                            output_file_name=output_file_name,
                            dim='1d')

            w.value = _index+1

        w.close()