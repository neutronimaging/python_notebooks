import codecs
import time, datetime
import inflect

# to be able to run this code from the command line for testing
try:
    import ipywe.fileselector
    from ipywidgets import widgets
except:
    pass
from IPython.display import display
from IPython.core.display import HTML

import numpy as np
import os
import pandas as pd

from __code.file_handler import get_file_extension
from __code.file_handler import make_ascii_file_from_string
from __code.file_handler import force_file_extension


class MetadataAsciiParser(object):

    metadata_file = ''

    def __init__(self, working_dir='./'):
        self.working_dir = working_dir

    def select_folder(self, instruction="Select Input Folder ...", next=None):

        self.input_folder_ui = ipywe.fileselector.FileSelectorPanel(instruction=instruction,
                                                                    start_dir=self.working_dir,
                                                                    type='directory',
                                                                    next=next)
        self.input_folder_ui.show()

    def save_metadata_file(self, filename):
        self.metadata_file = filename

    def select_metadata_file(self):
        _instruction = "Select Metadata File ..."
        self.metadata_ui = ipywe.fileselector.FileSelectorPanel(instruction=_instruction,
                                                                start_dir=self.working_dir,
                                                                next=self.save_metadata_file)
        self.metadata_ui.show()


class Metadata():
    nbr_row_metadata = -1

    def __init__(self,
                 filename='',
                 reference_line_showing_end_of_metadata='Number of loops',
                 end_of_metadata_after_how_many_lines_from_reference_line=1):
        self.filename = filename
        self.reference_line_showing_end_of_metadata = reference_line_showing_end_of_metadata
        self.end_of_metadata_after_how_many_lines_from_reference_line = end_of_metadata_after_how_many_lines_from_reference_line

    def calculate_nbr_row_metadata(self):
        file_handler = codecs.open(
            self.filename, 'r', encoding='utf_8', errors='ignore')

        for _row_index, _row in enumerate(file_handler.readlines()):
            if self.reference_line_showing_end_of_metadata in _row:
                self.nbr_row_metadata = _row_index + self.end_of_metadata_after_how_many_lines_from_reference_line + 1


class TimeInfoColumn:
    """this will allow to figure out where the time info is in the big table"""

    index = -1
    label = ''

    def __init__(self, index=-1, label=''):
        self.index = index
        self.label = label


