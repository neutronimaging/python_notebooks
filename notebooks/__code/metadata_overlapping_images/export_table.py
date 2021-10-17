import os
import numpy as np

from .._utilities.table_handler import TableHandler
from .._utilities.file import make_ascii_file
from .._utilities.status_message import StatusMessageStatus, show_status_message


class ExportTable:

    def __init__(self, parent=None, export_folder=None):
        self.parent = parent
        self.export_folder = export_folder

    def _create_output_file_name(self):
        working_dir = self.parent.working_dir
        base_working_dir = os.path.basename(working_dir)

        full_file_name = os.path.join(self.export_folder, base_working_dir + "_metadata_table.txt")
        return full_file_name

    def run(self):
        full_output_file_name = self._create_output_file_name()
        metadata = self.create_metadata_array()
        data = self.create_data_array()
        make_ascii_file(metadata=metadata,
                        data=data,
                        output_file_name=full_output_file_name,
                        dim="1d")

        show_status_message(parent=self.parent,
                            message=f"Table has been exported in {full_output_file_name}",
                            status=StatusMessageStatus.ready,
                            duration_s=5)

    def create_data_array(self):
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        nbr_row = o_table.row_count()

        data = []
        for _row in np.arange(nbr_row):
            index = str(_row)
            file_name = o_table.get_item_str_from_cell(row=_row, column=1)
            metadata_1 = o_table.get_item_str_from_cell(row=_row, column=2)
            metadata_2 = o_table.get_item_str_from_cell(row=_row, column=3)
            line = (index, file_name, metadata_1, metadata_2)
            str_line = ", ".join(line)
            data.append(str_line)
        return data

    def create_metadata_array(self):
        metadata = []
        metadata.append(f"# input folder: {self.parent.working_dir}")

        x_axis_index = self.parent.x_axis_column_index
        y_axis_index = self.parent.y_axis_column_index
        x_axis_metadata_operation = self.parent.metadata_operation[x_axis_index]
        y_axis_metadata_operation = self.parent.metadata_operation[y_axis_index]

        def get_maths_values(metadata_operation):
            math_1 = metadata_operation['math_1']
            value_1 = metadata_operation['value_1']
            math_2 = metadata_operation['math_2']
            value_2 = metadata_operation['value_2']
            return (math_1, value_1, math_2, value_2)

        def format_math(metadata_operation, metadata_axis='x_axis', metadata=None):
            math_1, value_1, math_2, value_2 = get_maths_values(metadata_operation)
            if value_1 == "":
                metadata.append(f"# Metadata {metadata_axis} operation: None")
            else:
                if value_2 == "":
                    metadata.append(f"# Metadata {metadata_axis} operation: {math_1} {value_1}")
                else:
                    metadata.append(f"# Metadata {metadata_axis} operation: {math_1} {value_1} {math_2} {value_2}")

        format_math(x_axis_metadata_operation, metadata_axis='x_axis', metadata=metadata)
        format_math(y_axis_metadata_operation, metadata_axis='y_axis', metadata=metadata)

        list_metadata = self.parent.list_metadata
        metadata.append(f"# column 0: file index")
        metadata.append(f"# column 1: file name")
        metadata.append(f"# column 2: metadata {list_metadata[self.parent.metadata_operation[2]['index_of_metadata']]}")
        metadata.append(f"# column 3: metadata {list_metadata[self.parent.metadata_operation[3]['index_of_metadata']]}")

        metadata.append("#")

        return metadata
