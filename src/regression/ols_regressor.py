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
from numpy import polyval, polyfit, vander, asarray, column_stack, ones

from statsmodels.api import OLS

#============= local library imports  ==========================
from base_regressor import BaseRegressor

class OLSRegressor(BaseRegressor):
    degree = Property(depends_on='_degree')
    _degree = Int
    constant = None
#    _result = None
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

#        xs = asarray(self.xs)
        ys = asarray(self.ys)
#        self._ols = OLS(ys, vander(xs, self.degree + 1))
#        self._result = self._ols.fit()
#            print len(xs), len(ys)
#        print self.degree
#        print vander(xs, self.degree + 1)
        X = self._get_X()
        if X is not None:
            try:
                self._ols = OLS(ys, X)
                self._result = self._ols.fit()
            except Exception, e:
                print e
#                print 'X', X
#                print 'ys', ys
#        print self.degree, self._result.summary()
    def predict(self, pos):
        pos = asarray(pos)
##        print pos.shape
#        pos = pos.reshape((len(pos), 1))
#        print pos
#        coeffs = self.coefficients
#        print 'coeffs', coeffs
#        print 'value_at polyval', polyval(coeffs, pos)
#        print 'value_at predict', self._ols.predict(pos)
#        return polyval(coeffs, pos)
        X = self._get_X(xs=pos)
        if self._result:
            return self._result.predict(X)

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
        if self._result:
#        print 'dsaffsadf', self._result.params
            return self._result.params
#        return polyfit(self.xs, self.ys, self.degree)

    def _calculate_coefficient_errors(self):
        if self._result:
#            result = self._result
#            covar_diag = result.cov_params().diagonal()
#            n = result.nobs
#            q = result.df_model
#            ssr = result.ssr
#            sigma_fit = (ssr / ((n - 1) - q)) ** 0.5
#            errors = sigma_fit * covar_diag
#            print errors, self._result.bse
            return self._result.bse

#    def _calculate_confidence_interval(self, x):
#        return self._result.conf_int


    def _get_degree(self):
        return self._degree

    def _set_degree(self, d):
        if isinstance(d, str):
            d = d.lower()
            fits = ['linear', 'parabolic', 'cubic']
            d = fits.index(d) + 1

        if d is None:
            d = 1
#        print 'set', d
        self._degree = d

    @property
    def summary(self):
        return self._result.summary()

class PolynomialRegressor(OLSRegressor):
    def _get_X(self, xs=None):
        if xs is None:
            xs = asarray(self.xs)

        c = vander(xs, self.degree + 1)
        if self.constant:
            c[:, self.degree] *= self.constant
        return c


class MultipleLinearRegressor(OLSRegressor):
    '''
        xs=[(x1,y1),(x2,y2),...,(xn,yn)]
        ys=[z1,z2,z3,...,zn]
        
        if you have a list of x's and y's 
        X=array(zip(x,y))
        if you have a tuple of x,y pairs
        X=array(xy)
    '''

    def value_at(self, pos):
        '''
            pos should be (x,y)
        '''
        return self._ols.predict(asarray(pos))


    def _get_X(self):
        '''
           
        '''
        xs = self.xs
        xs = asarray(xs)
        r, c = xs.shape
        if c == 2:
            xs = column_stack((xs, ones(r)))
            return xs

    def _calculate_coefficient_errors(self):
        result = self._result
        covar_diag = result.cov_params().diagonal()
        n = result.nobs
        q = result.df_model
        ssr = result.ssr
        sigma_fit = (ssr / ((n - 1) - q)) ** 0.5
        errors = sigma_fit * covar_diag
        print errors, self._result.bse
        return errors


#        return dict(result=result,
#                    coefficients=result.params,
#                    coefficient_errs=errors)


if __name__ == '__main__':
    import numpy as np
    xs = np.linspace(0, 10, 20)
    bo = 4
    b1 = 3
    ei = np.random.rand(len(xs))
    ys = bo + b1 * xs + ei
    print ys
    m = PolynomialRegressor(xs=xs, ys=ys, degree=1)
    print m.value_at(5)
#============= EOF =============================================
