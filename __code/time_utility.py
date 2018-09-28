import os
from PIL import Image
import numpy as np
import time
from collections import OrderedDict
from ipywidgets import widgets
from IPython.core.display import display

from __code import file_handler
from __code.metadata_handler import MetadataHandler


def format_time_stamp(file_name = None, time_stamp = None):
    """Format the time stamp to easily retrieve the day, time, hour,
    and keep only short file name"""
    
    _short_file_name = os.path.basename(file_name)
    [week_day, month, day, hours, year] = time_stamp.split()
    
    [hours, minutes, seconds] = hours.split(':')
    _dict_time = {"hours": hours,
                  "minutes": minutes,
                  "seconds": seconds}
    
    _dict_time_stamp = {"week_day": week_day,
                       "month": month,
                       "day": day,
                       "hours": _dict_time,
                       "year": year}
    
    return [_short_file_name, _dict_time_stamp]


def retrieve_time_stamp(filename=''):
    if not os.path.exists(filename):
        raise OSError
    
    image = Image.open(filename)
        
    metadata = image.tag_v2.as_dict()
    acquisition_time = metadata[65000][0]
    
    time_stamp = {}
    time_stamp['acquisition_time_computer_format'] = acquisition_time
    time_stamp['acquisition_time_user_format'] = time.ctime(acquisition_time)
    
    return time_stamp

def retrieve_exposure_time(filename=''):
    if not os.path.exists(filename):
        return -1
    
    image = Image.open(filename)
    metadata = image.tag_v2.as_dict()

    exposure_label_and_time = metadata[65021][0].split(':')
    exposure_time = np.float(exposure_label_and_time[1])
    
    return exposure_time

def keep_s_precision(time_s):
    time_10s = time_s / _coeff
    time_10s_int = int(time_10s)
    delta_time_10s = time_10s - time_10s_int
    delta_time_s = delta_time_10s * _coeff
    return delta_time_s

def get_dict_of_time_stamps(file, index_file=-1, time_zero=-1, coeff=1):
    _dict = OrderedDict()
    acquisition_time_dict = retrieve_time_stamp(filename=file)
    acquisition_time = acquisition_time_dict['acquisition_time_computer_format']
    _dict['raw_time_stamp'] = acquisition_time
    _dict['ctime'] = acquisition_time_dict['acquisition_time_user_format']
    if index_file == 0:
        _dict['ms_since_first_image'] = 0
    else:
        delta_time = acquisition_time - time_zero
        delta_time_ms = delta_time * 1000.
        _dict['ms_since_first_image'] = delta_time_ms
    return _dict


class RetrieveTimeStamp(object):

    list_time_stamp = []
    list_time_stamp_user_format = []
    output_list_files = []
    input_list_files  =[]

    def __init__(self, folder='', files=[], is_notebook=False):
        self.folder = folder
        self.input_list_files = files
        self.__is_notebook = is_notebook

    def _run(self):

        [list_files, ext] = file_handler.retrieve_list_of_most_dominand_extension_from_folder(folder=self.folder,
                                                                                              files=self.input_list_files)
        self.output_list_files = list_files

        if ext.lower() in ['.tiff', '.tif']:
            ext = 'tif'
        elif ext.lower() == '.fits':
            ext = 'fits'
        else:
            raise ValueError

        if self.__is_notebook:
            box = widgets.HBox([widgets.Label("Retrieving Time Stamp",
                                              layout=widgets.Layout(width='20%')),
                                widgets.IntProgress(min=0,
                                                    max=len(list_files),
                                                    value=0,
                                                    layout=widgets.Layout(width='50%'))
                                ])
            progress_bar = box.children[1]
            display(box)

        list_time_stamp = []
        list_time_stamp_user_format = []
        for _index, _file in enumerate(list_files):
            _time_stamp = MetadataHandler.get_time_stamp(file_name=_file, ext=ext)
            list_time_stamp.append(_time_stamp)

            _user_format = MetadataHandler.convert_to_human_readable_format(_time_stamp)
            list_time_stamp_user_format.append(_user_format)
            if self.__is_notebook:
                progress_bar.value = _index + 1

        self.list_time_stamp = list_time_stamp
        self.list_time_stamp_user_format = list_time_stamp_user_format

        if self.__is_notebook:
            box.close()


