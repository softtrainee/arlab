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
from traits.api import HasTraits, Str, Property, cached_property, Float, \
    Instance, Array, Event
#============= standard library imports ========================
from numpy import array, polyfit, polyval, where
import random
#from src.regression.regressor import Regressor
from uncertainties import ufloat
from src.regression.mean_regressor import MeanRegressor
from src.regression.ols_regressor import PolynomialRegressor
#============= local library imports  ==========================


class Signal(HasTraits):
    isotope = Str
    detector = Str
    xs = Array
    ys = Array
    fit = None
#    dirty = Event
    uvalue = Property(depends='value, error, _value, _error')
    value = Property(depends_on='_value')
    error = Property(depends_on='_error')
    _value = Float
    _error = Float
    regressor = Property(depends_on='xs,ys')

    def _set_error(self, v):
        self._error = v

    def _set_value(self, v):
        self._value = v

    @cached_property
    def _get_uvalue(self):
        return ufloat((self.value, self.error))

    @cached_property
    def _get_regressor(self):
        try:
            if 'average' in self.fit.lower():
                reg = MeanRegressor(xs=self.xs, ys=self.ys)
            else:
                reg = PolynomialRegressor(xs=self.xs, ys=self.ys, degree=self.fit)

        except Exception, e:
            reg = PolynomialRegressor(xs=self.xs, ys=self.ys, degree=self.fit)
        return reg

    @cached_property
    def _get_value(self):
        if self.xs is not None and len(self.xs) > 1:# and self.ys is not None:
#            if len(self.xs) > 2 and len(self.ys) > 2:
#            print self.xs
#            print self._get_regression_param('coefficients')
            return self._get_regression_param('coefficients')
        else:
            return self._value

    @cached_property
    def _get_error(self):
        if self.xs is not None and len(self.xs) > 1:
#            if len(self.xs) > 2 and len(self.ys) > 2:
            return self._get_regression_param('coefficient_errors')
        else:
            return self._error

    def _get_regression_param(self, name, ind= -1):
        return getattr(self.regressor, name)[ind]


class Baseline(Signal):
    @cached_property
    def _get_value(self):
        if self.ys:
            return array(self.ys).mean()
        else:
            return 0

    @cached_property
    def _get_error(self):
        if self.ys:
            return array(self.ys).std()
        else:
            return 0


def preceeding_predictors(xs, ys, es, tm, attr='value'):

    ti = where(xs < tm)[0][0]
    if attr == 'value':
        return ys[ti]
    else:
        return es[ti]

def bracketing_average_predictors(xs, ys, es, tm, attr='value'):
    try:
        pb, ab, _ = _bracketing_predictors(xs, ys, es, tm, attr)

        return (pb + ab) / 2.0
    except TypeError:
        return 0

def bracketing_interpolate_predictors(xs, ys, es, tm, attr='value'):
    try:
        pb, ab, ti = _bracketing_predictors(xs, ys, es, tm, attr)

        x = [xs[ti], xs[ti + 1]]
        y = [pb, ab]
        return polyval(polyfit(x, y, 1), tm)
    except TypeError:
        return 0

def _bracketing_predictors(ts, ys, es, tm, attr):
    try:
        ti = where(ts < tm)[0][-1]
        if attr == 'value':
            pb = ys[ti]
            ab = ys[ti + 1]
        else:
            pb = es[ti]
            ab = es[ti + 1]

        return pb, ab, ti
    except IndexError:
        return 0



class InterpolatedSignal(Signal):
    timestamp = None
    es = None
    @cached_property
    def _get_value(self):
        tm = self.timestamp
        fit = self.fit
        xs = self.xs
        ys = self.ys
        es = self.es
        if fit and xs is not None and ys is not None:
            xsyses = zip(xs, ys, es)
            xsyses = array(sorted(xsyses, key=lambda x: x[0]))
            xs, ys, es = zip(*xsyses)
            if fit == 'preceeding':
                return preceeding_predictors(xs, ys, es, tm)
            elif fit == 'bracketing interpolate':
                return bracketing_interpolate_predictors(xs, ys, es, tm)
            elif fit == 'bracketing average':
                v = bracketing_average_predictors(xs, ys, es, tm)
                return v
            else:
                v = self.regressor.predict([tm])[0]
                return v
        else:
            return self._value

    @cached_property
    def _get_error(self):
        tm = self.timestamp
        fit = self.fit
        xs = self.xs
        ys = self.ys
        es = self.es
        if fit and xs is not None and ys is not None:
            xsyses = zip(xs, ys, es)
            xsyses = array(sorted(xsyses, key=lambda x: x[0]))
            xs, ys, es = zip(*xsyses)
            if fit == 'preceeding':
                return preceeding_predictors(xs, ys, es, tm, attr='error')
            elif fit == 'bracketing interpolate':
                return bracketing_interpolate_predictors(xs, ys, es, tm, attr='error')
            elif fit == 'bracketing average':
                return bracketing_average_predictors(xs, ys, es, tm, attr='error')
            else:

                try:
                    reg = self.regressor
                    if 'average' in fit:

                        if fit.endswith('SEM'):
                            n = reg.sem
                        else:
                            n = reg.std
                    else:

                        t = tm - xs[0]
                        try:
                            lci, uci = reg.calculate_ci([t])
                            n = (lci[0] + uci[0]) / 2.0
                        except TypeError, e:
                            n = 2
                            #could not compute confidence interval
                            #use preceeding error
#                            n = preceeding_predictors(ts=ts, *args, attr='error')
                except IndexError:
                    n = 0.1

                return n
#                return self.regressor.get_value(fit, (xs, ys), tm)
        else:
            return self._error



class Blank(InterpolatedSignal):
    pass



class Background(InterpolatedSignal):
    pass
#============= EOF =============================================
