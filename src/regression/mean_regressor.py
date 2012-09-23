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
#============= local library imports  ==========================
from base_regressor import BaseRegressor

class MeanRegressor(BaseRegressor):

    def _calculate_coefficients(self):
        return [self.ys.mean()]

    def _calculate_coefficient_errors(self):
        ys = self.ys
        std = ys.std()
        sem = 1 / (len(ys) ** 0.5) * std
        return [std, sem]

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
        return self.ys.std()

    @property
    def sem(self):
        return self.std * 1 / len(self.ys) ** 0.5
#============= EOF =============================================
