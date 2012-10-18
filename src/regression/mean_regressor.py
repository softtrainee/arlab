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
from traits.api import Array
#============= standard library imports ========================
from numpy import average, ones, asarray, float64
#============= local library imports  ==========================
from base_regressor import BaseRegressor

class MeanRegressor(BaseRegressor):
    ddof = 1
    def _calculate_coefficients(self):
        return [self.ys.mean()]

    def _calculate_coefficient_errors(self):
        return [self.std, self.sem]

    @property
    def summary(self):

        m = self.mean
        e = self.std
        sem = self.sem
        return '''mean={}
std={}
sem={}

'''.format(m, e, sem)

    @property
    def mean(self):
        return self.ys.mean()

    @property
    def std(self):
        '''
            mass spec uses ddof=1
            ddof=0 provides a maximum likelihood estimate of the variance for normally distributed variables
            ddof=1 unbiased estimator of the variance of the infinite population
        '''
        ys = asarray(self.ys, dtype=float64)
        return ys.std(ddof=self.ddof)

    @property
    def sem(self):
        return self.std * 1 / len(self.ys) ** 0.5

    def predict(self, xs, *args):
        return ones(asarray(xs).shape) * self.mean


class WeightedMeanRegressor(MeanRegressor):
    errors = Array
    @property
    def mean(self):
        return average(self.ys, weights=self.weights)

    @property
    def std(self):
        var = 1 / sum(self.weights)
        return var ** 0.5

    @property
    def weights(self):
        return 1 / self.errors ** 2


#============= EOF =============================================
