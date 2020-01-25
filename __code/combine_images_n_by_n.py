import os
import ipywe.fileselector
from scipy.stats.mstats import gmean
import glob

from ipywidgets import widgets
from IPython.core.display import display, HTML
import numpy as np

from __code import file_handler
from NeuNorm.normalization import Normalization


class CombineImagesNByN(object):
    working_dir = ''

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_folder(self):
        self.folder_widget = ipywe.fileselector.FileSelectorPanel(instruction='select folder with images to combine',
                                                                  start_dir=self.working_dir,
                                                                  type='directory',
                                                                  next=self._retrieve_number_of_files,
                                                                  multiple=False)
        self.folder_widget.show()

    def _retrieve_number_of_files(self, folder_selected):
        [self.list_files, _] = file_handler.retrieve_list_of_most_dominand_extension_from_folder(folder=folder_selected)

    def how_to_combine(self):
        _file = open("__docs/combine_images/geometric_mean.png", 'rb')
        _geo_image = _file.read()
        geo_box = widgets.HBox([widgets.Label("Geometric Mean",
                                              layout=widgets.Layout(width='20%')),
                                widgets.Image(value=_geo_image,
                                              format='png')])
        _file = open("__docs/combine_images/algebric_mean.png", 'rb')
        _alge_image = _file.read()
        alge_box = widgets.HBox([widgets.Label("Arithmetic Mean",
                                              layout=widgets.Layout(width='20%')),
                                widgets.Image(value=_alge_image,
                                              format='png')])

        self.combine_method = widgets.RadioButtons(options=['add', 'arithmetic mean', 'geometric mean'],
                                                   value='arithmetic mean')

        vertical = widgets.VBox([alge_box, geo_box, self.combine_method])
        display(vertical)

    def how_many_files(self):
        nbr_files = len(self.list_files)
        radio_list_string = [str(_index) for _index in np.arange(2, nbr_files + 1)]

        vertical_layout = widgets.VBox([widgets.Dropdown(options=radio_list_string,
                                                      value=radio_list_string[0]),
                                     widgets.Label("",
                                                   layout=widgets.Layout(width='100%'))])
        display(vertical_layout)

        self.bin_size_ui = vertical_layout.children[0]
        self.bin_size_label = vertical_layout.children[1]

        self.bin_size_ui.observe(self.update_how_many_files, names='value')
        self.update_how_many_files()

    def _get_number_of_files_will_be_created(self, bin_value=2):
        return np.int(len(self.list_files)/bin_value)

    def update_how_many_files(self, bin_value_object=None):
        if bin_value_object:
            bin_value = np.int(bin_value_object['new'])
            nbr_images = self._get_number_of_files_will_be_created(bin_value=bin_value)
        else:
            nbr_images = self._get_number_of_files_will_be_created()
        message = "You are about to create {} files out of {} files selected.".format(nbr_images,
                                                                                      len(self.list_files))
        self.bin_size_label.value = message

    def select_output_folder(self):
        self.output_folder_widget = ipywe.fileselector.FileSelectorPanel(instruction='select where to create the ' + \
                                                                                     'combined image ...',
                                                                         start_dir=self.working_dir,
                                                                         next=self.merging,
                                                                         type='directory')

        self.output_folder_widget.show()

    def __get_formated_merging_algo_name(self):
        _algo = self.combine_method.value
        if _algo =='arithmetic mean':
            return 'arithmetic_mean'
        elif _algo == 'geometric mean':
            return 'geometric_mean'
        else:
            return _algo

    def create_list_of_files_to_merge(self):
        bin_value = np.int(self.bin_size_ui.value)
        self.bin_value = bin_value
        list_files = self.list_files
        nbr_files = len(list_files)

        dict_list_files = {}
        global_index = 0
        for _index in np.arange(0, nbr_files, bin_value):
            # make sure we don't go over board
            right_threshold = _index + bin_value
            if right_threshold >= nbr_files:
                break
            dict_list_files[global_index] = list_files[_index: _index+bin_value]
            global_index += 1

        self.dict_list_files = dict_list_files
        return dict_list_files

    def get_merging_algorithm(self):
        # get merging algorithm
        merging_algo = self.combine_method.value
        algorithm = self.__add
        if merging_algo == 'arithmetic mean':
            algorithm = self.__arithmetic_mean
        elif merging_algo == 'geometric mean':
            algorithm = self.__geo_mean
        return algorithm

    def merging(self, output_folder):
        """combine images using algorithm provided"""

        dict_list_files = self.create_list_of_files_to_merge()
        nbr_of_files_to_create = len(dict_list_files.keys())
        algorithm = self.get_merging_algorithm()

        horizontal_layout = widgets.HBox([widgets.Label("Merging Progress",
                                                        layout=widgets.Layout(width='20%')),
                                          widgets.IntProgress(max=len(dict_list_files.keys()),
                                                              value=0,
                                                              layout=widgets.Layout(width='50%'))])
        global_slider = horizontal_layout.children[1]
        display(horizontal_layout)

        for _key in dict_list_files.keys():
            list_files = dict_list_files[_key]
            o_load = Normalization()
            o_load.load(file=list_files, notebook=False)
            _data = o_load.data['sample']['data']
            metadata = o_load.data['sample']['metadata']

            combined_data = self.__merging_algorithm(algorithm, _data)
            del o_load

            output_file_name = self.__create_merged_file_name(bin_value=self.bin_value,
                                                              list_files_names=list_files,
                                                              index=_key)
            o_save = Normalization()
            o_save.load(data=combined_data)
            o_save.data['sample']['metadata'] = metadata
            o_save.data['sample']['file_name'] = [output_file_name]
            o_save.export(folder=output_folder, data_type='sample')
            del o_save

            global_slider.value += 1

        global_slider.close()

        display(HTML('<span style="font-size: 20px; color:blue">' + nbr_of_files_to_create +
                     ' files have been created in ' + output_folder + '</span>'))

    def __create_merged_file_name(self, list_files_names=[], bin_value=2, index=0):
        """Create the new base name using a combine name of all the input file
        """
        # ext = ''
        # list_base_name = []
        # for _file in list_files_names:
        #     basename = os.path.basename(_file)
        #     [_name, ext] = os.path.splitext(basename)
        #     list_base_name.append(_name)
        #
        # return ('_'.join(list_base_name), ext)
        return '{}_files_combined_{}.tiff'.format(bin_value, index)

    def __add(self, data_array):
        return np.sum(data_array, axis=0)

    def __arithmetic_mean(self, data_array):
        return np.mean(data_array, axis=0)

    def __geo_mean(self, data_array):
        return gmean(data_array, axis=0)

    def __merging_algorithm(self, function_, *args):
        return function_(*args)



