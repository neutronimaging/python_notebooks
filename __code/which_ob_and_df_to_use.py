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


class WhichOBandDFtoUse(object):
    working_dir = ''

    def __init__(self, working_dir=''):
        self.working_dir = working_dir
        self.list_of_images = []
        self.input_data_folder = []

        self.first_image_dict = {}
        self.last_image_dict = {}
        self.list_metadata_dict = {}

        # list of open beam files (full path)
        self.list_ob = []

        """ 
        {'list_images: [],
         'list_time_stamp': [],
         'list_time_stamp_user_format': [],
        }
        """
        self.ob_time_stamp_dict = {}

        # {'file1': time1, 'file2': time2, ...}
        self.ob_acquisition_time_dict = {}

        # list of dark field files (full path)
        self.list_df = []

        """ 
        {'list_images: [],
         'list_time_stamp': [],
         'list_time_stamp_user_format': [],
        }
        """
        self.df_time_stamp_dict = {}

        # {'file1': time1, 'file2': time2, ...}
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
        self.list_metadata_dict = WhichOBandDFtoUse.retrieve_metadata(self.list_of_images)

        display(HTML('<span style="font-size: 20px; color:blue">First image was taken at : ' + \
                     self.first_image_dict['user_format_time'] + '</span>'))
        display(HTML('<span style="font-size: 20px; color:blue">Last image was taken at : ' + \
                     self.last_image_dict['user_format_time'] + '</span>'))

    @staticmethod
    def retrieve_metadata(list_files):
        """list of metadata to retrieve is:
            - acquisition time -> 65027
            - detector type -> 65026 (Manufacturer)
            - slits positions ->
            - aperture value
        """
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
        #self.list_ob = dict_result['list_files_dict']
        self.ob_time_stamp_dict = dict_result['time_stamp_dict']
        self.ob_acquisition_time_dict = dict_result['acquisition_time_dict']

    def retrieve_df_metadata(self, selected_folder):
        dict_result = self.retrieve_metadata(selected_folder=selected_folder)
        # self.list_df = dict_result['list_files_dict']
        self.df_time_stamp_dict = dict_result['time_stamp_dict']
        self.df_acquisition_time_dict = dict_result['acquisition_time_dict']

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






