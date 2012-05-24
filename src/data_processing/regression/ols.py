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



#============= enthought library imports =======================

#============= standard library imports ========================
import numpy as np
import scikits.statsmodels.api as sm

#============= local library imports  ==========================

#============= views ===================================
class WLS(object):
    def __init__(self, x, y, w, fitdegree=1):
        order = fitdegree + 1
        self.X = np.asarray(x)
        self.Y = np.asarray(y)

        #weights = 1.0 / np.asarray(w)

        self._ols = sm.WLS(self.Y, np.vander(self.X, order))
        self.results = self._ols.results

        bse = self.results.bse

        n = len(x)
        print [b * (n ** 0.5 - 1) for b in bse]




class OLS(object):
    def __init__(self, x, y, fitdegree=1):
        order = fitdegree + 1
        self.X = np.asarray(x)
        self.Y = np.asarray(y)
        self._ols = sm.OLS(self.Y, np.vander(self.X, order))


        self.results = self._ols.fit()

    def get_coefficients(self):
        return self._get_result_param('params')

    def get_coefficient_standard_errors(self):
        #return np.sqrt(np.diagonal(self.results.cov_params()))
        return self.results.bse
    def get_residuals(self):
        return self._get_result_param('resid')

    def get_rsquared(self):
        return self._get_result_param('rsquared')

    def get_conf_int(self):
        return self._get_result_param('conf_int')

    def _get_result_param(self, name):
        return getattr(self.results, name)

if __name__ == '__main__':

    x = np.linspace(0, 10, 100)
    a = 1.1
    b = 2.3
    c = 3.4
    order = 3
    y = a * x ** 2 + b * x + c
    y[3] = 10
    y[5] = 100
    results = sm.OLS(y, np.vander(x, order))
    print dir(results.results)

    print results.results.params
    print results.results.pvalues

#============= EOF ====================================
