import sys
import glob
import os
from pathlib import PurePosixPath
from scipy.ndimage import rotate

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
import numpy as np
import json

from plotly.offline import plot, init_notebook_mode, iplot
import plotly.express as px
import plotly.graph_objects as go
import socket

from ipywidgets import interactive
import ipywidgets as widgets
from IPython.core.display import display, HTML

import matplotlib.pyplot as plt

from NeuNorm.normalization import Normalization

from __code.file_folder_browser import FileFolderBrowser
from __code._utilities.folder import make_folder
from __code._utilities.file import make_ascii_file
from .cylindrical_geometry_correction import number_of_pixels_at_that_position1, number_of_pixel_at_that_position2

if socket.gethostname() == 'mac113775': #home machine
    CONFIG_FILE_NAME = "./ipts_27939_code/config_home.json"
else:
    CONFIG_FILE_NAME = "./ipts_27939_code/config_work.json"


class IPTS_27939:
    debugging = False
    data = None
    number_of_images = None

    default_crop = {'x0': 369, 'x1': 522, 'y0': 756, 'y1': 1894}
    crop = {'x0': None, 'x1': None, 'y0': None, 'y1': None}

    # Profile, for each image loaded, of inner and outer cylinder with only outer cylinder corrected
    profile_with_outer_cylinder_removed = None

    # list of images full path names
    list_of_images = None

    def __init__(self, working_dir="./", debugging=False):
        self.debugging = debugging

        if debugging:
            self.working_dir = "/Volumes/G-DRIVE/IPTS/IPTS-28402/Li/normalized_test"
        else:
            self.working_dir = working_dir

        # load config
        with open(CONFIG_FILE_NAME) as f:
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
        self.list_of_images = list_of_images
        if self.number_of_images == 0:
            display(HTML('<span>0 images found!</span>'))
            return

        self.working_dir = os.path.dirname(list_of_images[0])

        o_norm = Normalization()
        o_norm.load(file=list_of_images,
                    notebook=True)
        self.data = o_norm.data['sample']['data']
        # self.data = [np.rot90(_data) for _data in data]

        if self.data:
            [self.height, self.width] = np.shape(np.squeeze(self.data[0]))

        display(HTML('<span>Number of images loaded: ' + str(len(list_of_images)) + '</span>'))

    def visualize_raw_images(self):
        fig, ax1 = plt.subplots(num="Raw Images")

        def plot(image_index):
            data = self.data[image_index]
            ax1.imshow(data, vmin=0, vmax=1)

        v = interactive(plot,
                        image_index=widgets.IntSlider(min=0,
                                                      max=len(self.data) - 1,
                                                      value=0,
                                                      layout=widgets.Layout(width='50%')))
        display(v)

    def rotate_images(self):
        fig, ax1 = plt.subplots(num="Rotation of images")

        default_rotate_angle = self.config["default_rotate_angle"]

        def plot(rot_value, image_index, vert_marker):
            ax1.cla()
            data = self.data[image_index]
            data = rotate(data, rot_value)
            ax1.imshow(data, vmin=0, vmax=1)
            ax1.axvline(x=vert_marker,
                        color='red',
                        linestyle="--")

        self.v = interactive(plot,
                        rot_value=widgets.FloatSlider(min=-5.,
                                                      max=5.,
                                                      value=default_rotate_angle,
                                                      layout=widgets.Layout(width='50%')),
                        image_index=widgets.IntSlider(min=0,
                                                      max=len(self.data) - 1,
                                                      value=0,
                                                      layout=widgets.Layout(width='50%')),
                        vert_marker=widgets.IntSlider(min=0,
                                                      max=self.width-1,
                                                      value=int(self.width/2),
                                                      layout=widgets.Layout(width="50%"),
                                                      continuous_update=False))

        display(self.v)

    def apply_rotation(self):
        rotation_value = self.v.children[0].value
        self.data = [rotate(_data, rotation_value) for _data in self.data]

    def select_crop_region(self):
        fig, ax = plt.subplots(nrows=2, ncols=1, num="Select Region to Crop")
        ax0, ax1 = ax
        fig.set_figheight(6)
        fig.set_figwidth(6)

        width = self.width
        height = self.height

        def plot(image_index, left, right, top, bottom, profile_mker):
            ax0.cla()
            ax0.imshow(self.data[image_index], vmin=0, vmax=1)
            ax0.axis('off')
            ax0.axvline(x=left, color='red', linestyle='--')
            ax0.axvline(x=right, color='red', linestyle='--')
            ax0.axhline(y=top, color='red', linestyle='-.')
            ax0.axhline(y=bottom, color='red', linestyle='-.')
            ax0.axhline(y=profile_mker, color='blue', linestyle='dotted')

            ax1.cla()
            profile = self.data[image_index][profile_mker, :]
            ax1.plot(profile, '.')
            delta_x = (right - left)
            if delta_x < 0:
                delta_x = 0
            left_x_profile = (left - delta_x) if (left - delta_x) > 0 else 0
            plt.xlim([left_x_profile, right + delta_x])
            plt.xlabel("Horizontal pixel")
            plt.ylabel("Counts")
            plt.title("Profile at marker's position (dotted blue line)")
            ax1.axvline(x=left, linestyle='--', color='red')
            ax1.axvline(x=right, linestyle='--', color='red')

            return left, right, top, bottom

        self.crop_ui = interactive(plot,
                                   image_index=widgets.IntSlider(min=0,
                                                                 max=self.number_of_images - 1,
                                                                 value=0),
                                   left=widgets.IntSlider(min=0,
                                                          max=width-1,
                                                          value=self.config["default_crop"]['x0']),
                                   right=widgets.IntSlider(min=0,
                                                           max=width-1,
                                                           value=self.config["default_crop"]['x1']),
                                   top=widgets.IntSlider(min=0,
                                                         max=height-1,
                                                         value=self.config["default_crop"]['y0']),
                                   bottom=widgets.IntSlider(min=0,
                                                            max=height-1,
                                                            value=self.config["default_crop"]['y1']),
                                   profile_mker=widgets.IntSlider(min=0,
                                                                       max=height-1,
                                                                       value=self.config['default_crop'][
                                                                                      'marker'])
                                   )
        display(self.crop_ui)

    def visualize_crop(self):
        [x0, x1, y0, y1] = self.crop_ui.result
        self.crop = {'x0': 0, 'x1': x1, 'y0': y0, 'y1': y1}

        cropped_data = [_data[y0: y1 + 1, x0: x1 + 1] for _data in self.data]
        self.cropped_data = cropped_data

        fig, ax1 = plt.subplots(num="Result of Cropping")

        def plot(image_index):
            data = cropped_data[image_index]
            ax1.imshow(data, vmin=0, vmax=1)
            # plt.tight_layout()

        v = interactive(plot,
                        image_index=widgets.IntSlider(min=0, max=self.number_of_images - 1, value=0))
        display(v)

    def background_range_selection(self):
        fig, ax1 = plt.subplots(num="Select top and bottom of background range")
        [height, _] = np.shape(self.cropped_data[0])

        def plot(image_index, top, bottom):
            ax1.cla()
            ax1.imshow(self.cropped_data[image_index], vmin=0, vmax=1)
            # ax1.axis('off')
            ax1.axhline(y=top, color='red')
            ax1.axhline(y=bottom, color='red')
            return top, bottom

        default_top = self.config["default_background"]["y0"]
        default_bottom = self.config["default_background"]["y1"]

        self.background_limit_ui = interactive(plot,
                                            image_index=widgets.IntSlider(min=0, max=self.number_of_images - 1,
                                                                          value=0),
                                            top=widgets.IntSlider(min=0, max=height - 1, value=default_top),
                                            bottom=widgets.IntSlider(min=0, max=height - 1, value=default_bottom))
        display(self.background_limit_ui)

    def sample_region_selection(self):
        fig, ax1 = plt.subplots(num="Select top and bottom of sample range")
        [height, _] = np.shape(self.cropped_data[0])

        def plot(image_index, top, bottom):
            ax1.cla()
            ax1.imshow(self.cropped_data[image_index], vmin=0, vmax=1)
            # ax1.axis('off')
            ax1.axhline(y=top, color='red')
            ax1.axhline(y=bottom, color='red')

            return top, bottom

        default_top = self.config["default_sample"]["y0"]
        default_bottom = self.config["default_sample"]["y1"]

        self.sample_limit_ui = interactive(plot,
                                            image_index=widgets.IntSlider(min=0, max=self.number_of_images - 1,
                                                                          value=0),
                                            top=widgets.IntSlider(min=0, max=height - 1, value=default_top),
                                            bottom=widgets.IntSlider(min=0, max=height - 1, value=default_bottom))
        display(self.sample_limit_ui)

    def remove_background_signal(self):
        """
        this is where the vertical integrated signal from the background selected is removed from the signal
        range selected
        """
        y0_background = self.background_limit_ui.children[1].value
        y1_background = self.background_limit_ui.children[2].value
        background_signal_integrated = [np.mean(_data[y0_background: y1_background+1, :], axis=0) for _data in self.cropped_data]

        y0_sample = self.sample_limit_ui.children[1].value
        y1_sample = self.sample_limit_ui.children[2].value
        sample_without_background = []
        for _background, _sample in zip(background_signal_integrated, self.cropped_data):
            _data = _sample[y0_sample: y1_sample+1]
            sample_without_background.append(np.abs((_data - _background)))

        self.sample_without_background = sample_without_background

        fig, ax1 = plt.subplots(num="Sample without background")

        def plot(image_index):
            ax1.cla()
            ax1.imshow(self.sample_without_background[image_index], vmin=0, vmax=1)

        self.sample_no_background_ui = interactive(plot,
                                            image_index=widgets.IntSlider(min=0, max=self.number_of_images - 1,
                                                                          value=0))
        display(self.sample_no_background_ui)

    def display_of_profiles(self):

        sample_without_background = self.sample_without_background

        fig, ax = plt.subplots(nrows=1, ncols=2, num="Display of Profiles")

        height, width = np.shape(sample_without_background[0])

        def plot(image_index, profile_height):
            ax[0].cla()
            image = sample_without_background[image_index]
            ax[0].imshow(image)
            ax[0].axhline(y=profile_height, color='red')

            ax[1].cla()
            data = sample_without_background[image_index]
            profile = data[profile_height, :]
            ax[1].plot(profile, '.')

        v = interactive(plot,
                        image_index=widgets.IntSlider(min=0, max=self.number_of_images - 1, value=0),
                        profile_height=widgets.IntSlider(min=0, max=height-1, value=0))
        display(v)

    def correct_cylinder_geometry(self):

        sample_without_background = self.sample_without_background
        width = np.shape(sample_without_background)[2]

        radius = int(width/2.)

        list_expected_array = []

        # looping over all images
        for list_profiles in sample_without_background:

            # looping from top to bottom through profiles
            for profile in list_profiles:

                number_of_pixels = []
                expected_array = []
                for _index, x in enumerate(profile):
                    measure = x[_index]
                    number_of_pixels_through_thickness = number_of_pixels_at_that_position1(position=x,
                                                                                            radius=radius)
                    number_of_pixels.append(number_of_pixels_through_thickness)
                    expected_array.append(measure / number_of_pixels_through_thickness)

                list_expected_array.append(expected_array)

            self.list_expected_array = list_expected_array




        def plot_final_inner(image_index):
            trace = go.Scatter(y=list_expected_array[image_index], mode='markers')
            layout = go.Layout(title=f"Expected Array of image #{image_index}",
                               xaxis=dict(title="pixel"),
                               yaxis=dict(title="Counts per pixel",
                                          range=[0, .0015],
                                          ))

            figure = go.Figure(data=[trace], layout=layout)
            iplot(figure)

        self.plot_final_inner_ui = interactive(plot_final_inner,
                                               image_index=widgets.IntSlider(min=0,
                                                                             max=self.number_of_images - 1,
                                                                             value=0),
                                               )
        display(self.plot_final_inner_ui)

    def export_profiles(self):
        working_dir = self.working_dir
        output_folder_browser = FileFolderBrowser(working_dir=working_dir,
                                                  next_function=self.export)
        output_folder_browser.select_output_folder()

    def export(self, output_folder):

        output_folder = os.path.abspath(output_folder)
        make_folder(output_folder)

        list_expected_array = self.list_expected_array
        list_images = self.list_of_images

        pixel_index = np.arange(len(list_expected_array[0]))
        list_of_ascii_file_created = []
        for _index, _image in enumerate(list_images):

            array_for_this_image = list_expected_array[_index]

            base_name = os.path.basename(_image)
            base_name_without_suffix = PurePosixPath(base_name).stem
            base_name_of_ascii_file = str(base_name_without_suffix) + "_profile_corrected.csv"
            full_name_of_ascii_file = os.path.join(output_folder, base_name_of_ascii_file)
            list_of_ascii_file_created.append(full_name_of_ascii_file)

            metadata = [f"# input working file: {_image}"]

            x0 = self.crop['x0']
            x1 = self.crop['x1']
            y0 = self.crop['y0']
            y1 = self.crop['y1']
            metadata.append(f"# crop: x0={x0}, x1={x1}, y0={y0}, y1={y1}")

            top_profile = self.config["profiles_limit"]["top"]
            bottom_profile = self.config["profiles_limit"]["bottom"]
            metadata.append(f"# profile range (those horizontal profiles will be combined via mean): top_profile="
                            f"{top_profile}, bottom_profile={bottom_profile}")

            center = self.config["cylinders_position"]["center"]
            inner_radius = self.config["cylinders_position"]["inner_radius"]
            outer_radius = self.config["cylinders_position"]["outer_radius"]
            metadata.append(f"# cylinders center: {center}")
            metadata.append(f"# inner_radius (pixels): {inner_radius}")
            metadata.append(f"# outer_radius (pixels): {outer_radius}")

            metadata.append("#")

            metadata.append("# pixel, counts per pixels")

            data_array = [f"{x}, {y}" for (x, y) in zip(pixel_index, array_for_this_image)]

            make_ascii_file(metadata=metadata,
                            data=data_array,
                            output_file_name=full_name_of_ascii_file,
                            dim="1d")

        display(HTML('<span style="font-size: 20px; color:blue">The following ASCII (csv) files have been '
                     'created: </span>'))
        for _ascii_file in list_of_ascii_file_created:
            display(HTML('<span style="font-size: 20px; color:blue"> - ' + _ascii_file + '</span>'))