from qtpy import QtGui
from qtpy.QtWidgets import QMenu
from PIL import Image

from .get import Get
from .metadata_selector_handler import MetadataSelectorHandler
from .utilities import string_cleaning, linear_operation, is_linear_operation_valid


class MetadataTableHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def right_click(self, position=None):
        o_get = Get(parent=self.parent)
        column_selected = o_get.metadata_column_selected()

        if column_selected == 1:
            return

        menu = QMenu(self.parent)

        _set_new_metadata = None
        if column_selected in [2, 3]:
            _set_new_metadata = menu.addAction("Select metadata ...")
            menu.addSeparator()

        _x_axis = None
        _y_axis = None
        if column_selected in [0, 2, 3]:
            if column_selected == self.parent.x_axis_column_index:
                x_axis_string = self.parent.xy_axis_menu_logo['enable'] + "X-axis"
            else:
                x_axis_string = self.parent.xy_axis_menu_logo['disable'] + "X-axis"
            _x_axis = menu.addAction(x_axis_string)

            if column_selected == self.parent.y_axis_column_index:
                y_axis_string = self.parent.xy_axis_menu_logo['enable'] + "Y-axis"
            else:
                y_axis_string = self.parent.xy_axis_menu_logo['disable'] + "Y-axis"
            _y_axis = menu.addAction(y_axis_string)

        action = menu.exec_(QtGui.QCursor.pos())

        if action == _set_new_metadata:
            o_selector = MetadataSelectorHandler(parent=self.parent, column=column_selected)
            o_selector.show()

        elif action == _x_axis:
            self.parent.x_axis_column_index = column_selected
            self.parent.update_metadata_pyqt_ui()

        elif action == _y_axis:
            self.parent.y_axis_column_index = column_selected
            self.parent.update_metadata_pyqt_ui()

    def metadata_list_changed(self, index, column):
        key_selected = self.parent.list_metadata[index]

        self.parent.eventProgress.setMinimum(1)
        self.parent.eventProgress.setMaximum(len(self.parent.data_dict['file_name']))
        self.parent.eventProgress.setValue(1)
        self.parent.eventProgress.setVisible(True)
        self.parent.eventProgress.setEnabled(True)

        for row, _file in enumerate(self.parent.data_dict['file_name']):
            o_image = Image.open(_file)
            o_dict = dict(o_image.tag_v2)
            value = o_dict[float(key_selected)]

            new_value = self.perform_cleaning_and_math_on_metadata(column=column, value=value)
            self.parent.ui.tableWidget.item(row, column).setText("{}".format(new_value))

            self.parent.eventProgress.setValue(row+1)
            QtGui.QGuiApplication.processEvents()

        self.parent.update_metadata_pyqt_ui()
        self.parent.eventProgress.setVisible(False)

    def perform_cleaning_and_math_on_metadata(self, column=1, value=""):
        metadata_operation = self.parent.metadata_operation

        first_part_of_string_to_remove = metadata_operation[column]['first_part_of_string_to_remove']
        last_part_of_string_to_remove = metadata_operation[column]['last_part_of_string_to_remove']
        string_cleaned = string_cleaning(first_part_of_string_to_remove=first_part_of_string_to_remove,
                                         last_part_of_string_to_remove=last_part_of_string_to_remove,
                                         string_to_clean=value)

        value_1 = metadata_operation[column]['value_1']
        value_2 = metadata_operation[column]['value_2']
        if is_linear_operation_valid(input_parameter=string_cleaned,
                                     value_1=value_1,
                                     value_2=value_2):

            math_1 = metadata_operation[column]['math_1']
            math_2 = metadata_operation[column]['math_2']
            result_linear_operation = linear_operation(input_parameter=string_cleaned,
                                                       math_1=math_1,
                                                       value_1=value_1,
                                                       math_2=math_2,
                                                       value_2=value_2)
        else:
            return string_cleaned

        return result_linear_operation
