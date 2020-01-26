import os
import collections
import numpy as np
from ipywidgets import widgets
from IPython.core.display import display, HTML
from enum import Enum

import ipywe.fileselector

from __code import file_handler
from __code import metadata_handler
from NeuNorm.normalization import Normalization

JSON_DEBUGGING = False


class MetadataName(Enum):
    EXPOSURE_TIME = 65027
    DETECTOR_MANUFACTURER = 65026
    APERTURE_HR = 65068
    APERTURE_HL = 65070
    APERTURE_VT = 65066
    APERTURE_VB = 65064

    def __str__(self):
        return self.value

# METADATA_KEYS = [EXPOSURE_TIME, APERTURE_HR, APERTURE_HL, APERTURE_VT, APERTURE_VB]

# METADATA_KEYS = {'ob': [EXPOSURE_TIME, DETECTOR_MANUFACTURER, APERTURE_HR, APERTURE_HL, APERTURE_VT,
#                         APERTURE_VB],
#                  'df': [EXPOSURE_TIME, DETECTOR_MANUFACTURER],
#                  'all': [DETECTOR_MANUFACTURER, EXPOSURE_TIME, APERTURE_HR, APERTURE_HL, APERTURE_VT,
#                          APERTURE_VB]}

METADATA_KEYS = {'ob': [MetadataName.EXPOSURE_TIME,
                        MetadataName.DETECTOR_MANUFACTURER,
                        MetadataName.APERTURE_HR,
                        MetadataName.APERTURE_HL,
                        MetadataName.APERTURE_VT,
                        MetadataName.APERTURE_VB],
                 'df': [MetadataName.EXPOSURE_TIME,
                        MetadataName.DETECTOR_MANUFACTURER],
                 'all': [MetadataName.EXPOSURE_TIME,
                        MetadataName.DETECTOR_MANUFACTURER,
                        MetadataName.APERTURE_HR,
                        MetadataName.APERTURE_HL,
                        MetadataName.APERTURE_VT,
                        MetadataName.APERTURE_VB]}


