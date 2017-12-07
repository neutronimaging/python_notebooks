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
from NeuNorm.normalization import Normalization


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

        self.o_norm = Normalization()
        self.o_norm.load(file=list_images, notebook=True)

        self.nbr_files = len(list_images)
        [self.images_dimension['height'], self.images_dimension['width']] = \
            np.shape(self.o_norm.data['sample']['data'][0])
        self.working_data = np.squeeze(self.o_norm.data['sample']['data'])
        self.list_images = list_images
