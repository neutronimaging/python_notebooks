import numpy as np
import os
from IPython.core.display import HTML
from IPython.core.display import display

from __code.file_handler import make_ascii_file


class ExportProfiles(object):

    def __init__(self, parent=None, export_folder=''):
        self.parent = parent
        self.export_folder = export_folder

    def _create_output_file_name(self, profile_index=0):
        base_name = os.path.basename(self.parent.working_dir)
        output_file_name = os.path.join(self.export_folder, "{}_profile_{}.txt".format(base_name, profile_index + 1))
        return output_file_name

    def _create_metadata(self, profile_index=0):
        metadata = ["# Counts vs pixel position"]
        metadata.append("#average counts of width of profile is used!")
        profile_dimension = self.parent.get_profile_dimensions(row=profile_index)
        is_x_profile_direction = self.parent.ui.profile_direction_x_axis.isChecked()
        x_left = profile_dimension.x_left
        x_right = profile_dimension.x_right
        y_top = profile_dimension.y_top
        y_bottom = profile_dimension.y_bottom
        metadata.append("#Profile dimension:")
        metadata.append("# * [x0, y0, x1, y1] = [{}, {}, {}, {}]".format(x_left, y_top, x_right, y_bottom))
        if is_x_profile_direction:
            metadata.append("# * integrated over y_axis")
            table_axis = ['#x_axis']
        else:
            metadata.append("# * integrated over x_axis")
            table_axis = ['#y_axis']
        nbr_files = len(self.parent.data_dict['file_name'])
        metadata.append("#List of files ({} files)".format(nbr_files))
        for _index, _file in enumerate(self.parent.data_dict['file_name']):
            metadata.append("# * {} -> col{}".format(_file, _index + 1))
            table_axis.append("# col.{}".format(_index + 1))
        metadata.append("#")
        metadata.append("#" + ",".join(table_axis))
        return metadata

    def _create_data(self, profile_index=0):
        all_profiles = []
        x_axis = []
        for _data in self.parent.data_dict['data']:
            [x_axis, profile] = self.parent.get_profile(image=np.transpose(_data),
                                                        profile_roi_row=profile_index)
            all_profiles.append(list(profile))

        data = []
        for _index, _row in enumerate(np.transpose(all_profiles)):
            str_row = [str(_value) for _value in _row]
            data.append("{}, ".format(x_axis[_index]) + ", ".join(str_row))

        return data

    def run(self):
        _nbr_profiles = self.parent.ui.tableWidget.rowCount()
        for _profile_index in np.arange(_nbr_profiles):
            _output_file_name = self._create_output_file_name(profile_index=_profile_index)
            metadata = self._create_metadata(profile_index=_profile_index)
            data = self._create_data(profile_index=_profile_index)
            make_ascii_file(metadata=metadata,
                            data=data,
                            output_file_name=_output_file_name,
                            dim='1d')

            display(HTML("Exported Profile file {}".format(_output_file_name)))
