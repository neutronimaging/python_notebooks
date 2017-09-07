#from ipywidgets.widgets import interact
from ipywidgets import widgets
from IPython.core.display import HTML
from IPython.display import display

import numpy as np
import os

from __code import file_handler
from __code import gui_widgets


class RadialProfile(object):

    nbr_files = 0
    images_dimension = {'height': 0,
                        'width': 0}

    working_data = []
    working_dir = ''
    list_images = []

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def import_images(self):
        display(HTML('<span style="font-size: 20px; color:blue">Select the images you want to work on!</span>'))
        list_images = gui_widgets.gui_fimage(dir = self.working_dir)
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

            [self.nbr_files, self.images_dimension['height'], self.images_dimension['width']] = np.shape(working_data)
            self.working_data = np.squeeze(working_data)
            self.working_dir = os.path.dirname(list_images[0])
            self.list_images = list_images