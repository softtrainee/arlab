#===============================================================================
# Copyright 2011 Jake Ross
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================



##============= enthought library imports =======================
##from traits.api import HasTraits, on_trait_change,Str,Int,Float,Button
##from traitsui.api import View,Item,Group,HGroup,VGroup
#
##============= standard library imports ========================
#from pylab import *
#from numpy.random import normal
#from uncertainties import ufloat
#from src.data_processing.regression.multiple_linear_regressor import MultipleLinearRegressor
##============= local library imports  ==========================
#class MonteCarloError(Exception):
#    def __init__(self, msg):
#        self.msg = msg
#    def __str__(self):
#        return repr(self.msg)
#
#def test():
#    regressor = MultipleLinearRegressor()
#    ntrials = 10000
#    nholes = 12
#    std_holes_positions = array([(1.0, 0.0),
#                                 (0.50000000000000011, 0.8660254037844386),
#                                 (-0.49999999999999978, 0.86602540378443882),
#                                 (-1.0, 1.2246467991473532e-16),
#                                 (-0.50000000000000044, -0.86602540378443837),
#                                 (0.5, -0.8660254037844386)])
#
#    unknown_holes_positions = array([(0.86602540378443871, 0.49999999999999994),
#                                    (6.123233995736766e-17, 1.0),
#                                    (-0.86602540378443871, 0.49999999999999994),
#                                    (-0.8660254037844386, -0.50000000000000011),
#                                    (-1.8369701987210297e-16, -1.0),
#                                    (0.86602540378443837, -0.50000000000000044)])
#
#    unknown_holes_js = array([ufloat(a) for a in [(1, 0.5), (1, 0.5), (1, 0.5), (1, 0.5), (1, 0.5), (1, 0.5)]])
#    std_holes_js = array([ufloat(a) for a in [(1, 0.5), (1, 0.5), (1, 0.5), (1, 0.5), (1, 0.5), (1, 0.5)]])
#
#    nstd_holes = len(std_holes_js)
#    perturbed_values = zeros(nstd_holes)
#    results = zeros((nholes, ntrials))
#    for i in xrange(ntrials):
#        #perturb the values
#        for j in range(nstd_holes):
#            perturbation = normal()
#            perturbed_values[j] = std_holes_js[j].nominal_value + std_holes_js[j].std_dev()* perturbation
#
#        #recalculate
#        perturbed_params = regressor.ordinary_regress(std_holes_positions, perturbed_values)
#        coeffs = perturbed_params['coefficients']
#
#        #record the results for all holes
#        positions = vstack((std_holes_positions, unknown_holes_positions))
#        js = hstack((std_holes_js , unknown_holes_js))
#        for k in range(nholes):
#            x, y = positions[k]
#            nr = js[k].nominal_value - eval_coeffs(coeffs, x, y)
#            results[k][i] = nr
#
#    predicted_errors = zeros(nholes)
#    for i in range(nholes):
#        r = get_mc_error(i, results, ntrials)
#        predicted_errors[i] = r
#
#def get_mc_error(i, results, ntrials):
#    percentile1 = results[i][int(ntrials * 0.1587)]
#    percentile2 = results[i][int(ntrials * 0.8413)]
#    return (abs(percentile1) + abs(percentile2)) / 2
#
#def eval_coeffs(*args):
#    coeffs = args[0]
#    xs = args[1:] + (1,)
#    if len(xs) != len(coeffs):
#        raise MonteCarloError('len of coeffs and xs doesnt match')
#    func = lambda a: a[0] * a[1]
#
#    return sum(map(func, zip(coeffs, xs)))
#
#if __name__ == '__main__':
#    from timeit import Timer
#    t = Timer('test()', 'from __main__ import test')
#    print t.timeit(1)
##============= EOF ====================================
