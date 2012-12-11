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
from traits.api import HasTraits, Str
from traitsui.api import View, Item, TableEditor
from src.regression.base_regressor import BaseRegressor
#============= standard library imports ========================
from numpy import where, polyval, polyfit, array
#============= local library imports  ==========================

class InterpolationRegressor(BaseRegressor):
    kind = Str
    def _calculate_coefficients(self):
        pass

    def predict(self, xs):
        kind = self.kind.replace(' ', '_')
        func = getattr(self, '{}_predictors'.format(kind))
        if isinstance(xs, (float, int)):
            xs = [xs]

        return [func(xi) for xi in xs]


    def preceeding_predictors(self, timestamp, attr='value'):
        xs = self.xs
        ys = self.ys
        es = self.yserr

        ti = where(xs < timestamp)[0][-1]
        if attr == 'value':
            return ys[ti]
        else:
            return es[ti]

    def bracketing_average_predictors(self, tm, attr='value'):
        try:
            pb, ab, _ = self._bracketing_predictors(tm, attr)

            return (pb + ab) / 2.0
        except TypeError:
            return 0

    def bracketing_interpolate_predictors(self, tm, attr='value'):
        xs = self.xs
        try:
            pb, ab, ti = self._bracketing_predictors(tm, attr)

            x = [xs[ti], xs[ti + 1]]
            y = [pb, ab]
            return polyval(polyfit(x, y, 1), tm)
        except TypeError:
            return 0

    def _bracketing_predictors(self, tm, attr):
        xs = self.xs
        ys = self.ys
        es = self.yserr

        try:
            ti = where(xs < tm)[0][-1]
            if attr == 'value':
                pb = ys[ti]
                ab = ys[ti + 1]
            else:
                pb = es[ti]
                ab = es[ti + 1]

            return pb, ab, ti
        except IndexError:
            return 0


#============= EOF =============================================
