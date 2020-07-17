import numpy as np
from copy import deepcopy

KROPFF_HIGH = {'a0': None, 'b0': None,
               'a0_error': None, 'b0_error': None,
               'xaxis_to_fit': None,
               'yaxis_fitted': None}

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
			                                    'low': None,
			                                    'bragg_peak': None,
			                                    },
			                        },
			             }
			fitting_input_dictionary['rois'][_roi_index] = deepcopy(_roi_dict)

		return fitting_input_dictionary
