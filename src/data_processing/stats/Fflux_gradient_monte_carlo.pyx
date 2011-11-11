'''
	this is a cython version of flux_gradient_monte_carlo.py
	
	it is about 2x faster
'''
import numpy as np
cimport numpy as np

from numpy.random import normal

#this import adds ~1sec to execution
from src.data_processing.regression.multiple_linear_regressor import MultipleLinearRegressor
regressor = MultipleLinearRegressor()

def calc_flux(np.ndarray[np.float64_t, ndim=2] std_pos,
                np.ndarray[np.float64_t, ndim=2] unk_pos,
                np.ndarray[np.float64_t, ndim=2] std_js,
                np.ndarray[np.float64_t, ndim=2] unk_js,
                int ntrials,
                int nholes,
                ):

    cdef int nstd = std_js.shape[0]
    cdef np.ndarray[np.float64_t] perturbed_values = np.zeros(nstd)
    cdef np.ndarray[np.float64_t, ndim = 2] results = np.zeros((nholes, ntrials))
    cdef np.ndarray[np.float64_t] coeffs
    cdef np.ndarray[np.float64_t, ndim = 2] positions
    cdef np.ndarray[np.float64_t, ndim = 2] js
    for i in range(ntrials):
        for j in range(nstd):
            perturbed_values[j] = std_js[j][0] + std_js[j][1] * normal()

        coeffs = regressor.fordinary_regress(std_pos, perturbed_values)

        positions = np.vstack((std_pos, unk_pos))
        js = np.vstack((std_js, unk_js))

        for k in range(nholes):
            results[k][i] = js[k][0] - (coeffs[0] * positions[k][0] + coeffs[1] * positions[k][1] + coeffs[2])

    cdef np.ndarray[np.float64_t] pred_errors = np.zeros(nholes)
    for i in range(nholes):
        pred_errors[i] = get_mc_error(results[i], ntrials)

    return pred_errors

cdef get_mc_error(np.ndarray[np.float64_t] result, int ntrials):
    cdef double percentile1 = result[ntrials * 0.1587]
    cdef double percentile2 = result[ntrials * 0.8413]
    return (abs(percentile1) + abs(percentile2)) / 2
