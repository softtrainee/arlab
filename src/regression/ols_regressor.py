#===============================================================================
# Copyright 2012 Jake Ross
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

#============= enthought library imports =======================
from traits.api import HasTraits, Int, Property, on_trait_change
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
from numpy import polyval, polyfit, vander, asarray

from statsmodels.api import OLS
#============= local library imports  ==========================
from base_regressor import BaseRegressor

class OLSRegressor(BaseRegressor):
    degree = Property(depends_on='_degree')
    _degree = Int

#    @on_trait_change('xs,ys')
#    def _update_data(self):
#        self._ols = OLS(self.xs, vander(self.ys, self.degree + 1))
#        self._result = self._ols.fit()
#    def _xs_changed(self):
#            xs = asarray(self.xs)
#            ys = asarray(self.ys)
##            print len(xs), len(ys)
#            self._ols = OLS(ys, vander(xs, self.degree + 1))
#            self._result = self._ols.fit()
    def __degree_changed(self):
        self.calculate()

    def _xs_changed(self):
#        if len(self.xs) and len(self.ys):
        self.calculate()

    def _ys_changed(self):
        self.calculate()

    def calculate(self):
        '''
            vander is equivalent to sm.add_constant(np.column_stack((x**n,..x**2,x**1)))
            vander(x,n+1)
        '''
        if not len(self.xs) or \
            not len(self.ys):
            return
        if len(self.xs) != len(self.ys):
            return

        xs = asarray(self.xs)
        ys = asarray(self.ys)
#            print len(xs), len(ys)
#        print self.degree
#        print vander(xs, self.degree + 1)
        X = self._get_X(xs)
        self._ols = OLS(ys, vander(xs, self.degree + 1))
        self._result = self._ols.fit()
#        print self.degree, self._result.summary()

    def calculate_y(self, x):
        coeffs = self.coefficients
        return polyval(coeffs, x)

    def calculate_yerr(self, x):
        if abs(x) < 1e-14:
            return self.coefficient_errors[-1]
        return

    def calculate_x(self, y):
        return 0

    def _calculate_coefficients(self):
        '''
            params = [a,b,c]
            where y=ax**2+bx+c
        '''
#        print 'dsaffsadf', self._result.params
        return self._result.params
#        return polyfit(self.xs, self.ys, self.degree)

    def _calculate_coefficient_errors(self):
        return self._result.bse

    def _get_degree(self):
        return self._degree

    def _set_degree(self, d):
        if isinstance(d, str):
            d = d.lower()
            fits = ['linear', 'parabolic', 'cubic']
            d = fits.index(d) + 1
#        print 'set', d
        self._degree = d

    @property
    def summary(self):
        return self._result.summary()

def PolynomialRegressor(OLSRegressor):
    def _get_X(self, xs):
        return vander(xs, self.degree + 1)
#============= EOF =============================================
