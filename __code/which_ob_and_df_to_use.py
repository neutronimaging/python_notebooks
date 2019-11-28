import os
import ipywe.fileselector
from scipy.stats.mstats import gmean
import glob
import collections

from ipywidgets import widgets
from IPython.core.display import display, HTML
import numpy as np

from __code import file_handler
from __code import time_utility
from __code import metadata_handler
from NeuNorm.normalization import Normalization

PV_EXPOSURE_TIME = 65027


class WhichOBandDFtoUse(object):
    working_dir = ''

    def __init__(self, working_dir=''):
        self.working_dir = working_dir
        self.list_of_images = []
        self.input_data_folder = []

    def select_images(self):
        self.list_of_images_widget = ipywe.fileselector.FileSelectorPanel(instruction='select folder of data'
                                                                                         'to normalize',
                                                                             start_dir=self.working_dir,
                                                                             next=self.retrieve_sample_metadata,
                                                                             multiple=True)
        self.list_of_images_widget.show()

    def retrieve_sample_metadata(self, list_of_images):
        self.list_of_images = list_of_images

        _dict = file_handler.retrieve_time_stamp(self.list_of_images)

        self.first_image_dict = self.isolate_infos_from_file_index(index=0, dict=_dict)
        self.last_image_dict = self.isolate_infos_from_file_index(index=-1, dict=_dict)
        self.list_metadata_dict = self.retrieve_acquisition_time(self.list_of_images)

        display(HTML('<span style="font-size: 20px; color:blue">First image was taken at : ' + \
                     self.first_image_dict['user_format_time'] + '</span>'))
        display(HTML('<span style="font-size: 20px; color:blue">Last image was taken at : ' + \
                     self.last_image_dict['user_format_time'] + '</span>'))

    def retrieve_acquisition_time(self, list_files):
        """acquisition time is tag 65027"""
        dict = metadata_handler.MetadataHandler.retrieve_metadata(list_files=list_files,
                                                                  list_metadata=[PV_EXPOSURE_TIME])
        for _file_key in dict.keys():
            _raw_value = dict[_file_key][PV_EXPOSURE_TIME]
            split_raw_value = _raw_value.split(":")
            dict[_file_key] = np.float(split_raw_value[1])
        return dict

    def isolate_infos_from_file_index(self, index=-1, dict=None, all_keys=False):
        result_dict = collections.OrderedDict()

        if all_keys:
            for _image in dict['list_images'].keys():
                _time_image = dict['list_time_stamp'][index]
                _user_format_time_image = dict['list_time_stamp_user_format'][index]
                result_dict[_image] = {'system_time': _time_image,
                                       'user_format_time': _user_format_time_image}
        else:
            _image = dict['list_images'][index]
            _time_image = dict['list_time_stamp'][index]
            _user_format_time_image = dict['list_time_stamp_user_format'][index]
            result_dict = {'file_name': _image,
                           'system_time': _time_image,
                           'user_format_time': _user_format_time_image}

        return result_dict

    def select_ob_folder(self):
        self.ob_folder_widget = ipywe.fileselector.FileSelectorPanel(instruction='select open beam folder',
                                                                     start_dir=self.working_dir,
                                                                     next=self.retrieve_ob_metadata,
                                                                     type='directory',
                                                                     multiple=False)
        self.ob_folder_widget.show()

    def retrieve_ob_metadata(self, selected_folder):
        self.list_ob = self.get_list_of_tiff_files(folder=selected_folder)
        self.ob_time_stamp_dict = file_handler.retrieve_time_stamp(self.list_ob)
        self._ob_acquisition_time_dict = self.retrieve_acquisition_time(self.list_ob)

        

    def get_list_of_tiff_files(self, folder=""):
        list_files = glob.glob(os.path.join(folder, "*.tiff"))
        list_files.sort()
        return list_files

    def select_ob_time_range(self):
        box = widgets.HBox([widgets.Label("Time (hours)",
                                          layout=widgets.Layout(width='20%')),
                            widgets.IntProgress(min=0,
                                                max=len(self.list_of_images),
                                                value=0,
                                                layout=widgets.Layout(width='50%'))
                            ])
        progress_bar = box.children[1]
        display(box)





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

    def select_output_folder(self):
        self.output_folder_widget = ipywe.fileselector.FileSelectorPanel(instruction='select where to create the ' + \
                                                                                     'combined image ...',
                                                                         start_dir=self.working_dir,
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

    def define_output_filename(self):
        list_files = self.files_list_widget.selected
        short_list_files = [os.path.basename(_file) for _file in list_files]

        merging_algo = self.__get_formated_merging_algo_name()
        [default_new_name, ext] = self.__create_merged_file_name(list_files_names=short_list_files)

        top_label = widgets.Label("You have the option to change the default output file name")

        box = widgets.HBox([widgets.Label("Default File Name",
                                          layout=widgets.Layout(width='20%')),
                            widgets.Text(default_new_name,
                                         layout=widgets.Layout(width='60%')),
                            widgets.Label("_{}{}".format(merging_algo, ext),
                                          layout=widgets.Layout(width='20%')),
                            ])
        self.default_filename_ui = box.children[1]
        self.ext_ui = box.children[2]
        vertical_box = widgets.VBox([top_label, box])
        display(vertical_box)

    def merging(self):
        """combine images using algorithm provided"""

        list_files = self.files_list_widget.selected
        nbr_files = len(list_files)

        # get merging algorithm
        merging_algo = self.combine_method.value
        algorithm = self.__add
        if merging_algo =='arithmetic mean':
            algorithm = self.__arithmetic_mean
        elif merging_algo == 'geometric mean':
            algorithm = self.__geo_mean

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

        #_new_name = self.__create_merged_file_name(list_files_names=o_load.data['sample']['file_name'])
        _new_name = self.default_filename_ui.value + self.ext_ui.value
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

        return ('_'.join(list_base_name), ext)

    def __add(self, data_array):
        return np.sum(data_array, axis=0)

    def __arithmetic_mean(self, data_array):
        return np.mean(data_array, axis=0)

    def __geo_mean(self, data_array):
        return gmean(data_array, axis=0)

    def __merging_algorithm(self, function_, *args):
        return function_(*args)



