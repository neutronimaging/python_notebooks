from qtpy.QtWidgets import QMainWindow
import os
from qtpy.QtGui import QIcon
import numpy as np

from notebooks.__code import load_ui

from __code.panoramic_stitching.utilities import make_full_file_name_to_static_folder_of, set_widget_size
from __code.panoramic_stitching.config_buttons import button
from __code.panoramic_stitching.event_handler import EventHandler
from __code.panoramic_stitching.image_handler import ImageHandler
from __code._utilities.table_handler import TableHandler

BORDER_RANGE = 50


class RemoteControlHandler:

    def __init__(self, parent=None):

        if parent.remote_control_id is None:
            parent.remote_control_id = RemoteControlWindow(parent=parent)
            parent.remote_control_id.show()
            parent.ui.remote_control_widget.setEnabled(False)
        else:
            parent.remote_control_id.setFocus()
            parent.remote_control_id.activateWindow()


class RemoteControlWindow(QMainWindow):

    def __init__(self, parent=None):
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui', 'ui_panoramic_remote_control.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Remote control")
        self.initialize_widget()

    def initialize_widget(self):
        _file_path = os.path.dirname(__file__)
        bring_to_focus_released = make_full_file_name_to_static_folder_of(button['bring_to_focus']['released'])
        self.ui.bring_to_focus.setIcon(QIcon(bring_to_focus_released))
        set_widget_size(widget=self.ui.bring_to_focus, width=500, height=203)

        self.check_previous_next_buttons_status()

    def check_previous_next_buttons_status(self):
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        current_row_selected = o_table.get_row_selected()
        number_of_rows = o_table.row_count()

        self.ui.previous_pushButton.setEnabled(True)
        self.ui.next_pushButton.setEnabled(True)
        if current_row_selected == 0:
            self.ui.previous_pushButton.setEnabled(False)
        if current_row_selected == (number_of_rows-1):
            self.ui.next_pushButton.setEnabled(False)

    def bring_to_focus_pressed(self):
        EventHandler.button_pressed(ui=self.ui.bring_to_focus, name='bring_to_focus')
        self.bring_to_focus_method()

    def bring_to_focus_released(self):
        EventHandler.button_released(ui=self.ui.bring_to_focus, name='bring_to_focus')

    def closeEvent(self, c):
        self.parent.ui.remote_control_widget.setEnabled(True)
        self.parent.remote_control_id = None

    # handling
    def bring_to_focus_method(self):
        _view = self.parent.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        [[x0, x1], [y0, y1]] = _state['viewRange']

        # horizontal profile
        horizontal_profile = self.parent.horizontal_profile
        if horizontal_profile['id']:
            self.parent.ui.image_view.removeItem(horizontal_profile['id'])
            horizontal_profile['id'] = None

        length = np.int(x1 - x0)/2
        horizontal_profile['x0'] = x0 + BORDER_RANGE
        horizontal_profile['x1'] = horizontal_profile['x0'] + length
        horizontal_profile['y'] = y0 + BORDER_RANGE
        self.parent.horizontal_profile = horizontal_profile

        is_horizontal_profile_enabled = self.parent.ui.enable_horizontal_profile_checkbox.isChecked()

        o_event = EventHandler(parent=self.parent)
        o_event.horizontal_profile(enabled=is_horizontal_profile_enabled)

        # vertical profile
        vertical_profile = self.parent.vertical_profile
        if vertical_profile['id']:
            self.parent.ui.image_view.removeItem(vertical_profile['id'])
            vertical_profile['id'] = None

        length = np.int(y1 - y0)/2
        vertical_profile['y0'] = y0 + BORDER_RANGE
        vertical_profile['y1'] = vertical_profile['y0'] + length
        vertical_profile['x'] = x0 + BORDER_RANGE
        self.parent.vertical_profile = vertical_profile

        is_vertical_profile_enabled = self.parent.ui.enable_vertical_profile_checkbox.isChecked()

        o_event = EventHandler(parent=self.parent)
        o_event.vertical_profile(enabled=is_vertical_profile_enabled)

        o_image_handler = ImageHandler(parent=self.parent)

        # from widgets
        from_roi = self.parent.from_roi
        from_roi['x'] = x0 + np.int((x1 - x0)/2)
        from_roi['y'] = np.int((y1 - y0)/3) + y0
        self.parent.from_roi = from_roi

        # to widgets
        to_roi = self.parent.to_roi
        to_roi['x'] = x0 + np.int((x1 - x0)/2)
        to_roi['y'] = 2 * np.int((y1 - y0)/3) + y0
        self.parent.to_roi = to_roi

        is_from_to_enabled = self.parent.ui.from_to_checkbox.isChecked()
        o_image_handler.update_from_to_roi(state=is_from_to_enabled)

    def previous_button_clicked(self):
        self._select_row(row_offset=-1)

    def next_button_clicked(self):
        self._select_row(row_offset=1)

    def _select_row(self, row_offset=1):
        o_table = TableHandler(table_ui=self.parent.ui.tableWidget)
        row_selected = o_table.get_row_selected()
        o_table.select_row(row_selected+row_offset)
