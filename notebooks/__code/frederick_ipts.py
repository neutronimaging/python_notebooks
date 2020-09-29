from collections import OrderedDict
import numpy as np
import os
import re

from IPython.core.display import display
from ipywidgets import widgets

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from __code.ipywe import fileselector

from __code.file_handler import make_ascii_file
from NeuNorm.normalization import Normalization
from __code.file_handler import retrieve_time_stamp
from __code.file_format_reader import DscReader

#from __code.file_metadata_display import Interface


class FrederickIpts(object):

    def __init__(self, working_dir='./'):
        self.working_dir = working_dir

    def select_file_help(self, value):
        import webbrowser
        webbrowser.open("https://neutronimaging.pages.ornl.gov/en/tutorial/notebooks/file_selector/#select_profile")

    def select_files(self):
        help_ui = widgets.Button(description="HELP",
                                 button_style='info')
        help_ui.on_click(self.select_file_help)
        display(help_ui)

        self.files_ui = fileselector.FileSelectorPanel(instruction='Select Images ...',
                                                       start_dir=self.working_dir,
                                                       next=self.load_and_sort,
                                                       multiple=True)

        self.files_ui.show()

    def load_and_sort(self, list_files):
        # list_files = self.files_ui.selected
        self.dict_files = retrieve_time_stamp(list_files)
        self.__sort_files_using_metadata_in_name()
        self.__load_files()
        self.__calculate_all_working_images()

    def __sort_files_using_metadata_in_name(self):
        my_re = r"\w*_(?P<temperature>\w+)_(?P<pressure>\w+)_\d{4}_(?P<digit>\d{4}).tiff$"
        exp_dict = OrderedDict()
        _new_exp = {'list_of_files': [],
                    'T': '',
                    'P': '',
                    'list_of_images': [],
                    'working_image': {'type': '',
                                      'image': []},
                    'folder': ''}

        previous_T = ''
        previous_P = ''

        list_of_files = self.dict_files['list_images']

        exp_index = 0
        for _index, _file in enumerate(list_of_files):
            _path = os.path.dirname(_file)
            _file = os.path.basename(_file)
            m = re.match(my_re, _file)
            if m is None:
                continue

            if m:
                _T = m.group('temperature')
                _P = m.group('pressure')
            else:
                _T = 'N/A'
                _P = 'N/A'

            # first entry
            if _new_exp['list_of_files'] == []:
                _new_exp['list_of_files'] = [os.path.basename(_file)]
                _new_exp['folder'] = _path

                _new_exp['T'] = _T
                previous_T = _T

                _new_exp['P'] = _P
                previous_P = _P

            # after first entry
            else:

                if (_T == previous_T) and (_P == previous_P):
                    # found the same T and P, just append file to list of files
                    _new_exp['list_of_files'].append(_file)

                else:
                    # we found a new T or new P, save previous dict and initialization of new one
                    exp_dict[str(exp_index)] = _new_exp
                    exp_index += 1
                    _new_exp = {'list_of_files': [],
                                'T': '',
                                'P': '',
                                'list_of_images': [],
                                'working_image': {'type': '',
                                                  'image': []},
                                'folder': ''}

                    # start recording new entry
                    _new_exp['list_of_files'] = [os.path.basename(_file)]
                    _new_exp['folder'] = _path

                    _new_exp['T'] = _T
                    previous_T = _T

                    _new_exp['P'] = _P
                    previous_P = _P

            # last entry, force the save of the dictionary
            if _index == len(list_of_files) - 1:
                exp_dict[str(exp_index)] = _new_exp

        self.exp_dict = exp_dict

    # Helper functions
    def __load_files(self):

        progress_bar_layout = widgets.Layout(border='1px solid blue')

        hbox = widgets.HBox([widgets.IntProgress(description="FUll Progress",
                                                 layout=progress_bar_layout),
                             widgets.Label(value='',
                                           layout=widgets.Layout(width='10%'))])
        w = hbox.children[0]
        nbr_groups = len(self.exp_dict.keys())
        w.max = nbr_groups
        label = hbox.children[1]
        label.value = f"0/{nbr_groups}"

        display(hbox)

        for _index, _key in enumerate(self.exp_dict.keys()):
            _item = self.exp_dict[_key]
            _path = _item['folder']
            list_files = _item['list_of_files']
            full_list_files = [os.path.join(_path, _file) for _file in list_files]
            o_norm = Normalization()
            o_norm.load(file=full_list_files, notebook=True)
            _data = o_norm.data['sample']['data']
            _item['list_of_images'] = _data
            self.exp_dict[_key] = _item

            w.value = _index + 1
            label.value = f"{_index+1}/{nbr_groups}"

        hbox.close()
        display(widgets.Label(value="Done!"))

    def __sort_files_using_time_stamp(self, dict_time_stamp):
        """Using the time stamp information, all the files will be sorted in ascending order of time stamp"""

        list_files = dict_time_stamp['list_files'].copy()
        list_time_stamp = dict_time_stamp['list_time_stamp'].copy()
        list_time_stamp_user_format = dict_time_stamp['list_time_stamp_user_format'].copy()

        list_files = np.array(list_files)
        time_stamp = np.array(list_time_stamp)
        time_stamp_user_format = np.array(list_time_stamp_user_format)

        # sort according to time_stamp array
        sort_index = np.argsort(time_stamp)

        # using same sorting index of the other list
        sorted_list_files = list_files[sort_index]
        sorted_list_time_stamp = time_stamp[sort_index]
        sorted_list_time_stamp_user_format = time_stamp_user_format[sort_index]

        self.dict_files = {'list_files': list(sorted_list_files),
                           'list_time_stamp': sorted_list_time_stamp,
                           'list_time_stamp_user_format': sorted_list_time_stamp_user_format}

    def __calculate_group_working_image(self, list_of_images):
        """Determine here if we should use the last image or a mean of all the images"""
        # TO DO
        _type = 'last_image'
        _type = 'mean'
        _image = np.mean(list_of_images, axis=0)

        working = {'type': _type,
                   'image': _image}

        return working

    def __calculate_all_working_images(self):
        for _group_number in self.exp_dict.keys():
            _group = self.exp_dict[_group_number]
            nbr_images = len(_group['list_of_images'])
            if nbr_images == 1:
                _group['working_image']['type'] = 'last_image'
                _group['working_image']['image'] = _group['list_of_images'][0].copy()
            else:
                _list_images = _group['list_of_images']

                _result_working_image = self.__calculate_group_working_image(_list_images)
                _group['working_image'] = _result_working_image
            self.exp_dict[_group_number] = _group


