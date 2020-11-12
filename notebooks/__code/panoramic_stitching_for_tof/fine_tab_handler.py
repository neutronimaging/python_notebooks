from qtpy.QtWidgets import QHBoxLayout, QCheckBox, QSpacerItem, QSizePolicy, QWidget
from qtpy import QtCore

from __code._utilities.table_handler import TableHandler
from __code.panoramic_stitching_for_tof.image_handler import ImageHandler


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

    def check_status_of_from_to_checkbox(self):
        state = self.parent.ui.from_to_checkbox.isChecked()
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        row_selected = o_table.get_row_selected()

        if state is False:
            self.parent.ui.from_to_button.setEnabled(False)
            self.parent.ui.from_to_error_label.setVisible(False)
        else:
            if row_selected == 0:
                state = False
            self.parent.ui.from_to_button.setEnabled(state)
            self.parent.ui.from_to_error_label.setVisible(not state)
            if state:
                o_image = ImageHandler(parent=self.parent)
                o_image.update_validity_of_from_to_button()

        o_image = ImageHandler(parent=self.parent)
        o_image.update_from_to_roi(state=state)

        if row_selected == 0:
            state_button = False
        else:
            state_button = True
        self.enabled_all_manual_widgets(state=state_button)

    def enabled_all_manual_widgets(self, state=True):
        list_ui = [self.parent.ui.left_button,
                   self.parent.ui.left_left_button,
                   self.parent.ui.right_button,
                   self.parent.ui.right_right_button,
                   self.parent.ui.up_button,
                   self.parent.ui.up_up_button,
                   self.parent.ui.down_button,
                   self.parent.ui.down_down_button]
        for _ui in list_ui:
            _ui.setEnabled(state)
