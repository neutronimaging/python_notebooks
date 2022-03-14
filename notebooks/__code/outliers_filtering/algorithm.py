import numpy as np
import scipy.ndimage.filters as flt2
import copy


class Algorithm:

    is_dead_pixel_activated = False
    is_high_counts_activated = False

    data = None
    median_data = None

    def __init__(self, parent=None, data=None):
        self.parent = parent
        self.data = data
        self.processed_data = copy.deepcopy(data)

        if self.parent.ui.fix_dead_pixels_checkBox.isChecked():
            self.is_dead_pixel_activated = True

        if self.parent.ui.fix_high_intensity_counts_checkBox.isChecked():
            self.is_high_counts_activated = True

        if self.is_dead_pixel_activated or self.is_high_counts_activated:
            self.calculate_median()

    def get_processed_data(self):
        return self.data

    def calculate_median(self):
        radius = self.parent.ui.median_filter_radius_spinBox.value()
        self.median_data = flt2.median_filter(self.data, radius)

    def run(self):
        if self.is_dead_pixel_activated:
            self.dead_pixels()
        if self.is_high_counts_activated:
            self.high_counts()

    def dead_pixels(self):
        mask = np.where(self.data == 0)
        self.data[mask] = self.median_data[mask]

    def high_counts(self):
        threshold = self.parent.ui.filtering_coefficient_value_2.value() / 100.
        where_above_threshold = np.where(self.data * threshold > self.median_data)
        self.data[where_above_threshold] = self.median_data[where_above_threshold]
