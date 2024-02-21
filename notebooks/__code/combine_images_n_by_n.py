from scipy.stats.mstats import gmean
from ipywidgets import widgets
from IPython.core.display import display, HTML
import numpy as np
from pathlib import Path, PurePath
import os
import glob

from NeuNorm.normalization import Normalization

from __code import file_handler
from __code.ipywe import fileselector

FILE_PREFIX = "image"


class CombineImagesNByN(object):
    working_dir = ''

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

        self.combine_method = None
        self.folder_widget = None
        self.bin_size_ui = None
        self.bin_size_label = None
        self.output_folder_widget = None
        self.timespectra_file_name = None

    def select_folder(self):
            self.folder_widget = fileselector.FileSelectorPanel(instruction='select folder with images to combine',
                                                                start_dir=self.working_dir,
                                                                type='directory',
                                                                next=self.post_select_folder,
                                                                multiple=False)
            self.folder_widget.show()

    def post_select_folder(self, folder_selected):
        self.input_folder_selected = folder_selected
        self._retrieve_number_of_files()
        self._check_if_working_with_time_spectra()

    def _retrieve_number_of_files(self):
        self.base_working_dir = str(PurePath(Path(self.input_folder_selected).parent).name)
        [self.list_files, _] = file_handler.retrieve_list_of_most_dominant_extension_from_folder(
                folder=self.input_folder_selected)

    def _check_if_working_with_time_spectra(self):
        input_folder = self.input_folder_selected
        list_files = glob.glob(input_folder + '/*')
        for _file in list_files:
            if "_Spectra.txt" in _file:
                self.timespectra_file_name = _file

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
        self.output_folder_widget = fileselector.FileSelectorPanel(instruction='select where to create the ' + \
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
        algorithm = CombineImagesNByN.add
        if merging_algo == 'arithmetic mean':
            algorithm = CombineImagesNByN.arithmetic_mean
        elif merging_algo == 'geometric mean':
            algorithm = CombineImagesNByN.geo_mean
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

        output_folder_name = CombineImagesNByN.__create_output_folder_name(
                output_folder=output_folder,
                base_file_name=self.base_working_dir,
                bin_value=self.bin_value)
        file_handler.make_or_reset_folder(folder_name=output_folder_name)

        output_timespectra_file_name = os.path.join(output_folder_name,
                                                    CombineImagesNByN.__create_timestamp_file_name())
        CombineImagesNByN.combine_timespectra(input_timespectra_file_name=self.timespectra_file_name,
                                              output_timespectra_file_name=output_timespectra_file_name,
                                              bin_value=self.bin_value,
                                              merging_algorithm=algorithm)

        for _key in dict_list_files.keys():
            list_files = dict_list_files[_key]
            o_load = Normalization()
            o_load.load(file=list_files, notebook=False)
            _data = o_load.data['sample']['data']
            metadata = o_load.data['sample']['metadata']

            combined_data = CombineImagesNByN.merging_algorithm(algorithm, _data)
            del o_load

            output_file_name = CombineImagesNByN.__create_merged_file_name(index=_key)
            o_save = Normalization()
            o_save.load(data=combined_data)
            o_save.data['sample']['metadata'] = metadata
            o_save.data['sample']['file_name'] = [output_file_name]
            o_save.export(folder=output_folder_name, data_type='sample')
            del o_save

            global_slider.value += 1

        global_slider.close()

        display(HTML('<span style="font-size: 20px; color:blue">' + str(nbr_of_files_to_create) +
                     ' files have been created in ' + output_folder_name + '</span>'))
        if self.timespectra_file_name:
            display(HTML('<span style="font-size: 20px; color:blue"> A new _Spectra.txt file has been created: ' \
                         + output_timespectra_file_name + '</span>'))

    @staticmethod
    def combine_timespectra(input_timespectra_file_name=None,
                            output_timespectra_file_name=None,
                            bin_value=2,
                            merging_algorithm=None):
        if input_timespectra_file_name is None:
            return

        data = np.genfromtxt(input_timespectra_file_name, delimiter='\t')
        nbr_rows, nbr_columns = np.shape(data)

        time_axis_binned = []
        count_axis_binned = []

        for index in np.arange(0, nbr_rows, bin_value):
            right_threshold = index + bin_value
            if right_threshold >= nbr_rows:
                break

            working_time_axis_to_bin = data[index: index + bin_value, 0]
            working_count_axis_to_bin = data[index: index + bin_value, 1]

            time_axis_binned.append(
                CombineImagesNByN.merging_algorithm(CombineImagesNByN.arithmetic_mean,
                                                    working_time_axis_to_bin))
            count_axis_binned.append(CombineImagesNByN.merging_algorithm(merging_algorithm,
                                                                         working_count_axis_to_bin))

        new_timespectra = list(zip(time_axis_binned, count_axis_binned))
        np.savetxt(output_timespectra_file_name, new_timespectra, delimiter="\t")

    @staticmethod
    def __create_output_folder_name(output_folder="./", base_file_name='', bin_value=2):
        output_folder = os.path.abspath(output_folder)
        output_folder_name = os.path.join(output_folder, "{}_files_combined_by_{:03d}".format(base_file_name,
                                                                                              bin_value))
        return output_folder_name

    @staticmethod
    def __create_merged_file_name(index=0):
        """Create the new base name using a combine name of all the input file
        """
        return FILE_PREFIX + '_{:03d}.tiff'.format(index)

    @staticmethod
    def __create_timestamp_file_name():
        return FILE_PREFIX + '_Spectra.txt'

    @staticmethod
    def add(data_array):
        return np.sum(data_array, axis=0)

    @staticmethod
    def arithmetic_mean(data_array):
        return np.mean(data_array, axis=0)

    @staticmethod
    def geo_mean(data_array):
        return gmean(data_array, axis=0)

    @staticmethod
    def merging_algorithm(function_, *args):
        return function_(*args)
