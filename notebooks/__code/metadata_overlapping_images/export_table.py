import os

from .._utilities.table_handler import TableHandler


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



        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        nbr_row = o_table.row_count()

    def create_metadata_array(self):
        metadata = []
        metadata.append(f"# input folder: {self.parent.working_dir}")

        list_metadata = self.parent.list_metadata
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

        def format_math(metadata_operation, metadata_axis='x_axis'):
            math_1, value_1, math_2, value_2 = get_maths_values(x_axis_metadata_operation)
            if value_1 == ""
                metadata.append(f"Metadata {metadata_axis} operation: None")
            else:
                if value_2 == "":
                    metadata.append(f"Metadata {metadata_axis} operation: {math_1} {value_1}")
                else:
                    metadata.append(f"Metadata {metadata_axis} operation: {math_1} {value_1} {math_2} {value_2}")

        format_math(x_axis_metadata_operation, metadata_axis='x_axis', metadata=metadata)
        format_math(y_axis_metadata_operation, metadata_axis='y_axis', metadata=metadata)



        


        return metadata