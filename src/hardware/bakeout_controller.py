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
from traits.api import List, Event, Float, Str, Instance, Bool, Property
from traitsui.api import View, Item, EnumEditor, spring, HGroup, Label, VGroup, Spring
#from pyface.timer.api import Timer
#============= standard library imports ========================
import time
import os
#============= local library imports  ==========================
from src.helpers.timer import Timer
from src.scripts.bakeout_script import BakeoutScript
from src.led.led import LED
from src.led.led_editor import LEDEditor
from src.helpers import paths
from watlow_ezzone import WatlowEZZone


class BakeoutMonitor():
    pass


class BakeoutController(WatlowEZZone):
    '''
        
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

    setpoint = Float(enter_set=True, auto_set=False)

    scripts = List()
    script = Str('---')
    led = Instance(LED, ())
    alive = Bool(False)
    active = Bool(False)
    cnt = 0
    ramp_scale = None

    update_interval = Float(1)
    process_value_flag = Event

    _active_script = None
    _oduration = 0

    record_process = Bool(False)

    max_output = Property(Float(enter_set=True, auto_set=False),
                          depends_on='_max_output')
    _max_output = Float

    def _record_process_changed(self):
        if self.record_process:
            if self._duration < 0.0001:
                self._duration = 100

    def _validate_max_output(self, v):
        try:
            return float(v)
        except Exception:
            pass

    def _set_max_output(self, v):
        self._max_output = v
        self.set_high_power_scale(v)

    def _get_max_output(self):
        return self._max_output

    def initialization_hook(self):
        '''
            suppress the normal initialization querys
            they are not necessary for the bakeout manager currently
        '''
        #read the current max output setting
        self._max_output = self.read_high_power_scale()

#    def _program_memory_block(self):
#        '''
#            see watlow ez zone pm communications rev b nov 07
#            page 5
#            User programmable memory blocks
#        ''' 
#        self.memory_block_len = 4 
#        self.info('programming memory block. start address:{}, len: {}'.format(self.memory_block_address, self.memory_block_len))
#
#        r=self.read(self.memory_block_address-160, nregisters=1, response_type='int')
#        self.info('{} pointing to {}'.format(self.memory_block_address-160, r))
#
#        r=self.read(self.memory_block_address+2-160, nregisters=1, response_type='int')
#        self.info('{} pointing to {}'.format(self.memory_block_address+2-160, r))
#
#        #set address block 200-203 to hold the process value and the heat power
#        #self.set_assembly_definition_address(self.memory_block_address, 360) #process value
#        #self.set_assembly_definition_address(self.memory_block_address + 1, 360) #process value
#        self.set_assembly_definition_address(160 + 40, 360) #process value
#        #self.set_assembly_definition_address(160 + 61, 361) #process value
#        
#        self.info('finish program memory block')
#        #self.set_assembly_definition_address(self.memory_block_address + 2, 1904) #heat power
#        #self.set_assembly_definition_address(self.memory_block_address + 3, 1904) #heat power
# 
#        #print self.read(82, nregisters=1, response_type='int')
#        #print self.read(80, nregisters=1, response_type='int')
#        #
#        #print self.read(85, nregisters=1, response_type='int')
#        #print self.read(83, nregisters=1, response_type='int')
#        #print self.read(81, nregisters=1, response_type='int')
#        
#        #now process value and heat power can be read with a single command
#        #self.read(200, nregisters=4, response_type='float')

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
            if self._active_script is not None:
                self._active_script._alive = False

            self.set_closed_loop_setpoint(0)

    def load_additional_args(self, config):
        '''
        '''
        self.load_scripts()
        return True

    def load_scripts(self):
        sd = os.path.join(paths.scripts_dir, 'bakeoutscripts')
        files = os.listdir(sd)
        self.scripts = ['---'] + [f for f in files
                    if not os.path.basename(f).startswith('.') and
                        os.path.isfile(os.path.join(sd, f)) and
                         os.path.splitext(f)[1] in ['.bo']]

    def ok_to_run(self):
        ok = True
        if not self.record_process:
            if self.script == '---':
                ok = not (self.setpoint == 0 or self.duration == 0)
        else:
            ok = not self.duration == 0

        return ok

    def run(self):
        '''
        '''
        self.cnt = 0
        self.start_time = time.time()
        self.active = True
        self.alive = True

        #set led to green
        self.led.state = 'green'
        if self.script == '---':
            self.set_control_mode('closed')
            self.set_closed_loop_setpoint(self.setpoint)

            self._oduration = self._duration
