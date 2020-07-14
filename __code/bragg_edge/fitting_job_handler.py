from lmfit import Model
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

		list_yaxis = []
		for _key in self.parent.fitting_input_dictionary['rois'].keys():
			_yaxis = self.parent.fitting_input_dictionary['rois'][_key]['profile']
			full_fitting_yaxis = _yaxis[left_xaxis_index: right_xaxis_index]
			list_yaxis.append(full_fitting_yaxis[fitting_range[0]: fitting_range[1]])

		self.list_yaxis = list_yaxis

	def run(self):
		gmodel = Model(kropff_high_lambda, missing='drop', independent_vars=['wavelength'])

		wavelength = self.xaxis_to_fit
		result = {}
		for _index, yaxis in enumerate(self.list_yaxis):
			result[_index] = gmodel.fit(yaxis, wavelength=wavelength,
		                                    a0=1, b0=1)
		self.result = result

	def display_result(self):
		ui = self.parent.ui.fitting

		yaxis_fit = kropff_high_lambda(self.xaxis_to_fit,
		                               self.result[0].values['a0'],
		                               self.result[0].values['b0'])


		ui.plot(self.xaxis_to_fit, yaxis_fit, pen=(self.parent.fit_rgb[0],
                                            self.parent.fit_rgb[1],
                                            self.parent.fit_rgb[2]))





