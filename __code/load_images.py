from ipywidgets import widgets
from IPython.core.display import HTML
from IPython.display import display
import ipywe.fileselector

import numpy as np
import os

try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication

from __code import file_handler


class LoadImages(object):

    nbr_files = 0
    images_dimension = {'height': 0,
                        'width': 0}

    working_data = []
    working_dir = ''
    list_images = []

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def select_images(self):
        display(HTML('<span style="font-size: 20px; color:blue">Select the images you want to work on!</span>'))
        self.list_images_ui = ipywe.fileselector.FileSelectorPanel(instruction='Select Images...',
                                                              multiple=True,
                                                              start_dir = self.working_dir)
        self.list_images_ui.show()

    def load_images(self):
        list_images = self.list_images_ui.selected

        if list_images:

            w = widgets.IntProgress()
            w.max = len(list_images)
            display(w)

            working_data = []
            for _index, _file in enumerate(list_images):
                _data = np.array(file_handler.load_data(_file))
                _data[_data == np.inf] = np.NaN  # removing inf values
                _data[np.isnan(_data)] = 0
                working_data.append(_data)
                w.value = _index + 1

            if len(np.shape(working_data)) < 3:
                raise ValueError("Check the Input Files! (no data loaded)")

            [self.nbr_files, self.images_dimension['height'], self.images_dimension['width']] = np.shape(working_data)
            self.working_data = np.squeeze(working_data)
            self.working_dir = os.path.dirname(list_images[0])
            self.list_images = list_images