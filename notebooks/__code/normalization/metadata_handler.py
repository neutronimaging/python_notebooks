from IPython.core.display import display, HTML
import collections
import numpy as np
from enum import Enum

from __code import file_handler
from __code import metadata_handler
from __code._utilities.dictionary import combine_dictionaries

class MetadataName(Enum):
    EXPOSURE_TIME = 65027
    DETECTOR_MANUFACTURER = 65026
    APERTURE_HR = 65068
    APERTURE_HL = 65070
    APERTURE_VT = 65066
    APERTURE_VB = 65064

    def __str__(self):
        return self.value

METADATA_KEYS = {'ob' : [MetadataName.EXPOSURE_TIME,
                         MetadataName.DETECTOR_MANUFACTURER,
                         MetadataName.APERTURE_HR,
                         MetadataName.APERTURE_HL,
                         MetadataName.APERTURE_VT,
                         MetadataName.APERTURE_VB],
                 'df' : [MetadataName.EXPOSURE_TIME,
                         MetadataName.DETECTOR_MANUFACTURER],
                 'all': [MetadataName.EXPOSURE_TIME,
                         MetadataName.DETECTOR_MANUFACTURER,
                         MetadataName.APERTURE_HR,
                         MetadataName.APERTURE_HL,
                         MetadataName.APERTURE_VT,
                         MetadataName.APERTURE_VB]}


class MetadataHandler:

    @staticmethod
    def retrieve_metadata(list_of_files=[], display_infos=False, label=""):
        """
        dict = {'file1': {'metadata1_key': {'value': value, 'name': name},
                          'metadata2_key': {'value': value, 'name': name},
                          'metadata3_key': {'value': value, 'name': name},
                          ...
                          },
                ...
                }
        """
        _dict = file_handler.retrieve_time_stamp(list_of_files, label=label)
        _time_metadata_dict = MetadataHandler._reformat_dict(dictionary=_dict)

        _beamline_metadata_dict = MetadataHandler.retrieve_beamline_metadata(list_of_files)
        _metadata_dict = combine_dictionaries(master_dictionary=_time_metadata_dict,
                                                                                  servant_dictionary=_beamline_metadata_dict)

        if display_infos:
            display(HTML('<span style="font-size: 20px; color:blue">Nbr of images: ' + str(len(_metadata_dict)) +
                         '</span'))
            display(HTML('<span style="font-size: 20px; color:blue">First image was taken at : ' + \
                         _metadata_dict[0]['time_stamp_user_format'] + '</span>'))
            last_index = len(_metadata_dict) - 1
            display(HTML('<span style="font-size: 20px; color:blue">Last image was taken at : ' + \
                         _metadata_dict[last_index]['time_stamp_user_format'] + '</span>'))

        return _metadata_dict

    @staticmethod
    def retrieve_beamline_metadata(list_files):
        """list of metadata to retrieve is:000
            - acquisition time -> 65027
            - detector type -> 65026 (Manufacturer)
            - slits positions ->
            - aperture value
        """
        list_metadata = METADATA_KEYS['all']
        _dict = metadata_handler.MetadataHandler.retrieve_metadata(list_files=list_files,
                                                                   list_metadata=list_metadata,
                                                                   using_enum_object=True)

        for _file_key in _dict.keys():
            _file_dict = {}
            for _pv in list_metadata:
                _raw_value = _dict[_file_key][_pv]
                if _raw_value is not None:
                    split_raw_value = _raw_value.split(":")
                    try:
                        _value = np.float(split_raw_value[1])
                    except ValueError:
                        _value = split_raw_value[1]
                    finally:
                        _file_dict[_pv.value] = {'value': _value, 'name': _pv.name}
                else:
                    _file_dict[_pv.value] = {}
            _dict[_file_key] = _file_dict
        return _dict

    @staticmethod
    def _reformat_dict(dictionary={}):
        """
        to go from
            {'list_images': [], 'list_time_stamp': [], 'list_time_stamp_user_format':[]}
        to
            {'0': {'filename': file1,
                   'time_stamp': 'value',
                   'time_stamp_user_format': 'value',
                   },
             ...,
             }
        """
        formatted_dictionary = collections.OrderedDict()
        list_files = dictionary['list_images']
        list_time_stamp = dictionary['list_time_stamp']
        list_time_stamp_user_format = dictionary['list_time_stamp_user_format']

        for _index, _file in enumerate(list_files):
            formatted_dictionary[_index] = {'filename'              : _file,
                                            'time_stamp'            : list_time_stamp[_index],
                                            'time_stamp_user_format': list_time_stamp_user_format[_index]}
        return formatted_dictionary
