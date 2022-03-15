import numpy as np
import scipy.ndimage.filters as flt2
import copy


class Algorithm:

    is_dead_pixel_activated = False
    is_high_counts_activated = False

    total_number_of_pixels = 0

    data = None
    median_data = None

    def __init__(self, parent=None, data=None):

        self.dead_pixel_stats = {'number': 0,
                                 'percentage': 0}
        self.high_counts_stats = {'number': 0,
                                  'percentage': 0}

        self.parent = parent
        self.data = copy.deepcopy(data)
        self.processed_data = copy.deepcopy(data)
        self.total_number_of_pixels = self.parent.image_size[0] * self.parent.image_size[1]

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
        if mask:
            nbr_pixels = len(mask[0])
            self.dead_pixel_stats['number'] = nbr_pixels
            self.dead_pixel_stats['percentage'] = (nbr_pixels / self.total_number_of_pixels) * 100
        self.data[mask] = self.median_data[mask]

    def high_counts(self):
        threshold = self.parent.ui.filtering_coefficient_value_2.value() / 100.
        where_above_threshold = np.where(self.data * threshold > self.median_data)
        if where_above_threshold:
            nbr_pixels = len(where_above_threshold[0])
            self.high_counts_stats['number'] = nbr_pixels
            self.high_counts_stats['percentage'] = (nbr_pixels / self.total_number_of_pixels) * 100
        self.data[where_above_threshold] = self.median_data[where_above_threshold]

    def get_dead_pixels_stats(self):
        return self.dead_pixel_stats

    def get_high_counts_stats(self):
        return self.high_counts_stats