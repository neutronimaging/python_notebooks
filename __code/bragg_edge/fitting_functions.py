import numpy as np
from scipy import special


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
	exp_expression_2 = np.exp(-(ahkl + bhkl * wavelength))
	return exp_expression_1 * exp_expression_2

def kropff_bragg_peak_lambda(wavelength, a0, b0, ahkl, bhkl, lambdahkl, sigma, tau):
	"""Equation 4.3 and 4.4 found in Development and application of Bragg edge neutron transmission
	imaging on the IMAT beamline. Thesis by Ranggi Sahmura Ramadhan. June 2019
	:param
	wavelength (lambda)
	a0 fix parameter
	b0 fix parameter
	ahkl fix parameter
	bhkl fix parameter
	lambdahkl parameter to fit
	tau parameter to fit
	sigma parameter to fit
	"""
	def B(lambdahkl, sigma, tau, wavelength):
		const1 = (sigma*sigma) / (2 * tau*tau)
		const2 = sigma / tau

		part1 = special.erfc(-(wavelength - lambdahkl) / (np.sqrt(2) * sigma))
		part2 = np.exp((-(wavelength - lambdahkl) / tau) + const1)
		part3 = special.erfc((-(wavelength - lambdahkl)/(np.sqrt(2) * sigma)) + const2)
		return 0.5 * (part1 - part2 * part3)

	exp_expression_1 = np.exp(-(a0 + b0 * wavelength))
	exp_expression_2 = np.exp(-(ahkl + bhkl * wavelength))
	expression_3 = (1 - np.exp(-(ahkl + bhkl * wavelength)) * B(lambdahkl, sigma, tau, wavelength))

	return exp_expression_1 * (exp_expression_2 + expression_3)
