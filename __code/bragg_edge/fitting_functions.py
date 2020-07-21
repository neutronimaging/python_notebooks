import numpy as np
from scipy import special


def kropff_high_tof(tof, a0, b0):
	"""Equation 7.2 found in Development and application of Bragg edge neutron transmission
	imaging on the IMAT beamline. Thesis by Ranggi Sahmura Ramadhan. June 2019
	:param
	tof (tof)
	a0 parameter to fit
	b0 parameter to fit
	"""
	exp_expression = np.exp(-(a0 + b0 * tof))
	return exp_expression


def kropff_low_tof(tof, a0, b0, ahkl, bhkl):
	"""Equation 7.3 found in Development and application of Bragg edge neutron transmission
	imaging on the IMAT beamline. Thesis by Ranggi Sahmura Ramadhan. June 2019
	:param
	tof (tof)
	a0 fix parameter
	b0 fix parameter
	ahkl parameter to fit
	bhkl parameter to fit
	"""
	exp_expression_1 = np.exp(-(a0 + b0 * tof))
	exp_expression_2 = np.exp(-(ahkl + bhkl * tof))
	return exp_expression_1 * exp_expression_2

def kropff_bragg_peak_tof(tof, a0, b0, ahkl, bhkl, tofhkl, sigma, tau):
	"""Equation 4.3 and 4.4 found in Development and application of Bragg edge neutron transmission
	imaging on the IMAT beamline. Thesis by Ranggi Sahmura Ramadhan. June 2019
	:param
	tof (tof)
	a0 fix parameter
	b0 fix parameter
	ahkl fix parameter
	bhkl fix parameter
	tofhkl parameter to fit
	tau parameter to fit
	sigma parameter to fit
	"""
	def B(tofhkl, sigma, tau, tof):
		const1 = (sigma*sigma) / (2 * tau*tau)
		const2 = sigma / tau

		part1 = special.erfc(-(tof - tofhkl) / (np.sqrt(2) * sigma))
		part2 = np.exp((-(tof - tofhkl) / tau) + const1)
		part3 = special.erfc((-(tof - tofhkl)/(np.sqrt(2) * sigma)) + const2)
		return 0.5 * (part1 - part2 * part3)

	exp_expression_1 = np.exp(-(a0 + b0 * tof))
	exp_expression_2 = np.exp(-(ahkl + bhkl * tof))
	expression_3 = (1 - np.exp(-(ahkl + bhkl * tof)) * B(tofhkl, sigma, tau, tof))

	return exp_expression_1 * (exp_expression_2 + expression_3)
