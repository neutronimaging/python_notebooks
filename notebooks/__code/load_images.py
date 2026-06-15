import os

import numpy as np
from IPython.display import HTML, display
from ipywidgets import widgets
from NeuNorm.normalization import Normalization

# from __code import file_handler
from __code.ipywe import fileselector

TIFF_EXTENSIONS = (".tif", ".tiff")


class LoadImages:
    nbr_files = 0
    images_dimension = {"height": 0, "width": 0}

    working_data = []
    working_dir = ""
    list_images = []

    # use with virtual array (data are loaded on the fly)
    data_dict = None

    def __init__(self, working_dir=""):
        self.working_dir = working_dir

    def select_images(self, use_next=False, virtual_load=False):
        if virtual_load:
            self._next_step = self.prepare_images_array
        else:
            self._next_step = self.load_images if use_next else None

        self.message = widgets.Label("SELECT THE FOLDER OF IMAGES YOU WANT TO WORK ON ...")
        display(self.message)

        self.list_images_ui = fileselector.FileSelectorPanel(
            instruction="Select Folder of Images...",
            type="directory",
            multiple=False,
            next=self.folder_selected,
            start_dir=self.working_dir,
        )
        self.list_images_ui.show()

    @staticmethod
    def get_list_of_tiff_in_folder(folder):
        """Return the sorted list of tiff files directly contained in ``folder``."""
        if not (folder and os.path.isdir(folder)):
            return []
        list_tiff = [
            os.path.join(folder, _file)
            for _file in os.listdir(folder)
            if _file.lower().endswith(TIFF_EXTENSIONS) and os.path.isfile(os.path.join(folder, _file))
        ]
        return sorted(list_tiff)

    def retrieve_list_of_tiff(self, folder):
        """Find tiff files in ``folder``, falling back to the first subfolder that has any.

        Returns
        -------
        tuple[list[str], str]
            The sorted list of tiff file paths and the folder they were found in.
            The list is empty (and the folder is the originally selected one) when no
            tiff images are found in ``folder`` or any of its immediate subfolders.
        """
        list_tiff = self.get_list_of_tiff_in_folder(folder)
        if list_tiff:
            return list_tiff, folder

        # no tiff directly in the selected folder; look for a subfolder that contains some
        subfolders = sorted(
            os.path.join(folder, _entry)
            for _entry in os.listdir(folder)
            if os.path.isdir(os.path.join(folder, _entry))
        )
        for subfolder in subfolders:
            list_tiff = self.get_list_of_tiff_in_folder(subfolder)
            if list_tiff:
                return list_tiff, subfolder

        return [], folder

    def folder_selected(self, folder):
        """Resolve the selected folder to a list of tiff files and continue loading."""
        list_images, source_folder = self.retrieve_list_of_tiff(folder)

        if not list_images:
            self.message.close()
            display(
                HTML(
                    '<span style="font-size: 15px; color:red">The folder '
                    + str(folder)
                    + " is empty and does not contain tiff images.</span>"
                )
            )
            return

        if source_folder != folder:
            display(
                HTML(
                    '<span style="font-size: 15px; color:blue">No tiff images in '
                    + str(folder)
                    + " -> loading tiff images found in "
                    + str(source_folder)
                    + " instead.</span>"
                )
            )

        if self._next_step is not None:
            self._next_step(list_images)

    def prepare_images_array(self, list_images):
        self.message.close()
        self.list_images = list_images

        self.data_dict = {}
        if list_images == []:
            return

        for index, image in enumerate(list_images):
            self.data_dict[index] = {"filename": image, "data": None}

    def load_images(self, list_images=[]):
        if list_images == []:
            list_images = self.list_images_ui.selected

        self.o_norm = Normalization()
        self.o_norm.load(file=list_images, notebook=True, check_shape=False)

        self.nbr_files = len(list_images)
        [self.images_dimension["height"], self.images_dimension["width"]] = np.shape(
            self.o_norm.data["sample"]["data"][0]
        )
        self.working_data = np.squeeze(self.o_norm.data["sample"]["data"])
        self.list_images = list_images
