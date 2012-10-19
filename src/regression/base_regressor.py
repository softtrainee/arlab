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
from traits.api import HasTraits, Array, List, Event, Property, cached_property, Any
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
import math
from numpy import array, polyval, asarray
#============= local library imports  ==========================
from src.loggable import Loggable
from tinv import tinv


class BaseRegressor(Loggable):
    xs = Array
    ys = Array
#    xs = Any
#    ys = Any
    xserr = Array
    yserr = Array

    dirty = Event
    coefficients = Property(depends_on='dirty')
    coefficient_errors = Property(depends_on='coefficients')
    _coefficients = List
    _coefficient_errors = List
    _result = None
    fit = Property
    _fit = None

    def predict(self, x):
        return x

    @cached_property
    def _get_coefficients(self):
        return self._calculate_coefficients()

    @cached_property
    def _get_coefficient_errors(self):
        return self._calculate_coefficient_errors()

    def _calculate_coefficients(self):
        raise NotImplementedError

    def _calculate_coefficient_errors(self):
        raise NotImplementedError

    def calculate_ci(self, rx):
        if isinstance(rx, (float, int)):
            rx = [rx]
        X = self.xs
        Y = self.ys
#        model = polyval(self.coefficients, X)
#        rmodel = polyval(self.coefficients, rx)
        model = self.predict(X)
        rmodel = self.predict(rx)
        return self._calculate_confidence_interval(X, Y, model, rx, rmodel)
#    def _calculate_confidence_interval(self, confidence, x, observations, model, rx, rmodel):

    def _calculate_confidence_interval(self,
                                       x,
                                       observations,
                                       model,
                                       rx,
                                       rmodel,
                                       confidence=95):

        alpha = 1.0 - confidence / 100.0

        n = len(observations)

        if n > 2:
            xm = x.mean()
            observations = array(observations)
            model = array(model)

#            syx = math.sqrt(1. / (n - 2) * ((observations - model) ** 2).sum())
#            ssx = ((x - xm) ** 2).sum()
            #ssx = sum([(xi - xm) ** 2 for xi in x])

            ti = tinv(alpha, n - 2)

            syx = self.syx
            ssx = self.ssx
#            for i, xi in enumerate(rx):
            def _calc_interval(xi):
                d = 1.0 / n + (xi - xm) ** 2 / ssx
                return ti * syx * math.sqrt(d)

            cors = [_calc_interval(xi) for xi in rx]
            lci, uci = zip(*[(yi - ci, yi + ci) for yi, ci in zip(rmodel, cors)])
            return asarray(lci), asarray(uci)

    @property
    def syx(self):
        n = len(self.xs)
        obs = self.ys
        model = self.predict(self.xs)
        return (1. / (n - 2) * ((obs - model) ** 2).sum()) ** 0.5

    @property
    def ssx(self):
        x = self.xs
        xm = self.xs.mean()
        return ((x - xm) ** 2).sum()

    def _get_fit(self):
        return self._fit

    def _set_fit(self, v):
        self._fit = v

#    fit = property(fset=_set_fit, fget=_get_fit)
#            lower=[]
#                lower.append(rmodel[i] - cor)
#                upper.append(rmodel[i] + cor)
#============= EOF =============================================
