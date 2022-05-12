import numpy as np
from collections import OrderedDict
import shutil

from NeuNorm.normalization import Normalization


def combine_images(output_folder="./", list_images=None, new_file_name=""):
    """
    This take a list of images and combine them using np.median and will create the new file in the output_folder
    using the new_file_name as base line.
    """
    if list_images is None:
        return

    o_norm = Normalization()
    o_norm.load(file=list_images, notebook=False)
    _data = o_norm.data['sample']['data']
    _metadata = o_norm.data['sample']['metadata'][0]

    _combined_data = np.median(_data, axis=0)
    del o_norm

    o_combined = Normalization()
    o_combined.load(data=_data)
    o_combined.data['sample']['metadata'] = [_metadata]
    o_combined.data['sample']['data'] = _data
    o_combined.data['sample']['file_name'] = [new_file_name]
    o_combined.export(folder=output_folder, data_type='sample')
    del o_combined


def make_dictionary_of_groups_new_names(dictionary_of_groups_sorted, dict_group_outer_value):
    dict_new_names = OrderedDict()
    for _group_index in dictionary_of_groups_sorted.keys():
        nbr_files = len(dictionary_of_groups_sorted[_group_index])
        outer_value = float(dict_group_outer_value[_group_index])
        str_outer_value = f"{outer_value:0.3f}"
        str_outer_value_formatted = str_outer_value.replace(".", "_", 1)
        before_and_after_decimal = str_outer_value_formatted.split("_")
        if len(before_and_after_decimal) > 1:
            before_decimal = int(before_and_after_decimal[0])
            before_decimal_str = f"{before_decimal:03d}"
            str_outer_value_formatted = "_".join([before_decimal_str, before_and_after_decimal[1]])
        list_new_names = [f"group_{str_outer_value_formatted}_{_index:07d}.tiff"
                          for _index
                          in np.arange(nbr_files)]
        dict_new_names[_group_index] = list_new_names
    return dict_new_names
