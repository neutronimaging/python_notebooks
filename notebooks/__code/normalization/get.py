import os
from ipywidgets import widgets
import numpy as np

from __code._utilities.get import Get as TopGet

from __code.normalization import LOG_FILENAME
from __code import file_handler

LIST_METADATA_NOT_INSTRUMENT_RELATED = ['filename', 'time_stamp', 'time_stamp_user_format']


class Get(TopGet):

    def log_file_name(self):
        return TopGet.log_file_name(LOG_FILENAME)

    def active_tabs(self):
        active_acquisition_tab = self.parent.acquisition_tab.selected_index
        config_tab_dict = self.parent.config_tab_dict[active_acquisition_tab]
        active_config_tab = config_tab_dict['config_tab_id'].selected_index
        return [active_acquisition_tab, active_config_tab]

    def active_tab_acquisition_key(self):
        active_acquisition_tab_index = self.parent.acquisition_tab.selected_index
        title = self.parent.acquisition_tab.get_title(active_acquisition_tab_index)
        [_, time_s] = title.split(": ")
        acquisition_key = time_s[:-1]
        return np.float(acquisition_key)

    def active_tab_config_key(self):
        [active_acquisition, _] = self.active_tabs()
        all_config_tab_of_acquisition = self.parent.config_tab_dict[active_acquisition]
        current_config_tab = all_config_tab_of_acquisition['config_tab_id']
        current_config_tab_index = current_config_tab.selected_index
        return current_config_tab.get_title(current_config_tab_index)

    def time_before_and_after_of_this_config(self, current_config=None):
        [time_before_selected_ui, time_after_selected_ui] = \
            self.time_before_and_after_ui_of_this_config(current_config=current_config)
        return [time_before_selected_ui.value, time_after_selected_ui.value]

    def time_before_and_after_ui_of_this_config(self, current_config=None):
        if current_config is None:
            current_config = self.current_config_of_widgets_id()
        return [current_config['time_slider_before_experiment'], current_config['time_slider_after_experiment']]

    def time_before_and_after_message_ui_of_this_config(self):
        current_config = self.current_config_of_widgets_id()
        return current_config['time_slider_before_message']

    def experiment_label_ui_of_this_config(self):
        current_config = self.current_config_of_widgets_id()
        return current_config['experiment_label']

    def current_config_dict(self):
        active_acquisition = self.active_tab_acquisition_key()
        active_config = self.active_tab_config_key()
        final_full_master_dict = self.parent.final_full_master_dict
        current_config = final_full_master_dict[active_acquisition][active_config]
        return current_config

    def current_config_of_widgets_id(self):
        [active_acquisition, active_config] = self.active_tabs()
        all_config_tab_of_acquisition = self.parent.config_tab_dict[active_acquisition]
        current_config_of_widgets_id = all_config_tab_of_acquisition[active_config]
        return current_config_of_widgets_id

    def max_time_elapse_before_experiment(self):
        # this will use the first sample image taken, the first OB image taken and will calculate that
        # difference. If the OB was taken after the first image, time will be 0

        # retrieve acquisition and config values
        acquisition_key = float(self.active_tab_acquisition_key())  # ex: 55.0
        config_key = self.active_tab_config_key()  # ex: 'config0'

        # retrieve list of ob and df for this config for this acquisition
        final_full_master_dict = self.parent.final_full_master_dict
        dict_for_this_config = final_full_master_dict[acquisition_key][config_key]

        # retrieve first and last sample file for this config and for this acquisition
        first_sample_image_time_stamp = dict_for_this_config['first_images']['sample']['time_stamp']
        first_ob = dict_for_this_config['first_images']['ob']['time_stamp']

        if first_ob > first_sample_image_time_stamp:
            return 0
        else:
            return first_sample_image_time_stamp - first_ob

    def max_time_elapse_after_experiment(self):
        # this will use the last sample image taken, the last OB image taken and will calculate that
        # difference. If the last OB was taken before the last image, time will be 0

        # retrieve acquisition and config values
        acquisition_key = float(self.active_tab_acquisition_key())  # ex: 55.0
        config_key = self.active_tab_config_key()  # ex: 'config0'

        # retrieve list of ob and df for this config for this acquisition
        final_full_master_dict = self.parent.final_full_master_dict
        dict_for_this_config = final_full_master_dict[acquisition_key][config_key]

        # retrieve first and last sample file for this config and for this acquisition
        last_sample_images_time_stamp = dict_for_this_config['last_images']['sample']['time_stamp']
        last_ob = dict_for_this_config['last_images']['ob']['time_stamp']

        if last_ob < last_sample_images_time_stamp:
            return 0
        else:
            return last_sample_images_time_stamp - last_ob

    def full_layout_for_this_config(self, dict_config):
        config_widgets_id_dict = {}

        def _make_list_basename_file(list_name='list_sample'):
            return [os.path.basename(_entry['filename']) for _entry in dict_config[list_name]]

        def _make_full_file_name(list_name='list_sample'):
            return [_entry['filename'] for _entry in dict_config[list_name]]

        # list_sample = _make_list_basename_file(list_name='list_sample')
        # list_ob = _make_list_basename_file(list_name='list_ob')
        # list_df = _make_list_basename_file(list_name='list_df')

        list_sample = _make_full_file_name(list_name='list_sample')
        list_ob = _make_full_file_name(list_name='list_ob')
        list_df = _make_full_file_name(list_name='list_df')

        # normalize or not this configuration
        use_this_config_widget = widgets.Checkbox(description="Normalize this configuration",
                                                  value=True,
                                                  layout=widgets.Layout(width="100%"))
        use_this_config_widget.observe(self.parent.update_use_this_config_widget, names='value')
        config_widgets_id_dict['use_this_config'] = use_this_config_widget

        # use custom time range check box
        check_box_user_time_range = widgets.Checkbox(description="Use selected OB & DF from custom time range",
                                                     value=False,
                                                     layout=widgets.Layout(width="35%"))
        config_widgets_id_dict['use_custom_time_range_checkbox'] = check_box_user_time_range
        check_box_user_time_range.observe(self.parent.update_config_widgets, names='value')

        [max_time_elapse_before_experiment,
         max_time_elapse_after_experiment] = self.parent.calculate_max_time_before_and_after_exp_for_this_config(
                dict_config)

        hori_layout1 = widgets.HBox([check_box_user_time_range,
                                     widgets.FloatSlider(value=-max_time_elapse_before_experiment - 0.1,
                                                         min=-max_time_elapse_before_experiment - 0.1,
                                                         max=0,
                                                         step=0.1,
                                                         readout=False,
                                                         layout=widgets.Layout(width="30%",
                                                                               visibility='hidden')),
                                     widgets.Label(" <<< EXPERIMENT >>> ",
                                                   layout=widgets.Layout(width="20%",
                                                                         visibility='hidden')),
                                     widgets.FloatSlider(value=max_time_elapse_before_experiment + 0.1,
                                                         min=0,
                                                         max=max_time_elapse_after_experiment + 0.1,
                                                         step=0.1,
                                                         readout=False,
                                                         layout=widgets.Layout(width="30%",
                                                                               visibility='hidden')),
                                     ])
        self.parent.hori_layout1 = hori_layout1
        self.parent.time_before_slider = hori_layout1.children[1]
        self.parent.time_after_slider = hori_layout1.children[3]
        self.parent.experiment_label = hori_layout1.children[2]
        self.parent.time_after_slider.observe(self.parent.update_time_range_event, names='value')
        self.parent.time_before_slider.observe(self.parent.update_time_range_event, names='value')
        config_widgets_id_dict['time_slider_before_experiment'] = hori_layout1.children[1]
        config_widgets_id_dict['time_slider_after_experiment'] = hori_layout1.children[3]
        config_widgets_id_dict['experiment_label'] = hori_layout1.children[2]

        # use all OB and DF
        hori_layout2 = widgets.HBox([widgets.Label("    ",
                                                   layout=widgets.Layout(width="20%")),
                                     widgets.HTML("",
                                                  layout=widgets.Layout(width="80%"))])
        self.parent.hori_layout2 = hori_layout2
        self.parent.time_before_and_after_message = hori_layout2.children[1]
        config_widgets_id_dict['time_slider_before_message'] = hori_layout2.children[1]

        #how to combine the OBs



        # table of metadata
        [metadata_table_label, metadata_table] = self.parent.populate_metadata_table(dict_config)

        select_width = '100%'
        sample_list_of_runs = widgets.VBox([widgets.Label(" List of Sample Runs (ALL WILL BE USED!)",
                                                          layout=widgets.Layout(width='100%')),
                                            widgets.Select(options=list_sample,
                                                           layout=widgets.Layout(width=select_width,
                                                                                 height='300px'))],
                                           layout=widgets.Layout(width="100%"))
        # self.list_of_runs_ui = box0.children[1]
        ob_list_of_runs = widgets.VBox([widgets.Label(" List of OB (ONLY SELECTED ONE ARE USED!)",
                                                      layout=widgets.Layout(width='100%')),
                                        widgets.SelectMultiple(options=list_ob,
                                                               value=list_ob,
                                                               layout=widgets.Layout(width=select_width,
                                                                             height='300px'))],
                                       layout=widgets.Layout(width="100%"))
        df_list_of_runs = widgets.VBox([widgets.Label(" List of DF (ONLY SELECTED ONE ARE USED!)",
                                                      layout=widgets.Layout(width='100%')),
                                        widgets.SelectMultiple(options=list_df,
                                                               value=list_df,
                                                               layout=widgets.Layout(width=select_width,
                                                                             height='300px'))],
                                       layout=widgets.Layout(width="100%"))

        list_runs_layout = widgets.VBox([sample_list_of_runs,
                                         ob_list_of_runs,
                                         df_list_of_runs])
        config_widgets_id_dict['list_of_sample_runs'] = sample_list_of_runs.children[1]
        config_widgets_id_dict['list_of_ob'] = ob_list_of_runs.children[1]
        config_widgets_id_dict['list_of_df'] = df_list_of_runs.children[1]

        verti_layout = widgets.VBox([use_this_config_widget,
                                     hori_layout1,
                                     hori_layout2,
                                     metadata_table_label,
                                     metadata_table,
                                     list_runs_layout])

        return {'verti_layout': verti_layout, 'config_widgets_id_dict': config_widgets_id_dict}

    @staticmethod
    def list_of_tiff_files(folder=""):
        list_of_tiff_files = file_handler.get_list_of_files(folder=folder,
                                                            extension='tiff')
        return list_of_tiff_files

    @staticmethod
    def get_instrument_metadata_only(metadata_dict):
        _clean_dict = {}
        for _key in metadata_dict.keys():
            if not _key in LIST_METADATA_NOT_INSTRUMENT_RELATED:
                _clean_dict[_key] = metadata_dict[_key]
        return _clean_dict
