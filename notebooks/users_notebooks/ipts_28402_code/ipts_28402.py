import sys
import glob
import os
from pathlib import PurePosixPath

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
import numpy as np
import json

from plotly.offline import plot, init_notebook_mode, iplot
import plotly.express as px
import plotly.graph_objects as go

from ipywidgets import interactive
import ipywidgets as widgets
from IPython.core.display import display, HTML

import matplotlib.pyplot as plt

from NeuNorm.normalization import Normalization

from __code.file_folder_browser import FileFolderBrowser
from __code._utilities.folder import make_folder
from __code._utilities.file import make_ascii_file
from .cylindrical_geometry_correction import number_of_pixels_at_that_position1, number_of_pixel_at_that_position2


class IPTS_28402:
    debugging = False
    data = None
    number_of_images = None

    default_crop = {'x0': 251, 'x1': 1749, 'y0': 1400, 'y1': 1650}
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
        with open("./ipts_28402_code/config_work.json") as f:
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
        fig2 = plt.figure(6)
        fig2.set_figheight(8)
        fig2.set_figwidth(8)

        [_, width] = np.shape(self.cropped_data[0])

        default_top = self.config["profiles_limit"]["top"]
        default_bottom = self.config["profiles_limit"]["bottom"]

        def plot(image_index, center, inner_radius, outer_radius):
            ax21 = plt.subplot2grid(shape=(6, 1), loc=(0, 0), colspan=1, rowspan=1)
            ax22 = plt.subplot2grid(shape=(6, 1), loc=(1, 0), colspan=1, rowspan=5)

            # top plot
            data = self.cropped_data[image_index][default_top: default_bottom + 1, :]
            ax21.imshow(data, vmin=0, vmax=1)
            ax21.axis('off')

            inner_left = center - inner_radius
            inner_right = center + inner_radius
            ax21.axvline(x=inner_left, color='green')
            ax21.axvline(x=inner_right, color='green')

            ax21.axvline(x=center, color='red', linestyle='--')

            outer_left = center - outer_radius
            outer_right = center + outer_radius
            ax21.axvline(x=outer_left, color='blue')
            ax21.axvline(x=outer_right, color='blue')

            # bottom plot
            ax22.plot(self.profiles[image_index])
            ax22.set_xlim([0, width])

            ax22.axvline(x=inner_left, color='green')
            ax22.axvline(x=inner_right, color='green')

            ax22.axvline(x=center, color='red', linestyle='--')

            ax22.axvline(x=outer_left, color='blue')
            ax22.axvline(x=outer_right, color='blue')

            # for reference, plotting the y-axis 1
            ax22.axhline(y=1, color="black")

            self.config["cylinders_position"] = {"center"      : center,
                                                 "inner_radius": inner_radius,
                                                 "outer_radius": outer_radius}

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
        [center, _, outer_radius] = self.cylinders_positions_ui.result

        left_outer = center - outer_radius
        right_outer = center + outer_radius + 1

        # calculate left and right inner cylinder positions
        inner_radius = self.config["cylinders_position"]["inner_radius"]
        left_inner_edge = center - inner_radius - left_outer
        right_inner_edge = center + inner_radius - left_outer
        self.config["profiles_plot"]["left_inner_cylinder"] = left_inner_edge
        self.config["profiles_plot"]["right_inner_cylinder"] = right_inner_edge

        profiles_cleaned = [_profile[left_outer: right_outer] for _profile in self.profiles]
        self.profiles_cleaned = profiles_cleaned

        fig, ax1 = plt.subplots(num="Outer and Inner cylinders profiles")

        def plot_profiles_cleaned(image_index):
            ax1.cla()
            plt.plot(profiles_cleaned[image_index], '.b')
            plt.axhline(y=1, color='green')

        plot_cleaning_edges_ui = interactive(plot_profiles_cleaned,
                                             image_index=widgets.IntSlider(min=0, max=self.number_of_images - 1,
                                                                           value=0))
        display(plot_cleaning_edges_ui)

    def switching_to_attenuation_mode(self):
        threshold_value = 1
        profiles_attenuation_mode = [(threshold_value - _profile) for _profile in self.profiles_cleaned]
        self.profiles_attenuation_mode = profiles_attenuation_mode

        fig_attenuation, ax_attenuation = plt.subplots(num="Profiles in attenuation mode")

        def plot_profiles_attenuation(image_index):
            ax_attenuation.cla()
            plt.plot(profiles_attenuation_mode[image_index], '.b')
            plt.axhline(y=1, color='green')

        plot_attenuation_ui = interactive(plot_profiles_attenuation,
                                          image_index=widgets.IntSlider(min=0, max=self.number_of_images - 1,
                                                                        value=0))
        display(plot_attenuation_ui)

    def outer_cylinder_geometry_correction(self, sampling_nbr_of_points=3):
        profiles_attenuation_mode = self.profiles_attenuation_mode
        nbr_pixel = len(profiles_attenuation_mode[0])
        pixel_index = np.arange(0, nbr_pixel)
        inner_radius = self.config["cylinders_position"]["inner_radius"]
        outer_radius = self.config["cylinders_position"]["outer_radius"]
        center = int(nbr_pixel / 2)

        # left_inner_cylinder = self.config["profiles_plot"]["left_inner_cylinder"]
        # nbr_point_to_use = sampling_nbr_of_points
        # delta = int(left_inner_cylinder / (nbr_point_to_use+1))
        #
        # # we gonna use 3 different points on each side of the outer cylinder to figure out the intensity
        # # per pixel
        #
        # left_positions_to_test = (np.arange(nbr_point_to_use)+1) * delta
        # right_positions_to_test = left_positions_to_test + 2 * inner_radius
        #
        # list_intensity_of_ring = []
        # for _profile in profiles_attenuation_mode:
        #     list_intensity = []
        #     for _value_to_test in left_positions_to_test:
        #         measure = _profile[_value_to_test]
        #         number_of_pixels_through_thickness = number_of_pixels_at_that_position1(position=_value_to_test,
        #                                                                                 radius=outer_radius)
        #         intensity_of_ring = measure / number_of_pixels_through_thickness
        #         list_intensity.append(intensity_of_ring)
        #
        #     for _value_to_test in right_positions_to_test:
        #         measure = _profile[_value_to_test]
        #         number_of_pixels_through_thickness = number_of_pixels_at_that_position1(position=_value_to_test,
        #                                                                                 radius=outer_radius)
        #         intensity_of_ring = measure / number_of_pixels_through_thickness
        #         list_intensity.append(intensity_of_ring)
        #
        #     intensity_of_ring = np.median(list_intensity)
        #     list_intensity_of_ring.append(intensity_of_ring)
        #
        # fig1, ax1 = plt.subplots(num="Outer cylinder pixel intensity")
        # fig1.set_figwidth(10)
        # plt.plot(list_intensity_of_ring, '.b')
        # ax1.set_xlabel("Image index")
        # ax1.set_ylabel("Counts per pixel in outer cylinder")
        # mean_list_intensity = np.mean(list_intensity_of_ring)
        # median_list_intensity = np.median(list_intensity_of_ring)
        # plt.axhline(y=mean_list_intensity, linestyle='--', color='green', label='Mean')
        # plt.axhline(y=median_list_intensity, linestyle='-', color='black', label='Median')
        #
        # ax1.legend()

        # Attenuation per pixel of outer ring
        intensity_of_left_ring_array_for_all_images = []
        x_axis_of_left_ring_array = np.arange(center - inner_radius)

        intensity_of_right_ring_array_for_all_images = []
        x_axis_of_right_ring_array = np.arange(center + inner_radius, nbr_pixel)

        median_intensity_for_all_images = []

        for _profile in profiles_attenuation_mode:

            intensity_of_ring_array = []

            intensity_of_left_ring_array = []
            for x in x_axis_of_left_ring_array:
                measure = _profile[x]
                number_of_pixels_through_thickness = number_of_pixels_at_that_position1(position=x,
                                                                                        radius=outer_radius)
                value = measure / number_of_pixels_through_thickness
                intensity_of_left_ring_array.append(value)
                intensity_of_ring_array.append(value)

            intensity_of_left_ring_array_for_all_images.append(intensity_of_left_ring_array)

            intensity_of_right_ring_array = []
            for x in x_axis_of_right_ring_array:
                measure = _profile[x]
                number_of_pixels_through_thickness = number_of_pixels_at_that_position1(position=x,
                                                                                        radius=outer_radius)
                value = measure / number_of_pixels_through_thickness
                intensity_of_right_ring_array.append(value)
                intensity_of_ring_array.append(value)

            intensity_of_right_ring_array_for_all_images.append(intensity_of_right_ring_array)

            median_intensity_for_all_images.append(np.median(intensity_of_ring_array))

        self.median_intensity_for_all_images = median_intensity_for_all_images

        fig_outer, ax_outer = plt.subplots(num="Outer cylinder corrected")
        fig_outer.set_figwidth(10)

        def plot_profiles_with_outer_cylinder_corrected(image_index):
            ax_outer.cla()
            plt.plot(x_axis_of_left_ring_array, intensity_of_left_ring_array_for_all_images[image_index], '.r')
            plt.plot(x_axis_of_right_ring_array, intensity_of_right_ring_array, '.r')

        plot_profile_outer_ui = interactive(plot_profiles_with_outer_cylinder_corrected,
                                            image_index=widgets.IntSlider(min=0, max=self.number_of_images - 1,
                                                                          value=0))
        display(plot_profile_outer_ui)

    def full_profile_with_only_outer_cylinder_corrected(self):
        outer_radius = self.config["cylinders_position"]["outer_radius"]
        inner_radius = self.config["cylinders_position"]["inner_radius"]
        profiles_attenuation_mode = self.profiles_attenuation_mode

        shape_of_ring_signal_for_all_images = []
        median_intensity_for_all_images = self.median_intensity_for_all_images

        new_profile_with_outer_cylinder_removed = []

        for _profile_index, _profile in enumerate(profiles_attenuation_mode):

            shape_of_ring_signal = []
            for x in np.arange(0, outer_radius + 1):
                nbr_pixels = number_of_pixel_at_that_position2(position=x,
                                                               inner_circle_r=inner_radius,
                                                               outer_circle_r=outer_radius)

                shape_of_ring_signal.append(nbr_pixels * median_intensity_for_all_images[_profile_index])

            full_shape_of_ring_signal = np.concatenate((shape_of_ring_signal[::-1], shape_of_ring_signal[:-1:]))
            shape_of_ring_signal_for_all_images.append(full_shape_of_ring_signal)

            # new profile with outer cylinder removed
            new_profile_with_outer_cylinder_removed.append(_profile - full_shape_of_ring_signal)

        self.profile_with_outer_cylinder_removed = new_profile_with_outer_cylinder_removed

        def plot_shape_ring_signal(image_index):

            trace = go.Scatter(y=shape_of_ring_signal_for_all_images[image_index])
            layout = go.Layout(title="Shape of profiles using calculated outer pixel intensity",
                               xaxis=dict(title=""),
                               yaxis=dict(title=""))

            figure = go.Figure(data=[trace], layout=layout)
            iplot(figure)

            trace = go.Scatter(y=new_profile_with_outer_cylinder_removed[image_index],
                               mode='markers',
                               marker=dict(color='Blue',
                                           line=dict(color='Red',
                                                     width=1)))
            layout = go.Layout(title="shape of ring with outside cylinder corrected",
                               xaxis=dict(title=""),
                               yaxis=dict(title=""))

            figure = go.Figure(data=[trace], layout=layout)
            iplot(figure)

        plot_shape_ring_signal_ui = interactive(plot_shape_ring_signal,
                                                image_index=widgets.IntSlider(min=0, max=self.number_of_images - 1,
                                                                              value=0))
        display(plot_shape_ring_signal_ui)

    def crop_to_inner_cylinder(self):

        nbr_pixel = len(self.profile_with_outer_cylinder_removed[0])
        inner_radius = self.config["cylinders_position"]["inner_radius"]
        center = int(nbr_pixel / 2)
        left_edge = center - inner_radius
        right_edge = center + inner_radius

        fig_crop_inner, ax_crop_inner = plt.subplots(num="Crop to inner cylinder")

        def plot_crop_inner(image_index, left_edge, right_edge):
            ax_crop_inner.cla()
            plt.plot(self.profile_with_outer_cylinder_removed[image_index], '.b')
            plt.axvline(x=left_edge, color='red')
            plt.axvline(x=right_edge, color='red')

            center = np.mean([left_edge, right_edge])
            plt.axvline(x=center, color='green', linestyle='--')

            return left_edge, right_edge

        self.plot_crop_inner_ui = interactive(plot_crop_inner,
                                              image_index=widgets.IntSlider(min=0,
                                                                            max=self.number_of_images - 1,
                                                                            value=0),
                                              left_edge=widgets.IntSlider(min=0,
                                                                          max=len(
                                                                                  self.profile_with_outer_cylinder_removed[
                                                                                      0]),
                                                                          value=left_edge),
                                              right_edge=widgets.IntSlider(min=0,
                                                                           max=len(
                                                                                   self.profile_with_outer_cylinder_removed[
                                                                                       0]),
                                                                           value=right_edge),
                                              )
        display(self.plot_crop_inner_ui)

    def correct_inner_cylinder_geometry(self):

        [left_edge, right_edge] = self.plot_crop_inner_ui.result

        inner_profiles = []
        for _profile in self.profile_with_outer_cylinder_removed:
            new_profile = _profile[left_edge: right_edge+1]
            inner_profiles.append(new_profile)

        new_inner_cylinder_radius = int(len(inner_profiles[0]) / 2)

        d = np.arange(len(inner_profiles[0]))
        list_intensity = inner_profiles

        list_expected_array = []

        for intensity in list_intensity:

            number_of_pixels = []
            expected_array = []
            for _index, x in enumerate(d):
                measure = intensity[_index]
                number_of_pixels_through_thickness = number_of_pixels_at_that_position1(position=x,
                                                                                        radius=new_inner_cylinder_radius)
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
