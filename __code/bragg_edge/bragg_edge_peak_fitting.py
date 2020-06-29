from IPython.core.display import HTML
import os
import random
import numpy as np
from IPython.display import display
try:
    from PyQt4.QtGui import QFileDialog
    from PyQt4 import QtCore, QtGui
    from PyQt4.QtGui import QMainWindow
except ImportError:
    from PyQt5.QtWidgets import QFileDialog
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow

from __code.bragg_edge.bragg_edge_normalization import BraggEdge as BraggEdgeParent
from __code.bragg_edge.peak_fitting_interface_initialization import Initialization
from __code import load_ui

DEBUGGING = True


class BraggEdge(BraggEdgeParent):

   pass



class Interface(QMainWindow):

    histogram_level = []

    def __init__(self, parent=None, o_norm=None):

        self.o_norm = o_norm

        display(HTML('<span style="font-size: 20px; color:blue">Check UI that poped up \
            (maybe hidden behind this browser!)</span>'))

        super(Interface, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    os.path.join('ui',
                                                 'ui_bragg_edge_peak_fitting.ui'))

        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Peak Fitting Tool")

        # initialization
        o_init = Initialization(parent=self)
        o_init.display(image=self.get_live_image())

    def get_live_image(self):
        if DEBUGGING:
            final_array = self.o_norm.data['sample']['data']
        else:
            nbr_data_to_use = np.int(self.number_of_data_to_use_ui.value)

            _data = self.o_norm.data['sample']['data']

            nbr_images = len(_data)
            list_of_indexes_to_keep = random.sample(list(range(nbr_images)), nbr_data_to_use)

            final_array = []
            for _index in list_of_indexes_to_keep:
                final_array.append(_data[_index])

        final_image = np.mean(final_array, axis=0)
        self.final_image = final_image
        return final_image

    def roi_moved(self):
        profile = self.get_profile_of_roi()
        self.ui.profile.clear()
        self.ui.profile.plot(profile)

    def get_profile_of_roi(self):
        roi_id = self.roi_id
        region = roi_id.getArraySlice(self.final_image,
                                      self.ui.image_view.imageItem)

        x0 = region[0][0].start
        x1 = region[0][0].stop
        y0 = region[0][1].start
        y1 = region[0][1].stop

        profile_value = []
        for _image in self.o_norm.data['sample']['data']:
            _value = np.mean(_image[y0:y1, x0:x1])
            profile_value.append(_value)

        return profile_value

    # event handler
    def cancel_clicked(self):
        self.close()

    def apply_clicked(self):
        # FIXME
        self.close()
