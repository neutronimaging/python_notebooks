import numpy as np
from collections import OrderedDict


class CalculateProfiles:

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):
        x_central_pixel = np.float(str(self.parent.ui.circle_x.text()))
        y_central_pixel = np.float(str(self.parent.ui.circle_y.text()))

        print(f"x_central_pixel: {x_central_pixel}")
        print(f"y_central_pixel: {y_central_pixel}")

        inner_radius = self.parent.ui.ring_inner_radius_doubleSpinBox.value()
        thickness = self.parent.ui.ring_thickness_doubleSpinBox.value()

        image_width = self.parent.width
        image_height = self.parent.height

        print(f"image_width: {image_width}")
        print(f"image_height: {image_height}")

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

        profile_dictionary = OrderedDict()
        list_angles = np.arange(0, 360, angle_bin)

        # find angles of all the pixels
        angles_matrix = self._build_angles_matrix(image_width=image_width, image_height=image_height,
                                                  x_central_pixel=x_central_pixel, y_central_pixel=y_central_pixel)

        # working for first image only for now
        first_image = self.parent.data[0]

        # for debugging only
        self.parent.ui.image_view.setImage(np.transpose(angles_matrix))


    def _build_angles_matrix(self, image_width=None, image_height=None,
                             x_central_pixel=None, y_central_pixel=None):

        full_angles_matrix = np.zeros((image_height, image_width))

        # bottom right corner of matrix
        right_bottom_corner_width = np.int(image_width - x_central_pixel)
        right_bottom_corner_height = np.int(image_height - y_central_pixel)

        x_right_bottom = np.arange(right_bottom_corner_width) + x_central_pixel
        y_right_bottom = np.arange(right_bottom_corner_height) + y_central_pixel

        xv_right_bottom, yv_right_bottom = np.meshgrid(x_right_bottom, y_right_bottom)

        angles_right_bottom = 90 + np.rad2deg(np.arctan(((yv_right_bottom - y_central_pixel)) /
                                                        (xv_right_bottom - x_central_pixel)))

        full_angles_matrix[np.int(y_right_bottom[0]): np.int(y_right_bottom[0]) + len(y_right_bottom),
                           np.int(x_right_bottom[0]): np.int(x_right_bottom[0]) + len(x_right_bottom)] = angles_right_bottom

        # top right corner of matrix
        right_top_corner_width = np.int(image_width - x_central_pixel)
        right_top_corner_height = np.int(y_central_pixel)

        x_right_top = np.arange(right_top_corner_width) + x_central_pixel
        y_right_top = np.arange(right_top_corner_height)

        xv_right_top, yv_right_top = np.meshgrid(x_right_top, y_right_top)

        angles_right_top = 90 + np.rad2deg(np.arctan((yv_right_top - y_central_pixel) /
                                                     (xv_right_top - x_central_pixel)))

        full_angles_matrix[np.int(y_right_top[0]): np.int(y_right_top[0])+len(y_right_top),
                           np.int(x_right_top[0]):np.int(x_right_top[0])+len(x_right_top)] = angles_right_top

        # top left corner
        left_top_corner_width = np.int(x_central_pixel)
        left_top_corner_height = np.int(y_central_pixel)

        x_left_top = np.arange(left_top_corner_width)
        y_left_top = np.arange(y_central_pixel)

        xv_left_top, yv_left_top = np.meshgrid(x_left_top, y_left_top)

        angles_left_top = 270 + np.rad2deg(np.arctan((yv_left_top - y_central_pixel) /
                                                     (xv_left_top - x_central_pixel)))
        full_angles_matrix[np.int(y_left_top[0]): np.int(y_left_top[0])+len(y_left_top),
                           np.int(x_left_top[0]): np.int(x_left_top[0])+len(x_left_top)] = angles_left_top

        # bottom left corner
        left_bottom_corner_width = np.int(x_central_pixel)
        left_bottom_corner_height = np.int(image_height - y_central_pixel)

        x_left_bottom = np.arange(left_bottom_corner_width)
        y_left_bottom = np.arange(left_bottom_corner_height) + y_central_pixel

        xv_left_bottom, yv_left_bottom = np.meshgrid(x_left_bottom, y_left_bottom)

        angles_left_bottom = 270 + np.rad2deg(np.arctan((yv_left_bottom - y_central_pixel) /
                                                        (xv_left_bottom - x_central_pixel)))
        full_angles_matrix[np.int(y_left_bottom[0]): np.int(y_left_bottom[0]) + len(y_left_bottom),
                           np.int(x_left_bottom[0]): np.int(x_left_bottom[0]) + len(x_left_bottom)] = angles_left_bottom

        return full_angles_matrix
