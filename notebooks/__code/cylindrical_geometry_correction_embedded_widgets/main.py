import os
import subprocess
import sys
from pathlib import PurePosixPath
import logging
import glob
from scipy.ndimage import rotate

module_path = os.path.abspath(os.path.join(".."))
if module_path not in sys.path:
    sys.path.append(module_path)
import json

import ipywidgets as widgets
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import HTML, display
from ipywidgets import interactive

matplotlib.rcParams["figure.figsize"] = (7, 7)

from NeuNorm.normalization import Normalization

from __code._utilities.file import make_or_increment_folder_name, make_tiff
from __code._utilities import notebook_legend

# from __code.cylindrical_geometry_correction_embedded_widgets.handler import CylinderGeometry
from __code.cylindrical_geometry_correction_embedded_widgets.handler import (
    DetectionConfig,
)
from __code.cylindrical_geometry_correction_embedded_widgets.handler import (
    detect_cylindrical_boundary,
)
from __code.cylindrical_geometry_correction_embedded_widgets.handler import (
    replace_with_nans,
)
from __code.cylindrical_geometry_correction_embedded_widgets.handler import (
    display_edges,
)
from __code.cylindrical_geometry_correction_embedded_widgets.handler import (
    display_detection,
)
from __code.cylindrical_geometry_correction_embedded_widgets.handler import (
    calculate_cylindrical_chord_map,
)
from __code.cylindrical_geometry_correction_embedded_widgets.handler import (
    display_chord_map,
)
from __code.cylindrical_geometry_correction_embedded_widgets.handler import (
    compute_correction_map_factor,
)
from __code.cylindrical_geometry_correction_embedded_widgets.handler import (
    apply_cylindrical_correction,
)
from __code.cylindrical_geometry_correction_embedded_widgets.handler import (
    visualize_correction_for_white_beam,
)
from __code.cylindrical_geometry_correction_embedded_widgets.handler import (
    visualize_correction_for_tof,
)
from __code.cylindrical_geometry_correction_embedded_widgets.handler import (
    export_config,
)
from __code.cylindrical_geometry_correction_embedded_widgets.handler import (
    export_images,
)
from __code.cylindrical_geometry_correction_embedded_widgets.handler import (
    display_compute_correction_map_factor,
)
from __code.cylindrical_geometry_correction_embedded_widgets.handler import (
    analyze_hyperspectral_comparison,
)
from __code.cylindrical_geometry_correction_embedded_widgets.handler import (
    visualize_hyperspectral_radiographs,
)
from __code.file_folder_browser import FileFolderBrowser

notebook_legend()

# def widget_output(func):
#     def wrapper_function(*args, **kwargs):
#         out = widgets.Output()
#         display(out)
#         return func(*args, **kwargs)
#     return wrapper_function


