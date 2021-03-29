import numpy as np
import pyqtgraph as pg
from qtpy.QtGui import QPen, QColor

COLOR_CONTOUR = QColor(255, 0, 0, 255)
PROFILE_ROI = QColor(255, 255, 255, 255)
INTER_CHIPS = QColor(0, 255, 0, 255)


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def display_setup_image(self):
        setup_image = self.parent.o_corrector.integrated_data
        self.parent.setup_live_image = setup_image
        _image = np.transpose(setup_image)
        self.parent.setup_image_view.setImage(_image)

    def chips_index_changed(self):
        new_index = self.get_index_of_chip_to_correct()
        self.display_chip_border(chip_index=new_index)

    def display_chip_border(self, chip_index=0):
        if self.parent.contour_id:
            self.parent.setup_image_view.removeItem(self.parent.contour_id)

        image_height = self.parent.image_size.height
        image_width = self.parent.image_size.width

        contour_width = np.int(image_width / 2)
        contour_height = np.int(image_height / 2)
        if chip_index == 0:
            x0, y0 = 0, 0
        elif chip_index == 1:
            x0 = np.int(image_width/2)
            y0 = 0
        elif chip_index == 2:
            x0 = 0
            y0 = np.int(image_height/2)
        else:
            x0 = np.int(image_width/2)
            y0 = np.int(image_height/2)

        _pen = QPen()
        _pen.setColor(COLOR_CONTOUR)
        _pen.setWidthF(0.01)
        _roi_id = pg.ROI([x0, y0],
                         [contour_width, contour_height],
                         pen=_pen,
                         scaleSnap=True,
                         movable=False)

        self.parent.setup_image_view.addItem(_roi_id)
        self.parent.contour_id = _roi_id

    def profile_type_changed(self):

        if self.parent.profile_id:
            self.parent.setup_image_view.removeItem(self.parent.profile_id)

        profile_type = self.get_profile_type()

        x0 = self.parent.profile[profile_type]['x0']
        y0 = self.parent.profile[profile_type]['y0']
        width = self.parent.profile[profile_type]['width']
        height = self.parent.profile[profile_type]['height']

        pen = QPen()
        pen.setColor(PROFILE_ROI)
        pen.setWidthF(0.05)

        profile_ui = pg.ROI([x0, y0],
                            [width, height],
                            scaleSnap=True,
                            pen=pen)
        profile_ui.addScaleHandle([0, 0.5], [0.5, 0])
        profile_ui.addScaleHandle([0.5, 0], [0, 0])
        self.parent.ui.setup_image_view.addItem(profile_ui)
        profile_ui.sigRegionChanged.connect(self.parent.profile_changed)

        self.parent.profile_id = profile_ui

    def profile_changed(self):
        roi_id = self.parent.profile_id
        x_y_width_height = EventHandler.get_x_y_width_height_of_roi(roi_id=roi_id)
        profile_type = self.get_profile_type()
        self.parent.profile[profile_type] = {'x0': x_y_width_height['x'],
                                             'y0': x_y_width_height['y'],
                                             'width': x_y_width_height['width'],
                                             'height': x_y_width_height['height']}

    def plot_profile(self):
        profile_type = self.get_profile_type()
        x0 = self.parent.profile[profile_type]['x0']
        y0 = self.parent.profile[profile_type]['y0']
        width = self.parent.profile[profile_type]['width']
        height = self.parent.profile[profile_type]['height']

        data = self.parent.integrated_data[y0: y0+height, x0: x0+width]
        if profile_type == 'horizontal':
            axis = 0
            start_value = x0
            end_value = x0 + width
        else:
            axis = 1
            start_value = y0
            end_value = y0 + height

        profile_data = np.mean(data, axis=axis)
        x_axis = np.arange(start_value, end_value)
        self.parent.profile_view.clear()

        gap_index = np.int(self.parent.image_size.height/2)
        where_is_gap_in_x_axis = np.where(x_axis == gap_index)
        index_of_chip = self.get_index_of_chip_to_correct()

        color_pen = EventHandler.get_color_of_pen(gap_index=gap_index,
                                                  index_of_chip=index_of_chip,
                                                  profile_type=profile_type,
                                                  x0=x0, y0=y0,
                                                  x_axis=x_axis)

        if len(where_is_gap_in_x_axis[0] > 0):
            "the inter chips space falls within the profile selected"

            x_axis_other_chip, x_axis_working_chip, y_axis_other_chip, y_axis_working_chip = \
                EventHandler.get_x_y_ranges(index_of_chip, profile_data,
                                            profile_type, where_is_gap_in_x_axis,
                                            x_axis)

            self.parent.profile_view.plot(x_axis_working_chip, y_axis_working_chip, pen=color_pen)
            self.parent.profile_view.plot(x_axis_other_chip, y_axis_other_chip, pen='w')

        else:

            # color_pen = 'r'
            # if index_of_chip == 0:
            #     if x_axis[-1] < gap_index:
            #         color_pen = 'r'

            self.parent.profile_view.plot(x_axis, profile_data, pen=color_pen)

        pen = QPen()
        pen.setColor(INTER_CHIPS)
        pen.setWidthF(0.3)
        line = pg.InfiniteLine(pos=self.parent.image_size.width/2,
                               angle=90,
                               pen=pen,
                               label="Inter Chips")
        self.parent.profile_view.addItem(line)

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
    def get_x_y_ranges(index_of_chip, profile_data, profile_type, where_is_gap_in_x_axis, x_axis):
        where_is_gap = where_is_gap_in_x_axis[0][0]
        if index_of_chip == 0:
            x_axis_working_chip = x_axis[0: where_is_gap]
            y_axis_working_chip = profile_data[0: where_is_gap]
            x_axis_other_chip = x_axis[where_is_gap:]
            y_axis_other_chip = profile_data[where_is_gap:]
        elif index_of_chip == 1:
            if profile_type == 'horizontal':
                x_axis_working_chip = x_axis[where_is_gap:]
                y_axis_working_chip = profile_data[where_is_gap:]
                x_axis_other_chip = x_axis[0:where_is_gap]
                y_axis_other_chip = profile_data[0:where_is_gap]
            else:
                x_axis_working_chip = x_axis[0: where_is_gap]
                y_axis_working_chip = profile_data[0: where_is_gap]
                x_axis_other_chip = x_axis[where_is_gap:]
                y_axis_other_chip = profile_data[where_is_gap:]
        elif index_of_chip == 2:
            if profile_type == 'horizontal':
                x_axis_working_chip = x_axis[0: where_is_gap]
                y_axis_working_chip = profile_data[0: where_is_gap]
                x_axis_other_chip = x_axis[where_is_gap:]
                y_axis_other_chip = profile_data[where_is_gap:]
            else:
                x_axis_working_chip = x_axis[where_is_gap:]
                y_axis_working_chip = profile_data[where_is_gap:]
                x_axis_other_chip = x_axis[0:where_is_gap]
                y_axis_other_chip = profile_data[0:where_is_gap]
        else:
            x_axis_working_chip = x_axis[where_is_gap:]
            y_axis_working_chip = profile_data[where_is_gap:]
            x_axis_other_chip = x_axis[0:where_is_gap]
            y_axis_other_chip = profile_data[0:where_is_gap]
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
                color_pen = 'w'
            else:
                if profile_type == 'horizontal':
                    if y0 < gap_index:
                        color_pen = 'r'
                    else:
                        color_pen = 'w'
                else:
                    if x0 < gap_index:
                        color_pen = 'r'
                    else:
                        color_pen = 'w'

            print(f"in chips 0: color_pen:{color_pen}")

        elif index_of_chip == 1:
            if profile_type == 'horizontal':
                if x_axis[0] > gap_index:
                    color_pen = 'r'
                else:
                    color_pen = 'w'
            else:
                if x_axis[0] > gap_index:
                    color_pen = 'w'
                else:
                    color_pen = 'r'
        elif index_of_chip == 2:
            if profile_type == 'horizontal':
                if x_axis[0] > gap_index:
                    color_pen = 'w'
                else:
                    color_pen = 'r'
            else:
                if x_axis[0] > gap_index:
                    color_pen = 'r'
                else:
                    color_pen = 'w'
        else:
            if x_axis[0] > gap_index:
                color_pen = 'r'
            else:
                color_pen = 'w'
        return color_pen

    @staticmethod
    def get_x_y_width_height_of_roi(roi_id=None):
        x, y = roi_id.pos()
        width, height = roi_id.size()
        return {'x'     : np.int(x),
                'y'     : np.int(y),
                'width' : np.int(width),
                'height': np.int(height)}
