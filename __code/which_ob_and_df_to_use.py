import os
import collections
import numpy as np
from ipywidgets import widgets
from IPython.core.display import display, HTML

import ipywe.fileselector

from __code import file_handler
from __code import metadata_handler
from __code import time_utility

PV_EXPOSURE_TIME = 65027
METADATA_KEYS = [PV_EXPOSURE_TIME, 65028, 65029]
MAX_DF_COUNTS_ALLOWED = 900
METADATA_ERROR_ALLOWED = 1
LIST_METADATA_NOT_INSTRUMENT_RELATED = ['filename', 'time_stamp', 'time_stamp_user_format']

class WhichOBandDFtoUse(object):
    working_dir = ''

    def __init__(self, working_dir=''):
        self.working_dir = working_dir
        self.list_of_images = []
        self.input_data_folder = []

        # {0: {65027: 55.0,
        #      65028: 59.2,
        #      65029: 1.0,
        #      'filename': 'full_filename',
        #      'time_stamp': 1454544.34545,
        #      'time_stamp_user_format': '2019-11-19 02:48:47'},
        #  ...,
        # }
        self.sample_metadata_dict = {}
        self.ob_metadata_dict = {}
        self.df_metadata_dict = {}

        # key of dictionary being the acquisition time
        # {50: {'config0': {'list_sample': [file1, file2, file3],
        #                     'list_ob': [file1, file2],
        #                     'list_df': [file1, file2, file3],
        #                     'metadata_infos': {},
        #                      },
        #         'config1': {...},
        #        },
        #  30: {...},
        # }
        self.final_full_master_dict = {}

        # same as the final_full_master_dict but in this one, the OB outside the time range
        # defined as excluded
        self.final_with_time_range_master_dict = {}

    def select_images(self):
        list_of_images_widget = ipywe.fileselector.FileSelectorPanel(instruction='select folder of data'
                                                                                 'to normalize',
                                                                     start_dir=self.working_dir,
                                                                     next=self.retrieve_sample_metadata,
                                                                     multiple=True)
        list_of_images_widget.show()

    def retrieve_sample_metadata(self, list_of_images):
        self.list_of_images = list_of_images
        self.sample_metadata_dict = WhichOBandDFtoUse.retrieve_metadata(list_of_files=list_of_images,
                                                                        display_infos=True)

    def select_ob_folder(self):
        self.select_folder(message='open beam',
                           next_function=self.retrieve_ob_metadata())

    def retrieve_ob_metadata(self, selected_folder):
        list_of_ob_files = WhichOBandDFtoUse.get_list_of_tiff_files(folder=selected_folder)
        self.ob_metadata_dict = WhichOBandDFtoUse.retrieve_metadata(list_of_files=list_of_ob_files)

    def select_folder(self, message="", next_function=None):
        folder_widget = ipywe.fileselector.FileSelectorPanel(instruction='select {} folder'.format(message),
                                                             start_dir=self.working_dir,
                                                             next=next_function,
                                                             type='directory',
                                                             multiple=False)
        folder_widget.show()

    def select_df_folder(self):
        self.select_folder(message='dark field',
                           next_function=self.retrieve_df_metadata())

    def retrieve_df_metadata(self, selected_folder):
        list_of_df_files = WhichOBandDFtoUse.get_list_of_tiff_files(folder=selected_folder)
        self.df_metadata_dict = WhichOBandDFtoUse.retrieve_metadata(list_of_files=list_of_df_files)

    def match_files(self):
        """This is where the files will be associated with their respective OB, DF"""

        final_full_master_dict = collections.OrderedDict()
        sample_metadata_dict = self.sample_metadata_dict
        for _file_index in sample_metadata_dict.keys():
            _dict_file_index = sample_metadata_dict[_file_index]
            _sample_file = _dict_file_index['filename']
            _acquisition_time = _dict_file_index[PV_EXPOSURE_TIME]
            _instrument_metadata = WhichOBandDFtoUse._isolate_instrument_metadata(_dict_file_index)

            # first entry or first time seeing that acquisition time
            if (len(final_full_master_dict) == 0) or not (_acquisition_time in final_full_master_dict.keys()):
                _temp_dict = {'list_sample': [_sample_file],
                              'list_ob': [],
                              'list_df': [],
                              'metadata_infos': WhichOBandDFtoUse.get_instrument_metadata_only(_instrument_metadata)}
                final_full_master_dict[_acquisition_time] = {}
                final_full_master_dict[_acquisition_time]['config0'] = _temp_dict
            else:
                # check that all the metadata_infos match for the first group of that acquisition time,
                # otherwise check the next one or create a group
                if _acquisition_time in final_full_master_dict.keys():
                    _dict_for_this_acquisition_time = final_full_master_dict[_acquisition_time]
                    _found_a_match = False
                    for _config_key in _dict_for_this_acquisition_time.keys():
                        _config = _dict_for_this_acquisition_time[_config_key]
                        if (WhichOBandDFtoUse.all_metadata_match(metadata_1=_config['metadata_infos'],
                                                                 metadata_2=_instrument_metadata)):
                            _config['list_sample'].append(_sample_file)
                            _found_a_match = True
                    if not _found_a_match:
                        _temp_dict = {'list_sample': [_sample_file],
                                      'list_ob': [],
                                      'list_df': [],
                                      'metadata_infos': WhichOBandDFtoUse.get_instrument_metadata_only(_instrument_metadata)}
                        nbr_config = len(_dict_for_this_acquisition_time.keys())
                        _dict_for_this_acquisition_time['config{}'.format(nbr_config)] = _temp_dict
                else:
                    _temp_dict = {'list_sample': [_sample_file],
                                  'list_ob': [],
                                  'list_df': [],
                                  'metadata_infos': WhichOBandDFtoUse.get_instrument_metadata_only(_instrument_metadata)}
                    final_full_master_dict[_acquisition_time] = {}
                    final_full_master_dict[_acquisition_time]['config0'] = _temp_dict

        self.final_full_master_dict = final_full_master_dict

    @staticmethod
    def get_instrument_metadata_only(metadata_dict):
        _clean_dict = {}
        for _key in metadata_dict.keys():
            if not _key in LIST_METADATA_NOT_INSTRUMENT_RELATED:
                _clean_dict[_key] = metadata_dict[_key]
        return _clean_dict
    
    @staticmethod
    def all_metadata_match(metadata_1={}, metadata_2={}):
        for _key in metadata_1.keys():
            if np.abs(np.float(metadata_1[_key] - np.float(metadata_2[_key]))) > METADATA_ERROR_ALLOWED:
                return False
        return True

    @staticmethod
    def _isolate_instrument_metadata(dictionary):
        """create a dictionary of all the instrument metadata without the acquisition time"""
        isolated_dictionary = {}
        for _key in dictionary.keys():
            if _key == PV_EXPOSURE_TIME:
                continue
            isolated_dictionary[_key] = dictionary[_key]
        return isolated_dictionary

    @staticmethod
    def _reformat_dict(dictionary={}):
        """
        to go from
            {'list_images': [], 'list_time_stamp': [], 'list_time_stamp_user_format':[]}
        to
            {'0': {'filename': file1,
                   'time_stamp': 'value',
                   'time_stamp_user_format': 'value',
                   },
             ...,
             }
        """
        formatted_dictionary = collections.OrderedDict()
        list_files = dictionary['list_images']
        list_time_stamp = dictionary['list_time_stamp']
        list_time_stamp_user_format = dictionary['list_time_stamp_user_format']

        for _index, _file in enumerate(list_files):
            formatted_dictionary[_index] = {'filename': _file,
                                            'time_stamp': list_time_stamp[_index],
                                            'time_stamp_user_format': list_time_stamp_user_format[_index]}
        return formatted_dictionary

    @staticmethod
    def _combine_dictionaries(master_dictionary={}, servant_dictionary={}):
        new_master_dictionary = collections.OrderedDict()
        for _key in master_dictionary.keys():
            _servant_key = master_dictionary[_key]['filename']
            _dict1 = master_dictionary[_key]
            _dict2 = servant_dictionary[_servant_key]
            _dict3 = {**_dict1, **_dict2}
            new_master_dictionary[_key] = _dict3
        return new_master_dictionary

    @staticmethod
    def retrieve_metadata(list_of_files=[], display_infos=True):
        """
        dict = {'file1': {'metadata1': 'value',
                          'metadata2': 'value',
                          'metadata3': 'value',
                          ...
                          },
                ...
                }
        """
        _dict = file_handler.retrieve_time_stamp(list_of_files)
        _time_metadata_dict = WhichOBandDFtoUse._reformat_dict(dictionary=_dict)

        _beamline_metadata_dict = WhichOBandDFtoUse.retrieve_beamline_metadata(list_of_files)
        _metadata_dict = WhichOBandDFtoUse._combine_dictionaries(master_dictionary=_time_metadata_dict,
                                                                 servant_dictionary=_beamline_metadata_dict)

        if display_infos:
            display(HTML('<span style="font-size: 20px; color:blue">Nbr of images: ' + str(len(_metadata_dict)) +
                         '</span'))
            display(HTML('<span style="font-size: 20px; color:blue">First image was taken at : ' + \
                         _metadata_dict[0]['time_stamp_user_format'] + '</span>'))
            last_index = len(_metadata_dict)-1
            display(HTML('<span style="font-size: 20px; color:blue">Last image was taken at : ' + \
                         _metadata_dict[last_index]['time_stamp_user_format'] + '</span>'))

        return _metadata_dict

    @staticmethod
    def retrieve_beamline_metadata(list_files):
        """list of metadata to retrieve is:000
            - acquisition time -> 65027
            - detector type -> 65026 (Manufacturer)
            - slits positions ->
            - aperture value
        """
        list_metadata = METADATA_KEYS
        _dict = metadata_handler.MetadataHandler.retrieve_metadata(list_files=list_files,
                                                                   list_metadata=list_metadata)

        for _file_key in _dict.keys():
            _file_dict = {}
            for _pv in list_metadata:
                _raw_value = _dict[_file_key][_pv]
                if _raw_value is not None:
                    split_raw_value = _raw_value.split(":")
                    _file_dict[_pv] = np.float(split_raw_value[1])
                else:
                    _file_dict[_pv] = None
            _dict[_file_key] = _file_dict
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





    @staticmethod
    def get_list_of_tiff_files(folder=""):
        list_of_tiff_files = file_handler.get_list_of_files(folder=folder,
                                                            extension='tiff')
        return list_of_tiff_files

    # def retrieve_metadata(self, selected_folder=""):
    #     list_files = WhichOBandDFtoUse.get_list_of_tiff_files(folder=selected_folder)
    #     time_stamp_dict = file_handler.retrieve_time_stamp(list_files)
    #     acquisition_time_dict = WhichOBandDFtoUse.retrieve_acquisition_time(list_files)
    #     return {'list_files_dict': list_files,
    #             'time_stamp_dict': time_stamp_dict,
    #             'acquisition_time_dict': acquisition_time_dict}


    def select_time_range(self):
        self.keep_df_and_ob_with_same_acquisition_time()
        max_time_range = self.calculate_max_time_range_between_images()
        box01 = widgets.HBox([widgets.Label("Time (hours)",
                                            layout=widgets.Layout(width='10%')),
                              widgets.IntSlider(min=1,
                                                max=max_time_range,
                                                value=0,
                                                layout=widgets.Layout(width='50%'))
                             ])
        self.time_slider = box01.children[1]
        self.time_slider.on_trait_change(self.recalculate_files_in_range, name='value')

        timelapse_options = {'BEFORE or AFTER sample data acquisition': 'before_or_after',
                             'Only BEFORE sample acquisition': 'before',
                             'Only AFTER sample acquisition': 'after'}
        box02 = widgets.HBox([widgets.Label("Select timelapse",
                                            layout=widgets.Layout(width='10%')),
                              widgets.RadioButtons(options=timelapse_options,
                                                   layout=widgets.Layout(width="300px"))])
        self.timelapse_selection_widget = box02.children[1]
        self.timelapse_selection_widget.on_trait_change(self.recalculate_files_in_range, name='value')

        list_of_ob_in_range = self.get_list_of_images_in_range(time_range_s=self.time_slider.value*3600,
                                                               data_type='ob')
        box1 = widgets.VBox([widgets.Label("List of OB Runs in the range",
                                           layout=widgets.Layout(width='100%')),
                             widgets.Select(options=list_of_ob_in_range,
                                            layout=widgets.Layout(width='500px',
                                                                  height='300px'))],
                            layout=widgets.Layout(width="520px"))
        self.list_of_ob_in_range_widget = box1.children[1]

        list_of_matching_df = self.get_list_of_matching_df()

        box2 = widgets.VBox([widgets.Label("List of DF",
                                           layout=widgets.Layout(width='100%')),
                             widgets.Select(options=list_of_matching_df,
                                            layout=widgets.Layout(width='500px',
                                                                  height='300px'))],
                            layout=widgets.Layout(width="520px"))
        self.list_of_df_in_range_widget = box2.children[1]

        spacer = "_" * 60
        box3 = widgets.Label(spacer + " R E S U L T " + spacer,
                             layout=widgets.Layout(width="100%"))

        master_box_12 = widgets.HBox([box1, box2],
                                     layout=widgets.Layout(width="100%"))
        master_box = widgets.VBox([box01, box02, box3, master_box_12])

        display(master_box)

    def keep_df_and_ob_with_same_acquisition_time(self):
        #FIXME
        pass

    def get_list_of_matching_df(self):
        #FIXME
        return []

    def get_list_of_images_in_range(self, time_range_s=1,
                                    timelapse_option="before_or_after",
                                    data_type='ob'):

        if data_type == 'ob':
            data = self.ob_time_stamp_dict
        else:
            data = self.df_time_stamp_dict

        first_image_system_time = self.first_image_dict['system_time']
        last_image_system_time = self.last_image_dict['system_time']

        list_filename = data['list_images']
        list_timestamp = data['list_time_stamp']

        # before
        list_index_to_keep = []
        for _index, _time in enumerate(list_timestamp):

            # ob or df was taken after first raw and before last raw data, we keep it
            if (_time > first_image_system_time) and (_time < last_image_system_time):
                list_index_to_keep.append(_index)
                continue

            if timelapse_option == 'before':
                if (_time < first_image_system_time) and \
                        (np.abs(first_image_system_time-_time) <= time_range_s):
                    list_index_to_keep.append(_index)
            elif timelapse_option == 'after':
                if (_time > last_image_system_time) and \
                        (np.abs(last_image_system_time-_time) <= time_range_s):
                    list_index_to_keep.append(_index)
            else:
                if ((_time < first_image_system_time) and
                    (np.abs(first_image_system_time - _time) <= time_range_s)) or \
                        ((_time > last_image_system_time) and
                         (np.abs(last_image_system_time - _time) <= time_range_s)):
                    list_index_to_keep.append(_index)

        return list_filename[list_index_to_keep]

    def recalculate_files_in_range(self):
        time_range_value = self.time_slider.value
        timelapse = self.timelapse_selection_widget.value

        list_ob_in_range = self.get_list_of_images_in_range(time_range_s=time_range_value*3600,
                                                            timelapse_option=timelapse,
                                                            data_type='ob')
        self.list_of_ob_in_range_widget.value = list_ob_in_range

    def calculate_max_time_range_between_images(self):
        """this method will determine what is the max time difference between the sample data set and
        the ob images
        The algorithm will use the first and last ob and sample data set to find this range
        """
        first_image_system_time = self.first_image_dict['system_time']
        last_image_system_time = self.last_image_dict['system_time']

        _ob_time_stamp_dict = self.ob_time_stamp_dict['list_time_stamp']
        first_and_last_ob_system_time = WhichOBandDFtoUse.calculate_first_and_last_system_time(_ob_time_stamp_dict)
        first_ob_system_time = first_and_last_ob_system_time['first_stamp']
        last_ob_system_time = first_and_last_ob_system_time['last_stamp']

        time_offset_before = 0
        if first_image_system_time > first_ob_system_time:
            time_offset_before = first_image_system_time - first_ob_system_time

        time_offset_after = 0
        if last_image_system_time < last_ob_system_time:
            time_offset_after = last_ob_system_time - last_image_system_time

        max_time_range_s = np.max([time_offset_before, time_offset_after])
        max_time_range_hours = time_utility.convert_system_time_into_hours(max_time_range_s)

        return np.ceil(max_time_range_hours)

    @staticmethod
    def calculate_first_and_last_system_time(list_stamp_dict):
        first_stamp = list_stamp_dict[0]
        last_stamp = list_stamp_dict[-1]
        for _time in list_stamp_dict[1:]:
            if _time < first_stamp:
                first_stamp = _time
            elif _time > last_stamp:
                last_stamp = _time

        return {'first_stamp': first_stamp,
                'last_stamp': last_stamp}

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






