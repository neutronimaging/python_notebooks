import glob
import os
from ipywidgets import widgets
from IPython.core.display import display, HTML
import numpy as np

from NeuNorm.normalization import Normalization

from __code import file_handler
from __code.ipywe import fileselector


class CombineFolders(object):
    working_dir = ''
    list_folders = []
    list_folders_short = []  # short name of list of folders
    list_files_dict = {}
    nbr_files_in_each_folder = np.NaN

    global_list_of_folders_to_combine = []

    def __init__(self, working_dir=''):
        self.working_dir = working_dir
        self.list_folders_short = []

    def select_folders(self):
        self.done_button = widgets.Button(description="Click me when done selecting folders!",
                                          button_style="success",
                                          layout=widgets.Layout(width="100%"))

        self.done_button.on_click(self.stop_selecting_folders)
        vertical_layout = widgets.VBox([self.done_button])
        display(vertical_layout)

        self.select_folders_file_selector()

    def select_folders_file_selector(self):
        self.folder_list_widget = fileselector.FileSelectorPanel(instruction='select folder to combine',
                                                                 start_dir=self.working_dir,
                                                                 type='directory',
                                                                 next=self.add_folder_selected_to_global_list,
                                                                 multiple=True)

        self.folder_list_widget.show()

    def add_folder_selected_to_global_list(self, list_folders):
        for _folder in list_folders:
            self.global_list_of_folders_to_combine.append(_folder)
        self.select_folders_file_selector()

    def stop_selecting_folders(self, value):
        self.folder_list_widget.remove()
        self.done_button.close()

        are_folders_valid = self.check_validity_of_folders_selected()

        if are_folders_valid:
            display(HTML('<span style="font-size: 20px; color:blue">You have selected ' +
                         str(len(self.global_list_of_folders_to_combine)) + ' folders!</span>'))
        else:
            display(HTML('<span style="font-size: 20px; color:red">Folders must contain the same number'
                         'of images!</span>'))

    def check_validity_of_folders_selected(self):
        globa_list_of_folers = self.global_list_of_folders_to_combine
        print(globa_list_of_folers)

        return True

    def __get_list_files(self, file_format='', folder=''):
        if file_format == '':
            _list_tif_files = glob.glob(folder + "/*.tif")
            if len(_list_tif_files) > 0:
                return {'file_format': 'tif', 'list_files': _list_tif_files}
            _list_tiff_files = glob.glob(folder + "/*.tiff")
            if len(_list_tiff_files) > 0:
                return {'file_format': 'tiff', 'list_files': _list_tiff_files}
            _list_fits_files = glob.glob(folder + "/*.fits")
            if len(_list_fits_files) > 0:
                return {'file_format': 'fits', 'list_files': _list_fits_files}
            else:
                return {'file_format': '', 'list_files': []}
        else:
            _list_files = glob.glob(folder + "/*." + file_format)
            return {'file_format': file_format, 'list_files': _list_files}

    def check_number_of_files(self, list_folders):
        # initialization of dictionary that will store the list of files
        list_files_dict = {}

        #self.list_folders = self.folder_list_widget.selected
        self.list_folders = list_folders

        nbr_files = {}
        file_format = ''
        for _folder in self.list_folders:
            _local_list_files_dict = self.__get_list_files(file_format=file_format, folder=_folder)

            _list_files = _local_list_files_dict['list_files']
            _list_files.sort()
            _format = _local_list_files_dict['file_format']

            _short = os.path.basename(_folder)
            list_files_dict[_short] = _list_files
            self.list_folders_short.append(_short)
            nbr_files[_short] = len(_list_files)

        self.list_files_dict = list_files_dict
        # checking the folders have the same number of files
        values = set(nbr_files.values())
        if len(values) > 1:
            display(HTML('<span style="font-size: 20px; color:red">All the folders selected DO NOT ' + \
                         'contain the same number of files </span>'))
