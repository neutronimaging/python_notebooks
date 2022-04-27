from qtpy.QtWidgets import QMainWindow
from qtpy.QtGui import QIcon
from qtpy import QtCore, QtGui
import os

from __code import load_ui


class RepeatWidgetChangeDialog(QMainWindow):

    def __init__(self, parent=None):

        self.grand_parent = parent
        super(RepeatWidgetChangeDialog, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_grating_excel_widget_dialog.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)

        self.init_widgets()

    def init_widgets(self):
        
        statis_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
        self.do_not_repeat_released_file = os.path.join(statis_file_path, "do_not_repeat_button_released.png")
        self.do_not_repeat_pressed_file = os.path.join(statis_file_path, "do_not_repeat_button_pressed.png")
        self.repeat_released_file = os.path.join(statis_file_path, "repeat_off.png")
        self.repeat_pressed_file = os.path.join(statis_file_path, "repeat_on.png")

        no_repeat_icon = QIcon(self.do_not_repeat_released_file)
        self.ui.do_not_repeat_pushButton.setIcon(no_repeat_icon)
        self.ui.do_not_repeat_pushButton.setIconSize(QtCore.QSize(204, 198))

        repeat_icon = QIcon(self.repeat_released_file)
        self.ui.repeat_pushButton.setIcon(repeat_icon)
        self.ui.repeat_pushButton.setIconSize(QtCore.QSize(204, 198))

    def do_not_repeat_pressed(self):
        no_repeat_icon = QIcon(self.do_not_repeat_pressed_file)
        self.ui.do_not_repeat_pushButton.setIcon(no_repeat_icon)

    def do_not_repeat_released(self):
        no_repeat_icon = QIcon(self.do_not_repeat_released_file)
        self.ui.do_not_repeat_pushButton.setIcon(no_repeat_icon)

    def repeat_pressed(self):
        pass

    def repeat_released(self):
        pass