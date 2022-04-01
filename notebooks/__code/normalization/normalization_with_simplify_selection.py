import os
import collections
import numpy as np
from ipywidgets import widgets
from IPython.core.display import display, HTML
import logging

from NeuNorm.normalization import Normalization

from __code import file_handler
from __code.ipywe import myfileselector
from __code.normalization.get import Get
from __code.normalization.metadata_handler import MetadataHandler, MetadataName, METADATA_KEYS
from __code.normalization import utilities

JSON_DEBUGGING = False

MAX_DF_COUNTS_ALLOWED = 900
METADATA_ERROR_ALLOWED = 1
LIST_METADATA_NOT_INSTRUMENT_RELATED = ['filename', 'time_stamp', 'time_stamp_user_format']


class NormalizationWithSimplifySelection:

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

        o_get = Get(parent=self)
        log_file_name = o_get.log_file_name()
        logging.basicConfig(filename=log_file_name,
                            filemode='w',
                            format='[%(levelname)s] - %(asctime)s - %(message)s',
                            level=logging.INFO)   # logging.INFO, logging.DEBUG
        logging.info("*** Starting new session ***")

    def select_sample_folder(self):
        folder_sample_widget = myfileselector.MyFileSelectorPanel(instruction='select folder of images to normalize',
                                                                  start_dir=self.working_dir,
                                                                  next=self.retrieve_sample_metadata_from_sample_folder,
                                                                  type='directory',
                                                                  multiple=False)
        folder_sample_widget.show()

    def retrieve_sample_metadata_from_sample_folder(self, sample_folder):
        logging.info(f"select sample folder: {sample_folder}")
        [list_of_images, _] = file_handler.retrieve_list_of_most_dominant_extension_from_folder(folder=sample_folder)
        can_we_continue = self.images_files_found_in_list(list_of_images)
        if can_we_continue:
            logging.info(f"-> number of images found: {len(list_of_images)}")
            self.retrieve_sample_metadata(list_of_images)
        else:
            logging.info(f"-> No images found!")
            display(HTML('<span style="font-size: 20px; color:Red">No images found in the folder selected!</span>'))

    def images_files_found_in_list(self, list_of_images):
        for _file in list_of_images:
            if (".tiff" in _file) or (".tif" in _file) or (".fits" in _file):
                return True
        return False

    def retrieve_sample_metadata(self, list_of_images):
        __name__ = "retrieve_sample_metadata"

        logging.info(f"Retrieving sample metadata ({__name__})")
        self.list_of_images = list_of_images
        self.sample_metadata_dict = MetadataHandler.retrieve_metadata(list_of_files=list_of_images,
                                                                      display_infos=False,
                                                                      label='sample')
        # logging.info(f"self.sample_metadata_dict: {self.sample_metadata_dict}")
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
        list_of_ob_files = Get.list_of_tiff_files(folder=selected_folder)
        self.ob_metadata_dict = MetadataHandler.retrieve_metadata(list_of_files=list_of_ob_files)

    def auto_retrieve_ob_metadata(self):
        logging.info(f"> auto_retrieve_ob_metadata")
        folder = os.path.join(self.working_dir, 'raw', 'ob')
        logging.info(f"-> folder: {folder}")
        list_of_ob_files = file_handler.get_list_of_all_files_in_subfolders(folder=folder,
                                                                            extensions=['tiff', 'tif'])
        logging.info(f"-> nbr of ob files found: {len(list_of_ob_files)}")
        self.ob_metadata_dict = MetadataHandler.retrieve_metadata(list_of_files=list_of_ob_files,
                                                                  label='ob')

        # logging.info(f"ob metadata dict")
        # logging.info(f"-> {self.ob_metadata_dict}")

    def select_folder(self, message="", next_function=None):
        folder_widget = myfileselector.MyFileSelectorPanel(instruction='select {} folder'.format(message),
                                                           start_dir=self.working_dir,
                                                           next=next_function,
                                                           type='directory',
                                                           multiple=False)
        folder_widget.show()

    def select_df_folder(self):
        self.select_folder(message='dark field',
                           next_function=self.retrieve_df_metadata())

    def retrieve_df_metadata(self, selected_folder):
        list_of_df_files = Get.list_of_tiff_files(folder=selected_folder)
        self.df_metadata_dict = MetadataHandler.retrieve_metadata(list_of_files=list_of_df_files)

    def auto_retrieve_df_metadata(self):
        folder = os.path.join(self.working_dir, 'raw', 'df')
        list_of_df_files = file_handler.get_list_of_all_files_in_subfolders(folder=folder,
                                                                            extensions=['tiff', 'tif'])
        logging.info(f"-> nbr of df files found: {len(list_of_df_files)}")
        self.df_metadata_dict = MetadataHandler.retrieve_metadata(list_of_files=list_of_df_files,
                                                                  label='df')

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
            _all_ob_instrument_metadata = Get.get_instrument_metadata_only(list_ob_dict[_index_ob])
            _ob_instrument_metadata = utilities.isolate_instrument_metadata(
                    _all_ob_instrument_metadata)
            _acquisition_time = _all_ob_instrument_metadata[MetadataName.EXPOSURE_TIME.value]['value']
            if _acquisition_time in list_of_sample_acquisition:
                for _config_id in final_full_master_dict[_acquisition_time].keys():
                    _sample_metadata_infos = final_full_master_dict[_acquisition_time][_config_id]['metadata_infos']
                    if utilities.all_metadata_match(_sample_metadata_infos, _ob_instrument_metadata):
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
            _all_df_instrument_metadata = Get.get_instrument_metadata_only(list_df_dict[_index_df])
            _df_instrument_metadata = utilities.isolate_instrument_metadata(
                    _all_df_instrument_metadata)
            _acquisition_time = _all_df_instrument_metadata[MetadataName.EXPOSURE_TIME.value]['value']

            if _acquisition_time in list_of_sample_acquisition:
                for _config_id in final_full_master_dict[_acquisition_time].keys():
                    _sample_metadata_infos = final_full_master_dict[_acquisition_time][_config_id]['metadata_infos']

                    if utilities.all_metadata_match(_sample_metadata_infos, _df_instrument_metadata,
                                                    list_key_to_check=[METADATA_KEYS['df'][
                                                                           1].value]):
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

            _acquisition_time = _dict_file_index[MetadataName.EXPOSURE_TIME.value]['value']
            _instrument_metadata = utilities.isolate_instrument_metadata(_dict_file_index)
            _sample_time_stamp = _dict_file_index['time_stamp']

            # find which image was first and which image was last
            if _sample_time_stamp < first_sample_image['time_stamp']:
                first_sample_image = _dict_file_index
            elif _sample_time_stamp > last_sample_image['time_stamp']:
                last_sample_image = _dict_file_index

            # first entry or first time seeing that acquisition time
            if (len(final_full_master_dict) == 0) or not (_acquisition_time in final_full_master_dict.keys()):
                _first_images_dict = {'sample': first_sample_image,
                                      'ob'    : {},
                                      'df'    : {}}
                _last_images_dict = {'sample': last_sample_image,
                                     'ob'    : {},
                                     'df'    : {}}
                _temp_dict = {'list_sample'          : [_dict_file_index],
                              'first_images'         : _first_images_dict,
                              'last_images'          : _last_images_dict,
                              'list_ob'              : [],
                              'list_df'              : [],
                              'time_range_s_selected': {'before': np.NaN,
                                                        'after' : np.NaN},
                              'time_range_s'         : {'before': np.NaN,
                                                        'after' : np.NaN},
                              'metadata_infos'       : Get.get_instrument_metadata_only(
                                      _instrument_metadata)}
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
                        if (utilities.all_metadata_match(metadata_1=_config['metadata_infos'],
                                                         metadata_2=_instrument_metadata)):
                            _config['list_sample'].append(_dict_file_index)

                            _first_images_dict = {'sample': first_sample_image,
                                                  'ob'    : {},
                                                  'df'    : {}}
                            _last_images_dict = {'sample': last_sample_image,
                                                 'ob'    : {},
                                                 'df'    : {}}

                            _config['first_images'] = _first_images_dict
                            _config['last_images'] = _last_images_dict
                            _found_a_match = True

                    if not _found_a_match:
                        _first_images_dict = {'sample': first_sample_image,
                                              'ob'    : {},
                                              'df'    : {}}
                        _last_images_dict = {'sample': last_sample_image,
                                             'ob'    : {},
                                             'df'    : {}}

                        _temp_dict = {'list_sample'          : [_dict_file_index],
                                      'first_images'         : _first_images_dict,
                                      'last_images'          : _last_images_dict,
                                      'list_ob'              : [],
                                      'list_df'              : [],
                                      'time_range_s_selected': {'before': np.NaN,
                                                                'after' : np.NaN},
                                      'time_range_s'         : {'before': np.NaN,
                                                                'after' : np.NaN},
                                      'metadata_infos'       : Get.get_instrument_metadata_only(
                                              _instrument_metadata)}
                        nbr_config = len(_dict_for_this_acquisition_time.keys())
                        _dict_for_this_acquisition_time['config{}'.format(nbr_config)] = _temp_dict

                else:
                    _first_images_dict = {'sample': first_sample_image,
                                          'ob'    : {},
                                          'df'    : {}}
                    _last_images_dict = {'sample': last_sample_image,
                                         'ob'    : {},
                                         'df'    : {}}

                    _temp_dict = {'list_sample'          : [_dict_file_index],
                                  'first_images'         : _first_images_dict,
                                  'last_images'          : _last_images_dict,
                                  'list_ob'              : [],
                                  'list_df'              : [],
                                  'time_range_s_selected': {'before': np.NAN,
                                                            'after' : np.NaN},
                                  'time_range_s'         : {'before': np.NaN,
                                                            'after' : np.NaN},
                                  'metadata_infos'       : Get.get_instrument_metadata_only(
                                          _instrument_metadata)}
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

            delta_time_before = first_sample_image.get('time_stamp', 0) - first_ob_image.get('time_stamp', 0)
            _time_range_s_before = delta_time_before if delta_time_before > 0 else 0

            last_sample_image = current_acquisition_config_dict['last_images']['sample']
            last_ob_image = current_acquisition_config_dict['last_images']['ob']
            delta_time_after = last_ob_image.get('time_stamp', 0) - last_sample_image.get('time_stamp', 0)
            _time_range_s_after = delta_time_after if delta_time_after > 0 else 0

            _final_full_master_dict[_acquisition][_config]['time_range_s']['before'] = _time_range_s_before
            _final_full_master_dict[_acquisition][_config]['time_range_s']['after'] = _time_range_s_after

    def display_time_range_selection_widgets(self):
        _final_full_master_dict = self.final_full_master_dict
        _config_tab_dict = {}  # will keep record of each config tab for each acquisition
        _acquisition_tabs = widgets.Tab()

        o_get = Get(parent=self)

        for _acquisition_index, _acquisition in enumerate(_final_full_master_dict.keys()):
            _dict_of_this_acquisition = _final_full_master_dict[_acquisition]

            _config_tab = widgets.Tab()
            _current_acquisition_tab_widgets_id = {'config_tab_id': _config_tab}
            for _index, _config in enumerate(_dict_of_this_acquisition.keys()):
                _dict_config = _dict_of_this_acquisition[_config]
                _dict = o_get.full_layout_for_this_config(_dict_config)
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

    def calculate_max_time_before_and_after_exp_for_this_config(self, dict_config):

        max_time_before = 0

        first_sample_image_time_stamp = dict_config['first_images']['sample']['time_stamp']
        first_ob_image_time_stamp = dict_config['first_images']['ob'].get('time_stamp', 0)

        if first_ob_image_time_stamp > first_sample_image_time_stamp:
            max_time_before = 0
        else:
            max_time_before = (first_sample_image_time_stamp - first_ob_image_time_stamp)

        max_time_after = 0

        last_sample_image_time_stamp = dict_config['last_images']['sample']['time_stamp']
        last_ob_image_time_stamp = dict_config['last_images']['ob'].get('time_stamp', 0)

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

    def update_use_this_config_widget(self, state):
       pass

    def update_config_widgets(self, state):
        if state['new'] is False:
            # use all files
            message = None
            visibility = 'hidden'
        else:
            # user defines ranges
            message = True
            visibility = 'visible'

        o_get = Get(parent=self)
        [time_before_selected_ui, time_after_selected_ui] = o_get.time_before_and_after_ui_of_this_config()
        experiment_label_ui = o_get.experiment_label_ui_of_this_config()
        experiment_label_ui.layout.visibility = visibility

        if visibility == 'hidden':
            time_before_selected_ui.layout.visibility = 'hidden'
            time_after_selected_ui.layout.visibility = 'hidden'
        else:
            self.show_or_not_before_and_after_sliders()

        self.update_time_range_event(message)

    def show_or_not_before_and_after_sliders(self):
        o_get = Get(parent=self)
        current_config = o_get.current_config_dict()
        [max_time_elapse_before_experiment, max_time_elapse_after_experiment] = \
            self.calculate_max_time_before_and_after_exp_for_this_config(current_config)

        slider_before_visibility = 'visible' if max_time_elapse_before_experiment > 0 else 'hidden'
        slider_after_visibility = 'visible' if max_time_elapse_after_experiment > 0 else 'hidden'

        [time_before_selected_ui, time_after_selected_ui] = o_get.time_before_and_after_ui_of_this_config()
        time_before_selected_ui.layout.visibility = slider_before_visibility
        time_after_selected_ui.layout.visibility = slider_after_visibility

    def is_custom_time_range_checked_for_this_config(self):
        o_get = Get(parent=self)
        current_config = o_get.current_config_of_widgets_id()
        return current_config['use_custom_time_range_checkbox'].value

    def update_time_range_event(self, value):
        # reach when user interact with the sliders in the config tab
        self.update_time_range_message(value)
        self.update_list_of_files_in_widgets_using_new_time_range()

    def update_list_of_files_in_widgets_using_new_time_range(self):
        o_get = Get(parent=self)
        # retrieve acquisition and config values

        acquisition_key = o_get.active_tab_acquisition_key()  # ex: '55.0'
        config_key = o_get.active_tab_config_key()  # ex: 'config0'

        # retrieve list of ob and df for this config for this acquisition
        final_full_master_dict = self.final_full_master_dict
        dict_for_this_config = final_full_master_dict[float(acquisition_key)][config_key]
        list_ob = dict_for_this_config['list_ob']

        # no need to do anything more if user wants to use all the files
        if not self.is_custom_time_range_checked_for_this_config():
            list_ob_to_keep = [_file['filename'] for _file in list_ob]

        else:

            # retrieve first and last sample file for this config and for this acquisition
            first_sample_image_time_stamp = dict_for_this_config['first_images']['sample']['time_stamp']
            last_sample_images_time_stamp = dict_for_this_config['last_images']['sample']['time_stamp']

            # retrieve time before and after selected
            [time_before_selected, time_after_selected] = o_get.time_before_and_after_of_this_config()

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

        self.update_list_of_ob_for_current_config_tab(list_ob=list_ob_to_keep)

    def update_list_of_ob_for_current_config_tab(self, list_ob=[]):
        o_get = Get(parent=self)
        [active_acquisition, active_config] = o_get.active_tabs()
        # short_version_list_ob = NormalizationWithSimplifySelection.keep_basename_only(list_files=list_ob)
        self.config_tab_dict[active_acquisition][active_config]['list_of_ob'].options = list_ob
        # select everything by default
        self.config_tab_dict[active_acquisition][active_config]['list_of_ob'].value = list_ob

    def update_time_range_message(self, value):
        o_get = Get(parent=self)
        if value is None:
            _message = "Select the <b><font color='red'>OBs</font></b> and " \
                       "<b><font color='red'>DFs</font></b> to use in the normalization"
            # _message = "Use <b><font color='red'>All </b> " \
            #            "<font color='black'>OBs and DFs " \
            #            "matching the samples images</font>"
        else:

            [time_before_selected, time_after_selected] = o_get.time_before_and_after_of_this_config()

            time_before_selected = np.abs(time_before_selected)

            def _format_time(_time_s):
                if _time_s < 60:
                    return "{:.2f}s".format(_time_s)
                elif _time_s < 3600:
                    _time_mn = int(_time_s / 60.)
                    _time_s = int(_time_s % 60)
                    return "{:d}mn {:d}s".format(_time_mn, _time_s)
                else:
                    _time_hr = int(_time_s / 3600.)
                    _time_s_left = _time_s - _time_hr * 3600
                    _time_mn = int(_time_s_left / 60.)
                    _time_s = int(_time_s_left % 60)
                    return "{:d}hr {:d}mn {:d}s".format(_time_hr, _time_mn, _time_s)

            str_time_before = _format_time(time_before_selected)
            str_time_after = _format_time(time_after_selected)

            logging.info(f"str_time_before: {time_before_selected} -> {str_time_before}")

            _message = "Use OB taken up to <b><font color='red'>" + str_time_before + "</b> " \
                                                                                      "<font color='black'>before and up to </font>" \
                                                                                      "<b><font color='red'>" + str_time_after + "</b> " \
                                                                                                                                 "<font color='black'>after experiment!</font>"

        time_before_and_after_message_ui = o_get.time_before_and_after_message_ui_of_this_config()
        time_before_and_after_message_ui.value = _message

    def do_you_want_to_combine_changed(self, value):
        do_you_want_to_combine = value['new']
        if do_you_want_to_combine == 'yes':
            disabled_how_to_combine = False
        else:
            disabled_how_to_combine = True

        o_get = Get(parent=self)
        [active_acquisition, active_config] = o_get.active_tabs()
        self.config_tab_dict[active_acquisition][active_config]['how_to_combine'].disabled = disabled_how_to_combine
        self.update_this_config_table()

    def how_to_combine_changed(self, value):
        self.update_this_config_table()

    def update_this_config_table(self):
        o_get = Get(parent=self)
        [active_acquisition, active_config] = o_get.active_tabs()
        table_ui = self.config_tab_dict[active_acquisition][active_config]['table']

        nbr_ob = len(self.config_tab_dict[active_acquisition][active_config]['list_of_ob'].value)
        nbr_sample = len(self.config_tab_dict[active_acquisition][active_config]['list_of_sample_runs'].options)
        nbr_df = len(self.config_tab_dict[active_acquisition][active_config]['list_of_df'].value)

        force_combine_disabled_state = self.config_tab_dict[active_acquisition][active_config]['force_combine'].disabled
        force_combine_value = self.config_tab_dict[active_acquisition][active_config]['force_combine'].value

        how_to_combine_value = self.config_tab_dict[active_acquisition][active_config]['how_to_combine'].value








    def selection_of_ob_changed(self, value):
        list_ob_selected = value['new']
        nbr_ob = len(list_ob_selected)
        o_get = Get(parent=self)
        [active_acquisition, active_config] = o_get.active_tabs()
        list_sample = self.config_tab_dict[active_acquisition][active_config]['list_of_sample_runs'].options
        nbr_sample = len(list_sample)

        if nbr_sample == nbr_ob:
            self.config_tab_dict[active_acquisition][active_config]['force_combine'].disabled = False
            self.config_tab_dict[active_acquisition][active_config]['force_combine_message'].value = ""
        else:
            self.config_tab_dict[active_acquisition][active_config]['force_combine'].disabled = True
            self.config_tab_dict[active_acquisition][active_config]['force_combine_message'].value = \
                "<font color='blue'>INFO</font>: the option to combine or not is disabled as the number of " \
                          "<b>sample</b> " \
                          "and " \
                          "<b>obs</b> do not match. The <b>OBs</b> will be combined!"

    def checking_normalization_workflow(self):
        self.create_final_json()
        self.normalization_recap()

    def create_final_json(self):
        _final_full_master_dict = self.final_full_master_dict
        _config_tab_dict = self.config_tab_dict
        _final_json_dict = {}

        for _acquisition_index, _acquisition in enumerate(_final_full_master_dict.keys()):

            _final_json_for_this_acquisition = {}
            _config_of_this_acquisition = _config_tab_dict[_acquisition_index]
            _dict_of_this_acquisition = _final_full_master_dict[_acquisition]
            for _config_index, _config in enumerate(_dict_of_this_acquisition.keys()):

                this_config_tab_dict = _config_tab_dict[_acquisition_index][_config_index]
                normalize_flag = this_config_tab_dict['use_this_config']

                list_sample = this_config_tab_dict['list_of_sample_runs'].options
                list_ob = this_config_tab_dict['list_of_ob'].value
                list_df = this_config_tab_dict['list_of_df'].value

                _final_json_for_this_acquisition[_config] = {'list_sample'          : list_sample,
                                                             'list_df'              : list_df,
                                                             'list_ob'              : list_ob,
                                                             'normalize_this_config': normalize_flag}

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
                normalize_this_config = _current_config_dict['normalize_this_config']
                nbr_ob = len(_current_config_dict['list_ob'])
                nbr_df = len(_current_config_dict['list_df'])
                nbr_sample = len(_current_config_dict['list_sample'])
                self.number_of_normalization += 1 if nbr_ob > 0 else 0
                table += utilities.populate_normalization_recap_row(
                        acquisition=_name_acquisition,
                        config=_name_config,
                        nbr_sample=nbr_sample,
                        nbr_ob=nbr_ob,
                        nbr_df=nbr_df,
                        normalize_this_config=normalize_this_config)

        table += "</table>"
        table_ui = widgets.HTML(table)
        display(table_ui)

    def select_output_folder(self):
        self.output_folder_ui = myfileselector.FileSelectorPanelWithJumpFolders(
                instruction='select where to create the ' + \
                            'normalized folders',
                start_dir=self.working_dir,
                ipts_folder=self.working_dir,
                next=self.normalization,
                type='directory',
                newdir_toolbar_button=True)

    def normalization(self, output_folder):
        display(HTML('<span style="font-size: 20px; color:blue">Make sure you do not close the notebook until'
                     'the busy signal (dark circle top right) is is gone!</span>'))

        self.output_folder_ui.shortcut_buttons.close()  # hack to hide the buttons

        final_json = self.final_json_dict
        number_of_normalization = self.number_of_normalization

        horizontal_layout = widgets.HBox([widgets.Label("Normalization progress",
                                                        layout=widgets.Layout(width='20%')),
                                          widgets.IntProgress(max=number_of_normalization + 1,
                                                              value=0,
                                                              layout=widgets.Layout(width='50%'))])
        normalization_progress = horizontal_layout.children[1]
        display(horizontal_layout)

        list_full_output_normalization_folder_name = []
        for _name_acquisition in final_json.keys():
            _current_acquisition_dict = final_json[_name_acquisition]
            for _name_config in _current_acquisition_dict.keys():
                _current_config = _current_acquisition_dict[_name_config]

                list_ob = _current_config['list_ob']
                if len(list_ob) == 0:
                    normalization_progress.value += 1
                    continue

                if not _current_config['normalize_this_config'].value:
                    normalization_progress.value += 1
                    continue

                list_sample = _current_config['list_sample']
                full_output_normalization_folder_name = \
                    utilities.make_full_output_normalization_folder_name(
                            output_folder=output_folder,
                            first_sample_file_name=list_sample[0],
                            name_acquisition=_name_acquisition,
                            name_config=_name_config)
                list_full_output_normalization_folder_name.append(full_output_normalization_folder_name)
                list_df = _current_config['list_df']

                o_load = Normalization()
                o_load.load(file=list(list_sample), notebook=True)
                o_load.load(file=list(list_ob), data_type='ob')

                if len(list_df) > 0:
                    o_load.load(file=list(list_df), data_type='df')

                o_load.normalization()
                o_load.export(folder=full_output_normalization_folder_name, file_type='tif')
                del o_load

                normalization_progress.value += 1

        horizontal_layout.close()

        display(HTML('<span style="font-size: 20px; color:blue">Following folders have been created:</span>'))
        for _folder in list_full_output_normalization_folder_name:
            _folder = _folder if _folder else "None"
            display(HTML('<span style="font-size: 15px; color:blue"> -> ' + _folder + '</span>'))