#            raise ValueError("Folder do not have the same number of files!")
        else:
            display(HTML('<span style="font-size: 20px; color:green">All the folders selected contain the ' + \
                         'same number of files (' + str(list(values)[0]) + ' files each)!</span>'))
            display(HTML('<span style="font-size: 20px; color:green">Format: ' + _format))
            self.nbr_files_in_each_folder = list(values)[0]

        self.list_files_dict = list_files_dict

    def how_many_folders(self):
        nbr_folder = len(self.list_folders)
        radio_list_string = [str(_index) for _index in np.arange(2, nbr_folder + 1)]
        self.bin_size = widgets.RadioButtons(options=radio_list_string,
                                             value=radio_list_string[0])
        display(self.bin_size)

    def how_to_combine(self):
        self.combine_method = widgets.RadioButtons(options=['add', 'mean'],
                                                   value='add')
        display(self.combine_method)

    def __create_merging_dictionary(self):
        """where we will figure out which file goes with witch one"""
        merging_value = np.int(self.bin_size.value)
        _list_folders_short = self.list_folders_short
        _list_files_dict = self.list_files_dict

        _index_folder = 0
        merging_dict = {}
        while (_index_folder < len(_list_folders_short)):
            _new_folder_name_list = []
            from_index = _index_folder
            to_index = from_index + (merging_value)
            if to_index > len(_list_folders_short):
                break

            _tmp_list_folder = []
            for _index in np.arange(from_index, to_index):
                _current_short_folder_name = _list_folders_short[_index]
                _tmp_list_folder.append(_current_short_folder_name)
                _new_folder_name_list.append(_current_short_folder_name)

            new_folder_name = "_".join(_new_folder_name_list)
            merging_dict[new_folder_name] = _tmp_list_folder

            _index_folder += merging_value

        return merging_dict

    def merging(self, output_folder):
        """combine images using algorithm provided"""

        # get merging algorithm
        merging_algo = self.combine_method.value
        algorithm = self.__add
        if merging_algo == 'mean':
            algorithm = self.__mean

        # get output folder
        output_folder = os.path.abspath(output_folder)

        # create dictionary of how the images will be combined
        merging_dict = self.__create_merging_dictionary()
        self.merginc_dict_debugging = merging_dict

        # create final list of files to merge
        final_dict_of_files_to_merge = self.__create_dict_of_files_to_merge(merging_dict)
        self.final_dict_of_files_to_merge_debugging = final_dict_of_files_to_merge

        final_nbr_folders = len(merging_dict.keys())
        folder_level_ui = widgets.HBox([widgets.Label("Folder Progress:",
                                                      layout=widgets.Layout(width='20%')),
                                        widgets.IntProgress(max=final_nbr_folders,
                                                            layout=widgets.Layout(width='50%'))])
        display(folder_level_ui)
        w1 = folder_level_ui.children[1]

        nbr_files_to_merge = self.nbr_files_in_each_folder
        file_level_ui = widgets.HBox([widgets.Label("File Progress:",
                                                    layout=widgets.Layout(width='20%')),
                                     widgets.IntProgress(max=nbr_files_to_merge,
                                                         layout=widgets.Layout(width='50%'))])
        display(file_level_ui)
        w2 = file_level_ui.children[1]

        for _index_final_folder, _final_folder in enumerate(final_dict_of_files_to_merge.keys()):

            file_handler.make_or_reset_folder(os.path.join(output_folder, _final_folder))

            list_files_to_merge = final_dict_of_files_to_merge[_final_folder]
            for _index_files_to_merge, _files_to_merge in enumerate(list_files_to_merge):

                _files_to_merge = [_file for _file in _files_to_merge]
                self.files_to_merge_for_testing = _files_to_merge
                o_load = Normalization()
                o_load.load(file=_files_to_merge)
                _data = o_load.data['sample']['data']
                combined_data = self.__merging_algorithm(algorithm, _data)
                self.combined_data_for_testing = combined_data

                _base_name_file = os.path.basename(_files_to_merge[0])
                output_file_name = os.path.join(output_folder, _final_folder, _base_name_file)

                file_handler.save_data(data=combined_data, filename=output_file_name)
                w2.value = _index_files_to_merge + 1

            w1.value = _index_final_folder + 1


    def __create_dict_of_files_to_merge(self, merging_dict):

        list_files_dict = self.list_files_dict

        final_dict_of_files_to_merge = {}
        for _key in merging_dict.keys():
            _list_folders_to_add = merging_dict[_key]
            _tmp_list_files_to_merge = []
            for _folder in _list_folders_to_add:
                _tmp_list_files_to_merge.append(list_files_dict[_folder])
            final_dict_of_files_to_merge[_key] = list(zip(*_tmp_list_files_to_merge))

        return final_dict_of_files_to_merge

    def __add(self, data_array):
        return np.sum(data_array, axis=0)

    def __mean(self, data_array):
        return np.mean(data_array, axis=0)

    def __merging_algorithm(self, function_, *args):
        return function_(*args)

    def select_output_folder(self):
        self.output_folder_widget = fileselector.FileSelectorPanel(instruction='select where to create the ' + \
                                                                               'output folders ...',
                                                                   start_dir=self.working_dir,
                                                                   next=self.merging,
                                                                   type='directory')

        self.output_folder_widget.show()
