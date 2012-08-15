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
from traits.api import HasTraits, Bool, Property, Str, Float, CInt
from traitsui.api import View, Item, HGroup, spring
#============= standard library imports ========================
#============= local library imports  ==========================
from src.helpers.timer import Timer as PTimer
from threading import Timer
from time import time

def convert_to_bool(v):
    try:
        v = float(v)
        return bool(v)
    except:
        return v.lower().strip() in ['t', 'true', 'on']

#@todo: convert to HasTraits
class Flag(HasTraits):
    name = Str
    _set = Bool(False)
    display_state = Property(Bool, depends_on='_state')

    def traits_view(self):
        v = View(
                 HGroup(Item('name', show_label=False, style='readonly'),
                        spring,
                        Item('display_state', show_label=False)
                        )
               )
        return v


    def _get_display_state(self):
        return self._set

    def _set_display_state(self, v):
        self.set(v)

    def __init__(self, name, *args, **kw):
        self.name = name
        super(Flag, self).__init__(*args, **kw)

    def get(self):
        return int(self._set)

    def set(self, value):
        print value
        if isinstance(value, str):
            value = convert_to_bool(value)
        else:
            value = bool(value)
        self._set = value
        return True

    def clear(self):
        self._set = False

    def isSet(self):
        return self._set

class TimedFlag(Flag):
    duration = Float(1)
    _start_time = None

    _uperiod = 1000
#    def __init__(self, name, t):
#        super(TimedFlag, self).__init__(name)
#        self.duration = float(t)
    display_time = Property(depends_on='_time_remaining')
    _time_remaining = CInt(0)

    def clear(self):
        super(TimedFlag, self).clear()
        self.pt.Stop()

    def _get_display_time(self):
        return self._time_remaining

    def traits_view(self):
        v = View(
                 HGroup(Item('name', style='readonly'),
                        spring,
                        Item('display_time',
                             format_str='%03i', style='readonly'),
                        Item('display_state'),
                        show_labels=False
                        )
               )
        return v

    def set(self, value):
        set_duration = True
        if isinstance(value, bool):
            set_duration = False

        try:
            value = float(value)
        except ValueError:
            return 'Invalid flag value'

        super(TimedFlag, self).set(value)
        if self.isSet():
            if set_duration:
                self.duration = value
                self._time_remaining = value
            else:
                self._time_remaining = self.duration

            self._start_time = time()
            self.pt = PTimer(self._uperiod, self._update_time)
            t = Timer(self.duration, self.clear)
            t.start()

        return True

    def isStarted(self):
        return self._start_time is not None

    def get(self):
        t = 0
        if self.isSet() and self.isStarted():
            t = max(0, self.duration - (time() - self._start_time))

        return t

    def _update_time(self):
        self._time_remaining = round(self.get())

#============= EOF =============================================
