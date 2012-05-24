#===============================================================================
# Copyright 2011 Jake Ross
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
from traits.api import HasTraits, Any, Instance, Float, Event, \
     Property, Bool, on_trait_change
from traitsui.api import View, Item, Handler, HGroup, ButtonEditor, spring
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import os
from threading import Thread, Condition
#============= local library imports  ==========================
from src.managers.manager import Manager
from src.helpers.paths import hidden_dir
from src.scripts.wait_dialog import WaitDialog


class PulseHandler(Handler):
    def close(self, info, ok):
        info.object.dump_pulse()

        return ok


class Pulse(HasTraits):
    duration = Float(1)
    wait_control = Instance(WaitDialog, transient=True)
    manager = Any(transient=True)
    power = Float(1.1, auto_set=False, enter_set=True)

    pulse_button = Event
    pulse_label = Property(depends_on='pulsing')
    pulsing = Bool(False)
    enabled = Bool(False)

    disable_at_end = Bool(False)
    def dump_pulse(self):
        p = os.path.join(hidden_dir, 'pulse')
        with open(p, 'wb') as f:
            pickle.dump(self, f)

    @on_trait_change('manager:enabled')
    def upad(self, obj, name, old, new):
        self.enabled = new

    def _power_changed(self):
        if self.pulsing and self.manager:
            self.manager.set_laser_power(self.power)

    def _duration_changed(self):
        self.wait_control.wtime = self.duration
        self.wait_control._current_time = self.duration

    def _wait_control_default(self):
        return WaitDialog(low_name=0,
                          auto_start=False,
                          wtime=self.duration,
                          title=None
                          )
    def start(self):
        self._duration_changed()

        condition = Condition()

        condition.acquire()

        man = self.manager
        if man is not None:
            #man.enable_laser()
            man.set_laser_power(self.power)

        self.wait_control.start(condition)
        condition.wait()
        condition.release()
        self.pulsing = False

        if man is not None:
            if self.disable_at_end:
                man.disable_laser()
            else:
                man.set_laser_power(0)

    def _get_pulse_label(self):
        return 'Fire' if not self.pulsing else 'Stop'

    def _pulse_button_fired(self):
        if self.pulsing:
            self.pulsing = False
            self.wait_control.current_time = -1
        else:
            self.pulsing = True
            t = Thread(target=self.start)
            t.start()

    def traits_view(self):
        v = View(
                 HGroup(Item('power'), spring, Item('pulse_button',
                                            editor=ButtonEditor(label_value='pulse_label'),
                                            show_label=False,
                                            enabled_when='object.enabled'
                                            )),

                 Item('duration'),
               Item('wait_control', show_label=False, style='custom'),
               kind='live',
               handler=PulseHandler()
               )
        return v


#class LaserPulseManager(Manager):
##    pulse_button = Event
##    pulse_label = Property
##    pulsing = Bool(False)
#    pulse = Instance(Pulse)
#
#    def dump_pulse(self):
#        p = os.path.join(hidden_dir, 'pulse')
#        with open(p, 'w') as f:
#            pickle.dump(self.pulse, f)
#
#    def _pulse_default(self):
#        p = os.path.join(hidden_dir, 'pulse')
#        if os.path.isfile(p):
#            with open(p, 'r') as f:
#                try:
#                    pul = pickle.load(f)
#                    pul.manager = self.parent
#                except pickle.PickleError:
#                    pul = Pulse(manager=self.parent)
#        else:
#            pul = Pulse(manager=self.parent)
##        pul = Pulse(manager=self.parent)
#
#        return pul
#
#    def standalone_view(self):
#        v = View(#self._button_factory('pulse_button', 'pulse_label', align='right'),
#                 Item('pulse', show_label=False, style='custom'),
#                 title='Pulse',
#                 resizable=True,
#                 handler=PulseHandler
#                 )
#        return v
#
#
#if __name__ == '__main__':
#    lp = LaserPulseManager()
#    lp.configure_traits()
#============= EOF ====================================
