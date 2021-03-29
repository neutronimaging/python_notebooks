import numpy as np


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def get_index_of_chip_to_correct(self):
        if self.parent.ui.chip1_radioButton.isChecked():
            return 0
        elif self.parent.ui.chip2_radioButton.isChecked():
            return 1
        elif self.parent.ui.chip3_radioButton.isChecked():
            return 2
        else:
            return 3

    def get_profile_type(self):
        if self.parent.ui.horizontal_radioButton.isChecked():
            return 'horizontal'
        else:
            return 'vertical'

    @staticmethod
    def get_x_y_ranges(index_of_chip,
                       profile_data,
                       profile_type,
                       where_is_gap_in_x_axis,
                       x_axis,
                       nbr_pixels_to_exclude_on_each_side_of_chips_gap):

        where_is_gap = where_is_gap_in_x_axis[0][0]
        delta = nbr_pixels_to_exclude_on_each_side_of_chips_gap

        if index_of_chip == 0:
            x_axis_working_chip = x_axis[0: where_is_gap - delta]
            y_axis_working_chip = profile_data[0: where_is_gap - delta]
            x_axis_other_chip = x_axis[where_is_gap + delta:]
            y_axis_other_chip = profile_data[where_is_gap + delta:]
        elif index_of_chip == 1:
            if profile_type == 'horizontal':
                x_axis_working_chip = x_axis[where_is_gap + delta:]
                y_axis_working_chip = profile_data[where_is_gap + delta:]
                x_axis_other_chip = x_axis[0:where_is_gap - delta]
                y_axis_other_chip = profile_data[0:where_is_gap - delta]
            else:
                x_axis_working_chip = x_axis[0: where_is_gap - delta]
                y_axis_working_chip = profile_data[0: where_is_gap - delta]
                x_axis_other_chip = x_axis[where_is_gap + delta:]
                y_axis_other_chip = profile_data[where_is_gap + delta:]
        elif index_of_chip == 2:
            if profile_type == 'horizontal':
                x_axis_working_chip = x_axis[0: where_is_gap - delta]
                y_axis_working_chip = profile_data[0: where_is_gap - delta]
                x_axis_other_chip = x_axis[where_is_gap + delta:]
                y_axis_other_chip = profile_data[where_is_gap + delta:]
            else:
                x_axis_working_chip = x_axis[where_is_gap + delta :]
                y_axis_working_chip = profile_data[where_is_gap + delta:]
                x_axis_other_chip = x_axis[0:where_is_gap - delta]
                y_axis_other_chip = profile_data[0:where_is_gap - delta]
        elif index_of_chip == 3:
            if profile_type == 'horizontal':
                x_axis_working_chip = x_axis[where_is_gap + delta:]
                y_axis_working_chip = profile_data[where_is_gap + delta:]
                x_axis_other_chip = x_axis[0:where_is_gap - delta]
                y_axis_other_chip = profile_data[0:where_is_gap - delta]
            else:
                x_axis_working_chip = x_axis[where_is_gap + delta:]
                y_axis_working_chip = profile_data[where_is_gap + delta:]
                x_axis_other_chip = x_axis[0:where_is_gap - delta]
                y_axis_other_chip = profile_data[0:where_is_gap - delta]

        return x_axis_other_chip, x_axis_working_chip, y_axis_other_chip, y_axis_working_chip

    @staticmethod
    def get_color_of_pen(gap_index=0, index_of_chip=0, profile_type='horizontal', x0=0, y0=0, x_axis=None):
        """
        This method will give the color of the pen to use 'w' (white) or 'r' (red) according to the position of
        the profile.
        For example, if the profile selected is outside the chip, color will be 'w'. Any data inside the chip
        will be 'r'
        """
        if x_axis is None:
            return 'w'

        if index_of_chip == 0:
            if x_axis[0] > gap_index:
                return 'w'
            else:
                if profile_type == 'horizontal':
                    if y0 < gap_index:
                        return 'r'
                    else:
                        return 'w'
                else:
                    if x0 < gap_index:
                        return 'r'
                    else:
                        return 'w'

        elif index_of_chip == 1:
            if profile_type == 'horizontal':
                if x_axis[-1] < gap_index:
                    return 'w'
                if y0 > gap_index:
                    return 'w'
                else:
                    return 'r'
            else:
                if x_axis[0] > gap_index:
                    return 'w'
                if x0 < gap_index:
                    return 'r'
                else:
                    return 'w'

        elif index_of_chip == 2:
            if profile_type == 'horizontal':
                if x_axis[0] > gap_index:
                    return 'w'
                if y0 < gap_index:
                    return 'w'
                else:
                    return 'r'
            else:
                if x_axis[-1] < gap_index:
                    return 'w'
                if x0 > gap_index:
                    return 'w'
                else:
                    return 'r'

        elif index_of_chip == 3:
            if profile_type == 'horizontal':
                if x_axis[-1] < gap_index:
                    return 'w'
                if y0 < gap_index:
                    return 'w'
                else:
                    return 'r'
            else:
                if x_axis[-1] < gap_index:
                    return 'w'
                if x0 < gap_index:
                    return 'w'
                else:
                    return 'r'

    @staticmethod
    def get_x_y_width_height_of_roi(roi_id=None):
        x, y = roi_id.pos()
        width, height = roi_id.size()
        return {'x'     : np.int(x),
                'y'     : np.int(y),
                'width' : np.int(width),
                'height': np.int(height)}
