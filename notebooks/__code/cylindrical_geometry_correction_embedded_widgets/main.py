import sys
import os
from pathlib import PurePosixPath
from scipy.ndimage import rotate
import pandas as pd

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
import matplotlib
matplotlib.rcParams['figure.figsize'] = (10, 10)

from NeuNorm.normalization import Normalization

from __code.file_folder_browser import FileFolderBrowser
from __code._utilities.file import make_ascii_file, make_or_increment_folder_name, make_tiff
from __code.cylindrical_geometry_correction_embedded_widgets.cylindrical_geometry_correction import \
    number_of_pixels_at_that_position1, number_of_pixel_at_that_position2


class CylindricalGeometryCorrectionEmbeddedWidgets:
    debugging = False
    data = None
    number_of_images = None

    config = None

    default_crop = {'x0': 369, 'x1': 522, 'y0': 756, 'y1': 1894}
    crop = {'x0': None, 'x1': None, 'y0': None, 'y1': None}

    # Profile, for each image loaded, of inner and outer cylinder with only outer cylinder corrected
    profile_with_outer_cylinder_removed = None

    # list of images full path names
    list_of_images = None

    def __init__(self, working_dir="./"):
        self.working_dir = working_dir

    def select_images(self):
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

    def select_config(self):
        config_browser = FileFolderBrowser(working_dir=os.path.dirname(self.working_dir),
                                           next_function=self.load_config)
        config_browser.select_images(instruction="Select config file ...",
                                     multiple_flag=False,
                                     filters={"config": "*.json"},
                                     default_filter="config")

    def load_config(self, config_filename):
        if config_filename:
            with open(config_filename, 'r') as f:
                self.config = json.load(f)

            display(HTML('<span>Config file ' + config_filename + 'loaded!</span>'))

    def visualize_raw_images(self):
        fig, ax1 = plt.subplots(num="Raw Images")
        fig.show()

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
        fig, ax = plt.subplots(ncols=1, nrows=2, num="Rotation of images")
        ax0, ax1 = ax

        default_rotate_angle = self.config["default_rotate_angle"]

        profile_margin = 100

        def plot(rot_value, image_index, vert_guide, profile1_h, profile2_h):

            ax0.cla()
            data = self.data[image_index]
            data = rotate(data, rot_value)
            ax0.imshow(data, vmin=0, vmax=1)
            ax0.axvline(x=vert_guide,
                        color='red',
                        linestyle="--")

            point1 = [vert_guide - profile_margin, profile1_h]
            point2 = [vert_guide + profile_margin, profile1_h]
            x_values = [point1[0], point2[0]]
            y_values = [point1[1], point2[1]]
            ax0.plot(x_values, y_values, linestyle="--", color='b')

            point3 = [vert_guide - profile_margin, profile2_h]
            point4 = [vert_guide + profile_margin, profile2_h]
            x_values = [point3[0], point4[0]]
            y_values = [point3[1], point4[1]]
            ax0.plot(x_values, y_values, linestyle="--", color='g')

            # ax0.axhline(y=profile1_h,
            #             xmin=vert_guide - profile_margin,
            #             xmax=vert_guide + profile_margin,
            #             color='b',
            #             linestyle="--")
            # ax0.axhline(y=profile2_h,
            #             xmin=vert_guide - profile_margin,
            #             xmax=vert_guide + profile_margin,
            #             color='g',
            #             linestyle="--")

            profile1 = data[profile1_h, vert_guide-profile_margin: vert_guide + profile_margin]
            profile2 = data[profile2_h, vert_guide-profile_margin: vert_guide + profile_margin]

            ax1.cla()
            ax1.plot(profile1, 'b', label='profile 1')
            ax1.plot(profile2, 'g', label='profile 2')
            plt.ylabel("Counts")
            plt.xlabel("Pixels")
            plt.title("horizontal profiles around vertical guide")
            plt.tight_layout()

        self.v = interactive(plot,
                        rot_value=widgets.FloatSlider(min=-5.,
                                                      max=5.,
                                                      value=default_rotate_angle,
                                                      layout=widgets.Layout(width='50%')),
                        image_index=widgets.IntSlider(min=0,
                                                      max=len(self.data) - 1,
                                                      value=0,
                                                      layout=widgets.Layout(width='50%')),
                        vert_guide=widgets.IntSlider(min=0,
                                                      max=self.width-1,
                                                      value=int(self.width/2),
                                                      layout=widgets.Layout(width="50%"),
                                                      continuous_update=False),
                        profile1_h=widgets.IntSlider(min=0,
                                                     max=self.height-1,
                                                     value=1135),
                        profile2_h=widgets.IntSlider(min=0,
                                                     max=self.height-1,
                                                     value=1794))

        display(self.v)

    def apply_rotation(self):
        rotation_value = self.v.children[0].value
        self.rotation_value = rotation_value
        self.data = [rotate(_data, rotation_value) for _data in self.data]

    def select_crop_region(self):
        fig, ax = plt.subplots(nrows=2, ncols=1, num="Select Region to Crop")
        ax0, ax1 = ax
        # fig.set_figheight(6)
        # fig.set_figwidth(6)

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

    def export_cropped_images(self):
        display(HTML(
            '<span style="font-size: 15px; color:blue">Select a folder if you want to export the cropped images!</span>'))
        working_dir = os.path.dirname(self.working_dir)
        self.file_selection_ui = FileFolderBrowser(working_dir=working_dir,
                                                   next_function=self.export_cropped_images_step2)
        self.file_selection_ui.select_output_folder()

    def export_cropped_images_step2(self, output_folder):
        output_folder = os.path.abspath(output_folder)
        working_dir = self.working_dir
        base_working_dir = os.path.join(output_folder, os.path.basename(working_dir) + "_cropped")
        base_working_dir = make_or_increment_folder_name(base_working_dir)

        list_images_corrected = self.cropped_data
        list_of_images = self.list_of_images

        nbr_images = len(list_of_images)
        progress_bar = widgets.IntProgress(min=0,
                                           max=nbr_images - 1)
        display(progress_bar)

        for index, image in enumerate(list_images_corrected):
            _name = os.path.basename(list_of_images[index])
            full_name = os.path.join(base_working_dir, _name)
            make_tiff(filename=full_name,
                      data=image)
            progress_bar.value = index + 1

        progress_bar.close()
        display(HTML('<span style="font-size: 12px; color:blue">' + str(nbr_images) + ' images created!</span>'))

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
        """
        apply the cylindrical geometry correction to the sample cropped, over the entire images
        """

        sample_without_background = self.sample_without_background
        width = np.shape(sample_without_background)[2]
        height = np.shape(sample_without_background)[1]

        radius = int(width/2.)

        list_images_corrected = np.zeros(np.shape(sample_without_background))

        # looping over all images
        for image_index, image in enumerate(sample_without_background):

            for h in np.arange(height):

                profile = image[h, :]

                number_of_pixels = []
                expected_array = []
                for x_index, x in enumerate(profile):
                    measure = x
                    number_of_pixels_through_thickness = number_of_pixels_at_that_position1(position=x_index,
                                                                                            radius=radius)
                    number_of_pixels.append(number_of_pixels_through_thickness)
                    expected_array.append(measure / number_of_pixels_through_thickness)

                list_images_corrected[image_index][h, :] = expected_array

        self.list_images_corrected = list_images_corrected

        fig, ax = plt.subplots(nrows=2, ncols=1, num="Sample and profiles corrected ")
        ax0, ax1 = ax

        def plot(image_index, index1, index2, plot_max):
            ax0.cla()
            ax0.imshow(self.list_images_corrected[image_index], vmin=0, vmax=0.01)
            ax0.axhline(y=index1, linestyle='--', color='r')
            ax0.axhline(y=index2, linestyle='--', color='b')

            ax1.cla()
            ax1.plot(self.list_images_corrected[image_index][index1, :], '.', color='r')
            ax1.plot(self.list_images_corrected[image_index][index2, :], '.', color='b')
            plt.ylim([0, plot_max])

        self.sample_corrected = interactive(plot,
                                            image_index=widgets.IntSlider(min=0,
                                                                          max=self.number_of_images - 1,
                                                                          value=0),
                                            index1=widgets.IntSlider(min=0,
                                                                            max=height-1,
                                                                            value=int((height-1)/3)),
                                            index2=widgets.IntSlider(min=0,
                                                                             max=height - 1,
                                                                             value=2*int((height-1)/3)),
                                            plot_max=widgets.FloatSlider(min=1e-5,
                                                                         max=1.,
                                                                         step=0.001,
                                                                         value=0.02))
        display(self.sample_corrected)

    def export_profiles(self):
        working_dir = os.path.dirname(self.working_dir)
        output_folder_browser = FileFolderBrowser(working_dir=working_dir,
                                                  next_function=self.export)
        output_folder_browser.select_output_folder()

    def export(self, output_folder):

        output_folder = os.path.abspath(output_folder)
        working_dir = self.working_dir
        base_working_dir = os.path.join(output_folder, os.path.basename(working_dir) + "_cylindrical_geo_corrected")
        base_working_dir = make_or_increment_folder_name(base_working_dir)

        # export images
        list_images_corrected = self.list_images_corrected
        list_of_images = self.list_of_images

        nbr_images = len(list_of_images)
        progress_bar = widgets.IntProgress(min=0,
                                           max=nbr_images-1)
        display(progress_bar)

        for index, image in enumerate(list_images_corrected):
            _name = os.path.basename(list_of_images[index])
            full_name = os.path.join(base_working_dir, _name)
            make_tiff(filename=full_name,
                      data=image)
            progress_bar.value = index + 1

        progress_bar.close()
        display(HTML('<span style="font-size: 12px; color:blue">' + str(nbr_images) + ' images created!</span>'))

        # export profiles

        progress_bar = widgets.IntProgress(min=0,
                                           max=nbr_images-1)
        display(progress_bar)

        metadata = {}
        metadata['rotation value (degrees)'] = self.rotation_value
        x0 = self.crop['x0']
        x1 = self.crop['x1']
        y0 = self.crop['y0']
        y1 = self.crop['y1']

        metadata['crop'] = {'crop': {'x0': x0,
                                     'y0': y0,
                                     'x1': x1,
                                     'y1': y1
                                     },
                            }
        metadata['input folder'] = working_dir
        metadata['output folder'] = base_working_dir

        for index, image in enumerate(list_images_corrected):

            _name = os.path.basename(list_of_images[index])
            base_name_without_suffix = PurePosixPath(_name).stem
            base_name_of_ascii_file = str(base_name_without_suffix) + "_profile_corrected.csv"
            full_name_of_ascii_file = os.path.join(base_working_dir, base_name_of_ascii_file)

            df = pd.DataFrame(image)
            df.to_csv(full_name_of_ascii_file)

            progress_bar.value = index + 1

        progress_bar.close()

        config_filename = os.path.join(output_folder, "config.json")
        self.export_config(output_folder=base_working_dir, config_filename=config_filename)

        display(HTML('<span style="font-size: 12px; color:blue">' + str(nbr_images) + ' ASCII files created!</span>'))

        json_file_name = os.path.join(base_working_dir, 'metadata.json')
        with open(json_file_name, 'w') as outfile:
            json.dump(metadata, outfile)
        display(HTML('<span style="font-size: 12px; color:blue"> metadata json file created (metadata.json)!</span>'))
        display(HTML('<span style="font-size: 12px; color:blue"> config file: ' + config_filename + '</span>'))

        display(HTML('<span style="font-size: 12px; color:blue"> Output folder: ' + base_working_dir + '!</span>'))

    def export_config(self, output_folder=None, config_filename=None):
        with open(config_filename, 'w') as outfile:
            outfile.write(self.config)
