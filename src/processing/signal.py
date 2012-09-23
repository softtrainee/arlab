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
    Instance, Array
#============= standard library imports ========================
from numpy import array, polyfit, polyval, where
import random
#from src.regression.regressor import Regressor
from uncertainties import ufloat
from src.regression.mean_regressor import MeanRegressor
from src.regression.ols_regressor import OLSRegressor
#============= local library imports  ==========================


class Signal(HasTraits):
    isotope = Str
    detector = Str
    xs = Array
    ys = Array
    fit = None

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
                reg = OLSRegressor(xs=self.xs, ys=self.ys, degree=self.fit)

        except Exception:
            reg = OLSRegressor(xs=self.xs, ys=self.ys, degree=self.fit)
        return reg

    @cached_property
    def _get_value(self):

        if self.xs is not None and len(self.xs) > 0:
            return self._get_regression_param('coefficients')
        else:
            return self._value

    @cached_property
    def _get_error(self):
        if self.xs is not None and len(self.xs) > 0:
            return self._get_regession_param('coefficient_errors')
        else:
            return self._error

    def _get_regression_param(self, name, ind= -1):
        return getattr(self.regressor, name)[ind]

def preceeding_blanks(xs, ys, tm):
    ti = where(xs < tm)
    return ys[ti]

def bracketing_average_blanks(xs, ys, tm):
    try:
        pb, ab, _ = _bracketing_blanks(xs, ys, tm)

        return (pb + ab) / 2.0
    except TypeError:
        return 0

def bracketing_interpolate_blanks(xs, ys, tm):
    try:
        pb, ab, ti = _bracketing_blanks(xs, ys, tm)

        x = [xs[ti], xs[ti + 1]]
        y = [pb, ab]
        return polyval(polyfit(x, y, 1), tm)
    except TypeError:
        return 0

def _bracketing_blanks(ts, ys, tm):
    try:
        ti = where(ts < tm)[0][-1]
        pb = ys[ti]
        ab = ys[ti + 1]
        return pb, ab, ti
    except IndexError:
        return 0

class Blank(Signal):
    timestamp = None
    @cached_property
    def _get_value(self):
        tm = self.timestamp
        fit = self.fit
        xs = self.xs
        ys = self.ys
        if fit and xs and ys:
            xsys = zip(self.xs, self.ys)
            xsys = array(sorted(xsys, key=lambda x: x[0]))
            xs, ys = zip(*xsys)
            if fit == 'preceeding':
                return preceeding_blanks(xs, ys, tm)
            elif fit == 'bracketing interpolate':
                return bracketing_interpolate_blanks(xs, ys, tm)
            elif fit == 'bracketing average':
                return bracketing_average_blanks(xs, ys, tm)
            else:
                return self.regressor.get_value(fit, (xs, ys), tm)
        else:
            return self._value

    def _get_error(self):
        return self._error

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


class Background(Signal):
    pass
#============= EOF =============================================
