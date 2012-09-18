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
from src.data_processing.regression.regressor import Regressor
from uncertainties import ufloat
#============= local library imports  ==========================


class Signal(HasTraits):
    isotope = Str
    detector = Str
    xs = Array
    ys = Array
    fit = 1

    uvalue = Property(depends='value, error, _value, _error')
    value = Property(depends_on='_value')
    error = Property(depends_on='_error')
    _value = Float
    _error = Float
    regressor = Instance(Regressor, ())

    regression_dict = Property(depends_on='xs,ys')
    def _set_error(self, v):
        self._error = v

    def _set_value(self, v):
        self._value = v

    @cached_property
    def _get_uvalue(self):
        return ufloat((self.value, self.error))

    @cached_property
    def _get_regression_dict(self):
        return self.regressor._regress_(self.xs, self.ys, self.fit)

    @cached_property
    def _get_value(self):

        if self.xs is not None and len(self.xs) > 0:
            rdict = self.regression_dict
            rdict = self.regressor._regress_(self.xs, self.ys, self.fit)
#            print 'cff', rdict['coefficients'], len(self.xs), len(self.ys), self.fit
            if rdict:
                return rdict['coefficients'][-1]
            else:
                return 0
#            return polyfit(self.xs, self.ys, self.fit)[-1]
        else:
            return self._value

    @cached_property
    def _get_error(self):
        if self.xs is not None and len(self.xs) > 0:
            rdict = self.regressor._regress_(self.xs, self.ys, self.fit)
#            print self.xs, self.ys
#            print 'afdas', rdict['coeff_errors'], len(self.xs), len(self.ys), self.fit
#            rdict = self.regression_dict
            if rdict:
                return rdict['coeff_errors'][-1]
            else:
                return random.random()
        else:
            return self._error

#    def _get_blank(self):
#        return self.blank_signal.value
#
#    def _get_blank_error(self):
#        return self.blank_signal.error
#
#    def _set_blank(self, v):
#        self.blank_signal._value = v
#
#    def _set_blank_error(self, v):
#        self.blank_signal._value_error = v
def preceeding_blanks(xs, ys, tm):
    ti = where(xs < tm)
    return ys[ti]

def bracketing_average_blanks(xs, ys, tm):
    pb, ab, _ = _bracketing_blanks(xs, ys, tm)
    return (pb + ab) / 2.0

def bracketing_interpolate_blanks(xs, ys, tm):
    pb, ab, ti = _bracketing_blanks(xs, ys, tm)
    x = [xs[ti], xs[ti + 1]]
    y = [pb, ab]
    return polyval(polyfit(x, y, 1), tm)

def _bracketing_blanks(ts, ys, tm):
    ti = where(ts < tm)[0][-1]
    pb = ys[ti]
    ab = ys[ti + 1]
    return pb, ab, ti

class Blank(Signal):
    timestamp = None
    @cached_property
    def _get_value(self):
        tm = self.timestamp
        fit = self.fit

        xsys = zip(self.xs, self.ys)
        xsys = array(sorted(xsys, key=lambda x: x[0]))
        xs, ys = zip(*xsys)
        if fit is 'preceeding':
            return preceeding_blanks(xs, ys, tm)
        elif fit is 'bracketing interpolate':
            return bracketing_interpolate_blanks(xs, ys, tm)
        elif fit is 'bracketing average':
            return bracketing_average_blanks(xs, ys, tm)
        else:
            return self.regressor.get_value(fit, (xs, ys), tm)

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
#============= EOF =============================================
