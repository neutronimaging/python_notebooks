from qtpy.QtWidgets import QMainWindow
from qtpy.QtGui import QIcon
from qtpy import QtCore
import os

from __code import load_ui
from __code.registration.get import Get


class ManualLauncher:
    parent = None

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.registration_tool_ui == None:
            tool_ui = Manual(parent=parent)
            tool_ui.show()
            self.parent.registration_tool_ui = tool_ui
        else:
            self.parent.registration_tool_ui.setFocus()
            self.parent.registration_tool_ui.activateWindow()


class Manual(QMainWindow):
    parent = None
    button_size = {'arrow'       : {'width' : 100,
                                    'height': 100},
                   'rotate'      : {'width' : 100,
                                    'height': 200},
                   'small_rotate': {'width' : 50,
                                    'height': 100},
                   }

    list_arrow_widgets = []
    list_rotate_widgets = []

    def __init__(self, parent=None):

        super(QMainWindow, self).__init__(parent)

        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_registration_tool.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.parent = parent
        self.setWindowTitle("Registration Tool")
        self.initialize_widgets()
        self.update_status_widgets()

    def initialize_widgets(self):
        _file_path = os.path.dirname(__file__)
        up_arrow_file = os.path.abspath(os.path.join(_file_path, '../static/up_arrow.png'))
        self.ui.up_button.setIcon(QIcon(up_arrow_file))

        down_arrow_file = os.path.abspath(os.path.join(_file_path, '../static/down_arrow.png'))
        self.ui.down_button.setIcon(QIcon(down_arrow_file))

        right_arrow_file = os.path.abspath(os.path.join(_file_path, '../static/right_arrow.png'))
        self.ui.right_button.setIcon(QIcon(right_arrow_file))

        left_arrow_file = os.path.abspath(os.path.join(_file_path, '../static/left_arrow.png'))
        self.ui.left_button.setIcon(QIcon(left_arrow_file))

        rotate_left_file = os.path.abspath(os.path.join(_file_path, '../static/rotate_left.png'))
        self.ui.rotate_left_button.setIcon(QIcon(rotate_left_file))

        rotate_right_file = os.path.abspath(os.path.join(_file_path, '../static/rotate_right.png'))
        self.ui.rotate_right_button.setIcon(QIcon(rotate_right_file))

        small_rotate_left_file = os.path.abspath(os.path.join(_file_path, '../static/small_rotate_left.png'))
        self.ui.small_rotate_left_button.setIcon(QIcon(small_rotate_left_file))

        small_rotate_right_file = os.path.abspath(os.path.join(_file_path, '../static/small_rotate_right.png'))
        self.ui.small_rotate_right_button.setIcon(QIcon(small_rotate_right_file))

        self.list_arrow_widgets = [self.ui.up_button,
                                   self.ui.down_button,
                                   self.ui.left_button,
                                   self.ui.right_button]
        self._set_widgets_size(widgets=self.list_arrow_widgets,
                               width=self.button_size['arrow']['width'],
                               height=self.button_size['arrow']['height'])

        self.list_rotate_widgets = [self.ui.rotate_left_button,
                                    self.ui.rotate_right_button]
        self._set_widgets_size(widgets=self.list_rotate_widgets,
                               width=self.button_size['rotate']['width'],
                               height=self.button_size['rotate']['height'])

        self.list_small_rotate_widgets = [self.ui.small_rotate_left_button,
                                          self.ui.small_rotate_right_button]
        self._set_widgets_size(widgets=self.list_small_rotate_widgets,
                               width=self.button_size['small_rotate']['width'],
                               height=self.button_size['small_rotate']['height'])

    def _set_widgets_size(self, widgets=[], width=10, height=10):
        for _widget in widgets:
            _widget.setIconSize(QtCore.QSize(width, height))

    def update_status_widgets(self):
        o_get = Get(parent=self.parent)
        list_row_selected = o_get.list_row_selected()
        _enabled = True

        if list_row_selected is None:
            _enabled = False

        elif not list_row_selected == []:
            if len(list_row_selected) == 1:
                if list_row_selected[0] == self.parent.reference_image_index:
                    _enabled = False

        for _widget in self.list_arrow_widgets:
            _widget.setEnabled(_enabled)

        for _widget in self.list_rotate_widgets:
            _widget.setEnabled(_enabled)

        for _widget in self.list_small_rotate_widgets:
            _widget.setEnabled(_enabled)

    def closeEvent(self, c):
        self.parent.set_widget_status(list_ui=[self.parent.ui.auto_registration_button,
                                               self.parent.ui.marker_registration_button,
                                               self.parent.ui.profiler_registration_button],
                                      enabled=True)
        self.parent.registration_tool_ui = None

    def modified_selected_images(self, motion=None, rotation=0.):
        # retrieve row selected and changed values
        self.parent.ui.tableWidget.blockSignals(True)

        o_get = Get(parent=self.parent)
        list_row_selected = o_get.list_row_selected()
        for _row in list_row_selected:

            # we never modified the reference image
            if _row == self.parent.reference_image_index:
                continue

            if motion:

                # left and right - > we works with xoffset, column 1
                if motion in ['left', 'right']:
                    _old_value = int(self.parent.ui.tableWidget.item(_row, 1).text())

                    if motion == 'left':
                        xoffset = -1
                    else:
                        xoffset = 1

                    _new_value = _old_value + xoffset
                    self.parent.ui.tableWidget.item(_row, 1).setText(str(_new_value))

                else:  # up and down -> yoffset, column 2

                    _old_value = int(self.parent.ui.tableWidget.item(_row, 2).text())

                    if motion == 'up':
                        yoffset = -1
                    else:
                        yoffset = 1

                    _new_value = _old_value + yoffset
                    self.parent.ui.tableWidget.item(_row, 2).setText(str(_new_value))

            if not rotation == 0:  # column 3

                _old_value = float(self.parent.ui.tableWidget.item(_row, 3).text())
                _new_value = _old_value + rotation
                self.parent.ui.tableWidget.item(_row, 3).setText("{:.2f}".format(_new_value))

        self.parent.ui.tableWidget.blockSignals(False)
        self.parent.table_cell_modified(-1, -1)

    # event handler
    def left_button_clicked(self):
        self.modified_selected_images(motion='left')

    def right_button_clicked(self):
        self.modified_selected_images(motion='right')

    def up_button_clicked(self):
        self.modified_selected_images(motion='up')

    def down_button_clicked(self):
        self.modified_selected_images(motion='down')

    def small_rotate_left_button_clicked(self):
        self.modified_selected_images(rotation=.1)

    def small_rotate_right_button_clicked(self):
        self.modified_selected_images(rotation=-.1)

    def rotate_left_button_clicked(self):
        self.modified_selected_images(rotation=1)

    def rotate_right_button_clicked(self):
        self.modified_selected_images(rotation=-1)
