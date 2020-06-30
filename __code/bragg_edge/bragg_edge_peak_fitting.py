from IPython.core.display import HTML
import os
import random
import numpy as np
from IPython.display import display
import pyqtgraph as pg
from qtpy.QtWidgets import QMainWindow
from qtpy import QtGui

# try:
#     from PyQt4.QtGui import QFileDialog
#     from PyQt4 import QtCore, QtGui
#     from PyQt4.QtGui import QMainWindow
# except ImportError:
#     from PyQt5.QtWidgets import QFileDialog
#     from PyQt5 import QtCore, QtGui
#     from PyQt5.QtWidgets import QApplication, QMainWindow

from neutronbraggedge.experiment_handler import *

from __code.bragg_edge.bragg_edge_normalization import BraggEdge as BraggEdgeParent
from __code.bragg_edge.peak_fitting_interface_initialization import Initialization
from __code import load_ui


DEBUGGING = True


class BraggEdge(BraggEdgeParent):

   pass



class Interface(QMainWindow):

    bragg_edge_range = [5, 20]

    def __init__(self, parent=None, o_norm=None, spectra_file=None):

        self.o_norm = o_norm
        self.spectra_file = spectra_file

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
        self.load_time_spectra()
        self.roi_moved()

    def load_time_spectra(self):
        _tof_handler = TOF(filename=self.spectra_file)
        _exp = Experiment(tof=_tof_handler.tof_array,
                          distance_source_detector_m=np.float(self.ui.distance_detector_sample.text()),
                          detector_offset_micros=np.float(self.ui.detector_offset.text()))
        self.lambda_array = _exp.lambda_array * 1e10  # to be in Angstroms
        self.tof_array = _tof_handler.tof_array

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

    @staticmethod
    def check_size(x_axis=None, y_axis=None):
        size_x = len(x_axis)
        size_y = len(y_axis)
        min_len = np.min([size_x, size_y])
        return x_axis[:min_len], y_axis[:min_len]

    def roi_moved(self):
        profile = self.get_profile_of_roi()
        tof_array = self.tof_array * 1e6  # to be in microS
        x_axis, y_axis = Interface.check_size(x_axis=tof_array,
                                              y_axis=profile)
        self.ui.profile.clear()
        self.ui.profile.plot(x_axis, y_axis)
        self.ui.profile.setLabel("bottom", u"TOF (\u00B5s)")
        self.ui.profile.setLabel("left", 'Mean counts')

        bragg_edge_range = pg.LinearRegionItem(values=self.bragg_edge_range,
                                               orientation=None,
                                               brush=None,
                                               movable=True,
                                               bounds=None)
        bragg_edge_range.sigRegionChanged.connect(self.bragg_edge_range_changed)
        bragg_edge_range.setZValue(-10)
        self.ui.profile.addItem(bragg_edge_range)

    def bragg_edge_range_changed(self):
        pass

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
    def distance_detector_sample_changed(self):
        pass

    def detector_offset_changed(self):
        pass

    def selection_axis_index_changed(self):
        pass
    
    def selection_axis_tof_changed(self):
        pass
    
    def selection_axis_lambda_changed(self):
        pass

    def fitting_axis_index_changed(self):
        pass

    def fitting_axis_tof_changed(self):
        pass

    def fitting_axis_lambda_changed(self):
        pass

    def cancel_clicked(self):
        self.close()

    def apply_clicked(self):
        # FIXME
        self.close()
        
        
