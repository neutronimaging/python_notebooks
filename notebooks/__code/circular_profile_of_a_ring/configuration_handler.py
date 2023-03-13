import numpy as np
import json
from qtpy.QtWidgets import QFileDialog
import os


class ConfigurationHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def load(self):
        working_dir = os.path.abspath(os.path.dirname(self.parent.working_dir))
        config_file_name = QFileDialog.getOpenFileName(self.parent,
                                                       caption="Select config file name ...",
                                                       directory=working_dir,
                                                       filter="config(*.cfg)",
                                                       initialFilter='config')

        if config_file_name[0]:
            with open(config_file_name[0]) as json_file:
                data = json.load(json_file)

                x_central_pixel = data['ring']['central_pixel']['x']
                y_central_pixel = data['ring']['central_pixel']['y']
                ring_radius = data['ring']['radius']
                ring_thickness = data['ring']['thickness']

                angle_bin_size = data['angle_bin_size']

                bin_size = data['grid']['bin_size']
                red = data['grid']['red']
                green = data['grid']['green']
                blue = data['grid']['blue']
                alpha = data['grid']['alpha']

            self.parent.ui.circle_x.setText(str(x_central_pixel))
            self.parent.ui.circle_y.setText(str(y_central_pixel))
            self.parent.ui.ring_inner_radius_doubleSpinBox.setValue(ring_radius)
            self.parent.ui.ring_inner_radius_slider.setValue(ring_radius*100)
            self.parent.ui.ring_thickness_doubleSpinBox.setValue(ring_thickness)
            self.parent.ui.ring_thickness_slider.setValue(ring_thickness*100)

            self.parent.ui.angle_bin_horizontalSlider.setValue(angle_bin_size)
            self.parent.angle_bin_slider_moved(angle_bin_size)

            self.parent.ui.grid_size_slider.setValue(bin_size)
            self.parent.ui.guide_red_slider.setValue(red)
            self.parent.ui.guide_green_slider.setValue(green)
            self.parent.ui.guide_blue_slider.setValue(blue)
            self.parent.ui.guide_alpha_slider.setValue(alpha)

            # clear plot
            self.parent.clear_image_view()

            self.parent.guide_color_changed(-1)
            self.parent.init_crosshair()
            self.parent.display_mode_changed()

            message = "{} ... Loaded!".format(os.path.basename(config_file_name[0]))
            self.parent.ui.statusbar.showMessage(message, 10000)  # 10s
            self.parent.ui.statusbar.setStyleSheet("color: green")

    def save(self):
        default_file_name = os.path.abspath(os.path.basename(self.parent.working_dir)) + "_configuration.cfg"
        working_dir = os.path.dirname(self.parent.working_dir)
        directory = os.path.join(working_dir, default_file_name)
        config_file_name = QFileDialog.getSaveFileName(self.parent,
                                                       caption="Define config file name ...",
                                                       directory=directory,
                                                       filter="config(*.cfg)",
                                                       initialFilter='config')

        if config_file_name[0]:
            config_dict = self.get_config_dict()
            with open(config_file_name[0], 'w') as outfile:
                json.dump(config_dict, outfile)

            message = "{} ... Saved!".format(os.path.basename(config_file_name[0]))
            self.parent.ui.statusbar.showMessage(message, 10000)  # 10s
            self.parent.ui.statusbar.setStyleSheet("color: green")

    def get_config_dict(self):
        # ring
        x_central_pixel = float(str(self.parent.ui.circle_x.text()))
        y_central_pixel = np.float(str(self.parent.ui.circle_y.text()))
        ring_radius = self.parent.ui.ring_inner_radius_doubleSpinBox.value()
        ring_thickness = self.parent.ui.ring_thickness_doubleSpinBox.value()

        # grid
        bin_size = self.parent.ui.grid_size_slider.value()
        red = self.parent.guide_color_slider['red']
        green = self.parent.guide_color_slider['green']
        blue = self.parent.guide_color_slider['blue']
        alpha = self.parent.guide_color_slider['alpha']

        # angle bin size
        angle_bin_size = self.parent.ui.angle_bin_horizontalSlider.value()

        config_dict = {'ring': {'central_pixel': {'x': x_central_pixel,
                                                  'y': y_central_pixel},
                                'radius': ring_radius,
                                'thickness': ring_thickness},
                       'angle_bin_size': angle_bin_size,
                       'grid': {'bin_size': bin_size,
                                'red': red,
                                'green': green,
                                'blue': blue,
                                'alpha': alpha},
                       }

        return config_dict
