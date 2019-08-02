from IPython.core.display import display, HTML
from ipywidgets import widgets, interact
from collections import OrderedDict
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from __code.file_handler import make_ascii_file
from __code.time_utility import TimestampFormatter


class ShiftTimeOffset:

    instrument = 'CG1D'
    facility = 'HFIR'
    first_file = ''
    list_of_fits_files = []
    timestamp_file = ''
    counts_vs_time_array = []

    def __init__(self):
        pass

    def display_counts_vs_time(self, input_folder):
        self.built_list_of_fits_files(input_folder)
        self.retrieve_name_of_timestamp_file(input_folder)
        if self.timestamp_file:
            self.load_timestamp_file()
            self.plot_timestamp_file()

    def built_list_of_fits_files(self, input_folder):
        list_of_fits_files = list(Path(input_folder).glob('*.fits'))
        list_of_fits_files.sort()
        if list_of_fits_files:
            nbr_fits_files = len(list_of_fits_files)
            display(HTML('<span style="font-size: 15px; color:green">Found ' + str(nbr_fits_files) + ' FITS files to process!</span>'))
            self.list_of_fits_files = list_of_fits_files
        else:
            display(HTML('<span style="font-size: 15px; color:red">No FITS files Found!</span>'))

    def retrieve_name_of_timestamp_file(self, input_folder):
        timestamp_files = list(Path(input_folder).glob('*_Spectra.txt'))
        timestamp_file = timestamp_files[0]
        if Path(timestamp_file).exists():
            display(HTML('<span style="font-size: 15px; color:green">Time stamp file Found (' +str(timestamp_file) + ')</span>'))
            self.timestamp_file = timestamp_file
        else:
            display(HTML('<span style="font-size: 15px; color:red">Time stamp not Found</span>'))

    def load_timestamp_file(self):
        timestamp_file = self.timestamp_file
        counts_vs_time_array = pd.read_csv(timestamp_file, sep='\t')
        self.counts_vs_time_array = np.array(counts_vs_time_array)

    def plot_timestamp_file(self):
        if self.counts_vs_time_array == []:
            return

        x_axis = self.counts_vs_time_array[:,0]
        y_axis = self.counts_vs_time_array[:,1]
        x_index_axis = np.arange(len(y_axis))

        def plot_cutoff(index):

            fig, ax1 = plt.subplots()
            ax1.plot(x_axis, y_axis)
            ax1.set_xlabel(r"Time (micros)")

            x_position = x_axis[index]
            plt.axvline(x_position, color='red')

        interact(plot_cutoff,
                 index=widgets.IntSlider(min=0,
                                         max=x_index_axis[-1],
                                         value=0,
                                         continuous_update=False))

    def step2(self, system=None, input_folder=""):
        if not input_folder:
            display(HTML('<span style="font-size: 20px; color:red">No data folder selected!</span>'))
            return

        if not system:
            display(HTML('<span style="font-size: 20px; color:red">No input folder selected!</span>'))
            return

        self.instrument = system.System.get_instrument_selected()
        self.facility = system.System.get_facility_selected()
        self.input_folder = input_folder






    def retrieve_list_metadata_with_examples(self):
        list_metadata = self.retrieve_list_metadata()
        raw_data = self.raw_oncat_metadata
        list_metadata_with_examples = ListMetadata.format_list_metadata_with_examples(list_metadata, raw_data)
        return list_metadata_with_examples

    @staticmethod
    def format_list_metadata_with_examples(list_metadata, raw_data):
        list_metadata_with_examples = []
        for _key in list_metadata:
            _key_with_value = "{:>40} \t --> \texample: {}".format(_key,
                                                                   raw_data[_key])
            list_metadata_with_examples.append(_key_with_value)
        return list_metadata_with_examples

    def retrieve_list_metadata(self):
        _data = oncat.GetEverything(instrument=self.instrument,
                                    facility=self.facility,
                                    run=self.first_file,
                                    oncat=self.oncat_session)

        self.raw_oncat_data = _data.datafiles
        sorted_dict_metadata = self.create_sorted_dict_metadata(_data)
        return sorted_dict_metadata.keys()

    def create_sorted_dict_metadata(self, _data):
        _data = _data.datafiles['metadata']
        dict_metadata = _data.to_dict()
        keys_sorted = sorted(dict_metadata.keys())
        sorted_dict_metadata = OrderedDict()
        for _key in keys_sorted:
            sorted_dict_metadata[_key] = dict_metadata[_key]
        self.raw_oncat_metadata = sorted_dict_metadata
        return sorted_dict_metadata

    def export_ascii(self, output_folder):
        list_files = self.list_of_files
        projection = self.create_projection()
        output_ascii_file_name = ListMetadata.create_output_ascii_name(list_files, output_folder)

        o_metadata_selected = oncat.GetProjection(instrument=self.instrument,
                                                  facility=self.facility,
                                                  list_files=list_files,
                                                  oncat=self.oncat_session,
                                                  projection=projection,
                                                  with_progressbar=True)
        metadata_selected = o_metadata_selected.datafiles

        name_metadata = self.create_metadata_name_row()
        value_metadata = self.create_metadata_value_rows(list_files, metadata_selected)
        make_ascii_file(metadata=name_metadata,
                        data=value_metadata,
                        output_file_name=output_ascii_file_name,
                        dim='1d')
        print("Done!")
        display(HTML('<span style="font-size: 20px; color:Green">File ' + output_ascii_file_name +
                     ' has been created with success!</span>'))

    def create_metadata_value_rows(self, list_files, metadata_selected):
        value_metadata = []
        for _file in list_files:
            time_stamp = self.unify_timestamp_format(metadata_selected[_file]['ingested'])
            _metadata = []
            for _metadata_name in self.get_list_metadata_selected():
                _metadata.append(str(metadata_selected[_file]['metadata'][_metadata_name]))
            row_string = "{}, {}, {}".format(_file,
                                             time_stamp,
                                             ", ".join(_metadata))
            value_metadata.append(row_string)
        return value_metadata

    def unify_timestamp_format(self, old_timestamp):
        o_time = TimestampFormatter(timestamp=old_timestamp)
        new_timestamp = o_time.format_oncat_timestamp()
        return new_timestamp

    def create_metadata_name_row(self):
        name_metadata = ["#filename, timestamp_user_format, " + ", ".join(self.get_list_metadata_selected())]
        return name_metadata

    @staticmethod
    def create_output_ascii_name(list_files, output_folder):
        output_ascii_file_name = os.path.basename(os.path.dirname(list_files[0]) + '_metadata_report_from_oncat.txt')
        output_folder = os.path.abspath(output_folder)
        return os.path.join(output_folder, output_ascii_file_name)

    def create_projection(self):
        list_metadata_selected = self.get_list_metadata_selected()
        projection = []
        for _metadata_selected in list_metadata_selected:
            projection.append('metadata.{}'.format(_metadata_selected.strip()))
        return projection

    def get_list_metadata_selected(self):
        list_metadata_selected = []
        for metadata_selected in self.select_box.value:
            metadata_name = metadata_selected.split("\t -->")
            list_metadata_selected.append(metadata_name[0].strip())
        return list_metadata_selected



