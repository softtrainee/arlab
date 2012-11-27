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
from numpy import array, polyval, asarray, where, std
#============= local library imports  ==========================
from src.loggable import Loggable
from tinv import tinv
from src.helpers.alphas import ALPHAS


class BaseRegressor(Loggable):
    xs = Array
    ys = Array
#    xs = Any
#    ys = Any
    xserr = Array
    yserr = Array

    dirty = Event
    coefficients = Property(depends_on='dirty, xs, ys')
    coefficient_errors = Property(depends_on='coefficients, xs, ys')
    _coefficients = List
    _coefficient_errors = List
    _result = None
    fit = Property
    _fit = None


    def percent_error(self, s, e):
        try:
            return abs(e / s * 100)
        except ZeroDivisionError:
            return 'Inf'

    def tostring(self, sig_figs=5, error_sig_figs=5):

        cs = self.coefficients
        ce = self.coefficient_errors

        pm = u'\u00b1'
        fmt = '{{}}={{:0.{}f}}{{}}{{:0.{}f}} ({{:0.2f}}%)'.format(sig_figs, error_sig_figs)
        s = ', '.join([fmt.format(a, ci, pm, cei, self.percent_error(ci, cei))
                       for a, ci, cei in zip(ALPHAS, cs, ce)
                       ])

        return s

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

    def calculate_devs(self):
        X = self.xs
        Y = self.ys
        return self.predict(X) - Y

    def calculate_outliers(self, n=2):
        devs = self.calculate_devs()
        dd = devs ** 2
        cd = abs(devs)
#        s = std(devs)
#        s = (dd.sum() / (devs.shape[0])) ** 0.5

        '''
            mass spec calculates error in fit as 
            see LeastSquares.CalcResidualsAndFitError
            
            SigmaFit=Sqrt(SumSqResid/((NP-1)-(q-1)))
  
            NP = number of points
            q= number of fit params... parabolic =3
        '''
        s = self.calculate_fit_std(dd.sum(), dd.shape[0])
#        q = self.fit
#        s = (dd.sum() / (n - q)) ** 0.5

        return where(cd > (s * n))[0]

    def calculate_fit_std(self, sum_sq_residuals, n):
        q = 0
        return (sum_sq_residuals / (n - q)) ** 0.5

    def calculate_ci(self, rx):
        if isinstance(rx, (float, int)):
            rx = [rx]
        X = self.xs
        Y = self.ys
        model = self.predict(X)
        rmodel = self.predict(rx)

        cors = self._calculate_confidence_interval(X, Y, model, rx, rmodel)
        lci, uci = zip(*[(yi - ci, yi + ci) for yi, ci in zip(rmodel, cors)])
        return asarray(lci), asarray(uci)

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
            return cors
#            lci, uci = zip(*[(yi - ci, yi + ci) for yi, ci in zip(rmodel, cors)])
#            return asarray(lci), asarray(uci)

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
        self.dirty = True

#    fit = property(fset=_set_fit, fget=_get_fit)
#            lower=[]
#                lower.append(rmodel[i] - cor)
#                upper.append(rmodel[i] + cor)
#============= EOF =============================================
