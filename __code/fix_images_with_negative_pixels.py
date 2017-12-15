import os
from collections import namedtuple
import numpy as np

from ipywidgets import widgets

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from IPython.core.display import display
from IPython.core.display import HTML

from NeuNorm.normalization import Normalization
from __code.file_folder_browser import FileFolderBrowser
from __code.file_handler import save_data, make_folder

class FixImages(FileFolderBrowser):

    list_files = []
    data = []
    full_statistics = {}

    Statistics = namedtuple('Statistics',
                            'nbr_pixel_modified percentage_pixel_modified total_pixels')

    def __init__(self, working_dir=''):
        super(FixImages, self).__init__(working_dir=working_dir)

    def load(self):

        self.list_files = self.list_images_ui.selected

        data = []

        w = widgets.IntProgress()
        w.max = len(self.list_files)
        display(w)

        for _index, _file in enumerate(self.list_files):

            _o_norm = Normalization()
            _o_norm.load(file=_file)
            _data = _o_norm.data['sample']['data'][0]
            data.append(_data)
            w.value = _index + 1

        self.data = data
        w.close()

    def display(self):

        _data = self.data
        _files = self.list_files
        def _plot_images(index):
            fig, ax_img = plt.subplots()

            plt.title(os.path.basename(_files[index]))
            cax = ax_img.imshow(_data[index], cmap='viridis', interpolation=None)

            # add colorbar
            cbar = fig.colorbar(cax)

        _ = widgets.interact(_plot_images,
                             index=widgets.IntSlider(min=0,
                                                     max=len(self.list_files) - 1,
                                                     step=1,
                                                     value=0,
                                                     description='File Index',
                                                     continuous_update=False))

    def remove_negative_values(self):

        clean_data = []
        full_statistics = {}

        for _index, _data in enumerate(self.data):
            _result = np.where(_data < 0)
            new_data = _data.copy()
            new_data[_result] = np.NaN
            clean_data.append(new_data)

            _nbr_pixel_modified = len(_result[0])
            _total_pixels =  np.size(_data)
            _percentage = (_nbr_pixel_modified / _total_pixels) * 100

            _stat = self.Statistics(nbr_pixel_modified=_nbr_pixel_modified,
                                    percentage_pixel_modified=_percentage,
                                    total_pixels=_total_pixels)
            full_statistics[_index] = _stat

        self.clean_data = clean_data
        self.full_statistics = full_statistics

    def get_statistics_of_roi_cleaned(self, x_left, y_top, height, width, data):

        _data = data[y_top:y_top+height, x_left:x_left+width]
        _result = np.where(_data < 0)
        nbr_negative_in_roi = len(_result[0])
        total = width * height
        percentage_in_roi = (nbr_negative_in_roi / total) * 100

        stat = self.Statistics(nbr_pixel_modified=nbr_negative_in_roi,
                               percentage_pixel_modified=percentage_in_roi,
                               total_pixels=total)
        return stat

    def display_images(self):

        _data = self.data
        _clean_data = self.clean_data
        _files = self.list_files
        _full_statistics = self.full_statistics

        [height, width] = np.shape(self.data[0])

        def _plot_images(index, x_left, y_top, width, height):

            _file_name = _files[index]
            fig, (ax0, ax1) = plt.subplots(ncols=2,
                                           figsize=(10, 5),
                                           num=os.path.basename(_file_name))
            _stat = _full_statistics[index]

            #plt.title(os.path.basename(_files[index]))
            cax0 = ax0.imshow(_data[index], cmap='viridis', interpolation=None)
            ax0.set_title("Before Correction")
            tmp1 = fig.colorbar(cax0, ax=ax0) # colorbar
            _rectangle1 = patches.Rectangle((x_left, y_top),
                                           width,
                                           height,
                                           edgecolor='white',
                                           linewidth=2,
                                           fill=False)
            ax1.add_patch(_rectangle1)

            cax1 = ax1.imshow(_clean_data[index], cmap='viridis', interpolation=None)
            ax1.set_title("After Correction")
            tmp2 = fig.colorbar(cax1, ax=ax1) # colorbar
            _rectangle2 = patches.Rectangle((x_left, y_top),
                                           width,
                                           height,
                                           edgecolor='white',
                                           linewidth=2,
                                            fill=False)
            ax0.add_patch(_rectangle2)

            fig.tight_layout()

            print("STATISTICS of FULL REGION")
            print("-> Number of pixels corrected: {}".format(_stat.nbr_pixel_modified))
            print("-> Total number of pixels: {}".format(_stat.total_pixels))
            print("-> Percentage of pixels corrected: {:.3}%".format(_stat.percentage_pixel_modified))
            print("")

            _stat_roi = self.get_statistics_of_roi_cleaned(x_left, y_top,
                                                       height,
                                                       width,
                                                       _data[index])

            print("STATISTICS of SELECTED REGION")
            print("-> Number of pixels corrected: {}".format(_stat_roi.nbr_pixel_modified))
            print("-> Total number of pixels: {}".format(_stat_roi.total_pixels))
            print("-> Percentage of pixels corrected: {:.3}%".format(_stat_roi.percentage_pixel_modified))

        tmp3 = widgets.interact(_plot_images,
                             index=widgets.IntSlider(min=0,
                                                     max=len(self.list_files) - 1,
                                                     step=1,
                                                     value=0,
                                                     description='File Index',
                                                     continuous_update=False),
                             x_left=widgets.IntSlider(min=0,
                                                      max=width - 1,
                                                      step=1,
                                                      value=0,
                                                      description='X Left',
                                                      continuous_update=False),
                             y_top=widgets.IntSlider(min=0,
                                                     max=height - 1,
                                                     value=0,
                                                     step=1,
                                                     description='Y Top',
                                                     continuous_update=False),
                             width=widgets.IntSlider(min=0,
                                                     max=width - 1,
                                                     step=1,
                                                     value=60,
                                                     description="Width",
                                                     continuous_update=False),
                             height=widgets.IntSlider(min=0,
                                                      max=height - 1,
                                                      step=1,
                                                      value=100,
                                                      description='Height',
                                                      continuous_update=False)
                             )

    def display_images_pretty(self):

        _data = self.data
        _clean_data = self.clean_data
        _files = self.list_files
        _full_statistics = self.full_statistics

        [height, width] = np.shape(self.data[0])

        def _plot_images(index):
            _file_name = _files[index]

            fig = plt.figure(figsize=(7,7))
            ax0 = plt.subplot(111)
            ax0.set_title(os.path.basename(_file_name))
            cax0 = ax0.imshow(_clean_data[index], cmap='viridis', interpolation=None)
            tmp2 = fig.colorbar(cax0, ax=ax0)  # colorbar
            fig.tight_layout()

        tmp3 = widgets.interact(_plot_images,
                                index=widgets.IntSlider(min=0,
                                                        max=len(self.list_files) - 1,
                                                        step=1,
                                                        value=0,
                                                        description='File Index',
                                                        continuous_update=False),
                                )


    def export(self):
        output_folder = os.path.abspath(self.list_output_folders_ui.selected)

        base_input_folder = os.path.basename(os.path.dirname(os.path.abspath(self.list_files[0])))
        new_folder_name = base_input_folder + '_cleaned'
        output_folder = os.path.join(output_folder, new_folder_name)
        make_folder(output_folder)

        for _index, _file in enumerate(self.list_files):
            _short_file_name = os.path.basename(_file)
            _full_output_file_name = os.path.join(output_folder, _short_file_name)

            _data = self.clean_data[_index]

            save_data(data=_data, filename=_full_output_file_name)

        display(HTML('<span style="font-size: 20px; color:blue">Files have been created in ' + output_folder + '</span>'))