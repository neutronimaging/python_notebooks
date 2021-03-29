import numpy as np
import pyqtgraph as pg
from qtpy.QtGui import QPen, QColor
import copy

from __code.mcp_chips_corrector.get import Get

COLOR_CONTOUR = QColor(255, 0, 0, 255)
PROFILE_ROI = QColor(255, 255, 255, 255)
INTER_CHIPS = QColor(0, 255, 0, 255)


class EventHandler:

    y_axis_other_chip = None
    y_axis_working_chip = None
    gap_index = 0       # width/2 (256)

    o_get = None

    def __init__(self, parent=None):
        self.parent = parent
        self.o_get = Get(parent=self.parent)

    def display_setup_image(self):
        setup_image = self.parent.o_corrector.integrated_data
        self.parent.setup_live_image = setup_image
        _image = np.transpose(setup_image)
        self.parent.setup_image_view.setImage(_image)

    def chips_index_changed(self):
        new_index = self.o_get.get_index_of_chip_to_correct()
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

        profile_type = self.o_get.get_profile_type()

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
        x_y_width_height = Get.get_x_y_width_height_of_roi(roi_id=roi_id)
        profile_type = self.o_get.get_profile_type()
        self.parent.profile[profile_type] = {'x0': x_y_width_height['x'],
                                             'y0': x_y_width_height['y'],
                                             'width': x_y_width_height['width'],
                                             'height': x_y_width_height['height']}

    def plot_profile(self):
        profile_type = self.o_get.get_profile_type()
        x0 = self.parent.profile[profile_type]['x0']
        y0 = self.parent.profile[profile_type]['y0']
        width = self.parent.profile[profile_type]['width']
        height = self.parent.profile[profile_type]['height']
        nbr_pixels_to_exclude_on_each_side_of_chips_gap = self.parent.nbr_pixels_to_exclude_on_each_side_of_chips_gap

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

        gap_index = self.parent.image_size.gap_index

        where_is_gap_in_x_axis = np.where(x_axis == gap_index)
        index_of_chip = self.o_get.get_index_of_chip_to_correct()

        color_pen = Get.get_color_of_pen(gap_index=gap_index,
                                                  index_of_chip=index_of_chip,
                                                  profile_type=profile_type,
                                                  x0=x0, y0=y0,
                                                  x_axis=x_axis)

        self.coefficient_corrector_can_be_calculated = False
        if len(where_is_gap_in_x_axis[0] > 0):
            "the inter chips space falls within the profile selected"

            x_axis_other_chip, x_axis_working_chip, y_axis_other_chip, y_axis_working_chip = \
                Get.get_x_y_ranges(index_of_chip, profile_data,
                                            profile_type, where_is_gap_in_x_axis,
                                            x_axis,
                                            nbr_pixels_to_exclude_on_each_side_of_chips_gap)

            self.y_axis_other_chip = y_axis_other_chip
            self.y_axis_working_chip = y_axis_working_chip

            self.parent.profile_view.plot(x_axis_working_chip, y_axis_working_chip, pen=color_pen, symbol='o')
            self.parent.profile_view.plot(x_axis_other_chip, y_axis_other_chip, pen='w', symbol='o')

            if color_pen == 'r':
                self.coefficient_corrector_can_be_calculated = True

        else:
            self.parent.profile_view.plot(x_axis, profile_data, pen=color_pen, symbol='o')

        pen = QPen()
        pen.setColor(INTER_CHIPS)
        pen.setWidthF(0.3)
        line = pg.InfiniteLine(pos=self.parent.image_size.width/2,
                               angle=90,
                               pen=pen,
                               label="Inter Chips")
        self.parent.profile_view.addItem(line)

    def calculate_coefficient_corrector(self):

        if self.y_axis_other_chip is None:
            coefficient_corrector_s = "N/A"
        elif self.coefficient_corrector_can_be_calculated:

            y_axis_working_chip = self.y_axis_working_chip
            y_axis_other_chip = self.y_axis_other_chip

            y_axis_working_chip_mean = np.nanmean(y_axis_working_chip)
            y_axis_other_chip_mean = np.nanmean(y_axis_other_chip)

            coefficient_corrector = y_axis_other_chip_mean / y_axis_working_chip_mean
            coefficient_corrector_s = "{:.2f}".format(coefficient_corrector)
        else:
            coefficient_corrector_s = "N/A"

        self.parent.ui.coefficient_corrector_lineEdit.setText(coefficient_corrector_s)

    def with_correction_tab(self):
        if str(self.parent.ui.coefficient_corrector_lineEdit.text()) == 'N/A':
            self.parent.ui.tabWidget.setTabEnabled(1, False)
            return
        else:
            self.parent.ui.tabWidget.setTabEnabled(1, True)

        # calculate corrected chip
        coefficient = np.float(str(self.parent.ui.coefficient_corrector_lineEdit.text()))

        setup_image = copy.deepcopy(self.parent.setup_live_image)
        index_of_chip_to_correct = self.o_get.get_index_of_chip_to_correct()
        gap_index = self.parent.image_size.gap_index

        if index_of_chip_to_correct == 0:
            from_x = 0
            to_x = gap_index
            from_y = 0
            to_y = gap_index
        elif index_of_chip_to_correct == 1:
            from_x = gap_index
            to_x = self.parent.image_size.width
            from_y = 0
            to_y = gap_index
        elif index_of_chip_to_correct == 2:
            from_x = 0
            to_x = gap_index
            from_y = gap_index
            to_y = self.parent.image_size.height
        else:
            from_x = gap_index
            to_x = self.parent.image_size.width
            from_y = gap_index
            to_y = self.parent.image_size.height

        setup_image[from_y: to_y, from_x: to_x] *= coefficient
        self.parent.corrected_live_image = setup_image
        self.display_corrected_image()

    def display_corrected_image(self):

        _view = self.parent.corrected_image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        first_update = False
        if self.parent.corrected_histogram_level is None:
            first_update = True
        _histo_widget = self.parent.corrected_image_view.getHistogramWidget()
        self.parent.corrected_histogram_level = _histo_widget.getLevels()

        corrected_image = self.parent.corrected_live_image
        _image = np.transpose(corrected_image)
        self.parent.corrected_image_view.setImage(_image)

        _view_box.setState(_state)

        if not first_update:
            _histo_widget.setLevels(self.parent.corrected_histogram_level[0],
                                    self.parent.corrected_histogram_level[1])
