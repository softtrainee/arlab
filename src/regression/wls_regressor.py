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
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
from numpy import asarray, vander
from statsmodels.api import WLS, OLS
#============= local library imports  ==========================
#from src.regression.base_regressor import BaseRegressor
from src.regression.ols_regressor import OLSRegressor
class WeightedPolynominalRegressor(OLSRegressor):
    def calculate(self):
        if not len(self.xs) or \
            not len(self.ys):
            return

        if len(self.xs) != len(self.ys):
            return

        xs = self.xs
        xs = asarray(xs)
        es = asarray(self.yserr)
        ys = self.ys

        X = self._get_X()
#        print ys.shape, X.shape
        self._wls = WLS(ys, X,
                        weights=1 / es ** 2
                        )
        self._result = self._wls.fit()
#        print self._result.summary()

#    def predict(self, x):
#        x = self._get_X(x)
#        rx = self._result.predict(x)
#        return rx
#    def _calculate_coefficients(self):
#============= EOF =============================================
