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



'''
see http://statsmodels.sourceforge.net/trunk/ for documentation

'''
#============= enthought library imports =======================

#============= standard library imports ========================
from numpy import ndarray, array
import scikits.statsmodels as sm
from scikits.statsmodels.sandbox.regression import wls_prediction_std

#============= local library imports  ==========================
class MultipleLinearRegressor():
    def fordinary_regress(self, observations, values):
        #returns only coeffs
        return self._regress_('OLS', observations, values, min_return=True)

    def weighted_regress(self, observations, values, weights=1):
        '''
            observations and values same as regress
            
            weights= array of 1/sigma**2
        '''
        return self._regress_('WLS', observations, values, weights=weights)

    def ordinary_regress(self, observations, values):
        '''
            for 2 predictor variables ie x,y in cartesian coords 
            observations should be column stacked array 
            obs=[[x1,y1],[x2,y2]...[xn,yn]]
            
            values = the measured value for (x,y)i
            
        '''
        return self._regress_('OLS', observations, values)

    def _regress_(self, kind, obs, values, min_return=False, **kw):
        if not isinstance(obs, ndarray):
            obs = array(obs)
        if not isinstance(values, ndarray):
            values = array(values)

        X = sm.add_constant(obs)
        model = getattr(sm, kind)(values, X, **kw)
        return self._format_results_(model.fit(), min_return)

    def get_predicted_value(self, x, y, result):
        coeffs = result.params
        if x or y is None:
            exog = None
        else:
            exog = array([x, y, coeffs[0] * x + coeffs[1] * y + coeffs[2]])

        prestd, lc, uc = wls_prediction_std(result, exog=exog)
        return prestd[0], lc[0], uc[0]

    def _format_results_(self, result, min_return):
        if min_return:
            return result.params

        covar_diag = result.cov_params().diagonal()
        n = result.nobs
        q = result.df_model
        ssr = result.ssr
        sigma_fit = (ssr / ((n - 1) - q)) ** 0.5
        errors = sigma_fit * covar_diag

        return dict(result=result,
                    coefficients=result.params,
                    coefficient_errs=errors)


def test():
    m = MultipleLinearRegressor()
    positions = array([
                     [1, 1],
                     [1, -1],
                     [-1, -1],
                     [-1, 1],
                     ])
    heights = array([2, 2, -1, -1.1])
    weights = [1, 1, 1, 1]

    r = m.weighted_regress(positions, heights, weights=weights)
    print m.get_predicted_value(None, None, r['result'])

if __name__ == '__main__':
    test()
#============= EOF ====================================
