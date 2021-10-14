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

    def linear_operation_lineedit_changed(self, new_string):
        pass

    def linear_operation_combobox_changed(self, new_string):
        pass

    def ok_clicked(self):
        index_selected = self.ui.select_metadata_combobox.currentIndex()
        self.parent.metadata_list_changed(index=index_selected, column=self.column)
        self.close()

    def cancel_clicked(self):
        self.close()
