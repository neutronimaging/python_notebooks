from qtpy.QtWidgets import QDialog
from qtpy.QtGui import QIcon
from qtpy import QtCore, QtGui
import os

from __code import load_ui


class RepeatWidgetChangeDialog(QDialog):

    def __init__(self, parent=None):

        self.grand_parent = parent
        super(RepeatWidgetChangeDialog, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_grating_excel_widget_dialog.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)

        # self.init_widgets()

    def init_widgets(self):
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static/")

        no_repeat_icon = QIcon()
        no_repeat_icon.addPixmap(QtGui.QPixmap(os.path.join(file_path, "do_no_repeat_off.png")), QtGui.QIcon.Active,
                               QtGui.QIcon.Off)
        no_repeat_icon.addPixmap(QtGui.QPixmap(os.path.join(file_path, "do_not_repeat_on.png")), QtGui.QIcon.Active,
                                 QtGui.QIcon.On)
        self.ui.do_not_repeat_pushButton.setIcon(no_repeat_icon)
        self.ui.do_not_repeat_pushButton.setStyleSheet("")
        self.ui.do_not_repeat_pushButton.setIconSize(QtCore.QSize(198, 204))

        repeat_icon = QIcon()
        repeat_icon.addPixmap(QtGui.QPixmap(os.path.join(file_path, "repeat_off.png")), QtGui.QIcon.Active,
                              QtGui.QIcon.Off)
        repeat_icon.addPixmap(QtGui.QPixmap(os.path.join(file_path, "repeat_on.png")), QtGui.QIcon.Active,
                              QtGui.QIcon.On)
        self.ui.repeat_pushButton.setIcon(repeat_icon)
        self.ui.repeat_pushButton.setIconSize(QtCore.QSize(198, 204))
        self.ui.repeat_pushButton.setStyleSheet("")
