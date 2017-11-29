import os
from PIL import Image
from PIL.ExifTags import TAGS
import numpy as np
import time
from collections import OrderedDict


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