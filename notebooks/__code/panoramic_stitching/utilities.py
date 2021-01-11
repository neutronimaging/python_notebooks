import os
from qtpy.QtCore import QSize


def make_full_file_name_to_static_folder_of(file_name):
    _file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    full_path_file = os.path.abspath(os.path.join(_file_path, file_name))
    return full_path_file


def set_widgets_size(widgets=[], width=10, height=10):
    for _widget in widgets:
        _widget.setIconSize(QSize(width, height))
