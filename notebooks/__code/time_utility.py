import os
from PIL import Image
import numpy as np
import time
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import datetime
from collections import OrderedDict
from ipywidgets import widgets
from IPython.core.display import display

from __code import file_handler
from __code.metadata_handler import MetadataHandler

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


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


def convert_system_time_into_hours(system_time_s):
    time_hour = system_time_s / 3600
    return time_hour


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
    exposure_time = float(exposure_label_and_time[1])
    
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

        [list_files, ext] = file_handler.retrieve_list_of_most_dominant_extension_from_folder(folder=self.folder,
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


class TimestampFormatter:

    list_input_timestamp = ["%m/%d/%Y %H:%M:%S",
                            "%m/%d/%Y %I:%M:%S",
                            "%Y-%m-%d %H:%M:%S",
                            "%Y-%m-%d %I:%M:%S",
                            "%d/%m/%Y %H:%M:%S",
                            "%d/%m/%Y %I:%M:%S",
                            "%Y/%m/%d %H:%M:%S",
                            "%Y/%m/%d %I:%M:%S",
                            "%Y-%m-%dT%I:%M:%S-"]

    def __init__(self, timestamp="",
                 input_timestamp_format=None,
                 output_timestamp_format=TIMESTAMP_FORMAT):
        self.timestamp = timestamp
        if input_timestamp_format is None:
            self.input_timestamp_format = self.list_input_timestamp
        else:
            self.input_timestamp_format = list(input_timestamp_format)
        self.output_timestamp_format = output_timestamp_format

    def format_oncat_timestamp(self):
        """go from 2018-09-17T21:50:50.978000-04:00, to 2018-09/17 21:50:50.978000"""
        oncat_timestamp = self.timestamp
        [date, time_edt] = oncat_timestamp.split("T")
        if "." in time_edt:
            [time, _] = time_edt.split(".")
        else:
            time = time_edt
        return "{} {}".format(date, time)

    def format(self):
        if self.input_timestamp_format[0] == TIMESTAMP_FORMAT:
            return self.timestamp

        if type(self.timestamp) is list:
            formatted_timestamp = [self.convert_timestamp(t) for t in self.timestamp]
        else:
            formatted_timestamp = self.convert_timestamp(self.timestamp)

        return formatted_timestamp

    def convert_timestamp(self, timestamp):
        """TIMESTAMP_FORMAT = "%Y-%m-%d %I:%M:%S"  """

        input_timestamp_format = self.list_input_timestamp

        o_time = None
        for _input_timestamp_format in input_timestamp_format:
            # print("trying this format {} with this {}".format(_input_timestamp_format, timestamp))
            o_time = TimestampFormatter.get_time_dict(timestamp=timestamp,
                                                      input_time_format=_input_timestamp_format)
            if o_time:
                break

        if o_time:
            converted_timestamp = "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(o_time.tm_year,
                                                                                 o_time.tm_mon,
                                                                                 o_time.tm_mday,
                                                                                 o_time.tm_hour,
                                                                                 o_time.tm_min,
                                                                                 o_time.tm_sec)
            return converted_timestamp
        else:
            raise ValueError("Time {} could not be converted! ".format(timestamp))

    @staticmethod
    def get_time_dict(timestamp="", input_time_format='%m/%d/%Y %H:%M:%S'):
        """return the time dict using the input time format proposed
        time_dict.tm_year
        time_dict.tm_mon
        time_dict.tm_mday
        time_dict.tm_hour
        time_dict.tm_min
        time_dict.tm_sec
        """
        # time_string = 09/18/2018 12:00:35
        try:
            time_dict = time.strptime(timestamp.strip(), input_time_format)
            # print("{} -> {}".format(timestamp, time_dict))
        except:
            ValueError("Error converting {} -> {}".format(timestamp, input_time_format))
            time_dict = None

        return time_dict

    @staticmethod
    def convert_to_second(timestamp_value, timestamp_format=TIMESTAMP_FORMAT):
        d = datetime.datetime.strptime(timestamp_value, timestamp_format)
        return time.mktime(d.timetuple())


class AbsoluteTimeHandler:

    def __init__(self, initial_absolute_time=None):
        if initial_absolute_time is None:
            raise ValueError("Please provide an initial absolute time format as 'YYYY-MM-DDTHH:MM:SS.SSSSSS-05:00")

        self.formatted_initial_absolute_time = parse(initial_absolute_time)

    def get_absolute_time_for_this_delta_time_array(self, delta_time_array=None, units='seconds'):
        '''

        :param delta_time_array: list of time offset
        :param units: seconds by default ['seconds', 'minutes', 'hours']
        :return:
        list of time in absolute scale
        '''
        if delta_time_array is None:
            raise ValueError("Empty delta time array!")

        if units == 'seconds':
            delta_time_formated = [relativedelta(seconds=t) for t in delta_time_array]
        elif units == 'minutes':
            delta_time_formated = [relativedelta(minutes=m) for m in delta_time_array]
        elif units == 'hours':
            delta_time_formated = [relativedelta(hours=h) for h in delta_time_array]
        else:
            raise NotImplementedError("time units not implemented!")

        self.delta_time_formated = delta_time_formated

        absolute_time = [delta_time + self.formatted_initial_absolute_time for delta_time in delta_time_formated]
        return absolute_time


class RelativeTimeHandler:
    '''the main goal of this class is to produce a relative time array using another starting time as a start.
     In other words, let suppose some metadata got recorded in a nexus that started at time t0, another file recorded
     another set of those same metadata but this file started at time t1. We want to calculate the time of this
     set of metadata relative to the first file recorded. To do so we simply need to add (t1-t0) to the second
     set of time array
     '''

    def __init__(self, master_initial_time=None, local_initial_time=None):
        if (master_initial_time is None) or (local_initial_time is None):
            raise ValueError("Please provide an initial absolute time format as 'YYYY-MM-DDTHH:MM:SS.SSSSSS-05:00")

        formatted_master_initial_time = parse(master_initial_time)
        formatted_local_initial_time = parse(local_initial_time)

        if formatted_local_initial_time < formatted_master_initial_time:
            raise ValueError("Master time should be before local time!")

        time_offset_calculated = formatted_local_initial_time - formatted_master_initial_time
        self.time_offset_calculated_s = time_offset_calculated.seconds

    def get_relative_time_for_this_time_array(self, time_array=None):

        if time_array is None:
            raise ValueError("Empty time array!")

        relative_time = [(t + self.time_offset_calculated_s) for t in time_array]
        return relative_time
