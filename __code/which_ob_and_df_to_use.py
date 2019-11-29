import os
import collections
import numpy as np
from ipywidgets import widgets
from IPython.core.display import display, HTML

import ipywe.fileselector

from __code import file_handler
from __code import metadata_handler

PV_EXPOSURE_TIME = 65027


class WhichOBandDFtoUse(object):
    working_dir = ''

    def __init__(self, working_dir=''):
        self.working_dir = working_dir
        self.list_of_images = []
        self.input_data_folder = []

        self.first_image_dict = {}
        self.last_image_dict = {}
        self.list_metadata_dict = {}

        self.list_ob = []
        self.ob_time_stamp_dict = {}
        self.ob_acquisition_time_dict = {}

        self.list_df = []
        self.df_time_stamp_dict = {}
        self.df_acquisition_time_dict = {}

    def select_images(self):
        list_of_images_widget = ipywe.fileselector.FileSelectorPanel(instruction='select folder of data'
                                                                                 'to normalize',
                                                                     start_dir=self.working_dir,
                                                                     next=self.retrieve_sample_metadata,
                                                                     multiple=True)
        list_of_images_widget.show()

    def retrieve_sample_metadata(self, list_of_images):
        self.list_of_images = list_of_images

        _dict = file_handler.retrieve_time_stamp(self.list_of_images)

        self.first_image_dict = WhichOBandDFtoUse.isolate_infos_from_file_index(index=0, dictionary=_dict)
        self.last_image_dict = WhichOBandDFtoUse.isolate_infos_from_file_index(index=-1, dictionary=_dict)
        self.list_metadata_dict = WhichOBandDFtoUse.retrieve_acquisition_time(self.list_of_images)

        display(HTML('<span style="font-size: 20px; color:blue">First image was taken at : ' + \
                     self.first_image_dict['user_format_time'] + '</span>'))
        display(HTML('<span style="font-size: 20px; color:blue">Last image was taken at : ' + \
                     self.last_image_dict['user_format_time'] + '</span>'))

    @staticmethod
    def retrieve_acquisition_time(list_files):
        """acquisition time is tag 65027"""
        _dict = metadata_handler.MetadataHandler.retrieve_metadata(list_files=list_files,
                                                                   list_metadata=[PV_EXPOSURE_TIME])
        for _file_key in _dict.keys():
            _raw_value = _dict[_file_key][PV_EXPOSURE_TIME]
            split_raw_value = _raw_value.split(":")
            _dict[_file_key] = np.float(split_raw_value[1])
        return _dict

    @staticmethod
    def isolate_infos_from_file_index(index=-1, dictionary=None, all_keys=False):
        result_dictionary = collections.OrderedDict()

        if all_keys:
            for _image in dictionary['list_images'].keys():
                _time_image = dictionary['list_time_stamp'][index]
                _user_format_time_image = dictionary['list_time_stamp_user_format'][index]
                result_dictionary[_image] = {'system_time': _time_image,
                                             'user_format_time': _user_format_time_image}
        else:
            _image = dictionary['list_images'][index]
            _time_image = dictionary['list_time_stamp'][index]
            _user_format_time_image = dictionary['list_time_stamp_user_format'][index]
            result_dictionary = {'file_name': _image,
                                 'system_time': _time_image,
                                 'user_format_time': _user_format_time_image}

        return result_dictionary

    def select_of_folder(self):
        self.select_folder(message='open beam',
                           next_function=self.retrieve_ob_metadata())

    def select_df_folder(self):
        self.select_folder(message='dark field',
                           next_function=self.retrieve_df_metadata())

    def select_folder(self, message="", next_function=None):
        folder_widget = ipywe.fileselector.FileSelectorPanel(instruction='select {} folder'.format(message),
                                                             start_dir=self.working_dir,
                                                             next=next_function,
                                                             type='directory',
                                                             multiple=False)
        folder_widget.show()

    @staticmethod
    def get_list_of_tiff_files(folder=""):
        list_of_tiff_files = file_handler.get_list_of_files(folder=folder,
                                                            extension='tiff')
        return list_of_tiff_files

    def retrieve_metadata(self, selected_folder=""):
        list_files = WhichOBandDFtoUse.get_list_of_tiff_files(folder=selected_folder)
        time_stamp_dict = file_handler.retrieve_time_stamp(list_files)
        acquisition_time_dict = WhichOBandDFtoUse.retrieve_acquisition_time(list_files)
        return {'list_files_dict': list_files,
                'time_stamp_dict': time_stamp_dict,
                'acquisition_time_dict': acquisition_time_dict}

    def retrieve_ob_metadata(self, selected_folder):
        dict_result = self.retrieve_metadata(selected_folder=selected_folder)
        self.list_ob = dict_result['list_files_dict']
        self.ob_time_stamp_dict = dict_result['time_stamp_dict']
        self.ob_acquisition_time_dict = dict_result['acquisition_time_dict']

    def retrieve_df_metadata(self, selected_folder):
        dict_result = self.retrieve_metadata(selected_folder=selected_folder)
        self.list_df = dict_result['list_files_dict']
        self.df_time_stamp_dict = dict_result['time_stamp_dict']
        self.df_acquisition_time_dict = dict_result['acquisition_time_dict']

    def select_time_range(self):
        box = widgets.HBox([widgets.Label("Time (hours)",
                                          layout=widgets.Layout(width='20%')),
                            widgets.IntProgress(min=0,
                                                max=len(self.list_of_images),
                                                value=0,
                                                layout=widgets.Layout(width='50%'))
                            ])
        progress_bar = box.children[1]
        display(box)











    def select_output_folder(self):
        self.output_folder_widget = ipywe.fileselector.FileSelectorPanel(instruction='select where to create the ' + \
                                                                                     'combined image ...',
                                                                         start_dir=self.working_dir,
                                                                         type='directory')

        self.output_folder_widget.show()



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






