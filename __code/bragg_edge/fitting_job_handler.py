from lmfit import Model
from copy import deepcopy
import numpy as np

from __code.bragg_edge.fitting_functions import kropff_high_lambda


class FittingJobHandler:
	"""https://lmfit.github.io/lmfit-py/examples/example_Model_interface.html"""

	def __init__(self, parent=None):
		self.parent = parent

	def prepare(self):
		fitting_range = self.parent.kropff_fitting_range['high']
		xaxis = self.parent.fitting_input_dictionary['xaxis']['lambda'][0]
		[left_xaxis_index, right_xaxis_index] = self.parent.bragg_edge_range
		full_fitting_xaxis = xaxis[left_xaxis_index: right_xaxis_index]
		self.xaxis_to_fit = full_fitting_xaxis[fitting_range[0]: fitting_range[1]]

		list_yaxis_to_fit = []
		for _key in self.parent.fitting_input_dictionary['rois'].keys():
			_yaxis = self.parent.fitting_input_dictionary['rois'][_key]['profile']
			full_fitting_yaxis = _yaxis[left_xaxis_index: right_xaxis_index]
			list_yaxis_to_fit.append(full_fitting_yaxis[fitting_range[0]: fitting_range[1]])
		self.list_yaxis_to_fit = list_yaxis_to_fit

	def run_kropff_high_lambda(self):
		gmodel = Model(kropff_high_lambda, missing='drop', independent_vars=['wavelength'])

		wavelength = self.xaxis_to_fit
		for _index, yaxis in enumerate(self.list_yaxis_to_fit):
			_result = gmodel.fit(yaxis, wavelength=wavelength,
		                                a0=1, b0=1)
			a0 = _result.params['a0'].value
			a0_error = _result.params['a0'].stderr
			b0 = _result.params['b0'].value
			b0_error = _result.params['b0'].stderr

			yaxis_fitted = kropff_high_lambda(self.xaxis_to_fit,
			                                  a0, b0)

			result_dict = {'a0': a0, 'b0': b0,
			               'a0_error': a0_error,
			               'b0_error': b0_error,
			               'xaxis_to_fit': self.xaxis_to_fit,
			               'yaxis_fitted': yaxis_fitted}

			self.parent.fitting_input_dictionary['rois'][_index]['fitting']['kropff'] = {'high': deepcopy(result_dict)}
