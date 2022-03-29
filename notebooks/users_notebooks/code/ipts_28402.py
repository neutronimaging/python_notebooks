import sys
import glob
import os
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
import numpy as np

from ipywidgets import interactive
import ipywidgets as widgets
from IPython.core.display import display, HTML

import matplotlib.pyplot as plt

from NeuNorm.normalization import Normalization

from __code.file_folder_browser import FileFolderBrowser


class IPTS_28402:

    debugging = False
    data = None
    number_of_images = None

    default_crop = {'x0': 251, 'x1': 1749, 'y0': 1400, 'y1': 1650}
    crop = {'x0': None, 'x1': None, 'y0': None, 'y1': None}

    def __init__(self, working_dir="./", debugging=False):
        self.debugging = debugging

        if debugging:
            self.working_dir = "/Volumes/G-DRIVE/IPTS/IPTS-28402/Li/normalized_test"
        else:
            self.working_dir = working_dir

    def select_images(self):
        if self.debugging:
            list_of_images = glob.glob(os.path.join(self.working_dir, "*.tif*"))
            self.load_images(list_of_images=list_of_images)
        else:
            file_folder_browser = FileFolderBrowser(working_dir=self.working_dir,
                                                    next_function=self.load_images)
            file_folder_browser.select_images(filters={"TIFF": "*.tif?"})

    def load_images(self, list_of_images):
        self.number_of_images = len(list_of_images)

        o_norm = Normalization()
        o_norm.load(file=list_of_images,
                    notebook=True)
        data = o_norm.data['sample']['data']
        self.data = [np.rot90(_data) for _data in data]

        if self.data:
            [self.height, self.width] = np.shape(np.squeeze(self.data[0]))

        display(HTML('<span>Number of images loaded: ' + str(len(list_of_images)) + '</span>'))

    def visualize_raw_images(self):
        fig, ax1 = plt.subplots(num="Raw Images after 90degrees rotation")

        def plot(image_index):
            data = self.data[image_index]
            ax1.imshow(data, vmin=0, vmax=1)

        v = interactive(plot,
                        image_index=widgets.IntSlider(min=0,
                                                      max=len(self.data) - 1,
                                                      value=0,
                                                      layout=widgets.Layout(width='50%')))
        display(v)

    def select_crop_region(self):
        fig, ax1 = plt.subplots(num="Select Region to Crop")
        fig.set_figheight(6)
        fig.set_figwidth(6)

        width = self.width
        height = self.height

        def plot(image_index, left, right, top, bottom):
            ax1.cla()
            ax1.imshow(self.data[image_index], vmin=0, vmax=1)
            ax1.axis('off')
            ax1.axvline(x=left, color='green')
            ax1.axvline(x=right, color='green')
            ax1.axhline(y=top, color='blue')
            ax1.axhline(y=bottom, color='blue')

            return left, right, top, bottom

        self.crop_ui = interactive(plot,
                        image_index=widgets.IntSlider(min=0, max=self.number_of_images-1, value=0),
                        left=widgets.IntSlider(min=0, max=width, value=self.default_crop['x0']),
                        right=widgets.IntSlider(min=0, max=width, value=self.default_crop['x1']),
                        top=widgets.IntSlider(min=0, max=height, value=self.default_crop['y0']),
                        bottom=widgets.IntSlider(min=0, max=height, value=self.default_crop['y1']))
        display(self.crop_ui)

    def visualize_crop(self):
        [x0, x1, y0, y1] = self.crop_ui.result
        self.crop = {'x0': 0, 'x1': x1, 'y0':y0, 'y1': y1}

        cropped_data = [_data[y0: y1+1, x0: x1+1] for _data in self.data]
        self.cropped_data = cropped_data

        fig, ax1 = plt.subplots(num="Result of Cropping")

        def plot(image_index):
            data = cropped_data[image_index]
            ax1 = plt.imshow(data, vmin=0, vmax=1)
            plt.tight_layout()

        v = interactive(plot,
                        image_index=widgets.IntSlider(min=0, max=self.number_of_images - 1, value=0))
        display(v)

    def selection_of_profiles_limit(self):
        fig = plt.figure(4)
        # fig.set_figheight(6)
        # fig.set_figwidth(6)

        [height, _] = np.shape(self.cropped_data[0])

        def plot(image_index, top, bottom):
            ax1 = plt.subplots(ncols=1, nrows=1, num='Selection of profile region')

            ax1.imshow(self.cropped_data[image_index], vmin=0, vmax=1)
            ax1.axis('off')
            ax1.axhline(y=top, color='blue')
            ax1.axhline(y=bottom, color='blue')

            return top, bottom

        self.profile_limit_ui = interactive(plot,
                                        image_index=widgets.IntSlider(min=0, max=self.number_of_images-1, value=0),
                                        top=widgets.IntSlider(min=0, max=height-1, value=0),
                                        bottom=widgets.IntSlider(min=0, max=height-1, value=height-1))
        display(self.profile_limit_ui)
