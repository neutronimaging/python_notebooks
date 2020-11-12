from qtpy.QtWidgets import QHBoxLayout, QCheckBox, QSpacerItem, QSizePolicy, QWidget
from qtpy import QtCore

from __code._utilities.table_handler import TableHandler


class FineTabHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def initialize_table_of_offset(self):
        self.parent.ui.tableWidget.blockSignals(True)

        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        o_table.remove_all_rows()

        editable_columns_boolean = [False, True, True, True]

        offset_dictionary = self.parent.offset_dictionary

        for _row_index, _folder in enumerate(offset_dictionary.keys()):
            o_table.insert_empty_row(row=_row_index)
            offset_entry = offset_dictionary[_folder]

            xoffset = offset_entry['xoffset']
            yoffset = offset_entry['yoffset']
            list_items = [_folder, xoffset, yoffset]

            for _column_index, _text in enumerate(list_items):

                if _row_index == 0:
                    editable_flag = False
                else:
                    editable_flag = editable_columns_boolean[_column_index]

                o_table.insert_item(row=_row_index,
                                    column=_column_index,
                                    value=_text,
                                    editable=editable_flag)

                # checkbox to turn on/off the visibility of the row
                hori_layout = QHBoxLayout()
                spacer_item_left = QSpacerItem(408, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
                hori_layout.addItem(spacer_item_left)
                check_box = QCheckBox()
                if offset_entry['visible']:
                    _state = QtCore.Qt.Checked
                else:
                    _state = QtCore.Qt.Unchecked
                check_box.setCheckState(_state)

                check_box.stateChanged.connect(lambda state=0, row=_row_index:
                                               self.parent.visibility_checkbox_changed(state=state,
                                                                                       row=row))
                hori_layout.addWidget(check_box)
                spacer_item_right = QSpacerItem(408, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
                hori_layout.addItem(spacer_item_right)
                cell_widget = QWidget()
                cell_widget.setLayout(hori_layout)
                o_table.insert_widget(row=_row_index,
                                      column=3,
                                      widget=cell_widget)

        o_table.select_row(0)
        self.parent.ui.tableWidget.blockSignals(False)
