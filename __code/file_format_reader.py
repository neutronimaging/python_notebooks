from collections import defaultdict
import numpy as np
import os
import re

from __code.file_handler import  read_ascii


class DscReader(object):

    dict_metadata = {}

    list_tags = {'time_stamp': '"Start time"',
                 'time_stamp_user_format': '"Start time (string)"',
                 'acquisition_time (s)': '"Acq time"'}

    def __init__(self, list_files=[]):
        self.list_files = list_files

    def read(self):
        dict_metadata = {}
        for _file in self.list_files:

            # make sure the file exists
            if not(os.path.exists(_file)):
                continue

            _short_file = os.path.basename(_file)
            dict_metadata[_short_file] = {}

            _data = read_ascii(filename=_file).split('\n')
            for _tags in self.list_tags.keys():
                for _row, _line in enumerate(_data):
                    if _line.startswith(self.list_tags[_tags]):
                        dict_metadata[_short_file][_tags] = _data[_row +2]

        self.dsc_metadata = dict_metadata

    def build_coresponding_file_image_name(self):
        """
        typical dsc file name:
            Sample5_1min_r000000..dsc
        corresponding to image
            Sample5_1min_r_0.tif
        :return:
        """
        _dsc_metadata = self.dsc_metadata
        re_string = r"^(?P<base>\w*_r)(?P<index>\d+)..dsc$"
        for _file in _dsc_metadata.keys():
            m = re.match(re_string, _file)
            if m:
                index = np.int(m.group('index'))
                base = m.group('base')
                correspoinding_tif_file_name = "{}_{}.tif".format(base, index)
                _dsc_metadata[_file]['tif_file_name'] = correspoinding_tif_file_name
        self.dsc_metadata = _dsc_metadata

    def make_tif_file_name_the_key(self):
        _dict_time_stamp_vs_tiff = defaultdict(lambda: {'time_stamp': 0,
                                                        'time_stamp_user_format': 'N/A'})
        _dsc_metadata = self.dsc_metadata

        for _key in _dsc_metadata.keys():
            _tif_name = _dsc_metadata[_key]['tif_file_name']
            _time_stamp = _dsc_metadata[_key]['time_stamp']
            _time_stamp_user_format = _dsc_metadata[_key]['time_stamp_user_format']
            _dict_time_stamp_vs_tiff[_tif_name]['time_stamp']= _time_stamp
            _dict_time_stamp_vs_tiff[_tif_name]['time_stamp_user_format'] = _time_stamp_user_format

        self.dict_time_stamp_vs_tiff = _dict_time_stamp_vs_tiff