class MetadataName:
    EXPOSURE_TIME = 65027
    DETECTOR_MANUFACTURER = 65026
    APERTURE_HR = 65068
    APERTURE_HL = 65070
    APERTURE_VT = 65066
    APERTURE_VB = 65064


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
        # {50: {'config0': {'list_sample': [self.sample_metadata_dict[0],
        #                                   self.sample_metadata_dict[1],..],
        #                   'list_ob': [self.ob_metadata_dict[0],
        #                               self.ob_metadata_dict[1],
        #                               ...],
        #                   'list_df': [file1, file2, file3],
        #                   'metadata_infos': {},
        #                   'first_images': {'sample': {},
        #                                    'ob': {},
        #                                    'df': {}},
        #                   'last_images': {'sample': {},
        #                                    'ob': {},
        #                                    'df': {}},
        #                   'time_range_s_selected': {'before': np.NaN,
        #                                             'after': np.NaN},
        #                   'time_range_s': {'before': np.NaN,
        #                                    'after': np.NaN},
        #                  },
        #       'config1': {...},
        #      },
        #  30: {...},
        # }
        self.final_full_master_dict = {}

        # same as the final_full_master_dict but in this one, the OB outside the time range
        # defined as excluded
        self.final_with_time_range_master_dict = {}

    def select_sample_images_and_create_configuration(self):
        self.select_sample_images()

    def select_sample_images(self):
        list_of_images_widget = ipywe.fileselector.FileSelectorPanel(instruction='select images'
                                                                                 'to normalize',
                                                                     start_dir=self.working_dir,
                                                                     next=self.retrieve_sample_metadata,
                                                                     multiple=True)
        list_of_images_widget.show()

    def retrieve_sample_metadata(self, list_of_images):
        self.list_of_images = list_of_images
        self.sample_metadata_dict = WhichOBandDFtoUse.retrieve_metadata(list_of_files=list_of_images,
                                                                        display_infos=True)
        self.auto_retrieve_ob_metadata()
        self.auto_retrieve_df_metadata()
        self.match_files()
        self.calculate_first_and_last_ob()
        self.calculate_time_range()
        self.display_time_range_selection_widgets()

    def select_ob_folder(self):
        self.select_folder(message='open beam',
                           next_function=self.retrieve_ob_metadata())

    def retrieve_ob_metadata(self, selected_folder):
        list_of_ob_files = WhichOBandDFtoUse.get_list_of_tiff_files(folder=selected_folder)
        self.ob_metadata_dict = WhichOBandDFtoUse.retrieve_metadata(list_of_files=list_of_ob_files)

    def auto_retrieve_ob_metadata(self):
        folder = os.path.join(self.working_dir, 'raw', 'ob')
        list_of_ob_files = file_handler.get_list_of_all_files_in_subfolders(folder=folder,
                                                                            extensions=['tiff','tif'])
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

    def auto_retrieve_df_metadata(self):
        folder = os.path.join(self.working_dir, 'raw', 'df')
        list_of_df_files = file_handler.get_list_of_all_files_in_subfolders(folder=folder,
                                                                            extensions=['tiff','tif'])
        self.df_metadata_dict = WhichOBandDFtoUse.retrieve_metadata(list_of_files=list_of_df_files)

    def match_files(self):
        """This is where the files will be associated with their respective OB, DF by using the metadata"""

        if not JSON_DEBUGGING:
            self.create_master_sample_dict()

        self.match_ob()
        self.match_df()

        if JSON_DEBUGGING:
            # for debugging only, exporting the json
            import json
            with open('/Users/j35/Desktop/which_ob_and_df_to_use.json', 'w') as outfile:
                json.dump(self.final_full_master_dict, outfile)

    def match_ob(self):
        """we will go through all the ob and associate them with the right sample based on
        - acquisition time
        - detector type
        - aperture
        """
        list_ob_dict = self.ob_metadata_dict
        final_full_master_dict = self.final_full_master_dict
        list_of_sample_acquisition = final_full_master_dict.keys()

        for _index_ob in list_ob_dict.keys():
            _all_ob_instrument_metadata = self.get_instrument_metadata_only(list_ob_dict[_index_ob])
            _ob_instrument_metadata = WhichOBandDFtoUse._isolate_instrument_metadata(_all_ob_instrument_metadata)
            _acquisition_time = _all_ob_instrument_metadata[MetadataName.EXPOSURE_TIME]['value']
            if _acquisition_time in list_of_sample_acquisition:
                for _config_id in final_full_master_dict[_acquisition_time].keys():
                    _sample_metadata_infos = final_full_master_dict[_acquisition_time][_config_id]['metadata_infos']
                    if WhichOBandDFtoUse.all_metadata_match(_sample_metadata_infos,
                                                            _ob_instrument_metadata):
                        final_full_master_dict[_acquisition_time][_config_id]['list_ob'].append(list_ob_dict[_index_ob])

        self.final_full_master_dict = final_full_master_dict

    def match_df(self):
        """
        we will go through all the df of the IPTS and will associate the df with the right samples
        based on:
        - detector type used
        - acquisition time
        """
        list_df_dict = self.df_metadata_dict
        final_full_master_dict = self.final_full_master_dict
        list_of_sample_acquisition = final_full_master_dict.keys()

        for _index_df in list_df_dict.keys():
            _all_df_instrument_metadata = self.get_instrument_metadata_only(list_df_dict[_index_df])
            _df_instrument_metadata = WhichOBandDFtoUse._isolate_instrument_metadata(_all_df_instrument_metadata)
            _acquisition_time = _all_df_instrument_metadata[MetadataName.EXPOSURE_TIME]['value']
            if _acquisition_time in list_of_sample_acquisition:
                for _config_id in final_full_master_dict[_acquisition_time].keys():
                    _sample_metadata_infos = final_full_master_dict[_acquisition_time][_config_id]['metadata_infos']
                    if WhichOBandDFtoUse.all_metadata_match(_sample_metadata_infos,
                                                            _df_instrument_metadata):
                        final_full_master_dict[_acquisition_time][_config_id]['list_df'].append(list_df_dict[_index_df])

        self.final_full_master_dict = final_full_master_dict

    def create_master_sample_dict(self):

        final_full_master_dict = collections.OrderedDict()
        sample_metadata_dict = self.sample_metadata_dict

        # we need to keep record of which image was the first one taken and which image was the last one taken
        first_sample_image = sample_metadata_dict[0]
        last_sample_image = sample_metadata_dict[0]

        for _file_index in sample_metadata_dict.keys():

            _dict_file_index = sample_metadata_dict[_file_index]
            _sample_file = _dict_file_index['filename']

            _acquisition_time = _dict_file_index[MetadataName.EXPOSURE_TIME]['value']
            _instrument_metadata = WhichOBandDFtoUse._isolate_instrument_metadata(_dict_file_index)
            _sample_time_stamp = _dict_file_index['time_stamp']

            # find which image was first and which image was last
            if _sample_time_stamp < first_sample_image['time_stamp']:
                first_sample_image = _dict_file_index
            elif _sample_time_stamp > last_sample_image['time_stamp']:
                last_sample_image = _dict_file_index

            # first entry or first time seeing that acquisition time
            if (len(final_full_master_dict) == 0) or not (_acquisition_time in final_full_master_dict.keys()):
                _first_images_dict = {'sample': first_sample_image,
                                      'ob': {},
                                      'df': {}}
                _last_images_dict = {'sample': last_sample_image,
                                     'ob': {},
                                     'df': {}}
                _temp_dict = {'list_sample': [_dict_file_index],
                              'first_images': _first_images_dict,
                              'last_images': _last_images_dict,
                              'list_ob': [],
                              'list_df': [],
                              'time_range_s_selected': {'before': np.NaN,
                                                        'after': np.NaN},
                              'time_range_s': {'before': np.NaN,
                                               'after': np.NaN},
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
                            _config['list_sample'].append(_dict_file_index)

                            _first_images_dict = {'sample': first_sample_image,
                                                  'ob': {},
                                                  'df': {}}
                            _last_images_dict = {'sample': last_sample_image,
                                                 'ob': {},
                                                 'df': {}}

                            _config['first_images'] = _first_images_dict
                            _config['last_images'] = _last_images_dict
                            _found_a_match = True

                    if not _found_a_match:
                        _first_images_dict = {'sample': first_sample_image,
                                              'ob': {},
                                              'df': {}}
                        _last_images_dict = {'sample': last_sample_image,
                                             'ob': {},
                                             'df': {}}

                        _temp_dict = {'list_sample': [_dict_file_index],
                                      'first_images': _first_images_dict,
                                      'last_images': _last_images_dict,
                                      'list_ob': [],
                                      'list_df': [],
                                      'time_range_s_selected': {'before': np.NaN,
                                                                'after': np.NaN},
                                      'time_range_s': {'before': np.NaN,
                                                       'after': np.NaN},
                                      'metadata_infos': WhichOBandDFtoUse.get_instrument_metadata_only(_instrument_metadata)}
                        nbr_config = len(_dict_for_this_acquisition_time.keys())
                        _dict_for_this_acquisition_time['config{}'.format(nbr_config)] = _temp_dict

                else:
                    _first_images_dict = {'sample': first_sample_image,
                                          'ob': {},
                                          'df': {}}
                    _last_images_dict = {'sample': last_sample_image,
                                         'ob': {},
                                         'df': {}}

                    _temp_dict = {'list_sample': [_dict_file_index],
                                  'first_images': _first_images_dict,
                                  'last_images': _last_images_dict,
                                  'list_ob': [],
                                  'list_df': [],
                                  'time_range_s_selected': {'before': np.NAN,
                                                            'after': np.NaN},
                                  'time_range_s': {'before': np.NaN,
                                                   'after': np.NaN},
                                  'metadata_infos': WhichOBandDFtoUse.get_instrument_metadata_only(_instrument_metadata)}
                    final_full_master_dict[_acquisition_time] = {}
                    final_full_master_dict[_acquisition_time]['config0'] = _temp_dict

        self.final_full_master_dict = final_full_master_dict

    def calculate_first_and_last_ob(self):
        """this will loop through all the acquisition time keys, and config keys, to figure out
        what is the first ob and last ob in this dictionary"""
        _final_full_master_dict = self.final_full_master_dict
        for _acquisition in _final_full_master_dict.keys():
            current_acquisition_dict = _final_full_master_dict[_acquisition]

            _first_ob_time = np.NaN
            _first_ob = {}
            _last_ob_time = np.NaN
            _last_ob = {}
            for _config in current_acquisition_dict.keys():
                current_acquisition_config_dict = current_acquisition_dict[_config]
                for _ob in current_acquisition_config_dict['list_ob']:
                    _current_ob_time = _ob['time_stamp']
                    if np.isnan(_first_ob_time):
                        _first_ob_time = _current_ob_time
                        _last_ob_time = _current_ob_time
                        _first_ob = _last_ob = _ob
                    elif _current_ob_time < _first_ob_time:
                        _first_ob_time = _current_ob_time
                        _first_ob = _ob
                    elif _current_ob_time > _last_ob_time:
                        _last_ob_time = _current_ob_time
                        _last_ob = _ob

                current_acquisition_config_dict['first_images']['ob'] = _first_ob
                current_acquisition_config_dict['last_images']['ob'] = _last_ob

    def calculate_time_range(self):
        """this method will calculate the max time range of OB taken before or after and will use that
        for the slider selection time range
        Provide option to use all (that means, do not used any time range)
        """
        _final_full_master_dict = self.final_full_master_dict
        for _acquisition in _final_full_master_dict.keys():
            current_acquisition_dict = _final_full_master_dict[_acquisition]
            for _config in current_acquisition_dict.keys():
                current_acquisition_config_dict = current_acquisition_dict[_config]

            first_sample_image = current_acquisition_config_dict['first_images']['sample']
            first_ob_image = current_acquisition_config_dict['first_images']['ob']
            delta_time_before = first_sample_image['time_stamp'] - first_ob_image['time_stamp']
            _time_range_s_before = delta_time_before if delta_time_before > 0 else 0

            last_sample_image = current_acquisition_config_dict['last_images']['sample']
            last_ob_image = current_acquisition_config_dict['last_images']['ob']
            delta_time_after = last_ob_image['time_stamp'] - last_sample_image['time_stamp']
            _time_range_s_after = delta_time_after if delta_time_after > 0 else 0

            _final_full_master_dict[_acquisition][_config]['time_range_s']['before'] = _time_range_s_before
            _final_full_master_dict[_acquisition][_config]['time_range_s']['after'] = _time_range_s_after

    def display_time_range_selection_widgets(self):
        _final_full_master_dict = self.final_full_master_dict
        _config_tab_dict = {}  # will keep record of each config tab for each acquisition
        _acquisition_tabs = widgets.Tab()

        for _acquisition_index, _acquisition in enumerate(_final_full_master_dict.keys()):
            _dict_of_this_acquisition = _final_full_master_dict[_acquisition]

            _config_tab = widgets.Tab()
            _current_acquisition_tab_widgets_id = {'config_tab_id': _config_tab}
            for _index, _config in enumerate(_dict_of_this_acquisition.keys()):
                _dict_config = _dict_of_this_acquisition[_config]
                _dict = self.get_full_layout_for_this_config(_dict_config)
                _layout = _dict['verti_layout']
                _config_widgets_id_dict = _dict['config_widgets_id_dict']
                _config_tab.children += (_layout,)
                _config_tab.set_title(_index, _config)
                _current_acquisition_tab_widgets_id[_index] = _config_widgets_id_dict
            _config_tab_dict[_acquisition_index] = _current_acquisition_tab_widgets_id

            _acquisition_tabs.children += (_config_tab,)  # add all the config tab to top acquisition tab
            _acquisition_tabs.set_title(_acquisition_index, "Acquisition: {}s".format(_acquisition))
            _config_tab

        display(_acquisition_tabs)

        self.acquisition_tab = _acquisition_tabs
        self.config_tab_dict = _config_tab_dict

    def get_max_time_elapse_before_experiment(self):
        # this will use the first sample image taken, the first OB image taken and will calculate that
        # difference. If the OB was taken after the first image, time will be 0

        # retrieve acquisition and config values
        acquisition_key = np.float(self.get_active_tab_acquisition_key())  # ex: 55.0
        config_key = self.get_active_tab_config_key()  # ex: 'config0'

        # retrieve list of ob and df for this config for this acquisition
        final_full_master_dict = self.final_full_master_dict
        dict_for_this_config = final_full_master_dict[acquisition_key][config_key]

        # retrieve first and last sample file for this config and for this acquisition
        first_sample_image_time_stamp = dict_for_this_config['first_images']['sample']['time_stamp']
        first_ob = dict_for_this_config['first_images']['ob']['time_stamp']

        if first_ob > first_sample_image_time_stamp:
            return 0
        else:
            return first_sample_image_time_stamp - first_ob

    def get_max_time_elapse_after_experiment(self):
        # this will use the last sample image taken, the last OB image taken and will calculate that
        # difference. If the last OB was taken before the last image, time will be 0

        # retrieve acquisition and config values
        acquisition_key = np.float(self.get_active_tab_acquisition_key())  # ex: 55.0
        config_key = self.get_active_tab_config_key()  # ex: 'config0'

        # retrieve list of ob and df for this config for this acquisition
        final_full_master_dict = self.final_full_master_dict
        dict_for_this_config = final_full_master_dict[acquisition_key][config_key]

        # retrieve first and last sample file for this config and for this acquisition
        last_sample_images_time_stamp = dict_for_this_config['last_images']['sample']['time_stamp']
        last_ob = dict_for_this_config['last_images']['ob']['time_stamp']

        if last_ob < last_sample_images_time_stamp:
            return 0
        else:
            return last_sample_images_time_stamp - last_ob

    def get_full_layout_for_this_config(self, dict_config):

        config_widgets_id_dict = {}

        def _make_list_basename_file(list_name='list_sample'):
            return [os.path.basename(_entry['filename']) for _entry in dict_config[list_name]]

        list_sample = _make_list_basename_file(list_name='list_sample')
        list_ob = _make_list_basename_file(list_name='list_ob')
        list_df = _make_list_basename_file(list_name='list_df')

        # use custom time range check box
        check_box_user_time_range = widgets.Checkbox(description="Use custom time range",
                                                     value=False,
                                                     layout=widgets.Layout(width="35%"))
        config_widgets_id_dict['use_custom_time_range_checkbox'] = check_box_user_time_range

        check_box_user_time_range.observe(self.update_config_widgets, names='value')

        [max_time_elapse_before_experiment, max_time_elapse_after_experiment] = self.calculate_max_time_before_and_after_exp_for_this_config(dict_config)

        hori_layout1 = widgets.HBox([check_box_user_time_range,
                                    widgets.FloatSlider(value=-max_time_elapse_before_experiment,
                                                        min=-max_time_elapse_before_experiment,
                                                        max=0,
                                                        step=0.1,
                                                        readout=False,
                                                        layout=widgets.Layout(width="30%",
                                                                              visibility='hidden')),
                                    widgets.Label(" <<< EXPERIMENT >>> ",
                                                  layout=widgets.Layout(width="20%",
                                                                        visibility='hidden')),
                                    widgets.FloatSlider(value=max_time_elapse_before_experiment,
                                                        min=0,
                                                        max=max_time_elapse_after_experiment,
                                                        step=0.1,
                                                        readout=False,
                                                        layout=widgets.Layout(width="30%",
                                                                              visibility='hidden')),
                                     ])
        self.hori_layout1 = hori_layout1
        self.time_before_slider = hori_layout1.children[1]
        self.time_after_slider = hori_layout1.children[3]
        self.experiment_label = hori_layout1.children[2]
        self.time_after_slider.observe(self.update_time_range_event, names='value')
        self.time_before_slider.observe(self.update_time_range_event, names='value')
        config_widgets_id_dict['time_slider_before_experiment'] = hori_layout1.children[1]
        config_widgets_id_dict['time_slider_after_experiment'] = hori_layout1.children[3]
        config_widgets_id_dict['experiment_label'] = hori_layout1.children[2]

        # use all OB and DF
        hori_layout2 = widgets.HBox([widgets.Label("    ",
                                                   layout=widgets.Layout(width="20%")),
                                     widgets.HTML("",
                                                   layout=widgets.Layout(width="80%"))])
        self.hori_layout2 = hori_layout2
        self.time_before_and_after_message = hori_layout2.children[1]
        config_widgets_id_dict['time_slider_before_message'] = hori_layout2.children[1]

        # table of metadata
        [metadata_table_label, metadata_table] = self.populate_metadata_table(dict_config)

        select_width = '300px'
        sample_list_of_runs = widgets.VBox([widgets.Label("List of Sample Runs",
                                           layout=widgets.Layout(width='100%')),
                             widgets.Select(options=list_sample,
                                            layout=widgets.Layout(width=select_width,
                                                                  height='300px'))],
                            layout=widgets.Layout(width="360px"))
        # self.list_of_runs_ui = box0.children[1]
        ob_list_of_runs = widgets.VBox([widgets.Label("List of OB",
                                                          layout=widgets.Layout(width='100%')),
                                            widgets.Select(options=list_ob,
                                                           layout=widgets.Layout(width=select_width,
                                                                                 height='300px'))],
                                           layout=widgets.Layout(width="360px"))
        df_list_of_runs = widgets.VBox([widgets.Label("List of DF",
                                                          layout=widgets.Layout(width='100%')),
                                            widgets.Select(options=list_df,
                                                           layout=widgets.Layout(width=select_width,
                                                                                 height='300px'))],
                                           layout=widgets.Layout(width="360px"))

        list_runs_layout = widgets.HBox([sample_list_of_runs,
                                         ob_list_of_runs,
                                         df_list_of_runs])
        config_widgets_id_dict['list_of_sample_runs'] = sample_list_of_runs.children[1]
        config_widgets_id_dict['list_of_ob'] = ob_list_of_runs.children[1]
        config_widgets_id_dict['list_of_df'] = df_list_of_runs.children[1]

        verti_layout = widgets.VBox([hori_layout1,
                                     hori_layout2,
                                     metadata_table_label,
                                     metadata_table,
                                     list_runs_layout])

        return {'verti_layout': verti_layout, 'config_widgets_id_dict': config_widgets_id_dict}

    def calculate_max_time_before_and_after_exp_for_this_config(self, dict_config):

        max_time_before = 0

        first_sample_image_time_stamp = dict_config['first_images']['sample']['time_stamp']
        first_ob_image_time_stamp = dict_config['first_images']['ob']['time_stamp']

        if first_ob_image_time_stamp > first_sample_image_time_stamp:
            max_time_before = 0
        else:
            max_time_before = (first_sample_image_time_stamp - first_ob_image_time_stamp)

        max_time_after = 0

        last_sample_image_time_stamp = dict_config['last_images']['sample']['time_stamp']
        last_ob_image_time_stamp = dict_config['last_images']['ob']['time_stamp']

        if last_ob_image_time_stamp < last_sample_image_time_stamp:
            max_time_after = 0
        else:
            max_time_after = last_ob_image_time_stamp - last_sample_image_time_stamp

        return [max_time_before, max_time_after]

    def populate_metadata_table(self, current_config):
        metadata_config = current_config['metadata_infos']
        table_label = widgets.Label("List of Metadata used to match data set",
                                    layout=widgets.Layout(width='30%'))

        table_value = "<table style='width:50%;background-color:#eee'>"
        for _key, _value in metadata_config.items():
            table_value += "<tr><th>{}</th><th>{}</th></tr>".format(_value['name'], _value['value'])
        table_value += "</table>"

        table = widgets.HTML(value=table_value)

        return [table_label, table]

    def update_config_widgets(self, state):

        if state['new'] is False:
            # use all files
            message = None
            visibility = 'hidden'
        else:
            # user defines ranges
            message = True
            visibility = 'visible'

        [time_before_selected_ui, time_after_selected_ui] = self.get_time_before_and_after_ui_of_this_config()
        time_before_selected_ui.layout.visibility = visibility
        time_after_selected_ui.layout.visibility = visibility
        experiment_label_ui = self.get_experiment_label_ui_of_this_config()
        experiment_label_ui.layout.visibility = visibility

        self.show_or_not_before_and_after_sliders()
        self.update_time_range_event(message)

    def show_or_not_before_and_after_sliders(self):
        current_config = self.get_current_config_dict()
        [max_time_elapse_before_experiment, max_time_elapse_after_experiment] = \
            self.calculate_max_time_before_and_after_exp_for_this_config(current_config)

        slider_before_visibility = 'visible' if max_time_elapse_before_experiment > 0 else 'hidden'
        slider_after_visibility = 'visible' if max_time_elapse_after_experiment > 0 else 'hidden'

        [time_before_selected_ui, time_after_selected_ui] = self.get_time_before_and_after_ui_of_this_config()
        time_before_selected_ui.layout.visibility = slider_before_visibility
        time_after_selected_ui.layout.visibility = slider_after_visibility

    def get_active_tabs(self):
        active_acquisition_tab = self.acquisition_tab.selected_index
        config_tab_dict = self.config_tab_dict[active_acquisition_tab]
        active_config_tab = config_tab_dict['config_tab_id'].selected_index
        return [active_acquisition_tab, active_config_tab]

    def get_active_tab_acquisition_key(self):
        active_acquisition_tab_index = self.acquisition_tab.selected_index
        title = self.acquisition_tab.get_title(active_acquisition_tab_index)
        [_, time_s] = title.split(": ")
        acquisition_key = time_s[:-1]
        return acquisition_key

    def get_active_tab_config_key(self):
        [active_acquisition, _] = self.get_active_tabs()
        all_config_tab_of_acquisition = self.config_tab_dict[active_acquisition]
        current_config_tab = all_config_tab_of_acquisition['config_tab_id']
        current_config_tab_index = current_config_tab.selected_index
        return current_config_tab.get_title(current_config_tab_index)

    def get_time_before_and_after_of_this_config(self, current_config=None):
        [time_before_selected_ui, time_after_selected_ui] = \
            self.get_time_before_and_after_ui_of_this_config(current_config=current_config)
        return [time_before_selected_ui.value, time_after_selected_ui.value]

    def get_time_before_and_after_ui_of_this_config(self, current_config=None):
        if current_config is None:
            current_config = self.get_current_config_of_widgets_id()
        return [current_config['time_slider_before_experiment'], current_config['time_slider_after_experiment']]

    def get_time_before_and_after_message_ui_of_this_config(self):
        current_config = self.get_current_config_of_widgets_id()
        return current_config['time_slider_before_message']

    def get_experiment_label_ui_of_this_config(self):
        current_config = self.get_current_config_of_widgets_id()
        return current_config['experiment_label']

    def is_custom_time_range_checked_for_this_config(self):
        current_config = self.get_current_config_of_widgets_id()
        return current_config['use_custom_time_range_checkbox'].value

    def get_current_config_dict(self):
        active_acquisition = self.get_active_tab_acquisition_key()
        active_config = self.get_active_tab_config_key()
        final_full_master_dict = self.final_full_master_dict
        current_config = final_full_master_dict[active_acquisition][active_config]
        return current_config

    def get_current_config_of_widgets_id(self):
        [active_acquisition, active_config] = self.get_active_tabs()
        all_config_tab_of_acquisition = self.config_tab_dict[active_acquisition]
        current_config_of_widgets_id = all_config_tab_of_acquisition[active_config]
        return current_config_of_widgets_id

    def update_time_range_event(self, value):
        # reach when user interact with the sliders in the config tab
        self.update_time_range_message(value)
        self.update_list_of_files_in_widgets_using_new_time_range()

    def update_list_of_files_in_widgets_using_new_time_range(self):

        # retrieve acquisition and config values
        acquisition_key = self.get_active_tab_acquisition_key()  # ex: '55.0'
        config_key = self.get_active_tab_config_key()  # ex: 'config0'

        # retrieve list of ob and df for this config for this acquisition
        final_full_master_dict = self.final_full_master_dict
        dict_for_this_config = final_full_master_dict[acquisition_key][config_key]
        list_ob = dict_for_this_config['list_ob']

        # no need to do anything more if user wants to use all the files
        if not self.is_custom_time_range_checked_for_this_config():
            list_ob_to_keep = [_file['filename'] for _file in list_ob]

        else:

            # retrieve first and last sample file for this config and for this acquisition
            first_sample_image_time_stamp = dict_for_this_config['first_images']['sample']['time_stamp']
            last_sample_images_time_stamp = dict_for_this_config['last_images']['sample']['time_stamp']

            # retrieve time before and after selected
            [time_before_selected, time_after_selected] = self.get_time_before_and_after_of_this_config()

            # calculate list of ob that are within that time range
            list_ob_to_keep = []
            for _ob_file in list_ob:
                _ob_time_stamp = _ob_file['time_stamp']
                if (_ob_time_stamp < first_sample_image_time_stamp) and \
                        ((first_sample_image_time_stamp-_ob_time_stamp) <= np.abs(time_before_selected)):
                    list_ob_to_keep.append(_ob_file['filename'])
                elif (_ob_time_stamp > last_sample_images_time_stamp) and \
                        ((_ob_time_stamp - last_sample_images_time_stamp) <= np.abs(time_after_selected)):
                    list_ob_to_keep.append(_ob_file['filename'])

        self.update_list_of_ob_for_current_config_tab(list_ob=list_ob_to_keep)

    def update_list_of_ob_for_current_config_tab(self, list_ob=[]):
        [active_acquisition, active_config] = self.get_active_tabs()
        short_version_list_ob = WhichOBandDFtoUse.keep_basename_only(list_files=list_ob)
        self.config_tab_dict[active_acquisition][active_config]['list_of_ob'].options = short_version_list_ob

    def update_time_range_message(self, value):
        if value is None:
            _message = f"Use <b><font color='red'>All </b> " \
                       f"<font color='black'>OBs and DFs " \
                       f"matching the samples images</font>"
        else:

            [time_before_selected, time_after_selected] = self.get_time_before_and_after_of_this_config()

            time_before_selected = np.abs(time_before_selected)

            def _format_time(_time_s):
                if _time_s < 60:
                    return "{:.02f}s".format(_time_s)
                elif _time_s < 3600:
                    _time_mn = _time_s / 60.
                    return "{:.02f}mn".format(_time_mn)
                else:
                    _time_hr = _time_s / 3600.
                    return "{:.02f}hr".format(_time_hr)

            str_time_before = _format_time(time_before_selected)
            str_time_after = _format_time(time_after_selected)

            _message = f"Use OB taken up to <b><font color='red'>{str_time_before}</b> " \
                       f"<font color='black'>before and up to </font>" \
                       f"<b><font color='red'>{str_time_after}</b> " \
                       f"<font color='black'>after experiment!</font>"

        time_before_and_after_message_ui = self.get_time_before_and_after_message_ui_of_this_config()
        time_before_and_after_message_ui.value = _message

    def create_final_json(self):
        # go through each of the acquisition tab and into each of the config to create the list of sample, ob and df
        # to use
        _final_full_master_dict = self.final_full_master_dict
        _config_tab_dict = self.config_tab_dict
        _final_json_dict = {}
        for _acquisition_index, _acquisition in enumerate(_final_full_master_dict.keys()):

            _final_json_for_this_acquisition = {}
            _config_of_this_acquisition = _config_tab_dict[_acquisition_index]
            _dict_of_this_acquisition = _final_full_master_dict[_acquisition]
            for _config_index, _config in enumerate(_dict_of_this_acquisition.keys()):
                this_config_tab_dict = _config_tab_dict[_acquisition_index][_config_index]

                _dict_of_this_acquisition_this_config = _dict_of_this_acquisition[_config]

                list_sample = [_file['filename'] for _file in _dict_of_this_acquisition_this_config['list_sample']]
                list_df = [_file['filename'] for _file in _dict_of_this_acquisition_this_config['list_df']]

                list_ob = _dict_of_this_acquisition_this_config['list_ob']
                use_custom_time_range_checkbox_id = this_config_tab_dict["use_custom_time_range_checkbox"]
                if not use_custom_time_range_checkbox_id.value:
                    list_ob_to_keep = [_file['filename'] for _file in _dict_of_this_acquisition_this_config['list_ob']]
                else:
                    # retrieve first and last sample file for this config and for this acquisition
                    first_sample_image_time_stamp = _dict_of_this_acquisition_this_config['first_images']['sample']['time_stamp']
                    last_sample_images_time_stamp = _dict_of_this_acquisition_this_config['last_images']['sample']['time_stamp']

                    [time_before_selected, time_after_selected] = \
                        self.get_time_before_and_after_of_this_config(current_config=this_config_tab_dict)

                    # calculate list of ob that are within that time range
                    list_ob_to_keep = []
                    for _ob_file in list_ob:
                        _ob_time_stamp = _ob_file['time_stamp']
                        if (_ob_time_stamp < first_sample_image_time_stamp) and \
                                ((first_sample_image_time_stamp - _ob_time_stamp) <= np.abs(time_before_selected)):
                            list_ob_to_keep.append(_ob_file['filename'])
                        elif (_ob_time_stamp > last_sample_images_time_stamp) and \
                                ((_ob_time_stamp - last_sample_images_time_stamp) <= np.abs(time_after_selected)):
                            list_ob_to_keep.append(_ob_file['filename'])

                _final_json_for_this_acquisition[_config] = {'list_sample': list_sample,
                                                             'list_df': list_df,
                                                             'list_ob': list_ob_to_keep}

            _final_json_dict[_acquisition] = _final_json_for_this_acquisition

        self.final_json_dict = _final_json_dict

    def normalization_recap(self):
        """this will show all the config that will be run and if they have the minimum requirements or not,
        which mean, at least 1 OB"""
        final_json = self.final_json_dict
        self.number_of_normalization = 0

        table = "<table style='width:50%;border:1px solid black'>"
        table += "<tr style='background-color:#eee'><th>Acquisition (s)</th><th>Config. name</th>" \
                 "<th>Nbr sample</th><th>Nbr OB</th><th>Nbr DF</th><th>Status</th></tr>"
        for _name_acquisition in final_json.keys():
            _current_acquisition_dict = final_json[_name_acquisition]
            for _name_config in _current_acquisition_dict.keys():
                _current_config_dict = _current_acquisition_dict[_name_config]

                nbr_ob = len(_current_config_dict['list_ob'])
                nbr_df = len(_current_config_dict['list_df'])
                nbr_sample = len(_current_config_dict['list_sample'])
                self.number_of_normalization += 1 if nbr_ob > 0 else 0
                table += WhichOBandDFtoUse.populate_normalization_recap_row(acquisition=_name_acquisition,
                                                                            config=_name_config,
                                                                            nbr_sample=nbr_sample,
                                                                            nbr_ob=nbr_ob,
                                                                            nbr_df=nbr_df)

        table += "</table>"
        table_ui = widgets.HTML(table)
        display(table_ui)

    def select_output_folder(self):
        self.output_folder_widget = ipywe.fileselector.FileSelectorPanel(instruction='select where to create the ' + \
                                                                                     'normalized folders',
                                                                         start_dir=self.working_dir,
                                                                         next=self.normalization,
                                                                         type='directory')

        self.output_folder_widget.show()

    def normalization(self, output_folder):
        final_json = self.final_json_dict
        number_of_normalization = self.number_of_normalization

        horizontal_layout = widgets.HBox([widgets.Label("Normalization progress",
                                                        layout=widgets.Layout(width='20%')),
                                          widgets.IntProgress(max=number_of_normalization,
                                                              value=0,
                                                              layout=widgets.Layout(width='50%'))])
        normalization_progress = horizontal_layout.children[1]
        display(horizontal_layout)

        for _name_acquisition in final_json.keys():
            _current_acquisition_dict = final_json[_name_acquisition]
            for _name_config in _current_acquisition_dict.keys():
                _current_config = _current_acquisition_dict[_name_config]

                list_ob = _current_config['list_ob']
                if list_ob == []:
                    continue

                list_sample = _current_config['list_sample']
                full_output_normalization_folder_name = \
                    WhichOBandDFtoUse.make_full_output_normalization_folder_name(output_folder=output_folder,
                                                                                 first_sample_file_name=list_sample[0],
                                                                                 name_acquisition=_name_acquisition,
                                                                                 name_config=_name_config)
                list_df = _current_config['list_df']

                o_load = Normalization()
                o_load.load(file=list_sample, notebook=False)
                o_load.load(file=list_ob, data_type='ob')
                o_load.load(file=list_df, data_type='df')

                o_load.normalization()
                o_load.export(folder=full_output_normalization_folder_name, file_type='tif')

                del o_load

                normalization_progress.value += 1

        normalization_progress.close()

        display(HTML('<span style="font-size: 20px; color:blue">Message here</span>'))

    @staticmethod
    def make_full_output_normalization_folder_name(output_folder='', first_sample_file_name='',
                                                   name_acquisition='', name_config=''):

        basename_sample_folder = os.path.basename(os.path.dirname(first_sample_file_name))
        basename_sample_folder += "_{}_{}".format(name_acquisition, name_config)
        full_basename_sample_folder = os.path.abspath(os.path.join(output_folder, basename_sample_folder))
        file_handler.make_or_reset_folder(full_basename_sample_folder)
        return full_basename_sample_folder

    @staticmethod
    def populate_normalization_recap_row(acquisition="", config="", nbr_sample=0, nbr_ob=0, nbr_df=0):
        if nbr_ob > 0:
            status_string = "<th style='color:#odbc2e'>OK</th>"
        else:
            status_string = "<th style='color:#ff0000'>Missing OB!</th>"

        _row = ""
        _row = "<tr><th>{}</th><th>{}</th><th>{}</th><th>{}</th><th>{}</th>{}</tr>".\
            format(acquisition, config, nbr_sample, nbr_ob, nbr_df, status_string)
        return _row


    @staticmethod
    def keep_basename_only(list_files=[]):
        basename_only = [os.path.basename(_file) for _file in list_files]
        return basename_only

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
            try:
                if np.abs(np.float(metadata_1[_key]['value'] - np.float(metadata_2[_key]['value']))) > METADATA_ERROR_ALLOWED:
                    return False
            except ValueError:
                if metadata_1[_key]['value'] != metadata_2[_key]['value']:
                    return False
        return True

    @staticmethod
    def _isolate_instrument_metadata(dictionary):
        """create a dictionary of all the instrument metadata without the acquisition time"""
        isolated_dictionary = {}
        for _key in dictionary.keys():
            if _key == MetadataName.EXPOSURE_TIME:
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
        dict = {'file1': {'metadata1_key': {'value': value, 'name': name},
                          'metadata2_key': {'value': value, 'name': name},
                          'metadata3_key': {'value': value, 'name': name},
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
        list_metadata = METADATA_KEYS['all']
        _dict = metadata_handler.MetadataHandler.retrieve_metadata(list_files=list_files,
                                                                   list_metadata=list_metadata,
                                                                   using_enum_object=True)

        for _file_key in _dict.keys():
            _file_dict = {}
            for _pv in list_metadata:
                _raw_value = _dict[_file_key][_pv]
                if _raw_value is not None:
                    split_raw_value = _raw_value.split(":")
                    try:
                        _value = np.float(split_raw_value[1])
                    except ValueError:
                        _value = split_raw_value[1]
                    finally:
                        _file_dict[_pv.value] = {'value': _value, 'name': _pv.name}
                else:
                    _file_dict[_pv.value] = {}
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














    # def get_list_of_images_in_range(self, time_range_s=1,
    #                                 timelapse_option="before_or_after",
    #                                 data_type='ob'):
    #
    #     if data_type == 'ob':
    #         data = self.ob_time_stamp_dict
    #     else:
    #         data = self.df_time_stamp_dict
    #
    #     first_image_system_time = self.first_image_dict['system_time']
    #     last_image_system_time = self.last_image_dict['system_time']
    #
    #     list_filename = data['list_images']
    #     list_timestamp = data['list_time_stamp']
    #
    #     # before
    #     list_index_to_keep = []
    #     for _index, _time in enumerate(list_timestamp):
    #
    #         # ob or df was taken after first raw and before last raw data, we keep it
    #         if (_time > first_image_system_time) and (_time < last_image_system_time):
    #             list_index_to_keep.append(_index)
    #             continue
    #
    #         if timelapse_option == 'before':
    #             if (_time < first_image_system_time) and \
    #                     (np.abs(first_image_system_time-_time) <= time_range_s):
    #                 list_index_to_keep.append(_index)
    #         elif timelapse_option == 'after':
    #             if (_time > last_image_system_time) and \
    #                     (np.abs(last_image_system_time-_time) <= time_range_s):
    #                 list_index_to_keep.append(_index)
    #         else:
    #             if ((_time < first_image_system_time) and
    #                 (np.abs(first_image_system_time - _time) <= time_range_s)) or \
    #                     ((_time > last_image_system_time) and
    #                      (np.abs(last_image_system_time - _time) <= time_range_s)):
    #                 list_index_to_keep.append(_index)
    #
    #     return list_filename[list_index_to_keep]

    # def recalculate_files_in_range(self):
    #     time_range_value = self.time_slider.value
    #     timelapse = self.timelapse_selection_widget.value
    #
    #     list_ob_in_range = self.get_list_of_images_in_range(time_range_s=time_range_value*3600,
    #                                                         timelapse_option=timelapse,
    #                                                         data_type='ob')
    #     self.list_of_ob_in_range_widget.value = list_ob_in_range

    # def calculate_max_time_range_between_images(self):
    #     """this method will determine what is the max time difference between the sample data set and
    #     the ob images
    #     The algorithm will use the first and last ob and sample data set to find this range
    #     """
    #     first_image_system_time = self.first_image_dict['system_time']
    #     last_image_system_time = self.last_image_dict['system_time']
    #
    #     _ob_time_stamp_dict = self.ob_time_stamp_dict['list_time_stamp']
    #     first_and_last_ob_system_time = WhichOBandDFtoUse.calculate_first_and_last_system_time(_ob_time_stamp_dict)
    #     first_ob_system_time = first_and_last_ob_system_time['first_stamp']
    #     last_ob_system_time = first_and_last_ob_system_time['last_stamp']
    #
    #     time_offset_before = 0
    #     if first_image_system_time > first_ob_system_time:
    #         time_offset_before = first_image_system_time - first_ob_system_time
    #
    #     time_offset_after = 0
    #     if last_image_system_time < last_ob_system_time:
    #         time_offset_after = last_ob_system_time - last_image_system_time
    #
    #     max_time_range_s = np.max([time_offset_before, time_offset_after])
    #     max_time_range_hours = time_utility.convert_system_time_into_hours(max_time_range_s)
    #
    #     return np.ceil(max_time_range_hours)

    # @staticmethod
    # def calculate_first_and_last_system_time(list_stamp_dict):
    #     first_stamp = list_stamp_dict[0]
    #     last_stamp = list_stamp_dict[-1]
    #     for _time in list_stamp_dict[1:]:
    #         if _time < first_stamp:
    #             first_stamp = _time
    #         elif _time > last_stamp:
    #             last_stamp = _time
    #
    #     return {'first_stamp': first_stamp,
    #             'last_stamp': last_stamp}





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






