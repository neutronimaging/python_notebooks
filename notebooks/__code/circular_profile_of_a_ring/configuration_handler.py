import numpy as np
import json
from qtpy.QtWidgets import QFileDialog
import os


class ConfigurationHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def load(self):
        pass

    def save(self):
        default_file_name = os.path.abspath(os.path.basename(self.parent.working_dir)) + "_configuration.cfg"
        working_dir = os.path.dirname(self.parent.working_dir)
        directory = os.path.join(working_dir, default_file_name)
        config_file_name = QFileDialog.getSaveFileName(self.parent,
                                                       caption="Define config file name ...",
                                                       directory=directory,
                                                       filter="config(*.config)",
                                                       initialFilter='config')

        if config_file_name:
            # ring
            x_central_pixel = np.float(str(self.parent.ui.circle_x.text()))
            y_central_pixel = np.float(str(self.parent.ui.circle_y.text()))
            ring_radius = self.parent.ui.ring_inner_radius_doubleSpinBox.value()
            ring_thickness = self.parent.ui.ring_thickness_doubleSpinBox.value()

            # grid
            bin_size = self.parent.ui.grid_size_slider.value()
            red = self.parent.guide_color_slider['red']
            green = self.parent.guide_color_slider['green']
            blue = self.parent.guide_color_slider['blue']
            alpha = self.parent.guide_color_slider['alpha']

            config_dict = {'ring': {'central_pixel': {'x': x_central_pixel,
                                                      'y': y_central_pixel},
                                    'radius'       : ring_radius,
                                    'thickness'    : ring_thickness},
                           'grid': {'bin_size': bin_size,
                                    'red'     : red,
                                    'green'   : green,
                                    'blue'    : blue,
                                    'alpha'   : alpha},
                           }
