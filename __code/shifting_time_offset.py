from IPython.core.display import display, HTML
from ipywidgets import widgets, interact
from collections import OrderedDict
from pathlib import Path
import pandas as pd
import numpy as np
import re
import os
from shutil import copyfile
import matplotlib.pyplot as plt

from __code.file_handler import make_ascii_file
from __code.file_handler import make_or_reset_folder
from __code.time_utility import TimestampFormatter


class ShiftTimeOffset:

    instrument = 'CG1D'
    facility = 'HFIR'
    first_file = ''
    list_of_fits_files = []
    timestamp_file = ''
    counts_vs_time_array = []
    list_of_other_folders = []

    def __init__(self):
        pass

    def display_counts_vs_time(self, input_folder):
        self.input_folder = input_folder
        self.built_list_of_fits_files(input_folder)
        self.retrieve_name_of_timestamp_file(input_folder)
        self.retrieve_parent_folder(input_folder)
        if self.timestamp_file:
            self.counts_vs_time_array = self.load_timestamp_file(self.timestamp_file)
            self.plot_timestamp_file()

    def get_list_of_fits_files(self, input_folder):
        list_of_fits_files = list(Path(input_folder).glob('*.fits'))
        list_of_fits_files.sort()
        return list_of_fits_files

    def built_list_of_fits_files(self, input_folder):
        list_of_fits_files = self.get_list_of_fits_files(input_folder)
        if list_of_fits_files:
            nbr_fits_files = len(list_of_fits_files)
            display(HTML('<span style="font-size: 15px; color:green">Found ' + str(nbr_fits_files) + ' FITS files to process!</span>'))
            self.list_of_fits_files = list_of_fits_files
        else:
            display(HTML('<span style="font-size: 15px; color:red">No FITS files Found!</span>'))

    def retrieve_parent_folder(self, folder):
        self.working_dir = Path(folder).parent

    def selected_other_folders(self, list_of_other_folders):
        self.list_of_other_folders = list_of_other_folders

        display(HTML(
            '<span style="font-size: 15px; color:green">The Time correction will also be applied to the following folders:</span>'))
        for _folder in list_of_other_folders:
            display(HTML(
                '<span style="font-size: 15px; color:green"> - ' + _folder + ' FITS files to process!</span>'))

    def retrieve_name_of_timestamp_file(self, input_folder):
        timestamp_files = list(Path(input_folder).glob('*_Spectra.txt'))
        timestamp_file = timestamp_files[0]
        if Path(timestamp_file).exists():
            display(HTML('<span style="font-size: 15px; color:green">Time stamp file Found (' +str(timestamp_file) + ')</span>'))
            self.timestamp_file = timestamp_file
        else:
            display(HTML('<span style="font-size: 15px; color:red">Time stamp not Found</span>'))

    def load_timestamp_file(self, timestamp_file):
        counts_vs_time_array = pd.read_csv(timestamp_file, sep='\t')
        return np.array(counts_vs_time_array)

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

            return index

        self.index_slider = interact(plot_cutoff,
                                     index=widgets.IntSlider(min=0,
                                                             max=x_index_axis[-1],
                                                             value=0,
                                                             continuous_update=False))

    def get_file_prefix(self, file_name):
        short_file_name = str(Path(file_name).name)
        m = re.match(r"(?P<prefix>.*)_\d*.fits", short_file_name)

        if m:
            return m.group("prefix")
        else:
            return ""

    def offset_images(self):
        list_of_folders = [self.input_folder]
        for _folder in self.list_of_other_folders:
            list_of_folders.append(_folder)

        list_of_folders = set(list_of_folders)

        nbr_folder = len(list_of_folders)

        progress_bar = widgets.IntProgress(max=nbr_folder,
                            layout=widgets.Layout(width='50%'))
        display(progress_bar)

        offset_index = self.index_slider.widget.result

        list_folder_with_error = []

        for _index, _current_working_folder in enumerate(list_of_folders):

            # get full list of FITS files
            list_of_fits_files = np.array(self.get_list_of_fits_files(_current_working_folder))
            if list_of_fits_files == []:
                continue

            # find out prefix of file name  -> prefix_#####.fits
            prefix = self.get_file_prefix(list_of_fits_files[0])

            # locate timestamp file
            self.retrieve_name_of_timestamp_file(_current_working_folder)
            timestamp_file = self.timestamp_file
            if not Path(timestamp_file).exists():
                list_folder_with_error.append("Error in {}. Timestamp file missing!".format(_current_working_folder))
                continue

            # rename all files starting by file at index offset_index which will become index 0
            new_list_of_fits_files = np.roll(list_of_fits_files, -offset_index)

            current_working_dir = str(Path(new_list_of_fits_files[0]).parent)
            new_output_dir = current_working_dir + "_timeoffset_corrected"

            self.copy_and_renamed_fits_files(output_dir=new_output_dir,
                                             original_list_of_files=new_list_of_fits_files,
                                             prefix=prefix)

            # modify timestamp file
            new_timestamp_filename = self.create_new_timestamp_filename(output_dir=new_output_dir,
                                                                        old_timestamp_filename=timestamp_file)
            self.create_new_timestamp_file(timestamp_file=timestamp_file,
                                           offset=offset_index,
                                           new_timestamp_filename=new_timestamp_filename)






            progress_bar.value = _index + 1

        progress_bar.close

        self.display_errors(list_folder_with_error=list_folder_with_error)


    def create_new_timestamp_filename(self, output_dir='./', old_timestamp_filename=''):
        short_old_timestamp_filename = str(Path(old_timestamp_filename).name)
        return str(Path(output_dir).joinpath(short_old_timestamp_filename))

    def create_new_timestamp_file(self, timestamp_file='', offset=0, new_timestamp_filename=''):
        timestamp_array = self.load_timestamp_file(timestamp_file)
        time_axis = timestamp_array[:,0]
        new_counts_axis = np.roll(np.array(timestamp_array[:,1]), -offset)

        delta_time = time_axis[1] - time_axis[0]

        new_time_axis = np.arange(len(new_counts_axis)) * delta_time

        # bring back axis together
        combined_array = np.stack((new_time_axis, new_counts_axis)).T
        # print("new timesamp_filename is {}".format(new_timestamp_filename))
        make_ascii_file(data=combined_array, output_file_name=new_timestamp_filename,sep='\t')

    def display_errors(self, list_folder_with_error=[]):
        for _line in list_folder_with_error:
            display(HTML('<span style="font-size: 20px; color:red">' + _line + '!</span>'))

    def copy_and_renamed_fits_files(self, output_dir='./', original_list_of_files=[], prefix='test'):
        current_working_dir = str(Path(original_list_of_files[0]).parent)
        make_or_reset_folder(output_dir)
        log_file = str(Path(output_dir).joinpath(f"renaming_log.txt"))

        renaming_log_file = [f"Renaming schema of folder {current_working_dir}",
                             "old name -> new name", ""]
        for index, _file  in enumerate(original_list_of_files):

            old_name = Path(_file).name
            new_name = Path(output_dir).joinpath(prefix + f"_{index:05d}.fits")
            new_short_name = Path(new_name).name
            renaming_log_file.append(f"{old_name} -> {new_short_name}")

            # renamed here
            copyfile(_file, new_name)

        make_ascii_file(metadata=renaming_log_file, data=[], output_file_name=log_file)
