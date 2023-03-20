import numpy as np
from scipy.special import erf
from scipy.optimize import curve_fit
from changepy import pelt
from changepy.costs import normal_var
from qtpy import QtGui


class ListAlgorithm:
    sliding_average = "sliding average"
    error_function = "error function"
    change_point = "change_point"
    all = "all"


class MeanRangeCalculation(object):
    '''
    Mean value of all the counts between left_pixel and right pixel
    '''

    def __init__(self, data=None):
        self.data = data
        self.nbr_pixel = len(self.data)

    def calculate_left_right_mean(self, pixel=-1):
        _data = self.data
        _nbr_pixel = self.nbr_pixel

        self.left_mean = np.nanmean(_data[0:pixel+1])
        self.right_mean = np.nanmean(_data[pixel+1:_nbr_pixel])

    def calculate_delta_mean_square(self):
        self.delta_square = np.square(self.left_mean - self.right_mean)


class Algorithms:
    """This class calculates the front edge position of a set of profiles"""

    # dict_profiles = {}   # {'0': {'data': [], 'delta_time': 45455}, '1': {...} ...}

    list_data = None

    data_have_been_reversed_in_calculation = False

    peak_sliding_average_data = None

    # fitting by error function requires that the signal goes from max to min values
    is_data_from_max_to_min = True
    peak_error_function_data = None
    peak_error_function_data_error = None

    peak_change_point_data = None

    water_intake_peak_erf = []
    water_intake_deltatime = []

    dict_error_function_parameters = {}

    progress_bar_ui = None  # progress bar ui

    def __init__(self, list_data=None,
                 ignore_first_dataset=True,
                 algorithm_selected='sliding_average',
                 progress_bar_ui=None):

        self.list_data = list_data
        self.ignore_first_dataset = ignore_first_dataset
        self.progress_bar_ui = progress_bar_ui

        if algorithm_selected == ListAlgorithm.sliding_average:
            self.calculate_using_sliding_average()
        elif algorithm_selected == ListAlgorithm.error_function:
            self.calculate_using_erf()
        elif algorithm_selected == ListAlgorithm.change_point:
            self.calculate_change_point()
        else:
            raise ValueError("algorithm not implemented yet!")

    @staticmethod
    def fitting_function(x, c, w, m, n):
        return ((m-n)/2.) * erf((x-c)/w) + (m+n)/2.

    def are_data_from_max_to_min(self, ydata):
        nbr_points = len(ydata)
        nbr_point_for_investigation = int(nbr_points * 0.1)

        mean_first_part = np.mean(ydata[0:nbr_point_for_investigation])

        ydata = ydata.copy()
        ydata_reversed = ydata[::-1]
        mean_last_part = np.mean(ydata_reversed[0: nbr_point_for_investigation])

        if mean_first_part > mean_last_part:
            return True
        else:
            return False

    def calculate_change_point(self):
        list_data = self.list_data
        nbr_files = len(list_data)

        if self.ignore_first_dataset:
            _start_file = 1
            _end_file = nbr_files+1
        else:
            _start_file = 0
            _end_file = nbr_files

        if self.progress_bar_ui:
            self.progress_bar_ui.setMaximum(len(list_data))
            self.progress_bar_ui.setVisible(True)
            QtGui.QGuiApplication.processEvents()

        water_intake_peaks = []
        water_intake_deltatime = []
        for _index_file in np.arange(_start_file, _end_file):
            ydata = list_data[_index_file]
            var = np.mean(ydata)
            result = pelt(normal_var(ydata, var), len(ydata))
            if len(result) > 2:
                peak = np.mean(result[2:])
            else:
                peak = np.mean(result[1:])
            water_intake_peaks.append(peak)

            if self.progress_bar_ui:
                self.progress_bar_ui.setValue(_index_file+1)
                QtGui.QGuiApplication.processEvents()

        self.peak_change_point_data = water_intake_peaks
        # self.water_intake_deltatime = water_intake_deltatime

        if self.progress_bar_ui:
            self.progress_bar_ui.setVisible(False)
            QtGui.QGuiApplication.processEvents()

    def calculate_using_erf(self):
        list_data = self.list_data
        nbr_files = len(list_data)

        if self.ignore_first_dataset:
            _start_file = 1
            _end_file = nbr_files + 1
        else:
            _start_file = 0
            _end_file = nbr_files

        if self.progress_bar_ui:
            self.progress_bar_ui.setMaximum(len(list_data))
            self.progress_bar_ui.setVisible(True)
            QtGui.QGuiApplication.processEvents()

        # dict_error_function_parameters = dict()
        # water_intake_peaks_erf = []
        # water_intake_peaks_erf_error = []
        # delta_time = []

        peak_error_function_data = []
        peak_error_function_data_error = []
        dict_error_function_parameters = dict()
        for _index_file in np.arange(_start_file, _end_file):
            ydata = list_data[_index_file]
            # ydata = _profile['data']
            # xdata = _profile['delta_time']

            is_data_from_max_to_min = self.are_data_from_max_to_min(ydata)
            self.is_data_from_max_to_min = is_data_from_max_to_min
            if not is_data_from_max_to_min:
                self.data_have_been_reversed_in_calculation = True
                ydata = ydata[::-1]

            (popt, pcov) = self.fitting_algorithm(ydata)

            _local_dict = {'c': popt[0],
                           'w': popt[1],
                           'm': popt[2],
                           'n': popt[3]}

            error = np.sqrt(np.diag(pcov))
            _peak = int(popt[0] + (popt[1]/np.sqrt(2)))

            if not is_data_from_max_to_min:
                _peak = len(ydata) - _peak

            peak_error_function_data.append(_peak)

            for _i, _err in enumerate(error):
                if np.isnan(_err):
                    error[_i] = np.sqrt(popt[0])
                elif np.isinf(_err):
                    error[_i] = np.sqrt(popt[0])
                else:
                    error[_i] = _err

            _peak_error = int(error[0] + (error[1]/np.sqrt(2)))

            peak_error_function_data_error.append(_peak_error)
            dict_error_function_parameters[str(_index_file)] = _local_dict

            if self.progress_bar_ui:
                self.progress_bar_ui.setValue(_index_file+1)
                QtGui.QGuiApplication.processEvents()

        self.peak_error_function_data = peak_error_function_data
        self.dict_error_function_parameters = dict_error_function_parameters
        self.peak_error_function_data_error = peak_error_function_data_error
        # self.water_intake_deltatime = delta_time

        if self.progress_bar_ui:
            self.progress_bar_ui.setVisible(False)
            QtGui.QGuiApplication.processEvents()

    def fitting_algorithm(self, ydata):
        fitting_xdata = np.arange(len(ydata))
        popt, pcov = curve_fit(self.fitting_function, fitting_xdata, ydata, maxfev=3000)
        return (popt, pcov)

    def calculate_using_sliding_average(self):
        list_data = self.list_data
        nbr_pixels = len(list_data[0])
        nbr_files = len(list_data)

        if self.ignore_first_dataset:
            _start_file = 1
            _end_file = nbr_files+1
        else:
            _start_file = 0
            _end_file = nbr_files

        if self.progress_bar_ui:
            self.progress_bar_ui.setMaximum(len(list_data))
            self.progress_bar_ui.setVisible(True)
            QtGui.QGuiApplication.processEvents()

        peak_sliding_average_data = []
        for _index_file in np.arange(_start_file, _end_file):
            _profile_data = list_data[_index_file]
            delta_array = []
            _o_range = MeanRangeCalculation(data=_profile_data)
            for _pixel in np.arange(0, nbr_pixels-5):
                _o_range.calculate_left_right_mean(pixel=_pixel)
                _o_range.calculate_delta_mean_square()
                delta_array.append(_o_range.delta_square)

            peak_value = delta_array.index(max(delta_array[0: nbr_pixels - 5]))
            peak_sliding_average_data.append(peak_value)

            if self.progress_bar_ui:
                self.progress_bar_ui.setValue(_index_file+1)
                QtGui.QGuiApplication.processEvents()

        self.peak_sliding_average_data = peak_sliding_average_data
        if self.progress_bar_ui:
            self.progress_bar_ui.setVisible(False)
            QtGui.QGuiApplication.processEvents()

    def get_peak_value_array(self, algorithm_selected='sliding_average'):
        if algorithm_selected == ListAlgorithm.sliding_average:
            return self.peak_sliding_average_data
        elif algorithm_selected == ListAlgorithm.change_point:
            return self.peak_change_point_data
        elif algorithm_selected == ListAlgorithm.error_function:
            return self.peak_error_function_data
        else:
            raise ValueError("algorithm not implemented yet!")

    @staticmethod
    def bin_data(data=None, bin_size=1, bin_type='median'):
        numpy_data = np.array(data).flatten()
        if bin_size == 1:
            return numpy_data

        nbr_bin = int(len(numpy_data) / bin_size)
        data_to_rebinned = numpy_data[0: nbr_bin * bin_size]
        binned_array_step1 = np.reshape(data_to_rebinned, [nbr_bin, bin_size])
        if bin_type == "mean":
            binned_array = np.mean(binned_array_step1, axis=1)
        elif bin_type == 'median':
            binned_array = np.median(binned_array_step1, axis=1)
        else:
            raise NotImplementedError("bin data type not supported!")

        return binned_array