class MPTFileParser(object):
    nbr_row_metadata = -1

    metadata_dict = {
        'Acquisition started on': {
            "split1": ' : ',
            "split2": '',
            "value": '',
        },
        'Electrode surface area': {
            "split1": ' : ',
            "split2": ' ',
            "value": '',
            "units": '',
        },
    }

    #     time_info_index_column = 2  # in this file, the time information is in the column #2
    time_info_column = None  # TimeInfoColumn object
    time_column = []

    def __init__(self,
                 filename='',
                 time_info_column=None,
                 reference_line_showing_end_of_metadata='Number of loops',
                 end_of_metadata_after_how_many_lines_from_reference_line=1,
                 ):
        self.filename = filename
        self.reference_line_showing_end_of_metadata = reference_line_showing_end_of_metadata
        self.end_of_metadata_after_how_many_lines_from_reference_line = end_of_metadata_after_how_many_lines_from_reference_line
        self.time_info_column = time_info_column

        self.evaluate_nbr_row_metadata()
        self.parse()
        self.set_time_info_as_index()
        self.add_acquisition_started_time_to_timestamp()

        # self.save_time_column()
        # self.remove_time_info_column()

    def add_acquisition_started_time_to_timestamp(self):
        str_acquisition_time = self.metadata_dict['Acquisition started on']['value']
        timestamp = time.mktime(datetime.datetime.strptime(str_acquisition_time, "%m/%d/%Y %H:%M:%S").timetuple())
        new_column_values = self.o_pd.index.values + timestamp
        self.o_pd = self.o_pd.set_index(new_column_values)

        #user friendly time stamp format
        user_format = [datetime.datetime.fromtimestamp(_time).strftime('%m/%d/%Y %H:%M:%S')
                       for _time in self.o_pd.index.values]
        self.o_pd['time_user_format'] = pd.Series(user_format, index=self.o_pd.index)

    def set_time_info_as_index(self):
        time_info_column = self.time_info_column
        if time_info_column.index != -1:
            column_title = self.o_pd.columns.values[time_info_column.index]
        elif time_info_column.label:
            column_title = time_info_column.label
            self.o_pd.set_index(column_title)
        else:
            return
        self.o_pd = self.o_pd.set_index(column_title)

    #     def save_time_column(self):
    #         time_info_column = self.time_info_column
    #         if time_info_column.index != -1:
    #             self.time_column = self.o_pd.iloc[:,time_info_column.index]
    #             column_title = self.o_pd.columns.values[time_info_column.index]
    #         elif time_info_column.label:
    #             column_title = time_info_column.label
    #             self.o_pd.set_index(column_title)
    #         else:
    #             self.time_colmn = []
    #             return
    #         self.time_column = self.o_pd[column_title]

    #     def remove_time_info_column(self):
    #         time_info_column = self.time_info_column
    #         list_columns = list(self.o_pd.columns.values)
    #         if time_info_column.index != -1:
    #             list_columns.pop(time_info_column.index)
    #         elif time_info_column.label != '':
    #             for _col_index, _col in enumerate(list_columns):
    #                 if time_info_column.label in _col:
    #                     list_columns.pop(_col_index)

    #         self.list_columns = list_columns

    def evaluate_nbr_row_metadata(self):
        o_metadata = Metadata(filename=self.filename,
                              reference_line_showing_end_of_metadata=self.reference_line_showing_end_of_metadata,
                              end_of_metadata_after_how_many_lines_from_reference_line=self.end_of_metadata_after_how_many_lines_from_reference_line)
        o_metadata.calculate_nbr_row_metadata()
        self.nbr_row_metadata = o_metadata.nbr_row_metadata

    def parse(self):
        self.read_data()
        self.read_metadata()
        self.read_specific_metadata()

    def get_metadata(self):
        return self.metadata

    def get_data(self):
        return self.o_pd

    def keep_only_columns_of_data_of_interest(self, list_columns_names=[]):
        column_of_data_to_keep = self.o_pd[list_columns_names]
        return column_of_data_to_keep

    def read_data(self):
        o_pd = pd.read_csv(
            self.filename,
            sep='\t',
            encoding='iso8859_5',
            error_bad_lines=False,
            skiprows=self.nbr_row_metadata,
        )
        self.o_pd = o_pd

    def read_metadata(self):
        fdata = codecs.open(self.filename, 'r', encoding='utf-8', errors='ignore')

        metadata = []
        for _row in np.arange(self.nbr_row_metadata):
            metadata.append(fdata.readline())
        self.metadata = metadata

        self.read_specific_metadata()

    def read_specific_metadata(self):
        for _keys in self.metadata_dict.keys():
            for _line in self.metadata:
                if _keys in _line:
                    result = _line.split(
                        self.metadata_dict[_keys]['split1'])  # 1st split
                    if not self.metadata_dict[_keys]['split2']:
                        self.metadata_dict[_keys]['value'] = result[1].strip()
                    else:  # 2nd split
                        [value, units] = result[1].strip().split(
                            self.metadata_dict[_keys]['split2'])
                        self.metadata_dict[_keys]['value'] = value.strip()
                        self.metadata_dict[_keys]['units'] = units.strip()


