import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

try:
    import ipywe.fileselector
    from ipywidgets import widgets
except:
    pass
from IPython.display import display
from IPython.core.display import HTML

from plotly.offline import plot, init_notebook_mode, iplot
init_notebook_mode()
import plotly.plotly as py
import plotly.graph_objs as go

from __code.utilities import display_html_message
from __code.time_utility import TimestampFormatter

INDEX_SIMPLE_MERGE = '#filename'
INDEX_EXTRAPOLATION_MERGE = 'timestamp_user_format'
TIMESTAMP_FORMAT = "%Y-%m-%d %I:%M:%S"

class ImagesAndMetadataExtrapolationMatcher:

    merged_dataframe = []
    extrapolated_dataframe_only = {}
    extrapolated_timestamp_only = {}
    figure = None

    def __init__(self, ascii_file_1='', ascii_file_2=''):
        self.ascii_file_1 = ascii_file_1
        self.ascii_file_2 = ascii_file_2

        self.load_ascii_files()
        self.unify_timestamp_columns()
        self.merge_data()

    def get_merged_dataframe(self):
        return self.merged_dataframe

    def load_ascii_files(self):
        self.ascii_file_1_dataframe = self.retrieve_dataframe(filename=self.ascii_file_1)
        self.ascii_file_2_dataframe = self.retrieve_dataframe(filename=self.ascii_file_2)

    def retrieve_dataframe(self, filename=''):
        _dataframe = pd.read_csv(filename)
        _dataframe = self.remove_white_space_in_column_names(_dataframe)
        return _dataframe

    def remove_white_space_in_column_names(self, dataframe):
        clean_column_names = [_old_col_name.strip() for _old_col_name in list(dataframe.columns.values)]
        dataframe.columns = clean_column_names
        return dataframe

    def unify_timestamp_columns(self):
        self.ascii_file_1_dataframe = self.format_timestamp(self.ascii_file_1_dataframe)
        self.ascii_file_2_dataframe = self.format_timestamp(self.ascii_file_2_dataframe)

    def format_timestamp(self, dataframe):
        timestamp_user_format = list(dataframe['timestamp_user_format'])
        o_time = TimestampFormatter(timestamp=timestamp_user_format)
        new_timestamp_user_format = o_time.format()
        dataframe['timestamp_user_format'] = new_timestamp_user_format
        return dataframe

    def merge_data(self):
        if (INDEX_SIMPLE_MERGE in self.ascii_file_1_dataframe) and \
                (INDEX_SIMPLE_MERGE in self.ascii_file_2_dataframe):
            self.simple_merge()

        else:
            self.merge_with_extrapolation()

    def simple_merge(self):
        self.set_index(self.ascii_file_1_dataframe)
        self.set_index(self.ascii_file_2_dataframe)

        self.merged_dataframe = pd.merge(self.ascii_file_1_dataframe,
                                         self.ascii_file_2_dataframe,
                                         on=INDEX_SIMPLE_MERGE,
                                         how='outer')

    def set_index(self, dataframe, index=INDEX_SIMPLE_MERGE):
        return dataframe.set_index(index)

    def merge_with_extrapolation(self):
        self.set_index(self.ascii_file_1_dataframe, index=INDEX_EXTRAPOLATION_MERGE)
        self.set_index(self.ascii_file_2_dataframe, index=INDEX_EXTRAPOLATION_MERGE)

        merged_dataframe = pd.merge(self.ascii_file_1_dataframe,
                                    self.ascii_file_2_dataframe,
                                    on=INDEX_EXTRAPOLATION_MERGE,
                                    how='outer')
        merged_dataframe.sort_values(by=INDEX_EXTRAPOLATION_MERGE,
                                     inplace=True)
        self.merged_dataframe = merged_dataframe.reset_index(drop=True)

        self.select_metadata_to_extrapolate()

    def select_metadata_to_extrapolate(self):
        list_metadata = self.get_column_names(self.merged_dataframe)
        display(HTML('<span style="font-size: 15px; color:blue">CTRL + Click to select multiple rows!</span>'))
        box = widgets.HBox([widgets.Label("Select Metadata to Extrapolate:",
                                         layout=widgets.Layout(width='30%')),
                           widgets.SelectMultiple(options=list_metadata,
                                                  layout=widgets.Layout(width='70%',
                                                                        height='70%'))
                           ],
                           layout=widgets.Layout(height='250px'))
        self.metadata_to_extrapolate_widget = box.children[1]
        display(box)

    def extrapolate_selected_metadata(self):
        self.list_metadata_to_extrapolate = self.metadata_to_extrapolate_widget.value
        for _metadata_to_extrapolate in self.list_metadata_to_extrapolate:
            self.extrapolate_metadata(metadata_name=_metadata_to_extrapolate)

        self.display_extrapolation()

    def extrapolate_metadata(self, metadata_name=''):
        metadata_array = self.merged_dataframe[metadata_name]
        timestamp_array = self.merged_dataframe['timestamp_user_format']

        new_metadata_array = []
        extrapolated_metadata_array = []
        extrapolated_timestamp_array = []
        for _index in np.arange(len(metadata_array)):
            _metadata_value = metadata_array[_index]
            if np.isnan(_metadata_value):
                _new_value = Extrapolate.calculate_extrapolated_metadata(global_index=_index,
                                                                         metadata_array=metadata_array,
                                                                         timestamp_array=timestamp_array)
                extrapolated_metadata_array.append(_new_value)
                extrapolated_timestamp_array.append(timestamp_array[_index])
            else:
                _new_value = _metadata_value

            new_metadata_array.append(_new_value)

        self.merged_dataframe[metadata_name] = new_metadata_array
        self.extrapolated_dataframe_only[metadata_name] = extrapolated_metadata_array
        self.extrapolated_timestamp_only[metadata_name] = extrapolated_timestamp_array

    def metadata_to_display_init(self):
        self.list_metadata_to_extrapolate = self.metadata_to_extrapolate_widget.value
        for value in self.list_metadata_to_extrapolate:
            self.metadata_to_display_changed(value)

    def metadata_to_display_changed(self, name_of_metadata_to_display):
        self.extract_known_and_unknown_axis_infos(metadata_name=name_of_metadata_to_display)

        data_known = go.Scatter(x=self.timestamp_s_metadata_known,
                                y=self.metadata_column,
                                mode='markers',
                                name="Original metadata")

        data_extrapolated = go.Scatter(x=self.timestamp_s_metadata_unknown,
                                       y=self.extrapolated_dataframe_only[name_of_metadata_to_display],
                                       mode='markers',
                                       name='Extrapolated')

        layout = go.Layout(width=800,
                           height=500,
                           showlegend=True,
                           title="Extrapolated metadata: {}".format(name_of_metadata_to_display),
                           xaxis=dict(title="Time (s)"),
                           yaxis=dict(title=name_of_metadata_to_display),
                           )

        data = [data_known, data_extrapolated]
        figure = go.Figure(data=data, layout=layout)
        iplot(figure)

    def extract_known_and_unknown_axis_infos(self, metadata_name=''):
        # known metadata values
        timestamp_metadata_known = self.ascii_file_2_dataframe['timestamp_user_format']
        self.timestamp_s_metadata_known = [TimestampFormatter.convert_to_second(_time,
                                                                                timestamp_format=TIMESTAMP_FORMAT)
                                           for _time in timestamp_metadata_known]
        self.metadata_column = self.ascii_file_2_dataframe[metadata_name]

        # unknown metadata values
        # list_index = list(np.where(np.isnan(self.merged_dataframe[metadata_name])))
        #timestamp_metadata_unknown = np.array(self.merged_dataframe['timestamp_user_format'])[list_index]
        # self.timestamp_s_metadata_unknown = [TimestampFormatter.convert_to_second(_time,
        #                                                                           timestamp_format=TIMESTAMP_FORMAT)
        #                                      for _time in timestamp_metadata_unknown]
        timestamp_metadata_unknown = self.extrapolated_timestamp_only[metadata_name]
        self.timestamp_s_metadata_unknown = [TimestampFormatter.convert_to_second(_time,
                                                                                  timestamp_format=TIMESTAMP_FORMAT)
                                             for _time in timestamp_metadata_unknown]

    def display_extrapolation(self):
        self.metadata_to_display_init()

    def get_column_names(self, dataframe):
        """removing INDEX_EXTRAPOLATION_MERGE from list"""
        list_columns = dataframe.columns
        clean_list_columns = [_name for _name in list_columns if
                               not self._is_name_in_list(name=_name,
                                                         list_name=[INDEX_EXTRAPOLATION_MERGE,
                                                         INDEX_SIMPLE_MERGE])]
        return clean_list_columns

    def _is_name_in_list(self, name='', list_name=[]):
        if name in list_name:
            return True
        return False

    def get_output_file_name(self):
        base_part1 = self.get_base_name(self.ascii_file_1)
        base_part2 = self.get_base_name(self.ascii_file_2)
        return "{}_combined_with_{}.txt".format(base_part1, base_part2)

    def get_base_name(self, part1):
        [base_name, _] = os.path.splitext(os.path.basename(part1))
        return base_name

    def make_and_inform_of_full_output_file_name(self, folder_name):
        folder_name = os.path.abspath(folder_name)
        display_html_message(title_message='Output folder name:', message=folder_name)

        output_file_name = self.get_output_file_name()
        display_html_message(title_message='Output file name:', message=output_file_name)

        return os.path.join(folder_name, output_file_name)

    def export_ascii(self, folder_name):
        full_output_file_name = self.make_and_inform_of_full_output_file_name(folder_name)
        self.cleanup_merged_dataframe()
        self.merged_dataframe.to_csv(full_output_file_name)
        display_html_message(title_message='File Created with Success!', message_type='ok')

    def cleanup_merged_dataframe(self):
        # keeping only the raws with filename information defined
        self.merged_dataframe = self.merged_dataframe.dropna(subset=['#filename'])

