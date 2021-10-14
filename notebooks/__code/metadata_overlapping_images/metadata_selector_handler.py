from qtpy.QtWidgets import QDialog
import os
import re

from __code import load_ui
from . import LIST_FUNNY_CHARACTERS


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
        self.check_linear_operation_is_valid()

    def initialization(self):
        list_metadata = self.parent.raw_list_metadata
        self.ui.select_metadata_combobox.addItems(list_metadata)

    def string_cleaning_changed(self, new_text):
        first_part_of_string_to_remove = str(self.ui.first_part_lineEdit.text())
        _clean_first_part = ""
        for _c in first_part_of_string_to_remove:
            if _c in LIST_FUNNY_CHARACTERS:
                _clean_first_part += "\{}".format(_c)
            else:
                _clean_first_part += "{}".format(_c)

        last_part_of_string_to_remove = str(self.ui.second_part_lineEdit.text())
        _clean_second_part = ""
        for _c in last_part_of_string_to_remove:
            if _c in LIST_FUNNY_CHARACTERS:
                _clean_second_part += "\{}".format(_c)
            else:
                _clean_second_part += "{}".format(_c)

        regular_expr = r"{}(.*){}".format(_clean_first_part, _clean_second_part)
        string_to_clean = self.ui.select_metadata_combobox.currentText()
        m = re.match(regular_expr, string_to_clean)
        if m and m.group(1):
            _new_str = m.group(1)
            self.ui.linear_operation_value_before.setText(_new_str)

        self.check_if_before_linear_operation_valid()
        self.linear_operation_lineedit_changed()

    def linear_operation_lineedit_changed(self, new_string=None):
        any_error_reported = self.check_linear_operation_is_valid()

        if any_error_reported:
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
        self.parent.metadata_list_changed(index=index_selected, column=self.column)
        self.close()

    def cancel_clicked(self):
        self.close()

    def check_if_before_linear_operation_valid(self):
        string_to_check = str(self.ui.linear_operation_value_before.text())

        enable_linear_operation_widgets = True
        try:
            float(string_to_check)
        except ValueError:
            enable_linear_operation_widgets = False
        self.ui.linear_operation_groupBox.setEnabled(enable_linear_operation_widgets)

    def check_linear_operation_is_valid(self):

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
            return True
        else:
            return False
