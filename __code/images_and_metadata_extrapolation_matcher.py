import os
import pandas as pd

try:
    import ipywe.fileselector
    from ipywidgets import widgets
except:
    pass
from IPython.display import display
from IPython.core.display import HTML

from __code.utilities import display_html_message
from __code.time_utility import TimestampFormatter

INDEX = '#filename'


class ImagesAndMetadataExtrapolationMatcher:

    merged_dataframe = []

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
        if (INDEX in self.ascii_file_1_dataframe) and \
                (INDEX in self.ascii_file_2_dataframe):
            self.simple_merge()

        else:
            self.merge_with_extrapolation()

    def simple_merge(self):
        self.set_index(self.ascii_file_1_dataframe)
        self.set_index(self.ascii_file_2_dataframe)

        self.merged_dataframe = pd.merge(self.ascii_file_1_dataframe,
                                         self.ascii_file_2_dataframe,
                                         on=INDEX,
                                         how='outer')

    def set_index(self, dataframe, index=INDEX):
        return dataframe.set_index(index)

    def merge_with_extrapolation(self):
        pass

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
        self.merged_dataframe.to_csv(full_output_file_name)
        display_html_message(title_message='File Created with Success!', message_type='ok')