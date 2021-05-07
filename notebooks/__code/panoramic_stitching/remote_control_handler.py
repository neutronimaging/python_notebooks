from qtpy.QtWidgets import QMainWindow
import os
from qtpy.QtGui import QIcon

from notebooks.__code import load_ui

from __code.panoramic_stitching.utilities import make_full_file_name_to_static_folder_of, set_widget_size
from __code.panoramic_stitching.config_buttons import button
from __code.panoramic_stitching.event_handler import EventHandler


class RemoteControlHandler:

    def __init__(self, parent=None):

        if parent.remote_control_id is None:
            parent.remote_control_id = RemoteControlWindow(parent=parent)
            parent.remote_control_id.show()
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
        self.setWindowTitle("Remonte control")

        self.initialize_widget()

    def initialize_widget(self):
        _file_path = os.path.dirname(__file__)
        bring_to_focus_released = make_full_file_name_to_static_folder_of(button['bring_to_focus']['released'])
        self.ui.bring_to_focus.setIcon(QIcon(bring_to_focus_released))
        set_widget_size(widget=self.ui.bring_to_focus, width=500, height=203)

    def bring_to_focus_pressed(self):
        EventHandler.button_pressed(ui=self.ui.bring_to_focus, name='bring_to_focus')

    def bring_to_focus_released(self):
        EventHandler.button_released(ui=self.ui.bring_to_focus, name='bring_to_focus')

    def closeEvent(self, c):
        self.parent.remote_control_id = None
