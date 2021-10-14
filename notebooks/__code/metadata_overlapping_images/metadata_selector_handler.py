from qtpy.QtWidgets import QDialog
import os

from __code import load_ui
from .utilities import string_cleaning

class MetadataSelectorHandler(QDialog):

    def __init__(self, parent=None, column=2):
        self.parent = parent
        self.column = column
        super(MetadataSelectorHandler, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui', 'ui_metadata_overlapping_metadata_selector.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)

        self.initialization()
        self.check_if_before_linear_operation_valid()
        _ = self.is_linear_operation_is_valid()

    def initialization(self):
        list_metadata = self.parent.dict_list_metadata.values()
        list_metadata = [str(_item) for _item in list_metadata]
        self.ui.select_metadata_combobox.addItems(list_metadata)

    def string_cleaning_changed(self, new_text=None):
        first_part_of_string_to_remove = str(self.ui.first_part_lineEdit.text())
        last_part_of_string_to_remove = str(self.ui.second_part_lineEdit.text())
        string_to_clean = self.ui.select_metadata_combobox.currentText()

        cleaned_string = string_cleaning(first_part_of_string_to_remove=first_part_of_string_to_remove,
                                         last_part_of_string_to_remove=last_part_of_string_to_remove,
                                         string_to_clean=string_to_clean)
        self.ui.linear_operation_value_before.setText(cleaned_string)

        self.check_if_before_linear_operation_valid()
        self.linear_operation_lineedit_changed()

    def list_of_metadata_changed(self, text=None):
        self.string_cleaning_changed()

    def linear_operation_lineedit_changed(self, new_string=None):
        is_linear_operation_valid = self.is_linear_operation_is_valid()
        if not is_linear_operation_valid:
            return

        is_before_linear_operation_is_valid = self.is_before_linear_operation_is_valid()
        if not is_before_linear_operation_is_valid:
            return

        input_parameter = float(str(self.ui.linear_operation_value_before.text()).strip())
        math_1 = str(self.ui.linear_operation_comboBox_1.currentText())
        value_1 = str(self.ui.linear_operation_lineEdit_1.text()).strip()
        math_2 = str(self.ui.linear_operation_comboBox_2.currentText())
        value_2 = str(self.ui.linear_operation_lineEdit_2.text()).strip()

        operation_to_eval = f"{input_parameter}"
        if value_1:
            operation_to_eval += f" {math_1} {float(value_1)}"
        if value_2:
            operation_to_eval += f" {math_2} {float(value_2)}"

        result = eval(operation_to_eval)
        self.ui.linear_operation_value_after.setText("{}".format(result))

    def linear_operation_combobox_changed(self, new_string=None):
        self.linear_operation_lineedit_changed()

    def ok_clicked(self):
        index_selected = self.ui.select_metadata_combobox.currentIndex()
        self.save_parameters()
        self.parent.metadata_list_changed(index=index_selected, column=self.column)
        self.close()

    def cancel_clicked(self):
        self.close()

    def save_parameters(self):
        first_part_of_string_to_remove = str(self.ui.first_part_lineEdit.text())
        last_part_of_string_to_remove = str(self.ui.second_part_lineEdit.text())

        math_1 = str(self.ui.linear_operation_comboBox_1.currentText())
        math_2 = str(self.ui.linear_operation_comboBox_2.currentText())
        if self.is_linear_operation_is_valid():
            value_1 = str(self.ui.linear_operation_lineEdit_1.text()).strip()
            value_2 = str(self.ui.linear_operation_lineEdit_2.text()).strip()
        else:
            value_1 = ""
            value_2 = ""

        self.parent.metadata_operation = {"first_part_of_string_to_remove": first_part_of_string_to_remove,
                                          "last_part_of_string_to_remove": last_part_of_string_to_remove,
                                          "math_1": math_1,
                                          "value_1": value_1,
                                          "math_2": math_2,
                                          "value_2": value_2,
                                          }

    def is_before_linear_operation_is_valid(self):
        string_to_check = str(self.ui.linear_operation_value_before.text())
        enable_linear_operation_widgets = True
        try:
            float(string_to_check)
        except ValueError:
            enable_linear_operation_widgets = False

        return enable_linear_operation_widgets

    def check_if_before_linear_operation_valid(self):
        enable_linear_operation_widgets = self.is_before_linear_operation_is_valid()
        self.ui.linear_operation_groupBox.setEnabled(enable_linear_operation_widgets)

    def is_linear_operation_is_valid(self):

        def result_of_checking_operation(ui=None):
            is_error_in_operation = False
            operation = str(ui.text()).strip()
            if operation:
                try:
                    float(operation)
                except ValueError:
                    is_error_in_operation = True
            return is_error_in_operation

        is_error_operation_1 = result_of_checking_operation(ui=self.ui.linear_operation_lineEdit_1)
        is_error_operation_2 = result_of_checking_operation(ui=self.ui.linear_operation_lineEdit_2)

        self.ui.error_label_1.setVisible(is_error_operation_1)
        self.ui.error_label_2.setVisible(is_error_operation_2)

        if is_error_operation_1 or is_error_operation_2:
            self.ui.linear_operation_value_after.setText("N/A")
            return False
        else:
            return True
