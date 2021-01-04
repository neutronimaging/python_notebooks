import numpy as np
from collections import OrderedDict
import copy


class CalculateProfiles:

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):
        matrices = self.calculate_matrices(display=False)
        angle_matrix = matrices['angles_matrix']
        mask_ring = matrices['mask_ring']

        # working for first image only for now
        first_image = self.parent.data[0]

        # create profile_dictionary
        angle_bin = self.parent.angle_bin_horizontalSlider.value()/100

        profile_dictionary = OrderedDict()
        list_angles = np.arange(0, 360, angle_bin)
        for _angle in list_angles:
            profile_dictionary[_angle] = np.NaN

        # image_width = self.parent.width
        # image_height = self.parent.height

        y_mask = mask_ring[0]
        x_mask = mask_ring[1]
        for y, x in zip(y_mask, x_mask):
            angle = angle_matrix[y, x]
            bin_angle = CalculateProfiles.get_corresponding_bin_angle(angle=angle,
                                                                      list_angles=list_angles)
            # print(f"angle:{angle} -> bin_angle:{bin_angle}")
            profile_dictionary[bin_angle] = first_image[y, x]

        y_profile = []
        x_profile = copy.deepcopy(list_angles)
        for _key in profile_dictionary.keys():
            y_profile.append(np.mean(profile_dictionary[_key]))

        self.parent.x_profile = x_profile
        self.parent.y_profile = y_profile

    def calculate_matrices(self, display=True):
        x_central_pixel = np.float(str(self.parent.ui.circle_x.text()))
        y_central_pixel = np.float(str(self.parent.ui.circle_y.text()))

        inner_radius = self.parent.ui.ring_inner_radius_doubleSpinBox.value()
        thickness = self.parent.ui.ring_thickness_doubleSpinBox.value()

        image_width = self.parent.width
        image_height = self.parent.height

        x = np.arange(image_width) + 0.5
        y = np.arange(image_height) + 0.5

        # find all the pixels that are within the ring
        xv, yv = np.meshgrid(x, y)
        distances_power = np.sqrt((np.power(yv - y_central_pixel, 2) + np.power(xv - x_central_pixel, 2)))

        mask_ring = np.where((distances_power > inner_radius) & (distances_power < (inner_radius + thickness)))

        # find angles of all the pixels
        angles_matrix = CalculateProfiles._build_angles_matrix(image_width=image_width,
                                                               image_height=image_height,
                                                               x_central_pixel=x_central_pixel,
                                                               y_central_pixel=y_central_pixel)
        y_mask = mask_ring[0]
        x_mask = mask_ring[1]

        ring_angles_matrix = np.zeros(np.shape(angles_matrix))
        for y, x in zip(y_mask, x_mask):
            ring_angles_matrix[y, x] = angles_matrix[y, x]

        if display:
            self.parent.ui.image_view.setImage(np.transpose(ring_angles_matrix))

        return {'angles_matrix': ring_angles_matrix,
                'mask_ring': mask_ring}

    @staticmethod
    def _build_angles_matrix(image_width=None, image_height=None,
                             x_central_pixel=None, y_central_pixel=None):

        full_angles_matrix = np.zeros((image_height, image_width))

        # bottom right corner of matrix
        right_bottom_corner_width = np.int(image_width - x_central_pixel)
        right_bottom_corner_height = np.int(image_height - y_central_pixel)

        x_right_bottom = np.arange(right_bottom_corner_width) + x_central_pixel
        y_right_bottom = np.arange(right_bottom_corner_height) + y_central_pixel

        xv_right_bottom, yv_right_bottom = np.meshgrid(x_right_bottom, y_right_bottom)

        angles_right_bottom = 90 + np.rad2deg(np.arctan((yv_right_bottom - y_central_pixel) /
                                                        (xv_right_bottom - x_central_pixel)))

        full_angles_matrix[np.int(y_right_bottom[0]): np.int(y_right_bottom[0]) + len(y_right_bottom),
                           np.int(x_right_bottom[0]): np.int(x_right_bottom[0]) + len(x_right_bottom)] = \
            angles_right_bottom

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
        # left_top_corner_height = np.int(y_central_pixel)

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

    def plot_profiles(self):
        x_profile = self.parent.x_profile
        y_profile = self.parent.y_profile

        if not (x_profile is None):

            plot_type = 'r'
            if self.parent.ui.point_radioButton.isChecked():
                plot_type += '.'
            elif self.parent.ui.plus_radioButton.isChecked():
                plot_type += '+'

            self.parent.profile_plot.axes.clear()
            self.parent.profile_plot.axes.plot(x_profile, y_profile, plot_type)
            self.parent.profile_plot.draw()

        # y_axis = np.mean(y_axis_of_profile, axis=dim_to_keep)
        # plot_ui.axes.plot(x_axis_of_profile, y_axis, color=color)
        # # plot_ui.axes.set_xlabel("Pixel")
        # # plot_ui.axes.set_ylabel("Average counts")

        #plot_ui.draw()

    @staticmethod
    def get_corresponding_bin_angle(angle=None, list_angles=None):
        index = np.abs(np.array(list_angles) - angle)
        argmin = index.argmin()
        return list_angles[argmin]
