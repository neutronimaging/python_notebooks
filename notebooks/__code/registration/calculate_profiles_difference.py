import numpy as np

MAX_PIXEL_RANGE = 20


class CalculateProfilesDifference:

    # {'horizontal': {'profiles': {'0': {'xaxis': None, 'profile': None},
    #                              '1': {'xaxis': None, 'profile': None},
    #                              ..., },
    #                 'x0': 0,
    #                 'y0': 0,
    #                 'width': None,
    #                 'length': None,
    #                 'max_width': 50,
    #                 'min_width': 1
    #                 'max_length': 500,
    #                 'min_length': 10,
    #                 'color': <PyQt5.QtGui.QColor ...,
    #                 'color-peak': (255, 0, 0),
    #                 'yaxis': [],
    #                },
    #   ....
    #  'vertical': 'profiles': {'0': {'xaxis': None, 'profile': None},
    #                           '1': {'xaxis': None, 'profile': None},
    #   ....
    #  }
    roi = None

    def __init__(self, parent=None):
        self.parent = parent
        self.roi = self.parent.roi

    def run(self):

        # horizontal
        reference_profile = self.roi['horizontal']['profiles']['0']['profile']

        self.parent.offset['horizontal'] = []
        for _key in self.roi['horizontal']['profiles'].keys():

            _profile = self.roi['horizontal']['profiles'][_key]['profile']
            offset_found = CalculateProfilesDifference.calculate_pixel_offset(profile_reference=reference_profile,
                                                                              working_profile=_profile,
                                                                              max_pixel_range=MAX_PIXEL_RANGE)
            self.parent.offset['horizontal'].append(-offset_found)

        # vertical
        reference_profile = self.roi['vertical']['profiles']['0']['profile']

        self.parent.offset['vertical'] = []
        for _key in self.roi['vertical']['profiles'].keys():
            _profile = self.roi['vertical']['profiles'][_key]['profile']
            offset_found = CalculateProfilesDifference.calculate_pixel_offset(profile_reference=reference_profile,
                                                                              working_profile=_profile,
                                                                              max_pixel_range=MAX_PIXEL_RANGE)
            self.parent.offset['vertical'].append(-offset_found)

    @staticmethod
    def sum_abs_diff(profile_a, profile_b):
        list_diff = profile_a - profile_b
        abs_list_diff = [np.abs(_value) for _value in list_diff]
        return np.sum(abs_list_diff)

    @staticmethod
    def calculate_pixel_offset(profile_reference=None, working_profile=None, max_pixel_range=20):
        list_profiles = []
        for _offset in np.arange(-max_pixel_range, max_pixel_range):
            list_profiles.append(np.roll(working_profile, _offset))

        list_sum_abs_diff = []
        for _profile in list_profiles:
            list_sum_abs_diff.append(CalculateProfilesDifference.sum_abs_diff(_profile, profile_reference))

        min_value = np.min(list_sum_abs_diff)
        min_index = np.where(min_value == list_sum_abs_diff)[0][0]

        offset_found = max_pixel_range - min_index

        return offset_found
