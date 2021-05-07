from qtpy.QtWidgets import QMainWindow
import os

from notebooks.__code import load_ui


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

    def bring_to_focus_pressed(self):
        pass

    def bring_to_focus_released(self):
        pass

    def closeEvent(self, c):
        self.parent.remote_control_id = None
