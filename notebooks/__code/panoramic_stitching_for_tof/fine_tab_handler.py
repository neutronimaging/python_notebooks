from qtpy.QtWidgets import QHBoxLayout, QCheckBox, QSpacerItem, QSizePolicy, QWidget
from qtpy import QtCore
import numpy as np
import pyqtgraph as pg

from __code._utilities.table_handler import TableHandler
from __code.panoramic_stitching_for_tof.image_handler import ImageHandler
from __code.panoramic_stitching_for_tof.event_handler import TOFEventHandler
from __code.panoramic_stitching.gui_handler import GuiHandler


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

    def roi_box_changed(self, roi_id=None, ):
        region = roi_id.getArraySlice(self.parent.current_live_image,
                                      self.parent.ui.image_view.imageItem)

        x0 = region[0][0].start
        y0 = region[0][1].start

        return {'x': x0, 'y': y0}

    def from_roi_box_changed(self):
        self.parent.from_roi = self.roi_box_changed(roi_id=self.parent.from_roi_id)
        o_image = ImageHandler(parent=self.parent)
        o_image.update_from_cross_line()
        o_image.update_from_label()
        o_image.update_validity_of_from_to_button()

    def to_roi_box_changed(self):
        self.parent.to_roi = self.roi_box_changed(roi_id=self.parent.to_roi_id)
        o_image = ImageHandler(parent=self.parent)
        o_image.update_to_cross_line()
        o_image.update_to_label()

    def from_to_button_pushed(self):
        self.parent.ui.tableWidget.blockSignals(True)

        from_roi = self.parent.from_roi
        to_roi = self.parent.to_roi

        from_x = from_roi['x']
        to_x = to_roi['x']
        delta_x = from_x - to_x

        from_y = from_roi['y']
        to_y = to_roi['y']
        delta_y = from_y - to_y

        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        row_selected = o_table.get_row_selected()

        current_xoffset_of_selected_row = int(o_table.get_item_str_from_cell(row=row_selected, column=1))
        new_xoffset = int(current_xoffset_of_selected_row - delta_x)
        self.parent.ui.tableWidget.item(row_selected, 1).setText(str(new_xoffset))
        o_event = TOFEventHandler(parent=self.parent)
        o_event.save_table_offset_of_this_cell(row=row_selected, column=1)

        current_yoffset_of_selected_row = int(o_table.get_item_str_from_cell(row=row_selected, column=2))
        new_yoffset = current_yoffset_of_selected_row - delta_y
        self.parent.ui.tableWidget.item(row_selected, 2).setText(str(new_yoffset))
        o_event.save_table_offset_of_this_cell(row=row_selected, column=2)

        self.parent.ui.tableWidget.blockSignals(False)

        o_pano = ImageHandler(parent=self.parent)
        o_pano.update_current_panoramic_image()
        o_pano.update_contour_plot()

    def horizontal_profile(self, enabled=True):
        o_gui = GuiHandler(parent=self.parent)
        o_gui.enabled_horizontal_profile_widgets(enabled=enabled)

        horizontal_profile = self.parent.horizontal_profile

        if enabled:
            if horizontal_profile['id']:
                self.parent.ui.image_view.addItem(horizontal_profile['id'])
            else:
                x0 = horizontal_profile['x0']
                x1 = horizontal_profile['x1']
                y = horizontal_profile['y']
                width = horizontal_profile['width']

                roi = pg.ROI([x0, y], [x1-x0, width])
                roi.addScaleHandle([0.5, 0], [0, 0])
                self.parent.ui.image_view.addItem(roi)
                self.parent.horizontal_profile['id'] = roi
                roi.sigRegionChanged.connect(self.parent.horizontal_profile_changed)

            self.parent.horizontal_profile_changed()

        else:
            if horizontal_profile['id']:
                self.parent.ui.image_view.removeItem(horizontal_profile['id'])
            self.parent.horizontal_profile_plot.axes.clear()
            self.parent.horizontal_profile_plot.draw()

    def vertical_profile(self, enabled=True):
        o_gui = GuiHandler(parent=self.parent)
        o_gui.enabled_vertical_profile_widgets(enabled=enabled)

        vertical_profile = self.parent.vertical_profile
        if enabled:
            if vertical_profile['id']:
                self.parent.ui.image_view.addItem(vertical_profile['id'])
            else:
                x = vertical_profile['x']
                y0 = vertical_profile['y0']
                y1 = vertical_profile['y1']
                width = vertical_profile['width']

                roi = pg.ROI([x, y0], [width, y1-y0])
                roi.addScaleHandle([0, 0.5], [0, 0])
                self.parent.ui.image_view.addItem(roi)
                self.parent.vertical_profile['id'] = roi
                roi.sigRegionChanged.connect(self.parent.vertical_profile_changed)

            self.parent.vertical_profile_changed()

        else:
            if vertical_profile['id']:
                self.parent.ui.image_view.removeItem(vertical_profile['id'])
            self.parent.vertical_profile_plot.axes.clear()
            self.parent.vertical_profile_plot.draw()
