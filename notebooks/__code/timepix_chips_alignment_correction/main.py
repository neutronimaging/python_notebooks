import glob
import os

from matplotlib import patches
import numpy as np
import ipywidgets as widgets
from IPython.display import HTML, display
import tqdm
import yaml
import matplotlib.pyplot as plt
from ipywidgets import interactive
from tqdm import tqdm

from timepix_geometry_correction.correct import TimepixGeometryCorrection

from __code._utilities.images import load_data_using_multithreading
from __code._utilities.images import make_tiff
from __code.ipywe import fileselector
from __code.ipywe import myfileselector
from __code.timepix_chips_alignment_correction import config


class DetectorType:
    TIMEPIX1 = "Timepix 1"
    TIMEPIX3 = "Timepix 3"
    # CUSTOM = "Custom"


class ChipsLabelPosition:
    x_left = 15
    x_right = 512 - x_left
    y_top = 20
    y_bottom = 512 - y_top

    chip1 = (x_right, y_top)
    chip2 = (x_left, y_top)
    chip3 = (x_left, y_bottom)
    chip4 = (x_right, y_bottom)


class TimepixChipsAlignmentCorrection:
    working_data = None

    working_list_files = None
    sum_file = None
    out = widgets.Output()

    def __init__(self, working_dir="./"):
        self.working_dir = working_dir
        _, _facility, _beamline, ipts = self.working_dir.split("/")
        self.ipts = ipts
        self.ipts_path = os.path.join("/", _facility, _beamline, ipts)

    def select_folder(self):
        select_data = fileselector.FileSelectorPanel(
            instruction="Select MCP Folder ...",
            start_dir=self.working_dir,
            next=self.load_data,
            type="directory",
            multiple=False,
        )
        select_data.show()
        self.out = widgets.Output()
        display(self.out)

    def load_data(self, folder_selected):
        full_list_files = glob.glob(os.path.join(folder_selected, "*.tif*"))
        full_list_files.sort()
        working_list_files = [
            file for file in full_list_files if "_SummedImg.fits" not in file
        ]
        self.working_list_files = (
            working_list_files  # full file name of the stack of tif files
        )

        self.working_data = load_data_using_multithreading(list_tif=working_list_files)
        self.input_working_folder = folder_selected
        self.working_list_files = working_list_files

        # create integrated data set
        self.integrated_data = np.sum(self.working_data, axis=0)

        with self.out:
            self.out.clear_output()
            display(
                HTML(
                    '<span style="font-size: 15px; color:blue">'
                    + str(len(working_list_files) + 1)
                    + " files have been loaded from "
                    + folder_selected
                    + "</span>"
                )
            )

    def select_detector(self):
        label = widgets.Label(
            "Select Detector Type:", layout=widgets.Layout(width="13%")
        )
        list_of_detector_types = [
            DetectorType.__dict__.get(key)
            for key in DetectorType.__dict__.keys()
            if not key.startswith("__")
        ]
        self.detector_type_ui = widgets.Dropdown(
            options=list_of_detector_types,
            value=DetectorType.TIMEPIX1,
            # value=DetectorType.CUSTOM,      # DEBUGGING PURPOSE
            # description='Detector Type:',
            disabled=False,
            layout=widgets.Layout(width="20%"),
        )
        box = widgets.HBox([label, self.detector_type_ui])
        display(box)

    def correction_settings(self):
        # if self.detector_type_ui.value == DetectorType.CUSTOM:
        #     # self.select_config_file()
        #     # for debugging purpose only
        #     config_file = "/SNS/VENUS/IPTS-35945/shared/processed_data/jean_test/detector_config.yaml"
        #     self.load_config_file(config_file)

        # else:
        if self.detector_type_ui.value == DetectorType.TIMEPIX1:
            _detector_config = config.config_timepix1
        elif self.detector_type_ui.value == DetectorType.TIMEPIX3:
            _detector_config = config.config_timepix3
        else:
            raise ValueError("Unsupported detector type")
        self.detector_config = _detector_config
        self.display_detector_config(editable=False)
        self.correct_integrated_data()
        self.display_correction()

    def select_config_file(self):
        select_config = fileselector.FileSelectorPanel(
            instruction="Select Detector Configuration File ...",
            start_dir=self.working_dir,
            next=self.load_config_file,
            type="file",
            multiple=False,
            filters={"YAML files": "*.yaml"},
            default_filter="YAML files",
        )
        select_config.show()

    def load_config_file(self, file_selected):
        with open(file_selected, "r") as f:
            detector_config = yaml.safe_load(f)
        self.default_config_file = file_selected
        self.detector_config = detector_config
        self.display_detector_config(editable=True)
        self.correct_integrated_data()
        self.display_correction()

    def correct_integrated_data(self):
        o_corrrector = TimepixGeometryCorrection(
            raw_images=self.integrated_data, config=self.detector_config
        )
        self.corrected_integrated_data = o_corrrector.correct(display=False)[0]

    def save_new_config(self):
        """this method updates the detector_config dictionary with the values from the UI"""
        updated_config = {}
        children = self.vbox.children
        for box in children:  # exclude the button and output widget
            chip_label = box.children[0].value
            chip_name = chip_label.split(" ")[0][3:]  # Extract chip name from label
            xoffset_ui = box.children[1]
            yoffset_ui = box.children[2]
            updated_config[chip_name] = {
                "description": self.detector_config[chip_name]["description"],
                "xoffset": float(xoffset_ui.value),
                "yoffset": float(yoffset_ui.value),
            }
        self.detector_config = updated_config

    def on_recalculate_clicked(self, status):
        with self.out:
            self.out.clear_output()
            self.save_new_config()
            self.correct_integrated_data()
            self.display_correction()

    def display_detector_config(self, editable=False):
        items = []
        detector_config = self.detector_config
        for chip, params in detector_config.items():
            if editable:
                if "chip2" in chip:
                    disabled_state = True
                else:
                    disabled_state = not editable
            else:
                disabled_state = True

            chip_label = widgets.HTML(
                value=f"<b>{chip} ({params['description']})</b>",
                layout=widgets.Layout(width="25%"),
            )
            xoffset_ui = widgets.FloatText(
                value=params["xoffset"],
                description="X Offset:",
                disabled=disabled_state,
                layout=widgets.Layout(width="15%"),
            )
            yoffset_ui = widgets.FloatText(
                value=params["yoffset"],
                description="Y Offset:",
                disabled=disabled_state,
                layout=widgets.Layout(width="15%"),
            )
            box = widgets.HBox([chip_label, xoffset_ui, yoffset_ui])

            items.append(box)

        self.vbox = widgets.VBox(items)
        display(self.vbox)

        # if editable:
        #     self.recalculate_button = widgets.Button(description="Recalculate Correction",
        #                                              layout=widgets.Layout(margin='10px 0px 0px 0px', width="60%"),
        #                                              )
        #     # display(self.recalculate_button)
        #     self.recalculate_button.on_click(self.on_recalculate_clicked)
        #     display(self.recalculate_button)
        #     self.out = widgets.Output()
        #     display(self.out)

        display(HTML("<hr>"))

    def display_correction(self):
        default_size = 25

        # def preview_correction(x, y, size=5, show_markers=True, recalculate_button=True):
        def preview_correction(x, y, size=5, show_markers=True):
            self.fig, axs = plt.subplots(2, 2, figsize=(12, 12))

            # left size, original integrated data
            im00 = axs[0, 0].imshow(self.integrated_data, cmap="viridis")

            axs[0, 0].set_title("Original Integrated Data")
            plt.colorbar(im00, ax=axs[0, 0], shrink=0.6)
            if show_markers:
                # add "chips1" in top right corner of the image
                axs[0, 0].text(
                    ChipsLabelPosition.chip3[0],
                    ChipsLabelPosition.chip3[1],
                    "Chips3",
                    color="white",
                    fontsize=12,
                    weight="bold",
                    ha="left",
                    va="bottom",
                )
                axs[0, 0].text(
                    ChipsLabelPosition.chip2[0],
                    ChipsLabelPosition.chip2[1],
                    "Chips2",
                    color="white",
                    fontsize=12,
                    weight="bold",
                    ha="left",
                    va="top",
                )
                axs[0, 0].text(
                    ChipsLabelPosition.chip1[0],
                    ChipsLabelPosition.chip1[1],
                    "Chips1",
                    color="white",
                    fontsize=12,
                    weight="bold",
                    ha="right",
                    va="top",
                )
                axs[0, 0].text(
                    ChipsLabelPosition.chip4[0],
                    ChipsLabelPosition.chip4[1],
                    "Chips4",
                    color="white",
                    fontsize=12,
                    weight="bold",
                    ha="right",
                    va="bottom",
                )

                axs[0, 0].axvline(x=x, color="r", linestyle="--", alpha=0.2)
                axs[0, 0].axvline(x=x + size, color="r", linestyle="--", alpha=0.2)
                axs[0, 0].axhline(y=y, color="r", linestyle="--", alpha=0.2)
                axs[0, 0].axhline(y=y + size, color="r", linestyle="--", alpha=0.2)

                # show the edge of the chips
                axs[0, 0].axhline(y=255, color="white", linestyle="-", alpha=0.2)
                axs[0, 0].axhline(y=256, color="white", linestyle="-", alpha=0.2)
                axs[0, 0].axvline(x=255, color="white", linestyle="-", alpha=0.2)
                axs[0, 0].axvline(x=256, color="white", linestyle="-", alpha=0.2)

            rect_container = patches.Rectangle(
                (x, y), size, size, linewidth=1, edgecolor="yellow", facecolor="none"
            )
            axs[0, 0].add_patch(rect_container)

            # right side, corrected integrated data (placeholder)
            corrected_data = self.corrected_integrated_data
            im01 = axs[0, 1].imshow(corrected_data, cmap="viridis")
            plt.colorbar(im01, ax=axs[0, 1], shrink=0.6)
            axs[0, 1].set_title("Corrected Integrated Data")
            if show_markers:
                axs[0, 1].text(
                    ChipsLabelPosition.chip3[0],
                    ChipsLabelPosition.chip3[1],
                    "Chips3",
                    color="white",
                    fontsize=12,
                    weight="bold",
                    ha="left",
                    va="bottom",
                )
                axs[0, 1].text(
                    ChipsLabelPosition.chip2[0],
                    ChipsLabelPosition.chip2[1],
                    "Chips2",
                    color="white",
                    fontsize=12,
                    weight="bold",
                    ha="left",
                    va="top",
                )
                axs[0, 1].text(
                    ChipsLabelPosition.chip1[0],
                    ChipsLabelPosition.chip1[1],
                    "Chips1",
                    color="white",
                    fontsize=12,
                    weight="bold",
                    ha="right",
                    va="top",
                )
                axs[0, 1].text(
                    ChipsLabelPosition.chip4[0],
                    ChipsLabelPosition.chip4[1],
                    "Chips4",
                    color="white",
                    fontsize=12,
                    weight="bold",
                    ha="right",
                    va="bottom",
                )

                axs[0, 1].axvline(x=x, color="r", linestyle="--", alpha=0.2)
                axs[0, 1].axvline(x=x + size, color="r", linestyle="--", alpha=0.2)
                axs[0, 1].axhline(y=y, color="r", linestyle="--", alpha=0.2)
                axs[0, 1].axhline(y=y + size, color="r", linestyle="--", alpha=0.2)
            rect_container = patches.Rectangle(
                (x, y), size, size, linewidth=1, edgecolor="yellow", facecolor="none"
            )
            axs[0, 1].add_patch(rect_container)

            # zoom in second row
            im10 = axs[1, 0].imshow(
                self.integrated_data[y : y + size, x : x + size], cmap="viridis"
            )
            axs[1, 0].set_title(f"Zoomed Original Data (x: {x}, y: {y}, Size: {size}x)")
            plt.colorbar(im10, ax=axs[1, 0], shrink=0.6)

            im11 = axs[1, 1].imshow(
                corrected_data[y : y + size, x : x + size], cmap="viridis"
            )
            axs[1, 1].set_title(
                f"Zoomed Corrected Data (x: {x}, y: {y}, Size: {size}x)"
            )
            plt.colorbar(im11, ax=axs[1, 1], shrink=0.6)

            # plt.show()
            plt.tight_layout()

        height, width = self.integrated_data.shape

        # if self.detector_type_ui.value == DetectorType.CUSTOM:
        recalculate_button_disabled = False
        # else:
        #     recalculate_button_disabled = True

        display_preview_correction = interactive(
            preview_correction,
            x=widgets.IntSlider(
                min=0,
                max=width - 1,
                step=1,
                value=width // 2 - default_size // 2,
                description="x:",
                layout=widgets.Layout(width="50%"),
            ),
            y=widgets.IntSlider(
                min=0,
                max=height - 1,
                step=1,
                value=height // 2 - default_size // 2,
                description="y:",
                layout=widgets.Layout(width="50%"),
            ),
            size=widgets.IntSlider(
                min=2,
                max=100,
                step=1,
                value=default_size,
                description="Size:",
                layout=widgets.Layout(width="50%"),
            ),
            show_markers=widgets.Checkbox(value=True, description="Show guides/labels"),
            # recalculate_button=widgets.ToggleButton(description="Recalculate Correction",
            #                                         value=False,
            #                                         disabled=recalculate_button_disabled,
            #                                         layout=widgets.Layout(width="60%"),
            #                               )
        )
        display(display_preview_correction)

    def select_output_folder(self):
        _ = myfileselector.FileSelectorPanelWithJumpFolders(
            instruction="Select Output Folder ...",
            start_dir=self.working_dir,
            newdir_toolbar_button=True,
            next=self.perform_correction_of_entire_stack,
            type="directory",
            multiple=False,
            ipts_folder=self.ipts_path,
        )
        self.out = widgets.Output()
        display(self.out)

    def perform_correction_of_entire_stack(self, folder_selected):
        stack_of_images = self.working_data
        working_file_names = self.working_list_files

        with self.out:
            self.out.clear_output()
            display(
                HTML(
                    '<span style="font-size: 15px; color:blue">'
                    + "Starting correction of "
                    + str(len(stack_of_images))
                    + " files...</span>"
                )
            )

        for idx, img in tqdm(enumerate(stack_of_images)):
            o_corrector = TimepixGeometryCorrection(
                raw_images=img, config=self.detector_config
            )
            corrected_image = o_corrector.correct(display=False)
            base_name = os.path.basename(working_file_names[idx])
            output_file = os.path.join(folder_selected, f"Corrected_{base_name}")
            make_tiff(data=corrected_image[0], filename=output_file)

        # o_corrector = TimepixGeometryCorrection(raw_images=stack_of_images,
        #                                         config=self.detector_config)
        # corrected_images = o_corrector.correct(display=False)

        # for idx, corrected_image in enumerate(corrected_images):
        #     base_name = os.path.basename(working_file_names[idx])
        #     output_file = os.path.join(folder_selected, f"Corrected_{base_name}")
        #     plt.imsave(output_file, corrected_image, cmap='viridis')

        with self.out:
            self.out.clear_output()
            display(
                HTML(
                    '<span style="font-size: 15px; color:green">'
                    + str(len(stack_of_images))
                    + " files have been corrected and saved to "
                    + folder_selected
                    + "</span>"
                )
            )