class Extrapolate:

    @staticmethod
    def get_first_metadata_and_index_value(index=-1, metadata_array=[], direction='left'):
        if direction == 'left':
            coeff = -1
        else:
            coeff = +1

        while np.isnan(metadata_array[index]):
            index += coeff

            # if last file timestamp is > last metadata recorded, raise error
            if index >= len(metadata_array):
                raise ValueError("Not enough metadata to extrapolate value!")

        return [metadata_array[index], index]

    @staticmethod
    def calculate_extrapolated_metadata(global_index=-1, metadata_array=[], timestamp_array=[]):
        [left_metadata_value, left_index] = Extrapolate.get_first_metadata_and_index_value(index=global_index,
                                                                                           metadata_array=metadata_array,
                                                                                           direction='left')
        [right_metadata_value, right_index] = Extrapolate.get_first_metadata_and_index_value(index=global_index,
                                                                                             metadata_array=metadata_array,
                                                                                             direction='right')

        left_timestamp_s_format = TimestampFormatter.convert_to_second(timestamp_array[left_index])
        right_timestamp_s_format = TimestampFormatter.convert_to_second(timestamp_array[right_index])

        x_timestamp_s_format = TimestampFormatter.convert_to_second(timestamp_array[global_index])

        extra_value = Extrapolate.extrapolate_value(x=x_timestamp_s_format,
                                                    x_left=left_timestamp_s_format,
                                                    x_right=right_timestamp_s_format,
                                                    y_left=left_metadata_value,
                                                    y_right=right_metadata_value)
        return extra_value

    @staticmethod
    def extrapolate_value(x=1, x_left=1, x_right=1, y_left=1, y_right=1):
        coeff = (float(y_right) - float(y_left)) / (float(x_right) - float(x_left))
        part1 = coeff * (float(x) - float(x_left))
        return part1 + float(y_left)
