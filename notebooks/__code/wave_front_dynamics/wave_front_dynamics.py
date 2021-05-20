import pandas as pd
import numpy as np
from ipywidgets.widgets import interact
from ipywidgets import widgets
import matplotlib.pyplot as plt
import os

from __code.ipywe import fileselector
from __code._utilities.file import retrieve_metadata_value_from_ascii_file


class WaveFrontDynamics:

    list_of_ascii_files = None
    list_of_original_image_files = None
    list_of_data = None

    def __init__(self, working_dir="~/"):
        self.working_dir = working_dir

    def select_data(self):
        self.list_data_widget = fileselector.FileSelectorPanel(instruction='select list of ascii profile data ...',
                                                               start_dir=self.working_dir,
                                                               next=self.load_data,
                                                               filters={"ASCII": "*.txt"},
                                                               default_filter="ASCII",
                                                               multiple=True)
        self.list_data_widget.show()

    def load_data(self, list_of_ascii_files=None):
        if list_of_ascii_files is None:
            return

        list_of_ascii_files.sort()
        self.list_of_ascii_files = list_of_ascii_files
        list_of_data = []
        list_of_original_image_files = []
        for _file in list_of_ascii_files:
            _data = pd.read_csv(_file,
                                skiprows=5,
                                delimiter=",",
                                names=['pixel', 'mean counts'],
                                dtype=np.float,
                                index_col=0)
            list_of_data.append(_data)
            _original_image_file = retrieve_metadata_value_from_ascii_file(filename=_file,
                                                                           metadata_name="# source image")
            list_of_original_image_files.append(_original_image_file)

        self.list_of_data = list_of_data
        self.list_of_original_image_files = list_of_original_image_files

    def display_data(self):

        def bin_data(data, bin_value, bin_type):

            numpy_data = np.array(data).flatten()
            if bin_value == 1:
                return numpy_data

            nbr_bin = np.int(len(numpy_data) / bin_value)
            data_to_rebinned = numpy_data[0: nbr_bin*bin_value]
            binned_array_step1 = np.reshape(data_to_rebinned, [nbr_bin, bin_value])
            if bin_type == "Mean":
                binned_array = np.mean(binned_array_step1, axis=1)
            else:
                binned_array = np.median(binned_array_step1, axis=1)
            return binned_array

        def plot_data(index, bin_value, bin_type):
            plt.figure(figsize=(5, 5))
            plt.title(os.path.basename(self.list_of_original_image_files[index]))

            _data = bin_data(self.list_of_data[index], bin_value, bin_type)
            plt.plot(_data)
            plt.xlabel("Pixel")
            plt.ylabel("Mean Counts")

        self.display = interact(plot_data,
                                index=widgets.IntSlider(min=0,
                                                        max=len(self.list_of_ascii_files)-1,
                                                        continuous_update=False),
                                bin_value=widgets.IntSlider(min=1,
                                                            max=30,
                                                            continuous_update=False),
                                bin_type=widgets.RadioButtons(options=['Mean', 'Median']))
