import matplotlib.pyplot as plt
from ipywidgets import interactive
import ipywidgets as widgets
from IPython.display import display
from matplotlib.widgets import RectangleSelector
import numpy as np
import matplotlib.patches as patches

from __code.ipywe import fileselector
from __code._utilities.file import retrieve_list_of_most_dominant_extension_from_folder
from __code._utilities.images import read_img_stack


class ImagesRegistrationPystackreg:

    working_dir = None

    def __init__(self, working_dir=None):
        self.working_dir = working_dir

    def select_folder(self):
        self.folder_list_widget = fileselector.FileSelectorPanel(instruction='select folder of images to register',
                                                                 start_dir=self.working_dir,
                                                                 type='directory',
                                                                 next=self.load_images,
                                                                 multiple=False)
        self.folder_list_widget.show()

    def load_images(self, folder_name=None):
        self.folder_name = folder_name

        # retrieve list of files
        self.list_of_files, ext = retrieve_list_of_most_dominant_extension_from_folder(folder=folder_name)

        self.stack = read_img_stack(list_files=self.list_of_files,
                                    ext=ext)

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

        # def _toggle_selector(event):
        #     print('Key pressed.')
        #     if event.key == 't':
        #         for selector in selectors:
        #             name = type(selector).__name__
        #             if selector.active:
        #                 print(f'{name} deactivated.')
        #                 selector.set_active(False)
        #             else:
        #                 print(f'{name} activated.')
        #                 selector.set_active(True)

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
        self.selector = RectangleSelector(
            ax,
            _select_callback,
            useblit=True,
            button=[1, 3],  # disable middle button
            minspanx=5, minspany=5,
            spancoords='pixels',
            interactive=True)

        # Activate the toggling of selection in the figure
        # It is not needed but a nice addition
        # fig.canvas.mpl_connect('key_press_event', _toggle_selector)
        #ax.set_title("Press 't' to turn ON the selection.\n" + ax.get_title());
        ax.set_title("Click and drag to select region to crop")
