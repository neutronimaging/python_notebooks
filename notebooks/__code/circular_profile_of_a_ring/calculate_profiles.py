import numpy as np


class CalculateProfiles:

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):
        x_central_pixel = np.float(str(self.parent.ui.circle_x.text()))
        y_central_pixel = np.float(str(self.parent.ui.circle_y.text()))

        inner_radius = self.parent.ui.ring_inner_radius_doubleSpinBox.value()
        thickness = self.parent.ui.ring_thickness_doubleSpinBox.value()

        image_width = self.parent.width
        image_height = self.parent.height

        x = np.arange(image_width) + 0.5
        y = np.arange(image_height) + 0.5

        # find all the pixels that are within the ring
        xv, yv = np.meshgrid(y, x)
        distances_power = np.sqrt((np.power(yv - y_central_pixel, 2) + np.power(xv - x_central_pixel, 2)))

        mask_ring1 = np.where(distances_power > inner_radius)
        mask_ring2 = np.where(distances_power < (inner_radius + thickness))
        mask_ring = np.where(mask_ring1 and mask_ring2)

        # create profile_dictionary
        angle_bin = self.parent.angle_bin_horizontalSlider.value()