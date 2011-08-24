#============= enthought library imports =======================
from traits.api import HasTraits, Any, Instance, Float, Event, Property, Bool
from traitsui.api import View, Item, Handler

import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import os
#============= local library imports  ==========================

from src.managers.manager import Manager
from src.helpers.paths import hidden_dir
from src.scripts.wait_dialog import WaitDialog
from threading import Thread, Condition
class Pulse(HasTraits):
    power = Float(1.1)
    duration = Float(1)
    wait_control = Instance(WaitDialog, transient = True)
    manager = Any(transient = True)
    def _duration_changed(self):
        self.wait_control.wtime = self.duration
        self.wait_control._current_time = self.duration

    def _wait_control_default(self):
        return WaitDialog(low_name = 0,
                          auto_start = False,
                          wtime = self.duration,
                          title = None

                          )
    def start(self):
        self._duration_changed()

        condition = Condition()
        condition.acquire()

        man = self.manager
        man.enable_laser()

        man.set_laser_power(self.power)
        self.wait_control.start(condition)
        condition.wait()
        condition.release()

        man.disable_laser()


    def traits_view(self):
        v = View(Item('power'),
                 Item('duration'),
               Item('wait_control', show_label = False, style = 'custom')
               )
        return v

class PulseHandler(Handler):
    def close(self, info, ok):
        info.object.dump_pulse()
        return ok

class LaserPulseManager(Manager):
    pulse_button = Event
    pulse_label = Property
    pulsing = Bool(False)
    pulse = Instance(Pulse)

    def dump_pulse(self):
        p = os.path.join(hidden_dir, 'pulse')
        with open(p, 'w') as f:
            pickle.dump(self.pulse, f)

    def _pulse_default(self):
        p = os.path.join(hidden_dir, 'pulse')
        if os.path.isfile(p):
            with open(p, 'r') as f:

                pul = pickle.load(f)
                pul.manager = self.parent
        else:
            pul = Pulse(manager = self.parent)

        return pul

    def _get_pulse_label(self):
        return 'Fire' if not self.pulsing else 'Stop'

    def _pulse_button_fired(self):

        t = Thread(target = self.pulse.start)
        t.start()

    def traits_view(self):
        v = View(self._button_factory('pulse_button', 'pulse_label', align = 'right'),
                 Item('pulse', show_label = False, style = 'custom'),
                 title = 'Pulse',
                 resizable = True,
                 handler = PulseHandler
                 )
        return v

if __name__ == '__main__':
    lp = LaserPulseManager()
    lp.configure_traits()
#============= EOF ====================================