class CylindricalGeometryCorrectionEmbeddedWidgets:
    debugging = False
    data = None
    number_of_images = None

    remove_background_flag = True
    background_limit_ui = None

    config = {
        "cylinders_position": {
            "description": "pixel position in the cropped data image of the center, inner and outer radius",
            "center": 757,
            "inner_radius": 450,
            "outer_radius": 643,
        },
        "profiles_plot": {
            "description": "pixel position of the inner cylinder left and right edges",
            "left_inner_cylinder": 0,
            "right_inner_cylinder": 0,
        },
        "default_crop": {"x0": 386, "x1": 540, "y0": 889, "y1": 1824, "marker": 1000},
        "rotation_angle": {"angle": 0.0, "rotate_90_flag": False},
        "default_background": {"y0": 35, "y1": 282, "flag": False},
        "default_sample": {"y0": 415, "y1": 935},
        "profiles_limit": {
            "description": "range to use and to combine to extract profile. Mean algorithm is used to combine profiles",
            "top": -1,
            "bottom": -1,
            "vertical_guide": -1,
        },
        "c_disc": None,
        "res_mask": None,
        "list_of_images": None,
        "output_folder": None,
    }

    default_crop = {"x0": 369, "x1": 522, "y0": 756, "y1": 1894}
    crop = {"x0": None, "x1": None, "y0": None, "y1": None}
    cropped_data = None

    # Profile, for each image loaded, of inner and outer cylinder with only outer cylinder corrected
    profile_with_outer_cylinder_removed = None

    # list of images full path names
    list_of_images = None

    def initialize_path(self, working_dir="~/"):
        self.working_dir = working_dir
        self.shared_dir = working_dir + "/shared"
        _, _facility, _beamline, self.ipts, _ = self.shared_dir.split("/")
        self.ipts_folder = os.path.join("/SNS", _beamline, self.ipts)
        logging.info(f"Initialized paths with working_dir: {self.working_dir}")
        logging.info(f"\tShared directory: {self.shared_dir}")
        logging.info(f"\tIPTS folder: {self.ipts_folder}")
        logging.info(
            f"\tFacility: {_facility}, Beamline: {_beamline}, IPTS: {self.ipts}"
        )

    def initialize(self, mode="white_beam"):
        LOG_PATH = "/SNS/VENUS/shared/log/"
        file_name = f"cylindrical_geometry_correction_embedded_widgets_{mode}"
        user_name = os.getlogin()  # add user name to the log file name
        log_file_name = os.path.join(LOG_PATH, f"{file_name}_{user_name}.log")
        logging.basicConfig(
            filename=log_file_name,
            filemode="w",
            format="[%(levelname)s] - %(asctime)s - %(message)s",
            level=logging.INFO,
        )
        logging.info(f"*** Starting a new script {file_name} ***")

    def __init__(self, working_dir="./", debug=False, mode="white_beam"):
        self.initialize(mode=mode)
        self.initialize_path(working_dir=working_dir)
        self.mode = mode  # white_beam or tof

        self.debug = debug
        logging.info(f"Debugging mode: {self.debug}")

    def select_images(self):
        if self.debug:
            data_dir = "/HFIR/CG1D/IPTS-34222/shared/processed_data/normalized/3_normalized_to_OB/2025_10_30_60s/"
            logging.info(f"{os.path.exists(data_dir) = }")
            list_files = glob.glob(os.path.join(data_dir, "*.tif*"))
            logging.info(f"{os.path.join(data_dir, "*.tif*") = }")
            logging.info(
                f"Found {len(list_files)} TIFF files in the debug data directory."
            )
            list_files = list_files[:4]  # Load only the first 4 images for debugging
            self.out = widgets.Output()
            display(self.out)
            self.load_images(list_of_images=list_files)
            logging.info(f"{list_files = }")
            return

        file_folder_browser = FileFolderBrowser(
            working_dir=self.working_dir, next_function=self.load_images
        )
        file_folder_browser.select_images(filters={"TIFF": "*.tif?"})
        self.out = widgets.Output()
        display(self.out)

    def select_folder(self):
        if self.debug:
            data_dir = "/SNS/VENUS/IPTS-35945/shared/autoreduce/mcp/images/Run_7815/"
            self.out = widgets.Output()
            display(self.out)
            self.load_images_from_folder(data_dir)
            return

        folder_browser = FileFolderBrowser(
            working_dir=self.working_dir, next_function=self.load_images_from_folder
        )
        folder_browser.select_input_folder()
        self.out = widgets.Output()
        display(self.out)

    def load_images(self, list_of_images):
        with self.out:
            self.out.clear_output()

        self.number_of_images = len(list_of_images)
        self.list_of_images = list_of_images
        if self.number_of_images == 0:
            with self.out:
                return

        self.ipts_folder = self.working_dir
        self.working_dir = os.path.dirname(list_of_images[0])

        o_norm = Normalization()
        o_norm.load(file=list_of_images, notebook=True)
        self.data = o_norm.data["sample"]["data"]
        # self.data = [np.rot90(_data) for _data in data]

        if self.data:
            # integrated image
            self.integrated_image = np.sum(self.data, axis=0)

            with self.out:
                self.out.clear_output()
                display(
                    HTML(
                        "<span>Number of images loaded: "
                        + str(len(list_of_images))
                        + "</span>"
                    )
                )
                logging.info(f"Number of images loaded: {len(list_of_images)}")

            [self.height, self.width] = np.shape(np.squeeze(self.data[0]))
            logging.info(
                f"Image dimensions (height x width): {self.height} x {self.width}"
            )

            logging.info(f"{np.shape(self.data) = }")

    def load_images_from_folder(self, folder_name):
        logging.info(f"Selected folder: {folder_name}")
        list_of_images = []
        for file in os.listdir(folder_name):
            if file.lower().endswith((".tif", ".tiff")):
                list_of_images.append(os.path.join(folder_name, file))
        list_of_images.sort()

        # if self.debug:
        #     logging.info("Debug mode is ON. Only loading a subset of images.")
        #     list_of_images = list_of_images[:20]  # Load only the first 5 images for debugging

        logging.info(
            f"Number of TIFF images found in the folder: {len(list_of_images)}"
        )
        self.load_images(list_of_images)

    def select_config(self):
        if self.debug:
            if self.mode == "tof":
                config_file = os.path.join(os.path.dirname(__file__), "config_tof.json")
            else:
                config_file = os.path.join(
                    os.path.dirname(__file__), "config_white_beam.json"
                )
            self.out = widgets.Output()
            display(self.out)
            self.load_config(config_file)
            return

        config_browser = FileFolderBrowser(
            working_dir=os.path.dirname(self.working_dir),
            next_function=self.load_config,
            ipts_folder=self.ipts_folder,
        )
        config_browser.select_input_file_with_jump(
            instruction="Select config file ...",
            filters={"config": "*.json"},
            default_filter="config",
        )
        # self.out = widgets.Output()
        # display(self.out)

    def load_config(self, config_filename):
        if config_filename:
            with open(config_filename) as f:
                self.config = json.load(f)

            with self.out:
                self.out.clear_output()
                display(
                    HTML(
                        "<span style='font-size: 12px; color:blue'> Config file loaded: "
                        + config_filename
                        + "</span>"
                    )
                )

    def visualize_raw_images(self):
        # fig, ax1 = plt.subplots(num="Raw Images")
        # fig.show()

        vmax = np.max(self.data)
        vmin = np.min(self.data)

        default_vmin = float(np.percentile(self.data, 2))
        default_vmax = float(np.percentile(self.data, 98))

        def plot(image_index, vrange):

            vmin, vmax = vrange

            fig, ax1 = plt.subplots(num="Raw Images")
            data = self.data[image_index]
            im = ax1.imshow(data, vmin=vmin, vmax=vmax)
            plt.colorbar(im, ax=ax1, shrink=0.5)

        v = interactive(
            plot,
            image_index=widgets.IntSlider(
                min=0,
                max=len(self.data) - 1,
                value=0,
                style={"description_width": "150px"},
                layout=widgets.Layout(width="50%"),
            ),
            vrange=widgets.FloatRangeSlider(
                min=vmin,
                max=vmax,
                value=[default_vmin, default_vmax],
                style={"description_width": "150px"},
                layout=widgets.Layout(width="50%"),
            ),
        )
        display(v)

    def update_config_after_rotation(self):
        profile_1, profile_2 = self.v.children[3].value, self.v.children[4].value
        profile_vertical_guide = self.v.children[1].value
        top_profileh = min(profile_1, profile_2)
        bottom_profileh = max(profile_1, profile_2)
        self.config["profiles_limit"]["top"] = top_profileh
        self.config["profiles_limit"]["bottom"] = bottom_profileh
        self.config["profiles_limit"]["vertical_guide"] = profile_vertical_guide

        self.config["rotation_angle"]["angle"] = self.v.children[1].value
        self.config["rotation_angle"]["rotate_90_flag"] = self.v.children[0].value

    def rotate_images(self):
        default_rotate_angle = self.config["rotation_angle"]["angle"]
        default_rot_90_flag = self.config["rotation_angle"]["rotate_90_flag"]

        profile_margin = 100
        vmax = np.max(self.integrated_image)
        vmin = np.min(self.integrated_image)

        default_vmin = float(np.percentile(self.integrated_image, 2))
        default_vmax = float(np.percentile(self.integrated_image, 98))

        height, width = np.shape(self.integrated_image)
        if self.config["profiles_limit"]["top"] == -1:
            default_profile1_h = int(self.height / 3)
            default_profile2_h = int(2 * self.height / 3)
            vertical_guide = int(self.width / 2)
        else:
            default_profile1_h = self.config["profiles_limit"]["top"]
            default_profile2_h = self.config["profiles_limit"]["bottom"]
            vertical_guide = self.config["profiles_limit"].get(
                "vertical_guide", int(self.width / 2)
            )

        # def plot(rot_90_flag, rot_value, image_index, vert_guide, profile1_h, profile2_h, vrange):
        def plot(rot_90_flag, rot_value, vert_guide, profile1_h, profile2_h, vrange):

            vmin, vmax = vrange

            fig = plt.figure(num="Rotation of images", figsize=(15, 10))
            ax0 = plt.subplot(231)  # preview
            ax1 = plt.subplot(234)  # horizontal profiles
            ax3 = plt.subplot(132)  # vertical profile
            ax2 = plt.subplot(133)  # region between the two profiles

            # ax0.cla()
            data = self.integrated_image
            if rot_90_flag:
                data = np.rot90(data)

            data = rotate(data, rot_value)

            ax0.imshow(data, vmin=vmin, vmax=vmax)
            ax0.axvline(x=vert_guide, color="red", linestyle="--")

            top_profileh = np.min([profile1_h, profile2_h])
            bottom_profileh = np.max([profile1_h, profile2_h])

            point1 = [vert_guide - profile_margin, top_profileh]
            point2 = [vert_guide + profile_margin, top_profileh]
            x_values = [point1[0], point2[0]]
            y_values = [point1[1], point2[1]]
            ax0.plot(x_values, y_values, linestyle="--", color="b")

            point3 = [vert_guide - profile_margin, bottom_profileh]
            point4 = [vert_guide + profile_margin, bottom_profileh]
            x_values = [point3[0], point4[0]]
            y_values = [point3[1], point4[1]]
            ax0.plot(x_values, y_values, linestyle="--", color="g")

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

            profile1 = data[
                top_profileh, vert_guide - profile_margin : vert_guide + profile_margin
            ]
            profile2 = data[
                bottom_profileh,
                vert_guide - profile_margin : vert_guide + profile_margin,
            ]
            ax1.set_ylabel("Counts")
            ax1.set_xlabel("Pixels")
            ax1.set_title("Profiles of horizontal lines")

            # ax1.cla()
            ax1.plot(profile1, "b", label="profile 1")
            ax1.plot(profile2, "g", label="profile 2")

            # ax2.cla()
            top = point1[1]
            bottom = point3[1]
            left = point1[0]
            right = point2[0]

            tilted_data = data[top:bottom, left:right]
            ax2.imshow(tilted_data, vmin=vmin, vmax=vmax)
            ax2.axvline(profile_margin, linestyle="--", color="r")
            ax2.set_title("Zoom between \n hori. guides")

            vertical_profile = data[top_profileh:bottom_profileh, vert_guide]
            vertical_profile = vertical_profile[::-1]
            pixels = np.arange(len(vertical_profile))
            ax3.plot(vertical_profile, pixels, "r", label="vertical profile")
            ax3.set_xlabel("Counts")
            ax3.set_ylabel("Pixels")
            ax3.invert_yaxis()
            ax3.set_title("Vertical profile")

            plt.tight_layout()

        self.v = interactive(
            plot,
            rot_90_flag=widgets.Checkbox(
                value=default_rot_90_flag, description="Rotate 90 deg"
            ),
            rot_value=widgets.FloatSlider(
                min=-5.0,
                max=5.0,
                value=default_rotate_angle,
                continuous_update=False,
                layout=widgets.Layout(width="50%"),
            ),
            # image_index=widgets.IntSlider(min=0,
            #                               max=len(self.data) - 1,
            #                               value=0,
            #                               layout=widgets.Layout(width="50%")),
            vert_guide=widgets.IntSlider(
                min=0,
                max=self.width - 1,
                value=vertical_guide,
                layout=widgets.Layout(width="50%"),
                continuous_update=False,
            ),
            profile1_h=widgets.IntSlider(
                min=0,
                max=self.height - 1,
                continuous_update=False,
                value=default_profile1_h,
                layout=widgets.Layout(width="50%"),
            ),
            profile2_h=widgets.IntSlider(
                min=0,
                max=self.height - 1,
                continuous_update=False,
                value=default_profile2_h,
                layout=widgets.Layout(width="50%"),
            ),
            vrange=widgets.FloatRangeSlider(
                min=vmin,
                max=vmax,
                value=[default_vmin, default_vmax],
                layout=widgets.Layout(width="50%"),
            ),
        )

        display(self.v)

    def apply_rotation(self):

        self.update_config_after_rotation()

        rotation_value = self.v.children[1].value
        rotation_90_flag = self.v.children[0].value
        if rotation_90_flag:
            rotation_value += 90.0

        self.rotation_value = rotation_value
        self.data = [rotate(_data, rotation_value) for _data in self.data]
        self.integrated_image = np.sum(self.data, axis=0)

    def select_crop_region(self):

        width = self.width
        height = self.height

        vmax = np.max(self.integrated_image)
        vmin = np.min(self.integrated_image)

        default_vmin = float(np.percentile(self.integrated_image, 2))
        default_vmax = float(np.percentile(self.integrated_image, 98))

        fig_size = 10

        def plot(fig_size, left_right, top_bottom, profile_marker, vrange):

            left, right = left_right
            top, bottom = top_bottom

            fig = plt.figure(num="Select Region to Crop", figsize=(fig_size, fig_size))
            ax0 = plt.subplot(221)
            ax1 = plt.subplot(223)
            ax2 = plt.subplot(122)
            # ax3 = plt.subplot(133) # vertical profile in the cropped region

            vmin, vmax = vrange

            ax0.imshow(self.integrated_image, vmin=vmin, vmax=vmax)
            # ax0.axis("off")
            ax0.axvline(x=left, color="red", linestyle="--")
            ax0.axvline(x=right, color="red", linestyle="--")
            ax0.axhline(y=top, color="red", linestyle="-.")
            ax0.axhline(y=bottom, color="red", linestyle="-.")
            ax0.axhline(y=profile_marker, color="blue", linestyle="dotted")

            profile = self.integrated_image[profile_marker, :]
            ax1.plot(profile, ".")
            ax1.set_title("Profile at marker's position (dotted blue line)")
            ax1.set_xlabel("Pixels")
            ax1.set_ylabel("Counts")
            delta_x = right - left
            if delta_x < 0:
                delta_x = 0
            left_x_profile = (left - delta_x) if (left - delta_x) > 0 else 0
            plt.xlim([left_x_profile, right + delta_x])
            ax1.axvline(x=left, linestyle="--", color="red")
            ax1.axvline(x=right, linestyle="--", color="red")

            ax2.cla()
            cropped_data = self.integrated_image[top : bottom + 1, left : right + 1]
            ax2.imshow(cropped_data, vmin=vmin, vmax=vmax)
            ax2.set_title("Cropped Data Preview")

            # vertical_profile = np.sum(self.data[image_index][top : bottom + 1, left : right + 1], axis=1)
            # vertical_profile = vertical_profile[::-1]
            # pixels = np.arange(len(vertical_profile))
            # ax3.plot(vertical_profile, pixels, "r")
            # #ax3.plot(pixels, vertical_profile, "r")
            # # ax3.set_yscale("log")
            # ax3.set_title("Vertical profile in the cropped region")
            # ax3.set_xlabel("Counts")
            # ax3.set_ylabel("Pixels")

            return left, right, top, bottom

        description_width = "150px"

        self.crop_ui = interactive(
            plot,
            fig_size=widgets.IntSlider(
                min=5,
                max=20,
                value=10,
                layout=widgets.Layout(width="50%"),
                style={"description_width": description_width},
            ),
            # image_index=widgets.IntSlider(min=0,
            #                               max=self.number_of_images - 1,
            #                               value=0,
            #                               layout=widgets.Layout(width="50%")),
            style={"description_width": description_width},
            left_right=widgets.IntRangeSlider(
                min=0,
                max=width - 1,
                continueous_update=False,
                value=[
                    self.config["default_crop"]["x0"],
                    self.config["default_crop"]["x1"],
                ],
                layout=widgets.Layout(width="50%"),
            ),
            top_bottom=widgets.IntRangeSlider(
                min=0,
                continuous_update=False,
                max=height - 1,
                value=[
                    self.config["default_crop"]["y0"],
                    self.config["default_crop"]["y1"],
                ],
                style={"description_width": description_width},
                layout=widgets.Layout(width="50%"),
            ),
            profile_marker=widgets.IntSlider(
                min=0,
                max=height - 1,
                continuous_update=False,
                value=self.config["default_crop"]["marker"],
                layout=widgets.Layout(width="50%"),
                style={"description_width": description_width},
            ),
            vrange=widgets.FloatRangeSlider(
                min=vmin,
                max=vmax,
                continuous_update=False,
                value=[default_vmin, default_vmax],
                step=0.01,
                layout=widgets.Layout(width="50%"),
            ),
        )
        display(self.crop_ui)

    def checking_edges(self):

        display(
            HTML(
                "Sample has been rotated by 90 degrees, so the vertical profile is now horizontal"
            )
        )
        display(
            HTML(
                "Check that the signal is relatively flat and that the edges are not too high counts!"
            )
        )

        [x0, x1, y0, y1] = self.crop_ui.result

        def plot_checking(image_index, integrated_flag):
            fig, axs = plt.subplots(
                nrows=2,
                ncols=1,
                figsize=(15, 10),
                # gridspec_kw={'hspace': 10},
                sharex=False,
            )

            data = (
                self.data[image_index] if not integrated_flag else self.integrated_image
            )
            data = data[y0 : y1 + 1, x0 : x1 + 1]
            # rotate 90 degrees
            data_rotated = np.rot90(data, k=1)

            axs[0].imshow(data_rotated, cmap="viridis")
            axs[0].tick_params(labelbottom=False)
            axs[0].tick_params(labeltop=True)

            profile = np.sum(data, axis=1)
            # profile = profile[::-1]
            pixels = np.arange(len(profile))
            axs[1].plot(pixels, profile, "r")
            # limit x axis to the cropped region
            axs[1].set_xlim([0, y1 - y0])
            axs[1].set_title("Vertical profile in the cropped region")
            axs[1].set_ylabel("")
            axs[1].set_xlabel("Pixels")

            plt.tight_layout()
            plt.show()

        v = interactive(
            plot_checking,
            image_index=widgets.IntSlider(
                min=0,
                max=self.number_of_images - 1,
                value=0,
                layout=widgets.Layout(width="50%"),
            ),
            integrated_flag=widgets.Checkbox(
                value=True,
                description="Integrate images",
                layout=widgets.Layout(width="50%"),
            ),
        )
        display(v)

    def crop_images(self):
        [x0, x1, y0, y1] = self.crop_ui.result
        self.crop = {"x0": 0, "x1": x1, "y0": y0, "y1": y1}
        self.config["default_crop"]["x0"] = x0
        self.config["default_crop"]["x1"] = x1
        self.config["default_crop"]["y0"] = y0
        self.config["default_crop"]["y1"] = y1

        cropped_data = [_data[y0 : y1 + 1, x0 : x1 + 1] for _data in self.data]
        self.cropped_data = np.array(cropped_data)
        self.integrated_cropped_image = np.sum(self.cropped_data, axis=0)

    def export_cropped_images(self):
        if self.cropped_data is None:
            self.crop_images()

        display(
            HTML(
                '<span style="font-size: 15px; color:blue">Select a folder if you want to export the cropped images!</span>'
            )
        )
        working_dir = os.path.dirname(self.working_dir)
        self.file_selection_ui = FileFolderBrowser(
            ipts_folder=self.ipts_folder,
            working_dir=working_dir,
            next_function=self.export_cropped_images_step2,
        )
        self.file_selection_ui.select_output_folder_with_new()
        self.out = widgets.Output()
        display(self.out)

    def export_cropped_images_step2(self, output_folder):
        output_folder = os.path.abspath(output_folder)
        working_dir = self.working_dir
        base_working_dir = os.path.join(
            output_folder, os.path.basename(working_dir) + "_cropped"
        )
        base_working_dir = make_or_increment_folder_name(base_working_dir)

        list_images_corrected = self.cropped_data
        list_of_images = self.list_of_images

        nbr_images = len(list_of_images)
        progress_bar = widgets.IntProgress(min=0, max=nbr_images - 1)
        with self.out:
            display(progress_bar)

        for index, image in enumerate(list_images_corrected):
            _name = os.path.basename(list_of_images[index])
            full_name = os.path.join(base_working_dir, _name)

            if not full_name.lower().endswith(".tif"):
                base_name_without_suffix = PurePosixPath(_name).stem
                full_name = os.path.join(
                    base_working_dir, base_name_without_suffix + ".tif"
                )

            make_tiff(filename=full_name, data=image)
            progress_bar.value = index + 1

        progress_bar.close()
        with self.out:
            display(
                HTML(
                    '<span style="font-size: 12px; color:blue">'
                    + str(nbr_images)
                    + " images exported to "
                    + base_working_dir
                    + "!</span>"
                )
            )
            display(widgets.Label(value="Exported images to: " + base_working_dir))

    def visualize_or_not_results(self):
        display(
            HTML(
                '<span style="font-size: 15px; color:blue">Do you want to visualize the calculated edges and chord length map?</span>'
            )
        )
        self.visualize_results = widgets.ToggleButtons(
            options=["Yes", "No"], description="", value="Yes"
        )
        display(self.visualize_results)

    def calculate_and_visualize(self):
        images = replace_with_nans(self.cropped_data)
        self.integrated_cropped_image = np.sum(images, axis=0)
        detection_config = DetectionConfig()
        detection_config.diagnostics = True
        geometry, diagnostics = detect_cylindrical_boundary(
            self.integrated_cropped_image, detection_config
        )
        res = calculate_cylindrical_chord_map(
            image_shape=self.integrated_cropped_image.shape,
            center_x=geometry.center_x,
            top_edge=geometry.top_edge,
            bottom_edge=geometry.bottom_edge,
            radius=geometry.radius,
            is_hollow=False,  # or True with inner_radius=...
            outside_fill="nan",  # or "zeros"
            edge_epsilon=0.0,  # usually 0 for Beer–Lambert workflows
        )
        logging.info(
            f"Calculated cylindrical chord map with center_x={geometry.center_x},"
            f" top_edge={geometry.top_edge}, bottom_edge={geometry.bottom_edge}, radius={geometry.radius}"
        )
        logging.info(f"res = {res.stats}")

        logging.info(f"DEBUGGING: {type(res.mask) = }")
        logging.info(f"DEBUGGING: {np.shape(res.mask) = }")
        self.config["res_mask"] = (
            res.mask.tolist()
        )  # save the mask in the config file for export (convert to list for json serialization)

        self.cropped_data = images  ## TRYING THIS
        mu_disc, mu_iter, C_disc = compute_correction_map_factor(
            self.cropped_data, geometry, res
        )
        logging.info(f"DEBUGGING: {type(C_disc) = }")
        logging.info(f"DEBUGGING: {np.shape(C_disc) = }")
        self.config["c_disc"] = C_disc[
            :, 0
        ].tolist()  # save only the 1D version of the correction map factor for export in the config file

        hyperspectral_stack = np.swapaxes(self.cropped_data, 0, 2)
        hyperspectral_stack = np.swapaxes(hyperspectral_stack, 0, 1)  # "H, W, L or TOF"

        Tcorr = apply_cylindrical_correction(
            T_yxl=hyperspectral_stack,
            C_xl=C_disc,
            mask_yx=res.mask,
            copy=True,  # keep original untouched
        )
        _intermediate = np.swapaxes(Tcorr, 0, 2)
        self.corrected_images = np.swapaxes(_intermediate, 1, 2)  # "nbr, H, W

        if self.visualize_results.value == "Yes":
            display_edges(geometry, diagnostics)
            display_detection(self.integrated_cropped_image, geometry, diagnostics)
            display_chord_map(
                res, geometry, background=self.integrated_cropped_image, figsize=(12, 8)
            )

            if self.mode == "tof":
                display_compute_correction_map_factor(mu_disc, mu_iter)
                visualize_correction_for_tof(
                    T_yxl=hyperspectral_stack,
                    Tcorr_yxl=Tcorr,
                    mask_yx=res.mask,
                    lambda_indices=[
                        int(0.1 * mu_disc.size),
                        int(0.5 * mu_disc.size),
                        int(0.9 * mu_disc.size),
                    ],
                )

            else:
                visualize_correction_for_white_beam(
                    T_yxl=hyperspectral_stack,
                    Tcorr_yxl=Tcorr,
                    mask_yx=res.mask,
                    lambda_indices=[
                        int(0.1 * mu_disc.size),
                        int(0.5 * mu_disc.size),
                        int(0.9 * mu_disc.size),
                    ],
                )
        else:
            display(
                HTML(
                    '<span style="font-size: 12px; color:blue">Edges detected but not visualized!</span>'
                )
            )

        self.hyperspectral_stack = hyperspectral_stack
        self.Tcorr = Tcorr

    def display_before_and_after_correction(self):
        def plot_before_after_correction(image_index):
            fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(15, 10))
            fig.suptitle(f"Before and After Correction of image #{image_index}")
            im0 = axs[0].imshow(self.cropped_data[image_index])
            plt.colorbar(im0, ax=axs[0], shrink=0.5, label="Counts")
            axs[0].set_title("Before correction")
            im1 = axs[1].imshow(self.corrected_images[image_index])
            plt.colorbar(im1, ax=axs[1], shrink=0.5, label="Counts")
            axs[1].set_title("After correction")
            plt.tight_layout()
            plt.show()

        interactive_plot = interactive(
            plot_before_after_correction,
            image_index=widgets.IntSlider(
                min=0,
                max=len(self.corrected_images) - 1,
                step=1,
                value=0,
                layout=widgets.Layout(width="50%"),
            ),
        )
        display(interactive_plot)

    def analyze_hyperspectral_comparison(self):
        cylindrical_corr_analysis_res = analyze_hyperspectral_comparison(
            T_yxl_before=self.hyperspectral_stack,
            T_yxl_after=self.Tcorr,
            title_prefix="Cylindrical Correction",
        )
        _ = visualize_hyperspectral_radiographs(self.Tcorr)

    def what_to_export(self):
        display(
            HTML(
                '<span style="font-size: 15px; color:blue">What do you want to export?</span>'
            )
        )
        self.export_options = widgets.SelectMultiple(
            options=["Corrected images", "Config file"],
            value=["Corrected images", "Config file"],
            description="",
            layout=widgets.Layout(width="50%"),
        )
        display(self.export_options)

    def select_export_location(self):
        if self.export_options.value == ():
            display(
                HTML(
                    '<span style="font-size: 12px; color:red">Please select at least one option to export!</span>'
                )
            )
            return

        working_dir = os.path.dirname(self.working_dir)
        self.output_folder_browser = FileFolderBrowser(
            working_dir=working_dir,
            ipts_folder=self.ipts_folder,
            next_function=self.export_images_and_config,
        )
        self.output_folder_browser.select_output_folder_with_new()
        self.out = widgets.Output()
        display(self.out)

    def export_images_and_config(self, output_folder):

        try:
            self.output_folder_browser.list_output_folders_ui.shortcut_buttons.close()  # close the jump to shared and home buttons
        except AttributeError:
            pass

        # make folder that will contain the exported content
        base_working_dir = os.path.join(
            output_folder,
            os.path.basename(self.working_dir) + "_cylindrical_geo_corrected",
        )
        base_working_dir = make_or_increment_folder_name(base_working_dir)
        self.output_folder = base_working_dir
        self.config["output_folder"] = self.output_folder

        if "Corrected images" in self.export_options.value:
            export_images(
                output_folder=self.output_folder,
                working_dir=self.working_dir,
                stack_of_images=self.corrected_images,
                out=self.out,
                list_of_input_filenames=self.list_of_images,
            )
        if "Config file" in self.export_options.value:
            export_config(
                config_filename=os.path.join(self.output_folder, "config.json"),
                config=self.config,
            )

    def select_images_for_batch_processing(self):
        if self.debug:
            data_dir = "/HFIR/CG1D/IPTS-34222/shared/processed_data/normalized/3_normalized_to_OB/2025_10_30_60s/"
            logging.info(f"{os.path.exists(data_dir) = }")
            list_files = glob.glob(os.path.join(data_dir, "*.tif*"))
            logging.info(f"{os.path.join(data_dir, '*.tif*') = }")
            logging.info(
                f"Found {len(list_files)} TIFF files in the debug data directory."
            )
            list_files = list_files[:20]  # Load only the first 20 images for debugging
            self.out = widgets.Output()
            display(self.out)
            logging.info(f"{list_files = }")
            self.config["list_of_images"] = list_files
            self.prepare_batch_processing_script_from_config(config=self.config)
            return

        file_folder_browser = FileFolderBrowser(
            working_dir=self.working_dir,
            next_function=self.prepare_batch_processing_script_from_list_of_files,
        )
        file_folder_browser.select_images(filters={"TIFF": "*.tif?"})
        self.out = widgets.Output()
        display(self.out)

    def prepare_batch_processing_script_from_config(self, config):
        export_config(
            config_filename=os.path.join(self.output_folder, "config.json"),
            config=config,
        )
        # inform here how to run the batch processing script with the exported config file, e.g. by running a command in the terminal like:
        self.how_to_run_batch_processing()
        self.create_batch_processing_script()
        # self.run_from_notebook()

    def prepare_batch_processing_script_from_list_of_files(self, list_of_images):
        self.config["list_of_images"] = list_of_images
        export_config(
            config_filename=os.path.join(self.output_folder, "config.json"),
            config=self.config,
        )
        self.create_batch_processing_script()
        self.how_to_run_batch_processing()
        # self.run_from_notebook()

    def run_from_notebook(self):
        with self.out:
            self.out.clear_output()

        run_button = widgets.Button(
            description="Run batch processing from notebook",
            layout=widgets.Layout(width="50%"),
            button_style="success",
        )
        display(run_button)
        run_button.on_click(self.button_to_run_batch_processing_clicked)

    def button_to_run_batch_processing_clicked(self, b):
        # subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"bash {self.run_script_path}; exec bash"])
        subprocess.Popen(["xterm", "-hold", "-e", f"bash {self.run_script_path}"])

    def how_to_run_batch_processing(self):
        with self.out:
            self.out.clear_output()
            display(
                HTML(
                    '<span style="font-size: 12px; color:black">Batch processing script prepared! Simply type the following command in the terminal:</span>'
                )
            )
            display(
                HTML(
                    f'<span style="font-size: 12px; color:blue">{self.run_script_path}</span>'
                )
            )

    def create_batch_processing_script(self):
        # create the run_batch_processing.sh file with the command to run the batch processing script with the exported config file
        run_script_path = os.path.join(self.output_folder, "run_batch_processing.sh")
        self.run_script_path = run_script_path
        with open(run_script_path, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# Run the batch processing script with the exported config file\n")
            f.write(
                f'pixi run --manifest-path /SNS/VENUS/shared/software/git/python_notebooks python /SNS/VENUS/shared/software/git/python_notebooks/notebooks/cylindrical_geometry_correction_cli.py "{os.path.join(self.output_folder, "config.json")}"\n'
            )

        os.chmod(run_script_path, 0o755)  # make the script executable
