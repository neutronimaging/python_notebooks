import os
import numpy as np
import collections

from __code import file_handler
from __code.normalization.metadata_handler import MetadataName

METADATA_ERROR_ALLOWED = 1


def make_full_output_normalization_folder_name(output_folder='', first_sample_file_name='',
                                               name_acquisition='', name_config=''):
    basename_sample_folder = os.path.basename(os.path.dirname(first_sample_file_name))
    basename_sample_folder += "_{}_{}".format(name_acquisition, name_config)
    full_basename_sample_folder = os.path.abspath(os.path.join(output_folder, basename_sample_folder))
    file_handler.make_or_reset_folder(full_basename_sample_folder)
    return full_basename_sample_folder


def populate_normalization_recap_row(acquisition="", config="", nbr_sample=0, nbr_ob=0, nbr_df=0,
                                     normalize_this_config=True,
                                     force_combine=True,
                                     roi=None,
                                     how_to_combine='median'):

    if not normalize_this_config.value:
        status_string = "<th style='color:black'>SKIP!</th>"
    else:
        if nbr_ob > 0:
            status_string = "<th style='color:green'>OK</th>"
        else:
            status_string = "<th style='color:red'>Missing OB!</th>"

    if force_combine:
        combine_ob = "Yes"
        how_to_combine_ob = how_to_combine
    else:
        combine_ob = 'No'
        how_to_combine_ob = "N/A"

    if roi is None:
        roi = 'No'
    else:
        roi = 'Yes'

    _row = ""
    _row = "<tr>" \
           "<th>{}</th>" \
           "<th>{}</th>" \
           "<th>{}</th>" \
           "<th>{}</th>" \
           "<th>{}</th>" \
           "<th>{}</th>" \
           "<th>{}</th>" \
           "<th>{}</th>" \
           "{}" \
           "</tr>". \
        format(acquisition, config, nbr_sample, nbr_ob, nbr_df, combine_ob, how_to_combine_ob, roi, status_string)

    return _row


def keep_basename_only(list_files=[]):
    basename_only = [os.path.basename(_file) for _file in list_files]
    return basename_only


def all_metadata_match(metadata_1={}, metadata_2={}, list_key_to_check=None):
    list_key = metadata_1.keys() if list_key_to_check is None else list_key_to_check

    for _key in list_key:
        try:
            if np.abs(np.float(
                    metadata_1[_key]['value']) - np.float(metadata_2[_key]['value'])) > METADATA_ERROR_ALLOWED:
                return False
        except ValueError:
            if metadata_1[_key]['value'] != metadata_2[_key]['value']:
                return False
    return True


def isolate_instrument_metadata(dictionary):
    """create a dictionary of all the instrument metadata without the acquisition time"""
    isolated_dictionary = {}
    for _key in dictionary.keys():
        if _key == MetadataName.EXPOSURE_TIME:
            continue
        isolated_dictionary[_key] = dictionary[_key]
    return isolated_dictionary


def _reformat_dict(dictionary=None):
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


def isolate_infos_from_file_index(index=-1, dictionary=None, all_keys=False):
    result_dictionary = collections.OrderedDict()

    if all_keys:
        for _image in dictionary['list_images'].keys():
            _time_image = dictionary['list_time_stamp'][index]
            _user_format_time_image = dictionary['list_time_stamp_user_format'][index]
            result_dictionary[_image] = {'system_time'     : _time_image,
                                         'user_format_time': _user_format_time_image}
    else:
        _image = dictionary['list_images'][index]
        _time_image = dictionary['list_time_stamp'][index]
        _user_format_time_image = dictionary['list_time_stamp_user_format'][index]
        result_dictionary = {'file_name'       : _image,
                             'system_time'     : _time_image,
                             'user_format_time': _user_format_time_image}

    return result_dictionary
