import os
from qtpy.QtWidgets import QFileDialog
import numpy as np

from __code._utilities.parent import Parent
from __code.wave_front_dynamics.get import Get
from __code._utilities.file import make_ascii_file
from __code._utilities.status_message import StatusMessageStatus, show_status_message


class Export(Parent):

    def run(self):
        parent_working_dir = os.path.dirname(self.parent.working_dir)
        output_folder = QFileDialog.getExistingDirectory(self.parent,
                                                         directory=parent_working_dir,
                                                         caption="Select where to export the data ...",
                                                         options=QFileDialog.ShowDirsOnly)
        if output_folder:

            output_file_name = self.make_up_output_file_name(output_folder=output_folder)

            o_get = Get(parent=self.parent)
            list_edge_calculation_algorithm = o_get.edge_calculation_algorithms_to_plot()

            metadata = self.retrieving_metadata(list_edge_calculation_algorithm)
            data = self.retrieve_data(list_edge_calculation_algorithm)
            make_ascii_file(output_file_name=output_file_name,
                            data=data,
                            metadata=metadata,
                            dim='1d')

            show_status_message(parent=self.parent,
                                message=f"File exported: {output_file_name}",
                                status=StatusMessageStatus.ready,
                                duration_s=10)

    def retrieve_data(self, list_edge_calculation_algorithm):
        peak_value_array = []
        for edge_calculation_algorithm in list_edge_calculation_algorithm:

            _array = self.parent.peak_value_arrays[edge_calculation_algorithm]
            if peak_value_array is None:
                continue

            peak_value_array.append(_array)

        transpose_array = np.transpose(peak_value_array)

        str_data_array = []
        for _data_row in transpose_array:
            str_data_row = [str(_item) for _item in _data_row]
            _str = ", ".join(str_data_row)
            str_data_array.append(_str)

        relative_timestamp = self.parent.list_of_timestamp_of_data_prepared
        for _row_index, _time in enumerate(relative_timestamp):
            str_data_array[_row_index] = "{}, {}".format(_time, str_data_array[_row_index])

        return str_data_array

    def retrieving_metadata(self, list_edge_calculation_algorithm):
        list_algo = []
        for edge_calculation_algorithm in list_edge_calculation_algorithm:
            list_algo.append(edge_calculation_algorithm + " (pixels number)")

        metadata = ["# Position of wave edge in nbr of pixels from center of profile using various algorithms"]
        metadata.append('# list of image files')
        for _file in self.parent.list_of_original_image_files_to_use:
            _str = "# " + _file
            metadata.append(_str)

        metadata.append("#")

        # columns label
        metadata.append(f"# relative time(s), {', '.join(list_algo)}")

        return metadata

    def make_up_output_file_name(self, output_folder="./"):
        list_of_original_files = self.parent.list_of_original_image_files_to_use
        parent_folder = os.path.dirname(list_of_original_files[0])
        base_name = os.path.basename(parent_folder)
        return os.path.join(output_folder, base_name + "_wave_front_dynamics.txt")
