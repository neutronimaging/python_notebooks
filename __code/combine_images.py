import glob
import os
import ipywe.fileselector

from ipywidgets import widgets
from IPython.core.display import display, HTML
import numpy as np

from __code import file_handler
from NeuNorm.normalization import Normalization


class CombineImages(object):
    working_dir = ''

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_files(self):
        self.files_list_widget = ipywe.fileselector.FileSelectorPanel(instruction='select files to combine',
                                                                      start_dir=self.working_dir,
                                                                      multiple=True)
        self.files_list_widget.show()

    def how_to_combine(self):
        self.combine_method = widgets.RadioButtons(options=['add', 'mean'],
                                                   value='add')
        display(self.combine_method)

    def select_output_folder(self):
        self.output_folder_widget = ipywe.fileselector.FileSelectorPanel(instruction='select where to create the ' + \
                                                                                     'combined image ...',
                                                                         start_dir=self.working_dir,
                                                                         type='directory')

        self.output_folder_widget.show()

    def merging(self):
        """combine images using algorithm provided"""

        list_files = self.files_list_widget.selected
        nbr_files = len(list_files)

        # get merging algorithm
        merging_algo = self.combine_method.value
        algorithm = self.__add
        if merging_algo == 'mean':
            algorithm = self.__mean

        # get output folder
        output_folder = os.path.abspath(self.output_folder_widget.selected)

        o_load = Normalization()
        o_load.load(file=list_files, notebook=True)
        _data = o_load.data['sample']['data']

        merging_ui = widgets.HBox([widgets.Label("Merging Progress",
                                                 layout=widgets.Layout(width='20%')),
                                   widgets.IntProgress(max=2)])
        display(merging_ui)
        w1 = merging_ui.children[1]

        combined_data = self.__merging_algorithm(algorithm, _data)
        w1.value = 1

        _new_name = self.__create_merged_file_name(list_files_names=o_load.data['sample']['file_name'])
        output_file_name = os.path.join(output_folder, _new_name)

        file_handler.save_data(data=combined_data, filename=output_file_name)

        w1.value = 2

        display(HTML('<span style="font-size: 20px; color:blue">File created: ' + \
                     os.path.basename(output_file_name) + '</span>'))
        display(HTML('<span style="font-size: 20px; color:blue">In Folder: ' + \
                     output_folder + '</span>'))

    def __create_merged_file_name(self, list_files_names=[]):
        """Create the new base name using a combine name of all the input file

        :param list_files_names: ['/Users/j35/image001.fits','/Users/j35/iamge002.fits']
        :return:
            'image001_image002.fits'
        """
        ext = ''
        list_base_name = []
        for _file in list_files_names:
            basename = os.path.basename(_file)
            [_name, ext] = os.path.splitext(basename)
            list_base_name.append(_name)

        return '_'.join(list_base_name) + ext

    def __add(self, data_array):
        return np.sum(data_array, axis=0)

    def __mean(self, data_array):
        return np.mean(data_array, axis=0)

    def __merging_algorithm(self, function_, *args):
        return function_(*args)



