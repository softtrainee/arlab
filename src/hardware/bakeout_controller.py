'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
from traits.api import List, Float, Str, Instance, Bool, Property
from traitsui.api import View, Item, EnumEditor, spring, HGroup, Label, VGroup
from pyface.timer.api import Timer

#============= standard library imports ========================
import time
import os
#============= local library imports  ==========================
from src.led.led import LED
from src.led.led_editor import LEDEditor
#from src.scripts.bakeout_timer_script import BakeoutTimerScript

from src.helpers import paths
from watlow_ezzone import WatlowEZZone
from src.scripts.bakeout_script import BakeoutScript
DUTY_CYCLE = False
class BakeoutController(WatlowEZZone):
    '''
        G{classtree}
        
        bakeout controller can be operated in one of two modes.
        
        Mode 1 is used when no script is specified and both a valid setpoint and duration are set.
        The controller will open loop set to the setpoint. After duration minutes have passed the 
        controller sets to 0
        
        Mode 2 is used when a script is set.
        The controller uses a BakeoutTimerScript to heat and cool ramp to setpoints.
        
        psuedo script
        goto_setpoint('heat')
        maintain()
        goto_setpoint('cool')
        
    '''
    duration = Property(Float(enter_set=True, auto_set=False),
                        depends_on='_duration')
    _duration = Float

    #setpoint = Property(depends_on = '_setpoint')
    #_setpoint = Float
    setpoint = Float(enter_set=True, auto_set=False)
    #temp = Float
    scripts = List()
    script = Str('---')
    led = Instance(LED, ())
    alive = Bool(False)
    active = Bool(False)
    cnt = 0
    ramp_scale = None
    
    update_interval = Float(1)
    def _setpoint_changed(self):
        if self.isAlive():
            self.set_closed_loop_setpoint(self.setpoint)

    def _get_duration(self):
        return self._duration

    def _set_duration(self, v):
        if self.isAlive():
            self._oduration = v
            self.start_time = time.time()

        self._duration = v

    def _validate_duration(self, v):
        try:
            value = float(v)
        except ValueError:
            value = self._duration

        return value

    def isAlive(self):
        return self.alive

    def isActive(self):
        return self.active

    def kill(self):
        if self.isAlive() and self.isActive():
            self.info('killing')
            self.set_closed_loop_setpoint(0)

    def load_additional_args(self, config):
        '''

        '''
        sd = os.path.join(paths.scripts_dir, 'bakeoutscripts')
        files = os.listdir(sd)

        self.scripts = ['---'] + [f for f in files
                    if not os.path.basename(f).startswith('.') and
                        os.path.isfile(os.path.join(sd, f)) and os.path.splitext(f)[1] in ['.bo' ]]
        return True
    def ok_to_run(self):
        ok = True
        if self.script == '---':
            ok = not (self.setpoint == 0 or self.duration == 0)

        return ok

    def run(self):
        '''
        '''
        self.cnt = 0
        self.start_time = time.time()
        self.active = True
        self.alive = True
        if self.script == '---':
            #if self.setpoint != 0:
            self.set_control_mode('closed')
            self.set_closed_loop_setpoint(self.setpoint)
#            self.alive = True
#            self.active = True
            self._oduration = self._duration
            self._timer = Timer(self.update_interval * 1000., self._update_)
            
            #set led to green
            self.led.state = 'green'

        else:
            
            t = BakeoutScript(source_dir=os.path.join(paths.scripts_dir, 'bakeoutscripts'),
                                 file_name=self.script,
                                 controller=self)
            t.bootstrap()
            self._active_script = t
            self._timer = Timer(self.update_interval * 1000., self._update2_)

    def ramp_to_setpoint(self, ramp, setpoint, scale):
        '''

        '''
        if scale is not None and scale != self.ramp_scale:
            self.ramp_scale = scale
            self.set_ramp_scale(scale)
            
        self.set_ramp_action('setpoint')
        self.set_ramp_rate(ramp)
        self.set_closed_loop_setpoint(setpoint)
        self.setpoint = setpoint

    def set_ramp_scale(self, value, **kw):
        '''

        '''

        scalemap = {'h':39,
                  'm':57}
        
        if 'value' in scalemap:
            self.info('setting ramp scale = {}'.format(value))
            value = scalemap[value]
            register = 2188
            self.write(register, value, nregisters=2, **kw)

    def set_ramp_action(self, value, **kw):
        '''
            
        '''
        rampmap = {'off':62,
                 'startup':88,
                 'setpoint':1647,
                 'both':13}

        if value in rampmap:
            self.info('setting ramp action = {}'.format(value))
            value = rampmap[value]
            register = 2186
            self.write(register, value, nregisters=2, **kw)

    def set_ramp_rate(self, value, **kw):
        '''
          
        '''
        self.info('setting ramp rate = {:0.3f}'.format(value))
        register = 2192
        self.write(register, value, nregisters=2, **kw)


    def end(self, user_kill=False, script_kill=False):
        if self.isActive() and self.isAlive():
            if hasattr(self, '_timer'):
                self._timer.Stop()

            if hasattr(self, '_active_script'):
                if not script_kill:
                    self._active_script.kill_script()

            self.led.state = 0
            msg = 'bakeout finished'
            if user_kill:
                msg = '%s - Canceled by user' % msg
                self.failure_reason = 'Canceled by user'

            self.kill()
            self.info(msg)
            self.alive = False

            self.process_value = 0

    def _update_(self):
        '''
        '''

        self.cnt += self.update_interval
        nsecs = 15
        if self.cnt == nsecs:
            self._duration -= nsecs / 3600.
            self.cnt = 0

        self.get_temperature(verbose=False)

        if DUTY_CYCLE:
        #make a duty cycle measurement
            self.duty_cycle_increment()

        if time.time() - self.start_time > self._oduration * 3600.:
            self.end()


    def _update2_(self):
        '''
        '''
        self.temp = self.get_temperature()


#============= views ===================================
    def traits_view(self):
        '''
        '''
        show_label = False
        if self.name.endswith('1'):
            show_label = True
            header_grp = HGroup(spring,
                            HGroup(
                                   Label(self.name[-1]),
                                  # spring,
                                   Item('led', editor=LEDEditor(),
                                        show_label=False, style='custom'),
                                    springy=True
                            ),
                            springy=True
                            )
        else:
            header_grp = HGroup(
                            HGroup(
                                Label(self.name[-1]),
                                Item('led', editor=LEDEditor(),
                                        show_label=False, style='custom'),
                                springy=True
                                ))

        v = View(
                 VGroup(
                    header_grp,
                    VGroup(
                            Item('script', show_label=False, editor=EnumEditor(values=self.scripts)),
                            Item('duration', label='Duration (hrs)', show_label=show_label, enabled_when='script=="---"', format_str='%0.3f'),
                            Item('setpoint', label='Setpoint (C)', show_label=show_label, enabled_when='script=="---"', format_str='%0.2f'),
                            Item('process_value', label='Temp (C)', show_label=show_label, style='readonly', format_str='%0.1f')
                            )
                        )
               )
        return v
#============= EOF ====================================
