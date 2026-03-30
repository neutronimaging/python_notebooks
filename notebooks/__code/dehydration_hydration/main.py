import os
import sys
from pathlib import PurePosixPath
import logging


module_path = os.path.abspath(os.path.join(".."))
if module_path not in sys.path:
    sys.path.append(module_path)

from mbirjax.hsnt import hyper_denoise

import ipywidgets as widgets
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from IPython.display import HTML, display
from ipywidgets import interactive

from NeuNorm.normalization import Normalization

from __code._utilities.file import make_or_increment_folder_name, make_tiff
from __code._utilities import notebook_legend
from __code.file_folder_browser import FileFolderBrowser

from __code.dehydration_hydration import debug_sample_folder

notebook_legend()

# def widget_output(func):
#     def wrapper_function(*args, **kwargs):
#         out = widgets.Output()
#         display(out)
#         return func(*args, **kwargs)
#     return wrapper_function


class DehydrationHydrationCorrection:
    debugging = False
    data = None
    number_of_images = None

    # list of images full path names
    list_of_images = None

    profile_region = None

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

    def initialize(self):
        LOG_PATH = "/SNS/VENUS/shared/log/"
        file_name = "dehydration_hydration"
        user_name = os.getlogin()  # add user name to the log file name
        log_file_name = os.path.join(LOG_PATH, f"{file_name}_{user_name}.log")
        logging.basicConfig(
            filename=log_file_name,
            filemode="w",
            format="[%(levelname)s] - %(asctime)s - %(message)s",
            level=logging.INFO,
        )
        logging.info(f"*** Starting a new script {file_name} ***")

    def __init__(self, working_dir="./", debug=False):
        self.initialize()
        self.initialize_path(working_dir=working_dir)

        self.debug = debug
        logging.info(f"Debugging mode: {self.debug}")

    def select_images(self):
        if self.debug:
            data_dir = debug_sample_folder
            self.out = widgets.Output()
            display(self.out)
            self.load_images_from_folder(data_dir)
            return

        file_folder_browser = FileFolderBrowser(
            working_dir=self.working_dir, next_function=self.load_images
        )
        file_folder_browser.select_images(filters={"TIFF": "*.tif?"})
        self.out = widgets.Output()
        display(self.out)

    def select_folder(self):
        if self.debug:
            data_dir = debug_sample_folder
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

        with self.out:
            o_norm = Normalization()
            o_norm.load(file=list_of_images, notebook=True)
        self.data = o_norm.data["sample"]["data"]
        # self.data = [np.rot90(_data) for _data in data]

        if self.data:
            self.data = np.array(self.data)
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

    def visualize_raw_images(self):
        vmax = np.max(self.data)

        def plot(image_index, vrange):
            vmin, vmax = vrange

            # Create subplots using plotly
            fig = make_subplots(
                rows=1,
                cols=2,
                subplot_titles=(f"Raw image #{image_index}", "Integrated image"),
                horizontal_spacing=0.1,
            )

            # Raw image plot
            data = self.data[image_index]
            fig.add_trace(
                go.Heatmap(
                    z=data,
                    zmin=vmin,
                    zmax=vmax,
                    colorscale="viridis",
                    showscale=True,
                    colorbar=dict(x=0.45, len=0.5),
                ),
                row=1,
                col=1,
            )

            # Integrated image plot
            fig.add_trace(
                go.Heatmap(
                    z=self.integrated_image,
                    colorscale="viridis",
                    showscale=True,
                    colorbar=dict(x=1.02, len=0.5),
                ),
                row=1,
                col=2,
            )

            # Update layout
            fig.update_layout(
                title="Raw Images Visualization",
                width=1000,
                height=500,
                showlegend=False,
            )

            # Update axes to remove ticks for cleaner look
            fig.update_xaxes(showticklabels=False)
            fig.update_yaxes(showticklabels=False)

            fig.show()

        v = interactive(
            plot,
            image_index=widgets.IntSlider(
                min=0,
                max=len(self.data) - 1,
                value=0,
                description="Image index:",
                style={"description_width": "150px"},
                layout=widgets.Layout(width="50%"),
            ),
            vrange=widgets.FloatRangeSlider(
                min=0,
                max=vmax,
                value=[0, vmax],
                description="Value range:",
                style={"description_width": "150px"},
                layout=widgets.Layout(width="50%"),
            ),
        )
        display(v)

    def setup_parameters_for_correction(self):
        self.dataset_type_ui = widgets.Dropdown(
            options=["attenuation", "transmission"],
            value="attenuation",
            description="Dataset type:",
            style={"description_width": "150px"},
            layout=widgets.Layout(width="50%"),
        )
        display(self.dataset_type_ui)

        self.num_materials_ui = widgets.IntSlider(
            min=1,
            max=10,
            value=2,
            description="Number of materials:",
            style={"description_width": "150px"},
            layout=widgets.Layout(width="50%"),
        )
        display(self.num_materials_ui)

        # self.safety_factor_ui = widgets.IntSlider(
        #     min=1,
        #     max=5,
        #     value=2,
        #     description="Safety factor:",
        #     style={"description_width": "150px"},
        #     layout=widgets.Layout(width="50%"))
        # display(self.safety_factor_ui)

        self.beta_loss_ui = widgets.Dropdown(
            options=["kullback-leibler", "frobenius"],
            value="frobenius",
            description="Beta loss:",
            style={"description_width": "150px"},
            layout=widgets.Layout(width="50%"),
        )
        display(self.beta_loss_ui)

        self.max_iterations_ui = widgets.IntSlider(
            min=50,
            max=1000,
            value=300,
            description="Max iterations:",
            style={"description_width": "150px"},
            layout=widgets.Layout(width="50%"),
        )
        display(self.max_iterations_ui)

    def perform_correction(self):
        dataset_type = self.dataset_type_ui.value
        num_materials = self.num_materials_ui.value
        beta_loss = self.beta_loss_ui.value
        max_iterations = self.max_iterations_ui.value
        # safety_factor = self.safety_factor_ui.value

        logging.info("Performing correction with parameters:")
        logging.info(f"\tDataset type: {dataset_type}")
        logging.info(f"\tNumber of materials: {num_materials}")
        logging.info(f"\tBeta loss: {beta_loss}")
        logging.info(f"\tMax iterations: {max_iterations}")
        # logging.info(f"\tSafety factor: {safety_factor}")

        raw_data = self.data
        logging.info(f"before swapping axes, raw data shape: {raw_data.shape}")
        swap_data = np.swapaxes(raw_data, 0, 2)
        logging.info(f"after swapping axes, data shape: {swap_data.shape}")

        out = widgets.Output()
        display(out)

        with out:
            display(
                HTML(
                    "<span style='color: blue; font-weight: bold;'>Performing correction, please wait...</span>"
                )
            )

        _denoised_data = hyper_denoise(
            swap_data,
            verbose=False,
            dataset_type=dataset_type,
            # safety_factor=safety_factor,
            num_materials=num_materials,
            beta_loss=beta_loss,
            max_iter=max_iterations,
        )

        # swapping axes back to original order
        self.corrected_images = np.swapaxes(_denoised_data, 0, 2)
        self.integrated_corrected_image = np.mean(self.corrected_images, axis=0)
        logging.info(f"Corrected images shape: {self.corrected_images.shape}")

        with out:
            out.clear_output()
            display(
                HTML(
                    "<span style='color: green; font-weight: bold;'>Correction completed successfully!</span>"
                )
            )

    def visualize_results(self):
        vmax = np.max(self.corrected_images)

        def plot(image_index, vrange):
            vmin, vmax = vrange

            # Create subplots using plotly
            fig = make_subplots(
                rows=1,
                cols=2,
                subplot_titles=(
                    f"Corrected image #{image_index}",
                    f"Uncorrected image #{image_index}",
                ),
                horizontal_spacing=0.1,
            )

            # Corrected image plot
            corrected_data = self.corrected_images[image_index]
            fig.add_trace(
                go.Heatmap(
                    z=corrected_data,
                    zmin=vmin,
                    zmax=vmax,
                    colorscale="viridis",
                    showscale=True,
                    colorbar=dict(x=0.45, len=0.5),
                ),
                row=1,
                col=1,
            )

            # Uncorrected image plot
            uncorrected_data = self.data[image_index]
            fig.add_trace(
                go.Heatmap(
                    z=uncorrected_data,
                    zmin=vmin,
                    zmax=vmax,
                    colorscale="viridis",
                    showscale=True,
                    colorbar=dict(x=1.02, len=0.5),
                ),
                row=1,
                col=2,
            )

            # Update layout
            fig.update_layout(
                title="Corrected vs Uncorrected Images",
                width=1000,
                height=500,
                showlegend=False,
            )

            # Update axes to remove ticks for cleaner look
            fig.update_xaxes(showticklabels=False)
            fig.update_yaxes(showticklabels=False)

            fig.show()

        v = interactive(
            plot,
            image_index=widgets.IntSlider(
                min=0,
                max=len(self.corrected_images) - 1,
                value=0,
                description="Image index:",
                style={"description_width": "150px"},
                layout=widgets.Layout(width="50%"),
            ),
            vrange=widgets.FloatRangeSlider(
                min=0,
                max=vmax,
                value=[0, vmax],
                description="Value range:",
                style={"description_width": "150px"},
                layout=widgets.Layout(width="50%"),
            ),
        )
        display(v)

    def visualize_profiles(self):

        if self.profile_region is not None:
            top = self.profile_region["top"]
            bottom = self.profile_region["bottom"]
            left = self.profile_region["left"]
            right = self.profile_region["right"]
        else:
            left = self.width // 4
            right = 2 * self.width // 4
            top = self.height // 4
            bottom = 2 * self.height // 4

        def plot(left_right, top_bottom):
            top, bottom = top_bottom
            left, right = left_right

            # Create subplots with custom width ratios (1:2 like gridspec)
            fig = make_subplots(
                rows=1,
                cols=2,
                column_widths=[0.33, 0.67],
                subplot_titles=(
                    "Integrated corrected image with selected region",
                    f"Profiles for region ({top}:{bottom}, {left}:{right})",
                ),
                specs=[[{"secondary_y": False}, {"secondary_y": False}]],
            )

            # Left subplot: Integrated image with rectangle overlay
            fig.add_trace(
                go.Heatmap(
                    z=self.integrated_corrected_image,
                    colorscale="viridis",
                    showscale=False,
                    hovertemplate="x: %{x}<br>y: %{y}<br>intensity: %{z}<extra></extra>",
                ),
                row=1,
                col=1,
            )

            # Add rectangle shape to show selected region
            fig.add_shape(
                type="rect",
                x0=left,
                y0=top,
                x1=right,
                y1=bottom,
                line=dict(color="red", width=2),
                fillcolor="rgba(0,0,0,0)",
                row=1,
                col=1,
            )

            # Calculate profiles
            uncorrected_images = self.data[:, top:bottom, left:right]
            uncorrected_profile = np.mean(uncorrected_images, axis=(1, 2))

            corrected_images = self.corrected_images[:, top:bottom, left:right]
            corrected_profile = np.mean(corrected_images, axis=(1, 2))

            # Right subplot: Profile plots
            fig.add_trace(
                go.Scatter(
                    y=uncorrected_profile,
                    mode="markers",
                    marker=dict(symbol="cross", size=5),
                    name="Uncorrected profile",
                    hovertemplate="Image: %{x}<br>Intensity: %{y}<extra></extra>",
                ),
                row=1,
                col=2,
            )

            fig.add_trace(
                go.Scatter(
                    y=corrected_profile,
                    mode="markers",
                    marker=dict(symbol="circle", size=3),
                    name="Corrected profile",
                    hovertemplate="Image: %{x}<br>Intensity: %{y}<extra></extra>",
                ),
                row=1,
                col=2,
            )

            # Update layout
            fig.update_layout(
                title="Profiles for Selected Region",
                width=1200,
                height=400,
                showlegend=True,
                legend=dict(x=0.7, y=1),
            )

            # Update x and y axes
            fig.update_xaxes(title_text="", showticklabels=False, row=1, col=1)
            fig.update_yaxes(title_text="", showticklabels=False, row=1, col=1)
            fig.update_xaxes(title_text="Image index", row=1, col=2)
            fig.update_yaxes(title_text="Average intensity", row=1, col=2)

            fig.show()

            self.profile_region = {
                "top": top,
                "bottom": bottom,
                "left": left,
                "right": right,
            }

        v = interactive(
            plot,
            left_right=widgets.IntRangeSlider(
                min=0,
                max=self.width,
                value=[left, right],
                step=1,
                description="Left-Right:",
                style={"description_width": "150px"},
                layout=widgets.Layout(width="50%"),
            ),
            top_bottom=widgets.IntRangeSlider(
                min=0,
                max=self.height,
                value=[top, bottom],
                step=1,
                description="Top-Bottom:",
                style={"description_width": "150px"},
                layout=widgets.Layout(width="50%"),
            ),
        )
        display(v)

    def export(self):
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
        self.export_images(
            output_folder=output_folder,
            working_dir=self.working_dir,
            stack_of_images=self.corrected_images,
            out=self.out,
            list_of_input_filenames=self.list_of_images,
        )

    def export_images(
        self,
        output_folder=None,
        working_dir=None,
        stack_of_images=None,
        out=None,
        list_of_input_filenames=None,
    ):
        logging.info(f"Exporting images to folder: {output_folder}")
        logging.info(f"\tworking_dir: {working_dir}")
        logging.info(f"\tstack_of_images shape: {np.shape(stack_of_images)}")
        logging.info(f"\tlist_of_input_filenames: {list_of_input_filenames}")

        self.output_folder_browser.list_output_folders_ui.shortcut_buttons.close()

        with self.out:
            self.out.clear_output()

        output_folder = os.path.abspath(output_folder)
        base_working_dir = os.path.join(
            output_folder, os.path.basename(working_dir) + "_cylindrical_geo_corrected"
        )
        base_working_dir = make_or_increment_folder_name(base_working_dir)

        with self.out:
            display(
                HTML(
                    '<span style="font-size: 12px; color:blue">Exporting to folder: '
                    + base_working_dir
                    + " ...</span>"
                )
            )

        # export images
        list_of_images_corrected = stack_of_images

        nbr_images = len(list_of_images_corrected)
        progress_bar = widgets.IntProgress(min=0, max=nbr_images - 1)
        with self.out:
            display(progress_bar)

        for index, image in enumerate(list_of_images_corrected):
            logging.info(f"\tExporting image {index + 1}/{nbr_images} to TIFF...")
            logging.info(f"\t\t{list_of_input_filenames[index]= }")
            _name = os.path.basename(list_of_input_filenames[index])
            logging.info(f"\t\t{_name= }")
            full_name = os.path.join(base_working_dir, _name)
            # make sure the extension is .tif
            if not full_name.lower().endswith(".tif"):
                base_name_without_suffix = PurePosixPath(_name).stem
                full_name = os.path.join(
                    base_working_dir, base_name_without_suffix + ".tif"
                )
            make_tiff(filename=full_name, data=image)
            with self.out:
                progress_bar.value = index + 1

            progress_bar.close()

        with self.out:
            self.out.clear_output()
            display(
                HTML(
                    '<span style="font-size: 12px; color:green">'
                    + str(nbr_images)
                    + " images created in "
                    + base_working_dir
                    + "  !</span>"
                )
            )