#            self._timer = Timer(self.update_interval * 1000., self._update_)

        else:
            t = BakeoutScript(source_dir=os.path.join(paths.scripts_dir,
                                                      'bakeoutscripts'),
                                 file_name=self.script,
                                 controller=self)
            t.bootstrap()
            self._active_script = t
        self._timer = Timer(self.update_interval * 1000., self._update_)

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
        scalemap = {'h': 39,
                  'm': 57}

        if 'value' in scalemap:
            self.info('setting ramp scale = {}'.format(value))
            value = scalemap[value]
            register = 2188
            self.write(register, value, nregisters=2, **kw)

    def set_ramp_action(self, value, **kw):
        '''
        '''
        rampmap = {'off': 62,
                 'startup': 88,
                 'setpoint': 1647,
                 'both': 13}

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

    def end(self, user_kill=False, script_kill=False, msg=None, error=None):
        if self.isActive() and self.isAlive():
            if hasattr(self, '_timer'):
                self._timer.Stop()

            if self._active_script is not None:
                if not script_kill:
                    self._active_script.kill_script()
                    self._active_script = None

            self.led.state = 0
            if msg is None:
                msg = 'bakeout finished'

            func = self.info
            if user_kill:
                msg = '{} - Canceled by user'.format(msg)
            elif error:
                msg = error
                func = self.warning

            self.kill()

            func(msg)
            self.alive = False
            self.active = False

#            self.process_value = 0

#    def complex_query(self, **kw):
#        if 'verbose' in kw and kw['verbose']:
#            self.info('Do complex query')
#
#        t = self.read_process_value(1, **kw)
#        hp = self.read_heat_power(**kw)
#        
#        #data = self.read(self.memory_block_address, nregisters=self.memory_block_len, response_type='float', verbose=True)
#        data = None
#        if data is not None:
#            t = data[0]
#            hp = data[1]
#            
#        if self.simulation:
##            t = 4 + self.closed_loop_setpoint
#            t = self.get_random_value() + self.closed_loop_setpoint
#            hp = self.get_random_value()
#            time.sleep(0.25)
#            
#        try:
#            self.heat_power_value = hp
#            self.process_value = t
#            self.process_value_flag = True
#        except (ValueError, TypeError, UnboundLocalError), e:
#            print e

    def get_temp_and_power(self, **kw):
        kw['verbose'] = True
        pr = WatlowEZZone.get_temp_and_power(self, **kw)
        self.process_value_flag = True
        return pr

    def get_temperature(self, **kw):
        t = WatlowEZZone.get_temperature(self, **kw)
        self.process_value_flag = True
        return t
#    def complex_query(self, **kw):
#        if 'verbose' in kw and kw['verbose']:
#            self.info('Do complex query')
#
#        t = self.read_process_value(1, **kw)
#        hp = self.read_heat_power(**kw)
#        
#        #data = self.read(self.memory_block_address, nregisters=self.memory_block_len, response_type='float', verbose=True)
#        data = None
#        if data is not None:
#            t = data[0]
#            hp = data[1]
#            
#        if self.simulation:
##            t = 4 + self.closed_loop_setpoint
#            t = self.get_random_value() + self.closed_loop_setpoint
#            hp = self.get_random_value()
#            time.sleep(0.25)
#        try:
#            self.heat_power_value = hp
#            self.process_value = t
#            self.process_value_flag = True
#        except (ValueError, TypeError), e:
#            print e

#        if t is not None and hp is not None:
#            try:
#                hp = float(hp)
#                self.heat_power = hp
#                
#                t = float(t)
#                self.process_value = t
#                self.process_value_flag = True
#                
#                
#                return t, hp
#            except ValueError, TypeError:
#                pass

    def _update_(self):
        '''
        '''

        self.cnt += self.update_interval
        nsecs = 15
        if self.cnt >= nsecs:
            self._duration -= (nsecs + self.cnt % nsecs) / 3600.
            self.cnt = 0

        #self.get_temperature(verbose=False)
        #self.complex_query(verbose=False)
        self.get_temp_and_power(verbose=False)
        if self._active_script is None:
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
#                                   spring,
                                   Label(self.name[-1]),
                                  # spring,
                                   Item('led', editor=LEDEditor(),
                                        show_label=False, style='custom'),
                                    springy=True
                            ),
                            springy=True
                            )
            process_grp = HGroup(
                                 Spring(width=35, springy=False),
                                 Label('Temp. (C)'),
                                 spring,
                                   Item('process_value', show_label=False,
                                  style='readonly', format_str='%0.1f'),
#                                   spring,
                                   Item('record_process', show_label=False),
                                   springy=False
                                   )
        else:
            header_grp = HGroup(
                            HGroup(
                                Label(self.name[-1]),
                                Item('led', editor=LEDEditor(),
                                        show_label=False, style='custom'),
                                springy=True
                                ))
            process_grp = HGroup(
                                   spring,
                                   Item('process_value', label='Temp (C)',
                                        show_label=False,
                                  style='readonly', format_str='%0.1f'),
#                                   spring,
                                   Item('record_process', show_label=False),
                                   springy=False
                                   )
        v = View(
                 VGroup(
                    header_grp,
                    VGroup(
                            Item('script', show_label=False,
                                 editor=EnumEditor(name='scripts')),
                            Item('duration', label='Duration (hrs)',
                                 show_label=show_label,
                                 enabled_when='script=="---"',
                                 format_str='%0.3f'),
                            Item('setpoint', label='Setpoint (C)',
                                  show_label=show_label,
                                  enabled_when='script=="---"',
                                  format_str='%0.2f'),
                            Item('max_output', label='Max.Out (%)',
                                 format_str='%0.2f',
                                 show_label=show_label,
                                 enabled_when='not object.alive'),
                            process_grp
                            )
                        )
               )
        return v
#============= EOF ====================================
