import glob
import os
import ipywe.fileselector

from ipywidgets.widgets import interact
from ipywidgets import widgets
from IPython.core.display import display, HTML
import numpy as np


class MergeFolders(object):
    working_dir = ''
    list_folders = []
    list_folders_short = []  # short name of list of folders
    list_files_dict = {}
    nbr_files_in_each_folder = np.NaN

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

        self.list_folders_short = []

    def select_folders(self):
        self.folder_list_widget = ipywe.fileselector.FileSelectorPanel(instruction='select folder to combine',
                                                                       start_dir=self.working_dir,
                                                                       type='directory',
                                                                       multiple=True)
        self.folder_list_widget.show()

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

    def check_number_of_files(self):
        # initialization of dictionary that will store the list of files
        list_files_dict = {}
        self.list_folders = self.folder_list_widget.selected

        nbr_files = {}
        file_format = ''
        for _folder in self.list_folders:
            _list_files = self.__get_list_files(file_format=file_format, folder=_folder)
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
            raise ValueError("Folder do not have the same number of files!")
        else:
            display(HTML('<span style="font-size: 20px; color:green">All the folders selected contain the ' + \
                         'same number of files (' + str(list(values)[0]) + ' files each)!</span>'))
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

        _list_folders = self.list_folders_short

    def merging(self):

        merging_algo = self.combine_method.value

        # create dictionary of how the images will be combined
        self.__create_merging_dictionary()

    # combine images using algorithm provided






    def load_list_files(self, filename_array=[]):
        data = []
        for _filename in filename_array:
            data = file_handler.load_data(filename=_filename)
            data.append(_data)
        return data

    def add(self, array=[]):
        return np.array(array).sum(axis=0)

    def mean(self, array=[]):
        return np.array(array).mean(axis=0)

    def run(self):
        merged_images = {'file_name': [],
                         'data': []}
        nbr_files = list(values)[0]

        box1 = widgets.HBox([widgets.Label("Merging Progress:",
                                           layout=widgets.Layout(width='10%')),
                             widgets.IntProgress(max=nbr_files)])
        display(box1)
        w1 = box1.children[1]

        for _index_file in np.arange(nbr_files):
            _list_file_to_merge = []
            for _key in list_files_dict.keys():
                _file = list_files_dict[_key][_index_file]
                _list_file_to_merge.append(_file)
                merged_images['file_name'].append(os.path.basename(_file))

            _data_array = load_list_files(_list_file_to_merge)
            merged_data = add(_data_array)

            w1.value = _index_file + 1