class MetadataFileParser(object):
    """This class will parse the entire file and isolate the metadata and data.
    Then the time/s column will be used as index, the list of the columns left will be returned in
    order for the user to select the columns he wants to keep. Once those selected, a new pandas object
    of only the columns of interst and time/s as index will be created"""

    filename = ''
    meta_type = ''

    data_to_keep = []
    data = []
    metadata = []

    def __init__(self,
                 filename='',
                 meta_type='',
                 time_label='time/s',
                 time_index=-1,
                 reference_line_showing_end_of_metadata='Number of loops',
                 end_of_metadata_after_how_many_lines_from_reference_line=1,
                 ):
        """
        Arguments:
         * filename: ascii input file name to parse
         * meta_type: right now, only support file with extension mpt
         * time_label: name of columns to use that contains time information
         * time_index: column index to use to retrieve time info (take priority over time_label)
         * reference_line_showing_end_of_metadata: string to use to locate end of metadata file (for complex ascii)
         * end_of_metadata_after_how_many_lines_from_reference_line: number of rows to keep considering as part of metadata from reference_line...
        """
        self.filename = filename
        self.working_dir = os.path.dirname(filename)
        self.short_filename = os.path.basename(filename)
        self.time_label = time_label
        self.time_index = time_index
        if meta_type:
            self.meta_type = meta_type
        else:
            self.meta_type = get_file_extension(filename)

    def get_list_columns(self):
        return list(self.meta.o_pd.columns.values)

    def parse(self):
        if self.meta_type == 'mpt':
            time_info_column = TimeInfoColumn(label=self.time_label, index=self.time_index)
            o_mpt = MPTFileParser(filename=self.filename, time_info_column=time_info_column)
            self.meta = o_mpt
        else:
            raise NotImplementedError("This file format is not supported!")

    def keep_only_columns_of_data_of_interest(self, list_columns_names=[]):
        if list_columns_names == []:
            list_columns_names = list(self.box.children[1].value)

        if list_columns_names:
            self.data_to_keep =  self.meta.keep_only_columns_of_data_of_interest(list_columns_names=list_columns_names)
        else:
            self.data_to_keep = []

    def add_time_offset(self, time_offset_s=0):
        o_pd = self.meta.o_pd
        new_column_values = o_pd.index.values + time_offset_s
        self.meta.o_pd = o_pd.set_index(new_column_values)

    def get_metadata(self):
        return self.meta.get_metadata()

    def get_data(self):
        return self.meta.get_data()

    def get_data_column_names(self):
        return list(self.meta.o_pd.columns.values)

    def select_data_to_keep(self, default_selection=[-1]):

        # names of the columns in the data part
        list_columns = self.get_data_column_names()

        # what to select by default when showing the widget
        default_value = [list_columns[_index] for _index in default_selection]

        self.box = widgets.HBox([widgets.Label("Select Metadata(s) to Keep:",
                                          layout=widgets.Layout(width='30%'),
                                          ),
                            widgets.SelectMultiple(options=list_columns,
                                                   value=default_value,
                                                   rows=10,
                                                   layout=widgets.Layout(width='30%')),
                            ])
        display(self.box)

    def select_output_location(self, default_filename=''):

        if default_filename == '':
            [filename, ext] = os.path.splitext(self.short_filename)
            [_, nbr_columns] = np.shape(self.data_to_keep)
            p = inflect.engine()
            default_filename = filename + '_{}'.format(nbr_columns) + p.plural("column", nbr_columns)

        self.box2 = widgets.HBox([widgets.Label("Output File Name:",
                                           layout=widgets.Layout(width='20%')),
                             widgets.Text(default_filename,
                                          layout=widgets.Layout(width='70%')),
                             widgets.Label(".txt",
                                           layout=widgets.Layout(width='10%'))])
        display(self.box2)

        o_folder = MetadataAsciiParser(working_dir  = self.working_dir)
        o_folder.select_folder(instruction = 'Select Output Folder:',
                               next=self.__export_table)

    def __export_table(self, folder):

        display(HTML('<span style="font-size: 20px; color:blue">You selected the metadata file: ' +
                     self.filename + '!</span>'))

        display(HTML('<span style="font-size: 20px; color:black">Work in progress! ... </span>'))

        output_filename = self.box2.children[1].value
        output_filename = force_file_extension(output_filename, '.txt')

        self.box2.close()

        # record metadata selected
        metadata_name_selected = np.array(self.box.children[1].value)
        data = self.get_data()
        self.data_to_export = data[metadata_name_selected]

        self.export_table(data=self.data_to_export, folder=folder, filename=output_filename)

    def export_table(self, data=None, folder='', filename=''):
        full_output_filename = os.path.join(os.path.abspath(folder), filename)

        # reformat data
        pandas_data = pd.DataFrame(data)
        pandas_data = pandas_data.reset_index()
        pandas_data = pandas_data.rename(index=str, columns={"index": "TimeStamp"})

        self.data_to_export = pandas_data

        csv_format = pandas_data.to_csv()
        make_ascii_file_from_string(text=csv_format, filename=full_output_filename)

        display(HTML('<span style="font-size: 20px; color:black">Done!</span>'))

        display(HTML('<span style="font-size: 20px; color:green">Output file created: ' +
                     full_output_filename + '!</span>'))


if __name__ == "__main__":

    import glob
    import platform

    if platform.node() == 'mac95470':
        git_dir = os.path.abspath('~/git/')
    else:
        git_dir = '/Volumes/my_book_thunderbolt_duo/git/'

    # testing mpt files
    metadata_list_files = glob.glob(git_dir + '/standards/ASCII/*.mpt')

    for _index_file, _file in enumerate(metadata_list_files):
        metadata_file = _file
        if os.path.exists(metadata_file):
            print("working with file: {}".format(metadata_file))
        else:
            print("Failed to work with file: {}".format(metadata_file))

        print("Running MetadataFileParser ...", end='\r')
        o_meta = MetadataFileParser(filename=metadata_file,
                                    meta_type='mpt',
                                    time_label='time/s',
                                    reference_line_showing_end_of_metadata='Number of loops',
                                    end_of_metadata_after_how_many_lines_from_reference_line=1)
        o_meta.parse()
        print("MetadataFileParser ... Done!            ")

        print("Adding arbitrary time offset of 2000s!")
        o_meta.add_time_offset(time_offset_s=2000)
        o_meta.meta.o_pd

        print("Done working with file: {}".format(metadata_file))
        print("")