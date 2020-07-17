import numpy as np


def kropff_high_lambda(wavelength, a0, b0):
	"""Equation 7.2 found in Development and application of Bragg edge neutron transmission
	imaging on the IMAT beamline. Thesis by Ranggi Sahmura Ramadhan. June 2019
	:param
	wavelength (lambda)
	a0 parameter to fit
	b0 parameter to fit
	"""
	exp_expression = np.exp(-(a0 + b0 * wavelength))
	return exp_expression


def kropff_low_lambda(wavelength, a0, b0, ahkl, bhkl):
	"""Equation 7.3 found in Development and application of Bragg edge neutron transmission
	imaging on the IMAT beamline. Thesis by Ranggi Sahmura Ramadhan. June 2019
	:param
	wavelength (lambda)
	a0 fix parameter
	b0 fix parameter
	ahkl parameter to fit
	bhkl parameter to fit
	"""
	exp_expression_1 = np.exp(-(a0 + b0 * wavelength))
	exp_expression_2 = 	np.exp(-(ahkl + bhkl * wavelength))
	return exp_expression_1 * exp_expression_2
