import ipywe.fileselector
from NeuNorm.normalization import Normalization

from IPython.core.display import HTML
from IPython.core.display import display

from ipywidgets.widgets import interact
from ipywidgets import widgets

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


class ProfileVsFileIndex(object):

    o_load = None
    folder_ui = None

    list_data_files = [] # filename
    list_data = [] # data

    def __init__(self, working_dir='./'):
        self.working_dir = working_dir


    def select_images(self):
        self.folder_ui = ipywe.fileselector.FileSelectorPanel(instruction = 'Select Input Images ...',
                                                              start_dir = self.working_dir,
                                                              multiple = True)

        self.folder_ui.show()

    def load_images(self):

        try:
            self.list_data_files = self.folder_ui.selected
        except:
            display(HTML('<span style="font-size: 20px; color:red">Please Select a set of Images First!</span>'))
            return

        self.o_load = Normalization()
        self.o_load.load(file = self.list_data_files, notebook = True)

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

            fig_box = plt.figure(figsize=(5, 5))
            ax_img = plt.subplot(111)

            ax_img.imshow(self.integrated_data, cmap='rainbow',
                          interpolation=None)
            #                   vmin = min_intensity,
            #                   vmax = max_intensity)

            ax_img.add_patch(patches.Rectangle((x_left, y_top), width, height, fill=False))

            return [x_left, y_top, width, height]

        self.profile = interact(plot_images_with_roi,
                           x_left=widgets.IntSlider(min = 0,
                                                    max = self.width - 1,
                                                    step = 1,
                                                    value = roi_left,
                                                    continuous_update = False),
                           y_top=widgets.IntSlider(min = 0,
                                                   max = self.height - 1,
                                                   step = 1,
                                                   value = roi_top,
                                                   continuous_update = False),
                           width=widgets.IntSlider(min = 0,
                                                   max = self.width - 1,
                                                   step = 1,
                                                   value = roi_width,
                                                   continuous_update = False),
                           height=widgets.IntSlider(min = 0,
                                                    max = self.height - 1,
                                                    step = 1,
                                                    value = roi_height,
                                                    continuous_update = False))

