import pandas as pd
import numpy as np
from ipywidgets.widgets import interact
from ipywidgets import widgets
from IPython.core.display import display
import matplotlib.pyplot as plt
import os

from __code.ipywe import fileselector
from __code._utilities.file import retrieve_metadata_value_from_ascii_file
from __code.wave_front_dynamics.algorithms import Algorithms, ListAlgorithm


class WaveFrontDynamics:

    list_of_ascii_files = None
    list_of_original_image_files = None
    list_of_data = None
    list_of_data_prepared = None
    peak_value_arrays = {ListAlgorithm.sliding_average: None,
                         ListAlgorithm.change_point: None,
                         ListAlgorithm.error_function: None}

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

    def bin_data(self, data=None, bin_value=1, bin_type='Mean'):
        numpy_data = np.array(data).flatten()
        if bin_value == 1:
            return numpy_data

        nbr_bin = np.int(len(numpy_data) / bin_value)
        data_to_rebinned = numpy_data[0: nbr_bin * bin_value]
        binned_array_step1 = np.reshape(data_to_rebinned, [nbr_bin, bin_value])
        if bin_type == "Mean":
            binned_array = np.mean(binned_array_step1, axis=1)
        else:
            binned_array = np.median(binned_array_step1, axis=1)
        return binned_array

    def display_data(self):

        def plot_data(index, bin_value, bin_type):
            plt.figure(figsize=(5, 5))
            plt.title(os.path.basename(self.list_of_original_image_files[index]))

            _data = self.bin_data(data=self.list_of_data[index],
                                  bin_value=bin_value,
                                  bin_type=bin_type)
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

    def select_algorithm(self):
        self.algo_choice_ui = widgets.RadioButtons(options=['sliding average',
                                                            'error function',
                                                            'change point'])
        display(self.algo_choice_ui)

    def prepare_data(self):
        bin_value = self.display.widget.children[1].value
        bin_type = self.display.widget.children[2].value

        list_of_data_prepared = []
        for _data in self.list_of_data:
            _prepared_data = self.bin_data(data=_data,
                                           bin_value=bin_value,
                                           bin_type=bin_type)
            list_of_data_prepared.append(_prepared_data)

        self.list_of_data_prepared = list_of_data_prepared

    def get_algorithm_selected(self):
        algorithm_name = self.algo_choice_ui.value
        if algorithm_name == ListAlgorithm.sliding_average:
            return ListAlgorithm.sliding_average
        elif algorithm_name == ListAlgorithm.error_function:
            return ListAlgorithm.error_function
        elif algorithm_name == ListAlgorithm.change_point:
            return ListAlgorithm.change_point
        else:
            raise NotImplementedError("Algorithm not implemented yet!")

    def calculate(self):
        algorithm_selected = self.get_algorithm_selected()
        self.prepare_data()
        list_of_data_prepared = self.list_of_data_prepared

        o_algo = Algorithms(list_data=list_of_data_prepared,
                            ignore_first_dataset=False,
                            algorithm_selected=algorithm_selected)
        peak_value_array = o_algo.get_peak_value_array(algorithm_selected=algorithm_selected)
        self.peak_value_arrays[algorithm_selected] = peak_value_array

        def plot_data(index):
            plt.figure(figsize=(5, 5))
            plt.title(os.path.basename(self.list_of_original_image_files[index]))
            peak_value = peak_value_array[index]
            plt.axvline(peak_value, color='red')
            plt.plot(list_of_data_prepared[index])
            plt.xlabel("Pixel")
            plt.ylabel("Mean Counts")

        display = interact(plot_data,
                           index=widgets.IntSlider(min=0,
                                                   max=len(self.list_of_ascii_files) - 1,
                                                   continuous_update=False))

    def wave_front_vs_file_index(self):
        algorithm_selected = self.get_algorithm_selected()
        peak_value_array = self.peak_value_arrays[algorithm_selected]

        plt.figure(figsize=(5, 5))
        plt.title(f"Wave front for algorithm {algorithm_selected}")
        plt.plot(peak_value_array, '*')
        plt.xlabel("File index")
        plt.ylabel("Wave front position (pixel)")
