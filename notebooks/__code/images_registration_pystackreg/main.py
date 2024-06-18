import os.path

import matplotlib.pyplot as plt
from ipywidgets import interactive
import ipywidgets as widgets
from IPython.display import display, HTML
from matplotlib.widgets import RectangleSelector
import numpy as np
import matplotlib.patches as patches
from pystackreg import StackReg
from tqdm import tqdm
from PIL import Image
import copy

from __code.ipywe import fileselector
from __code._utilities.file import retrieve_list_of_most_dominant_extension_from_folder
from __code._utilities.file import make_or_reset_folder
from __code._utilities.images import read_img_stack
from __code._utilities.time import get_current_time_in_special_file_name_format
from __code._utilities.json import save_json


class AlgoList:

    translation = StackReg.TRANSLATION
    rigid_body = StackReg.RIGID_BODY
    scaled_rotation = StackReg.SCALED_ROTATION
    affine = StackReg.AFFINE
    bilinear = StackReg.BILINEAR


class ReferenceList:

    previous = 'previous'
    first = 'first'
    mean = 'mean'


def props(cls):
    return [i for i in cls.__dict__.keys() if i[:1] != '_']


class ImagesRegistrationPystackreg:

    working_dir = None

    selector_unregistered = None
    selector_registered = None

    crop = {'before registration': None,
            'after registration': None}

    def __init__(self, working_dir=None):
        self.working_dir = working_dir

    def select_folder(self):
        self.folder_widget = fileselector.FileSelectorPanel(instruction='select folder of images to register',
                                                            start_dir=self.working_dir,
                                                            type='directory',
                                                            next=self.load_images,
                                                            multiple=False)
        self.folder_widget.show()

    def load_images(self, folder_name=None):
        self.folder_name = folder_name

        # retrieve list of files
        self.list_of_files, ext = retrieve_list_of_most_dominant_extension_from_folder(folder=folder_name)

        self.stack = read_img_stack(list_files=self.list_of_files,
                                    ext=ext)

        display(HTML("Data have been loaded!"))
        print("Data have been loaded!")

    def display_unregistered(self):

        def preview_unregistered(image_index, vmin=0.8, vmax=1.2):
            fig, ax = plt.subplots(ncols=3, nrows=1,
                                   num="Unregistered images",
                                   figsize=(15, 5))
            ax[0].imshow(self.stack[0], vmin=0, vmax=1)
            ax[0].set_title("First image")

            ax[1].imshow(self.stack[image_index], vmin=0, vmax=1)
            ax[1].set_title(f"Image #{image_index}")

            image = ax[2].imshow(np.divide(self.stack[image_index], self.stack[0]), vmin=vmin, vmax=vmax)
            ax[2].set_title(f"Image[{image_index}] / First image")
            cb = plt.colorbar(image, ax=ax[2])

        v = interactive(preview_unregistered,
                        image_index=widgets.IntSlider(min=0,
                                                      max=len(self.list_of_files) - 1,
                                                      value=1),
                        vmin=widgets.FloatSlider(min=0,
                                                 max=2,
                                                 value=0.8),
                        vmax=widgets.FloatSlider(min=0,
                                                 max=2,
                                                 value=1.2),
                        )
        display(v)

    def crop_unregistered_images(self):

        def _select_callback(eclick, erelease):
            """
            Callback for line selection.

            *eclick* and *erelease* are the press and release events.
            """
            x1, y1 = eclick.xdata, eclick.ydata
            x2, y2 = erelease.xdata, erelease.ydata

        # fig = plt.figure(layout='constrained')
        fig = plt.figure()
        ax = fig.subplots(1)

        img = self.stack[0]
        ax.imshow(img)

        ax.set_title(f"Click and drag to select a rectangular ROI.")
        self.selector_unregistered = RectangleSelector(
                                    ax,
                                    _select_callback,
                                    useblit=True,
                                    button=[1, 3],  # disable middle button
                                    minspanx=5, minspany=5,
                                    spancoords='pixels',
                                    interactive=True)

        ax.set_title("Click and drag to select region to crop")

    def _get_crop_region(self, selector):

        data_have_been_cropped = True

        x_corners = selector.corners[0]
        y_corners = selector.corners[1]

        x0 = int(x_corners[0])
        x1 = int(x_corners[2])
        y0 = int(y_corners[0])
        y1 = int(y_corners[2])

        if (x0 == 0) and (y0 == 0) and (x1 == 0) and (y1 == 1):
            data_have_been_cropped = False

            first_image = self.stack[0]
            height, width = np.shape(first_image)
            x1 = width - 1
            y1 = height - 1

        return x0, x1, y0, y1, data_have_been_cropped

    def perform_cropping(self):

        x0, x1, y0, y1, data_have_been_cropped = self._get_crop_region(self.selector_unregistered)
        self.crop['before registration'] = {'x0': x0,
                                            'x1': x1,
                                            'y0': y0,
                                            'y1': y1}

        if data_have_been_cropped:
            _stack_cropped = []
            for _image in self.stack:
                _image = np.array(_image)
                _image_cropped = _image[y0:y1, x0:x1]
                _stack_cropped.append(_image_cropped)
            self.stack_cropped = np.array(_stack_cropped)
        else:
            self.stack_cropped = copy.deepcopy(self.stack)

        fig, ax = plt.subplots(ncols=1, nrows=1,
                               num="Cropped images",
                               figsize=(5, 5))

        image = ax.imshow(self.stack_cropped[0], vmin=0, vmax=1)
        ax.set_title("First image")
        cb = plt.colorbar(image, ax=ax)

    def define_parameters(self):
        label1 = widgets.Label("Types of registration:")
        list_options = props(AlgoList)
        self.algo_options = widgets.RadioButtons(options=list_options)
        col1 = widgets.VBox([label1, self.algo_options])

        label2 = widgets.Label("Image of reference:")
        list_options_ref = props(ReferenceList)
        self.reference_options = widgets.RadioButtons(options=list_options_ref)
        col2 = widgets.VBox([label2, self.reference_options])

        row = widgets.HBox([col1, col2])
        display(row)

    def _get_registration_type(self, registration_name):
        return getattr(AlgoList, registration_name)

    def run(self):
        registration_name = self.algo_options.value
        image_reference = self.reference_options.value
        registration_type = self._get_registration_type(registration_name)

        o_sr = StackReg(registration_type)
        self.registered_stack = o_sr.register_transform_stack(self.stack_cropped,
                                                              reference=image_reference,
                                                              verbose=True)

        self.display_registered()

    def display_registered(self):

        self.fig2 = None

        def preview_registered(image_index, vmin=0.8, vmax=1.2):
            if self.fig2:
                self.fig2.clear()

            self.fig2, ax2 = plt.subplots(ncols=3, nrows=1,
                                     num="Registered images",
                                     figsize=(15, 5))

            ax2[0].imshow(self.registered_stack[0], vmin=0, vmax=1)
            ax2[0].set_title("First image")

            ax2[1].imshow(self.registered_stack[image_index], vmin=0, vmax=1)
            ax2[1].set_title(f"Image #{image_index}")

            image = ax2[2].imshow(np.divide(self.registered_stack[image_index],
                                            self.registered_stack[0]),
                                 vmin=vmin, vmax=vmax)
            ax2[2].set_title(f"Image[{image_index}] / First image")
            cb = plt.colorbar(image, ax=ax2[2])
            # display(fig)

        v2 = interactive(preview_registered,
                        image_index=widgets.IntSlider(min=0,
                                                      max=len(self.list_of_files) - 1,
                                                      value=1),
                        vmin=widgets.FloatSlider(min=0,
                                                 max=2,
                                                 value=0.8),
                        vmax=widgets.FloatSlider(min=0,
                                                 max=2,
                                                 value=1.2),
                        )
        display(v2)

    def crop_registered_images(self):

        def _select_callback(eclick, erelease):
            """
            Callback for line selection.

            *eclick* and *erelease* are the press and release events.
            """
            x1, y1 = eclick.xdata, eclick.ydata
            x2, y2 = erelease.xdata, erelease.ydata

        # fig3 = plt.figure(layout='constrained')  # for matplotlib 3.8.3
        fig3 = plt.figure()
        ax = fig3.subplots(1)

        img = self.registered_stack[0]
        ax.imshow(img)

        ax.set_title(f"Click and drag to select a rectangular ROI.")
        self.selector_registered = RectangleSelector(
                                    ax,
                                    _select_callback,
                                    useblit=True,
                                    button=[1, 3],  # disable middle button
                                    minspanx=5, minspany=5,
                                    spancoords='pixels',
                                    interactive=True)

        ax.set_title("Click and drag to select region to crop")

    def perform_cropping_for_export(self):

        x0, x1, y0, y1, data_have_been_cropped = self._get_crop_region(self.selector_registered)
        self.crop['after registration'] = {'x0': x0,
                                           'x1': x1,
                                           'y0': y0,
                                           'y1': y1}

        if data_have_been_cropped:
            _final_stack_cropped = []
            for _image in self.registered_stack:
                _image = np.array(_image)
                _image_cropped = _image[y0:y1, x0:x1]
                _final_stack_cropped.append(_image_cropped)
            self.final_stack_cropped = np.array(_final_stack_cropped)
        else:
            self.final_stack_cropped = copy.deepcopy(self.registered_stack)

        # fig4 = plt.figure(layout='constrained')
        fig4 = plt.figure()
        ax4 = fig4.subplots(1)

        image = ax4.imshow(self.final_stack_cropped[0], vmin=0, vmax=1)
        ax4.set_title("First image")
        plt.colorbar(image, ax=ax4)

    def export(self):
        display(HTML("<span><b>Exporting the registered data:</b></span>"))
        self.output_label = widgets.Label(f" IN PROGRESS")
        display(self.output_label)

        self.output_folder_widget = fileselector.FileSelectorPanel(instruction='select output folder',
                                                                   start_dir=self.working_dir,
                                                                   type='directory',
                                                                   next=self.export_images,
                                                                   multiple=False)
        self.output_folder_widget.show()

    def export_images(self, output_folder):

        output_folder = os.path.abspath(output_folder)
        registered_crop_stack = self.final_stack_cropped
        list_file_names = self.list_of_files

        # create output folder
        source_folder = os.path.basename(os.path.dirname(list_file_names[0]))
        time_stamp = get_current_time_in_special_file_name_format()
        full_output_folder_name = os.path.join(output_folder, f"{source_folder}_{time_stamp}")
        make_or_reset_folder(full_output_folder_name)

        for i, file_name in tqdm(enumerate(list_file_names)):
            short_file_name = os.path.basename(file_name)
            full_output_file_name = os.path.join(full_output_folder_name, short_file_name)
            _image = Image.fromarray(registered_crop_stack[i])
            _image.save(full_output_file_name)

        # create json with parameters used
        metadata = {'input folder': source_folder,
                    'number of files': len(list_file_names),
                    'crop': self.crop,
                    'registration': {'type': self.algo_options.value,
                                     'image of reference': self.reference_options.value}
                    }
        json_file_name = os.path.join(full_output_folder_name, 'config.json')
        save_json(json_file_name, metadata)

        self.output_label.value = f"DONE! (Registered files have been created in {full_output_folder_name})"
        display(HTML(f"Registered files have been created in {full_output_folder_name}"))
