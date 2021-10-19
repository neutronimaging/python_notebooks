import numpy as np
import os
from qtpy.QtWidgets import QHBoxLayout, QCheckBox, QSpacerItem, QSizePolicy, QWidget, QMenu, QFileDialog
from qtpy.QtWidgets import QApplication
from qtpy import QtCore, QtGui
from qtpy.QtGui import QIcon
import pyqtgraph as pg
import json
import copy

from __code._utilities.table_handler import TableHandler
from __code._utilities.widgets_handler import WidgetsHandler
from __code.panoramic_stitching.get import Get
from __code.panoramic_stitching.image_handler import ImageHandler
from __code.panoramic_stitching import config_buttons as config
from __code.panoramic_stitching.utilities import make_full_file_name_to_static_folder_of
from __code.panoramic_stitching.gui_handler import GuiHandler
from __code.panoramic_stitching.status_message_config import StatusMessageStatus, show_status_message
from __code.panoramic_stitching.gui_initialization import GuiInitialization


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def save_table_offset_of_this_cell(self, row=-1, column=-1, state=-1):
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)

        file_name = o_table.get_item_str_from_cell(row=row, column=0)

        o_get = Get(parent=self.parent)
        folder_selected = o_get.get_combobox_folder_selected()

        offset_dictionary = self.parent.offset_dictionary
        if (column == 1) or (column == 2):
            offset_value = np.int(o_table.get_item_str_from_cell(row=row, column=column))

        if column == 1:
            offset_dictionary[folder_selected][file_name]['xoffset'] = offset_value
        elif column == 2:
            offset_dictionary[folder_selected][file_name]['yoffset'] = offset_value
        elif column == 3:
            is_visible = True if state == 2 else False
            offset_dictionary[folder_selected][file_name]['visible'] = is_visible
        self.parent.offset_dictionary = offset_dictionary

    def list_folder_combobox_value_changed(self, new_folder_selected=None):

        self.parent.ui.tableWidget.blockSignals(True)

        update_image = True
        if new_folder_selected is None:
            update_image = False
            new_folder_selected = self.parent.ui.list_folders_combobox.currentText()

        group_name = os.path.basename(new_folder_selected)
        group_offset_dictionary = self.parent.offset_dictionary[group_name]

        list_files = list(self.parent.data_dictionary[group_name].keys())
        list_files.sort()

        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        o_table.remove_all_rows()

        editable_columns_boolean = [False, True, True, True]

        for _row_index, _file in enumerate(list_files):

            o_table.insert_empty_row(_row_index)

            offset_file_entry = group_offset_dictionary[_file]

            xoffset = offset_file_entry['xoffset']
            yoffset = offset_file_entry['yoffset']
            list_items = [_file, xoffset, yoffset]

            for _column_index, _text in enumerate(list_items):

                if _row_index == 0:
                    editable_flag = False
                else:
                    editable_flag = editable_columns_boolean[_column_index]

                o_table.insert_item(row=_row_index,
                                    column=_column_index,
                                    value=_text,
                                    editable=editable_flag)

            # checkbox to turn on/off visibility of the row
            hori_layout = QHBoxLayout()
            spacer_item_left = QSpacerItem(408, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
            hori_layout.addItem(spacer_item_left)
            check_box = QCheckBox()
            if offset_file_entry['visible']:
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

        o_pano = ImageHandler(parent=self.parent)
        if update_image:
            o_pano.update_current_panoramic_image()
        o_pano.update_contour_plot()

        self.check_status_of_from_to_checkbox()

        self.parent.ui.tableWidget.blockSignals(False)

    def check_status_of_from_to_checkbox(self):
        state = self.parent.ui.from_to_checkbox.isChecked()
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        row_selected = o_table.get_row_selected()

        if state is False:
            self.parent.ui.from_to_button.setEnabled(False)
            self.parent.ui.from_to_error_label.setVisible(False)
            if self.parent.remote_control_id:
                self.parent.remote_control_id.ui.move_active_image_pushButton.setEnabled(False)
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
        self.parent.ui.from_to_button.setEnabled(False)
        QApplication.processEvents()

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

        current_xoffset_of_selected_row = np.int(o_table.get_item_str_from_cell(row=row_selected, column=1))
        new_xoffset = np.int(current_xoffset_of_selected_row - delta_x)
        self.parent.ui.tableWidget.item(row_selected, 1).setText(str(new_xoffset))
        self.save_table_offset_of_this_cell(row=row_selected, column=1)

        current_yoffset_of_selected_row = np.int(o_table.get_item_str_from_cell(row=row_selected, column=2))
        new_yoffset = current_yoffset_of_selected_row - delta_y
        self.parent.ui.tableWidget.item(row_selected, 2).setText(str(new_yoffset))
        self.save_table_offset_of_this_cell(row=row_selected, column=2)

        self.parent.ui.tableWidget.blockSignals(False)

        o_pano = ImageHandler(parent=self.parent)
        o_pano.update_current_panoramic_image()
        o_pano.update_contour_plot()
        o_pano.update_validity_of_from_to_button()

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
            #self.parent.horizontal_profile_plot.draw()

    def horizontal_slider_width_changed(self, width=1):
        self.parent.horizontal_profile['width'] = width
        length, _ = self.parent.horizontal_profile['id'].size()
        self.parent.horizontal_profile['id'].setSize((length, width))
        self.parent.horizontal_profile_changed()

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
            #self.parent.vertical_profile_plot.draw()

    def vertical_slider_width_changed(self, width=1):
        self.parent.vertical_profile['width'] = width
        _, length = self.parent.vertical_profile['id'].size()
        self.parent.vertical_profile['id'].setSize((width, length))
        self.parent.vertical_profile_changed()

    def manual_offset_changed(self, direction='horizontal', nbr_pixel=1):
        """
        apply in the select row the value of the pixel offset
        :param:
        change_direction: 'horizontal' or 'vertical'
        nbr_pixel: 1 by default, but can be any negative or positive values
        """
        column = 1 if direction == 'horizontal' else 2

        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        row_selected = o_table.get_row_selected()
        current_offset = o_table.get_item_str_from_cell(row=row_selected, column=column)

        new_offset = np.int(current_offset) + nbr_pixel
        o_table.set_item_with_str(row=row_selected, column=column, cell_str=str(new_offset))

        self.parent.table_of_offset_cell_changed(row_selected, column)

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

    def table_right_click(self):
        top_menu = QMenu(self.parent)

        load_table = top_menu.addAction("Load ...")
        save_as_table = top_menu.addAction("Save as ...")
        if self.parent.save_as_table_file_name == "":
            state = False
            button_name = "Save"
        else:
            base_name = os.path.basename(self.parent.save_as_table_file_name)
            button_name = f"Save ({base_name})"
            state = True
        save_table = top_menu.addAction(button_name)
        save_table.setEnabled(state)

        top_menu.addSeparator()
        reset_table = top_menu.addAction("Reset")

        action = top_menu.exec_(QtGui.QCursor.pos())

        if action == load_table:
            self.load_table()
        elif action == save_as_table:
            self.export_table()
        elif action == save_table:
            self.export_table(table_file_name=self.parent.save_as_table_file_name )
        elif action == reset_table:
            self.reset_table()

    def load_table(self):
        table_file_name = QFileDialog.getOpenFileName(self.parent,
                                                      directory=self.parent.working_dir,
                                                      caption="Select table file ...",
                                                      filter="Table (*.json)",
                                                      initialFilter="Table")
        QApplication.processEvents()
        table_file_name = table_file_name[0]

        if table_file_name:

            with open(table_file_name, "r") as read_file:
                table_data = json.load(read_file)

            o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
            table_ui_nbr_row = o_table.row_count()
            input_table_nbr_row = len(table_data.keys())

            if table_ui_nbr_row != input_table_nbr_row:
                show_status_message(parent=self.parent,
                                    message=f"Size of table and loaded file DO NOT MATCH!",
                                    status=StatusMessageStatus.error,
                                    duration_s=10)
                return

            WidgetsHandler.block_signals(ui=o_table.table_ui,
                                         status=True)

            for _row in np.arange(table_ui_nbr_row):
                xoffset, yoffset = table_data[str(_row)]
                o_table.set_item_with_str(row=_row,
                                          column=1,
                                          cell_str=xoffset)
                self.save_table_offset_of_this_cell(_row, 1)
                o_table.set_item_with_str(row=_row,
                                          column=2,
                                          cell_str=yoffset)
                self.save_table_offset_of_this_cell(_row, 2)
                QApplication.processEvents()

            WidgetsHandler.block_signals(ui=o_table.table_ui,
                                         status=False)

            o_pano = ImageHandler(parent=self.parent)
            o_pano.update_current_panoramic_image()
            o_pano.update_contour_plot()

            self.parent.horizontal_profile_changed()
            self.parent.vertical_profile_changed()

            show_status_message(parent=self.parent,
                                message=f"Loaded {table_file_name} ...",
                                status=StatusMessageStatus.ready,
                                duration_s=10)

    def reset_table(self):
        self.offset_dictionary = copy.deepcopy(self.parent.offset_dictionary_for_reset)

        o_init = GuiInitialization(parent=self)
        o_init.after_loading_data()

        self.check_status_of_from_to_checkbox()

        o_image = ImageHandler(parent=self)
        o_image.update_current_panoramic_image()
        o_image.update_contour_plot()

    def export_table(self, table_file_name=""):
        if table_file_name == "":
            table_file_name = QFileDialog.getSaveFileName(self.parent,
                                                          caption="Enter or select file name to export table data ...",
                                                          directory=self.parent.working_dir,
                                                          filter="Table (*.json);;All (*.*)",
                                                          initialFilter="Table")
            QApplication.processEvents()
            table_file_name = table_file_name[0]

        if table_file_name:
            table_dict = self.make_table_dict()
            with open(table_file_name, 'w') as json_file:
                json.dump(table_dict, json_file)

            show_status_message(parent=self.parent,
                                message=f"Table saved in {table_file_name}",
                                status=StatusMessageStatus.ready,
                                duration_s=10)

            self.parent.save_as_table_file_name = table_file_name
            self.parent.ui.actionSave_Table.setEnabled(True)
            self.parent.ui.actionSave_Table.setText(f"Save ({os.path.basename(table_file_name)})")

    def make_table_dict(self):
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        nbr_row = o_table.row_count()
        nbr_column = 2
        my_dictionary = {}
        for _row in np.arange(nbr_row):
            local_list = [o_table.get_item_str_from_cell(_row, _column)
                          for _column in (np.arange(nbr_column)+1)]
            my_dictionary[str(_row)] = local_list
        return my_dictionary

    def update_remote_ui(self):
        if self.parent.remote_control_id:
            self.parent.remote_control_id.check_previous_next_buttons_status()

    @staticmethod
    def button_pressed(ui=None, name='left'):
        full_file = make_full_file_name_to_static_folder_of(config.button[name]['pressed'])
        ui.setIcon(QIcon(full_file))

    @staticmethod
    def button_released(ui=None, name='left'):
        full_file = make_full_file_name_to_static_folder_of(config.button[name]['released'])
        ui.setIcon(QIcon(full_file))


