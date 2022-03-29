import sys
import glob
import os

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
import numpy as np
import json

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

        # load config
        with open("./config.json") as f:
            self.config = json.load(f)

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
                                   image_index=widgets.IntSlider(min=0, max=self.number_of_images - 1, value=0),
                                   left=widgets.IntSlider(min=0, max=width, value=self.config["default_crop"]['x0']),
                                   right=widgets.IntSlider(min=0, max=width, value=self.config["default_crop"]['x1']),
                                   top=widgets.IntSlider(min=0, max=height, value=self.config["default_crop"]['y0']),
                                   bottom=widgets.IntSlider(min=0, max=height, value=self.config["default_crop"]['y1']))
        display(self.crop_ui)

    def visualize_crop(self):
        [x0, x1, y0, y1] = self.crop_ui.result
        self.crop = {'x0': 0, 'x1': x1, 'y0': y0, 'y1': y1}

        cropped_data = [_data[y0: y1 + 1, x0: x1 + 1] for _data in self.data]
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
        fig, ax1 = plt.subplots(num="Select top and bottom profile limits")
        [height, _] = np.shape(self.cropped_data[0])

        def plot(image_index, top, bottom):
            ax1.cla()
            ax1.imshow(self.cropped_data[image_index], vmin=0, vmax=1)
            ax1.axis('off')
            ax1.axhline(y=top, color='blue')
            ax1.axhline(y=bottom, color='blue')

            return top, bottom

        default_top = self.config["profiles_limit"]["top"]
        default_bottom = self.config["profiles_limit"]["bottom"]

        self.profile_limit_ui = interactive(plot,
                                            image_index=widgets.IntSlider(min=0, max=self.number_of_images - 1,
                                                                          value=0),
                                            top=widgets.IntSlider(min=0, max=height - 1, value=default_top),
                                            bottom=widgets.IntSlider(min=0, max=height - 1, value=default_bottom))
        display(self.profile_limit_ui)

    def extraction_of_profiles(self):
        [top_profile, bottom_profile] = self.profile_limit_ui.result
        self.config["profiles_limit"] = {'top'   : top_profile,
                                         'bottom': bottom_profile}

        profiles = []
        for _data in self.cropped_data:
            _data_profile_range = _data[top_profile: bottom_profile + 1, :]
            _data_profile_range = _data_profile_range.mean(axis=0)
            profiles.append(_data_profile_range)

        self.profiles = profiles

    def display_of_profiles(self):
        self.extraction_of_profiles()

        fig, ax1 = plt.subplots(num="Display of Profiles")

        def plot(image_index):
            ax1.cla()
            data = self.profiles[image_index]
            ax1.plot(data, '.')
            plt.tight_layout()

        v = interactive(plot,
                        image_index=widgets.IntSlider(min=0, max=self.number_of_images - 1, value=0))
        display(v)

    def cylinders_positions(self):
        fig = plt.figure(6)
        fig.set_figheight(8)
        fig.set_figwidth(8)

        [_, width] = np.shape(self.cropped_data[0])

        default_top = self.config["profiles_limit"]["top"]
        default_bottom = self.config["profiles_limit"]["bottom"]

        def plot(image_index, center, inner_radius, outer_radius):
            ax1 = plt.subplot2grid(shape=(6, 1), loc=(0, 0), colspan=1, rowspan=1)
            ax2 = plt.subplot2grid(shape=(6, 1), loc=(1, 0), colspan=1, rowspan=5)

            # top plot
            data = self.cropped_data[image_index][default_top: default_bottom + 1, :]
            ax1.imshow(data, vmin=0, vmax=1)
            ax1.axis('off')

            inner_left = center - inner_radius
            inner_right = center + inner_radius
            ax1.axvline(x=inner_left, color='green')
            ax1.axvline(x=inner_right, color='green')

            ax1.axvline(x=center, color='red', linestyle='--')

            outer_left = center - outer_radius
            outer_right = center + outer_radius
            ax1.axvline(x=outer_left, color='blue')
            ax1.axvline(x=outer_right, color='blue')

            # bottom plot
            ax2.plot(self.profiles[image_index])
            ax2.set_xlim([0, width])

            ax2.axvline(x=inner_left, color='green')
            ax2.axvline(x=inner_right, color='green')

            ax2.axvline(x=center, color='red', linestyle='--')

            ax2.axvline(x=outer_left, color='blue')
            ax2.axvline(x=outer_right, color='blue')

            # for reference, plotting the y-axis 1
            ax2.axhline(y=1, color="black")

            return center, inner_radius, outer_radius

        default_inner_radius = self.config["cylinders_position"]["inner_radius"]
        default_outer_radius = self.config["cylinders_position"]["outer_radius"]
        default_center = self.config["cylinders_position"]["center"]

        self.cylinders_positions_ui = interactive(plot,
                                                  image_index=widgets.IntSlider(min=0, max=self.number_of_images - 1,
                                                                                value=0),
                                                  center=widgets.IntSlider(min=0,
                                                                           max=width,
                                                                           value=default_center),
                                                  inner_radius=widgets.IntSlider(min=0,
                                                                                 max=width,
                                                                                 value=default_inner_radius),
                                                  outer_radius=widgets.IntSlider(min=0,
                                                                                 max=width,
                                                                                 value=default_outer_radius),
                                                  )
        display(self.cylinders_positions_ui)

    def cleaning_edges(self):
        pass
