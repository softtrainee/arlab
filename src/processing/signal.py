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
from traits.api import HasTraits, Str, Property, cached_property, Float
#============= standard library imports ========================
from numpy import array, polyfit
import random
#============= local library imports  ==========================


class Signal(HasTraits):
    isotope = Str
    detector = Str
    xs = None
    ys = None
    fit = 1

    value = Property(depends_on='_value')
    error = Property(depends_on='_error')
    _value = Float
    _error = Float

    def _set_error(self, v):
        self._error = v

    def _set_value(self, v):
        self._value = v

    @cached_property
    def _get_value(self):
        if self.xs:
            return polyfit(self.xs, self.ys, self.fit)[-1]
        else:
            return self._value

    @cached_property
    def _get_error(self):
        if self.xs:
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


class Baseline():
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
