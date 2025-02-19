from qtpy.QtWidgets import QFileDialog
from pathlib import Path
import numpy as np
import os

from __code._utilities.file import make_ascii_file
from __code._utilities.status_message import show_status_message, StatusMessageStatus


class Export:

    def __init__(self, parent=None):
        self.parent = parent

    def export(self):
        base_folder = os.path.basename(self.parent.working_folder)
        _export_folder = QFileDialog.getExistingDirectory(self.parent,
                                                          directory=os.path.dirname(base_folder),
                                                          caption="Select Output Folder")

        if _export_folder:
            output_base_file_name = str(base_folder) + "_statistics.txt"
            full_output_base_file_name = os.path.join(_export_folder, output_base_file_name)

            x_axis = self.parent.x_axis
            time_offset_array = x_axis['time_offset']

            y_axis = self.parent.y_axis
            mean_array = y_axis['mean']
            max_array = y_axis['max']
            min_array = y_axis['min']
            std_array = y_axis['std']
            median_array = y_axis['median']

            list_of_images = self.parent.list_of_images
            roi = self.parent.roi_dict

            metadata = ["# Statistics created with roi_statistics_vs_stack notebook"]
            metadata.append(f"# working dir: {self.parent.working_folder}")
            metadata.append(f"# roi selected: x0:{roi['x0']}, y0:{roi['y0']}, "
                            f"width:{roi['width']}, height:{roi['height']}")
            metadata.append("#")
            metadata.append("#file index, file name, time offset (s), min, max, mean, median, standard deviation")

            data = []
            for _row in np.arange(len(list_of_images)):
                _file_index = _row
                _file_name = os.path.basename(list_of_images[_row])
                _time_offset = time_offset_array[_row]
                _min = min_array[_row]
                _max = max_array[_row]
                _mean = mean_array[_row]
                _median = median_array[_row]
                _std = std_array[_row]

                _row = [_file_index, _file_name, _time_offset, _min, _max, _mean, _median, _std]
                _row_str = [str(_entry) for _entry in _row]
                _row_str_formatted = ",".join(_row_str)
                data.append(_row_str_formatted)

            make_ascii_file(metadata=metadata, data=data,
                            output_file_name=full_output_base_file_name,
                            dim="1d")

            show_status_message(parent=self.parent,
                                message=f"ASCII file has been created! -> {full_output_base_file_name}",
                                status=StatusMessageStatus.ready,
                                duration_s=10)
