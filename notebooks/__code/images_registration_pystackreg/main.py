import matplotlib.pyplot as plt
from ipywidgets import interactive
import ipywidgets as widgets
from IPython.display import display, HTML
from matplotlib.widgets import RectangleSelector
import numpy as np
import matplotlib.patches as patches
from pystackreg import StackReg

from __code.ipywe import fileselector
from __code._utilities.file import retrieve_list_of_most_dominant_extension_from_folder
from __code._utilities.images import read_img_stack


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
        print("Data have been load!")

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

        fig = plt.figure(layout='constrained')
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

        x_corners = selector.corners[0]
        y_corners = selector.corners[1]

        x0 = int(x_corners[0])
        x1 = int(x_corners[2])
        y0 = int(y_corners[0])
        y1 = int(y_corners[2])

        if (x0 == 0) and (y0 == 0) and (x1 == 0) and (y1 == 1):
            first_image = self.stack[0]
            height, width = np.shape(first_image)
            x1 = width - 1
            y1 = height - 1

        return x0, x1, y0, y1

    def perform_cropping(self):

        x0, x1, y0, y1 = self._get_crop_region(self.selector_unregistered)

        _stack_cropped = []
        for _image in self.stack:
            _image = np.array(_image)
            _image_cropped = _image[y0:y1, x0:x1]
            _stack_cropped.append(_image_cropped)
        self.stack_cropped = np.array(_stack_cropped)

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

        fig3 = plt.figure(layout='crop registered')
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

    def perform_cropping(self):

        x0, x1, y0, y1 = self._get_crop_region(self.selector_registered)

        _final_stack_cropped = []
        for _image in self.stack:
            _image = np.array(_image)
            _image_cropped = _image[y0:y1, x0:x1]
            _final_stack_cropped.append(_image_cropped)
        self.final_stack_cropped = np.array(_final_stack_cropped)

        fig, ax = plt.subplots(ncols=1, nrows=1,
                               num="Cropped images to export",
                               figsize=(5, 5))

        image = ax.imshow(self.stack_cropped[0], vmin=0, vmax=1)
        ax.set_title("First image")
        cb = plt.colorbar(image, ax=ax)

    def export(self):
        self.output_folder_widget = fileselector.FileSelectorPanel(instruction='select output folder',
                                                                 start_dir=self.working_dir,
                                                                 type='directory',
                                                                 next=self.export_images,
                                                                 multiple=False)
        self.output_folder_widget.show()
