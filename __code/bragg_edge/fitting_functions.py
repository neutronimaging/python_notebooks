import numpy as np
from scipy import special
import math


def kropff_high_lambda(lda, a0, b0):
	"""Equation 7.2 found in Development and application of Bragg edge neutron transmission
	imaging on the IMAT beamline. Thesis by Ranggi Sahmura Ramadhan. June 2019
	:param
	lda (Lambda - Angstroms)
	a0 parameter to fit
	b0 parameter to fit
	"""
	if (a0 == np.NaN) or (b0 == np.NaN):
		return None
	exp_expression = np.exp(-(a0 + b0 * lda))
	return exp_expression


def kropff_low_lambda(lda, a0, b0, ahkl, bhkl):
	"""Equation 7.3 found in Development and application of Bragg edge neutron transmission
	imaging on the IMAT beamline. Thesis by Ranggi Sahmura Ramadhan. June 2019
	:param
	lda (Lambda - Angstroms)
	a0 fix parameter
	b0 fix parameter
	ahkl parameter to fit
	bhkl parameter to fit
	"""
	if (a0 == np.NaN) or (b0 == np.NaN) or (ahkl == np.NaN) or (bhkl == np.NaN):
		return None
	exp_expression_1 = np.exp(-(a0 + b0 * lda))
	exp_expression_2 = np.exp(-(ahkl + bhkl * lda))
	return exp_expression_1 * exp_expression_2


def kropff_bragg_peak_tof(lda, a0, b0, ahkl, bhkl, ldahkl, sigma, tau):
	"""Equation 4.3 and 4.4 found in Development and application of Bragg edge neutron transmission
	imaging on the IMAT beamline. Thesis by Ranggi Sahmura Ramadhan. June 2019
	:param
	lda (Lambda - Angstroms)
	a0 fix parameter
	b0 fix parameter
	ahkl fix parameter
	bhkl fix parameter
	ldahkl parameter to fit
	tau parameter to fit
	sigma parameter to fit
	"""
	def B(ldahkl, sigma, tau, lda):
		const1 = (sigma*sigma) / (2 * tau*tau)
		const2 = sigma / tau

		part1 = special.erfc(-(lda - ldahkl) / (np.sqrt(2) * sigma))
		part2 = np.exp((-(lda - ldahkl) / tau) + const1)
		part3 = special.erfc((-(lda - ldahkl)/(np.sqrt(2) * sigma)) + const2)
		return 0.5 * (part1 - part2 * part3)

	exp_expression_1 = np.exp(-(a0 + b0 * lda))
	exp_expression_2 = np.exp(-(ahkl + bhkl * lda))

	final_part1 = (B(ldahkl, sigma, tau, lda) * exp_expression_1)
	final_part2 = (1 - B(ldahkl, sigma, tau, lda)) * exp_expression_1 * exp_expression_2

	return final_part1 + final_part2

def march_dollase_basic_fit(t, d_spacing, alpha, sigma, a1, a2):
    t0 = 2 * d_spacing
    term2 = special.erfc(-((t - t0) / (sigma * math.sqrt(2))) + sigma / alpha)
    term1 = np.exp((t - t0) / alpha + (sigma * sigma) / (2 * alpha * alpha))
    term0 = special.erfc(-((t - t0) / (sigma * math.sqrt(2))))

    y = a1 + a2 * (term0 - (term1 * term2))

    return y


def march_dollase_advanced_fit(t, d_spacing, alpha, sigma, a1, a2, a5, a6):
    t0 = 2 * d_spacing
    term0 = a2 * (t - a6)
    term1 = ((a5 - a2) / 2) * (t - a6)
    term3 = special.erfc(-((t - t0) / (sigma * math.sqrt(2))))
    term4 = np.exp(-((t - t0) / alpha) + ((sigma * sigma) / (2 * alpha * alpha)))
    term5 = special.erfc(-((t - t0) / (sigma * math.sqrt(2))) + sigma / alpha)

    y = a1 + term0 + term1 * (term3 - term4 * term5)

    return y
