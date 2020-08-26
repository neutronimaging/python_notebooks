import numpy as np
from copy import deepcopy

KROPFF_HIGH = {'a0': None, 'b0': None,
               'a0_error': None, 'b0_error': None,
               'xaxis_to_fit': None,
               'yaxis_fitted': None}
KROPFF_LOW = {'ahkl': None, 'bhkl': None,
              'ahkl_error': None, 'bhkl_error': None,
              'xaxis_to_fit': None,
              'yaxis_fitted': None}
KROPFF_BRAGG_PEAK = {'tofhkl': None,
                     'tofhkl_error': None,
                     'tau': None,
                     'tau_error': None,
                     'sigma': None,
                     'sigma_error': None}
MARCHE_DOLLASE = {'d_spacing': None,
                  'd_spacing_error': None,
                  'alpha': None,
                  'alpha_error': None,
                  'sigma': None,
                  'sigma_error': None,
                  'a1': None,
                  'a1_error': None,
                  'a2': None,
                  'a2_error': None,
                  'a5': None,
                  'a5_error': None,
                  'a6': None,
                  'a6_error': None,
                  }


class PeakFittingInitialization:

	def __init__(self, parent=None):
		self.parent = parent

	def fitting_input_dictionary(self, nbr_rois=0):

		fitting_input_dictionary = {'xaxis': {},
									'rois': {},
		                            'fit_infos': {}}

		for _roi_index in np.arange(nbr_rois):
			_roi_dict = {'x0': None, 'y0': None,
			             'width': None, 'height': None,
			             'profile': None,
			             'fitting': {'kropff': {'high': deepcopy(KROPFF_HIGH),
			                                    'low': deepcopy(KROPFF_LOW),
			                                    'bragg_peak': deepcopy(KROPFF_BRAGG_PEAK),
			                                    },
			                         'march_dollase': deepcopy(MARCHE_DOLLASE),
			                        },
			             }
			fitting_input_dictionary['rois'][_roi_index] = deepcopy(_roi_dict)

		return fitting_input_dictionary
