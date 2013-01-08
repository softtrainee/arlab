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
#============= standard library imports ========================
import time
from numpy import linspace
#============= local library imports  ==========================
from src.pyscripts.pyscript import verbose_skip, makeRegistry
from src.lasers.laser_managers.laser_manager import ILaserManager
from src.pyscripts.valve_pyscript import ValvePyScript
ELPROTOCOL = 'src.extraction_line.extraction_line_manager.ExtractionLineManager'


'''
    make a registry to hold all the commands exposed by ExtractionLinePyScript
    used when building the context
    see PyScript.get_context and get_command_register
    
'''
command_register = makeRegistry()

class ExtractionLinePyScript(ValvePyScript):
    _resource_flag = None

    def get_command_register(self):
        cm = super(ExtractionLinePyScript, self).get_command_register()
        return command_register.commands.items() + cm

    def _post_execute_hook(self):
        #remove ourselves from the script runner
        if self.runner:
            self.runner.scripts.remove(self)

    def _cancel_hook(self):
        if self._resource_flag:
            self._resource_flag.clear()
#===============================================================================
# properties
#===============================================================================
    @property
    def pattern(self):
        return self.get_context()['pattern']

    @property
    def analysis_type(self):
        return self.get_context()['analysis_type']

    @property
    def extract_device(self):
        return self.get_context()['extract_device']

    @property
    def tray(self):
        return self.get_context()['tray']

    @property
    def position(self):
        '''
            if position is 0 return None 
        '''
        pos = self.get_context()['position']
        if pos:
            return pos

    @property
    def extract_value(self):
        return self.get_context()['extract_value']
#===============================================================================
# commands
#===============================================================================

    @verbose_skip
    @command_register
    def set_x(self, value, velocity=''):
        self._set_axis('x', value, velocity)

    @verbose_skip
    @command_register
    def set_y(self, value, velocity=''):
        self._set_axis('y', value, velocity)

    @verbose_skip
    @command_register
    def set_z(self, value, velocity=''):
        self._set_axis('z', value, velocity)

    @verbose_skip
    @command_register
    def set_xy(self, value, velocity=''):
        self._set_axis('xy', value, velocity)

    def _set_axis(self, name, value, velocity):
        kw = dict(block=True)
        if velocity:
            kw['velocity'] = value

        success = self._manager_action([('set_{}'.format(name), (value,), kw)],
                                       protocol='src.lasers.laser_managers.laser_manager.ILaserManager',
                                       name=self.extract_device)
        if not success:
            self.info('{} move to position failed'.format(self.extract_device))
        else:
            self.info('move to position suceeded')
        return True

    @verbose_skip
    @command_register
    def move_to_position(self, position=''):
        if position == '':
            position = self.position

        if position:
            self.info('{} move to position {}'.format(self.extract_device, position))
            success = self._manager_action([('move_to_position', (position,), {})
                                            ],
                                          protocol='src.lasers.laser_managers.laser_manager.ILaserManager',
    #                                      protocol=ILaserManager,
                                          name=self.extract_device
                                          )
            if not success:
                self.info('{} move to position failed'.format(self.extract_device))
            else:
                self.info('move to position suceeded')
                return True
        else:
            self.info('not move required position is None')
            return True

    @verbose_skip
    @command_register
    def execute_pattern(self, pattern='', block=False):
        if pattern == '':
            pattern = self.pattern

        st = time.time()
        #set block=True to wait for pattern completion
        self._manager_action([('execute_pattern', pattern, {'block':block})],
                             name=self.extract_device,
                              protocol=ILaserManager)

        return time.time() - st

    @verbose_skip
    @command_register
    def set_tray(self, tray=''):
        if tray == '':
            tray = self.tray

        self.info('set tray to {}'.format(tray))
        result = self._manager_action([('set_stage_map', (tray), {})
                                        ],
                                      protocol=ILaserManager,
                                      name=self.extract_device
                                      )
        return result

    @verbose_skip
    @command_register
    def extract(self, power=''):
        if power == '':
            power = self.extract_value

        self.info('extract sample to power {}'.format(power))
        self._manager_action([('enable_laser', (), {}),
                                       ('set_laser_power', (power,), {})
                                       ],
                                      protocol=ILaserManager,
                                      name=self.extract_device
                             )

    @verbose_skip
    @command_register
    def end_extract(self):
        self._manager_action([('disable_laser', (), {})],
                             protocol=ILaserManager,
                             name=self.extract_device
                             )

    @verbose_skip
    @command_register
    def ramp(self, setpoint=0, rate=0, start=0, period=2):

        setpoint = float(setpoint)
        rate = float(rate)
        period = float(period)

        self.info('ramping from {} to {} rate= {} W/s, step_period= {} s'.format(start,
                                                                    setpoint,
                                                                    rate,
                                                                    period
                                                                    ))

        dT = setpoint - start
        dur = abs(dT / rate)

        if not self._manager_action([('enable_laser', (), {})],
                             protocol=ILaserManager,
                             name=self.extract_device)[0]:
            return

        check_period = 0.5
        samples_per_sec = 1 / float(period)
        n = int(dur * samples_per_sec)
        steps = linspace(start, setpoint, n)

        st = time.time()
        for i, si in enumerate(steps):
            if self._cancel:
                break
            self.info('ramp step {} of {}. setpoint={}'.format(i + 1, n, si))
            self._manager_action([('set_laser_power', (si,), {})],
                             protocol=ILaserManager,
                             name=self.extract_device
                             )
            for _ in xrange(int(period / check_period)):
                if self._cancel:
                    break
                time.sleep(check_period)

        return int(time.time() - st)

    @verbose_skip
    @command_register
    def acquire(self, name=None):
        if self.runner is None:
            return

        self.info('acquire {}'.format(name))
        r = self.runner.get_resource(name)

        s = r.isSet()
        if s:
            self.info('waiting for access')

        while s:

            if self._cancel:
                break
            self._sleep(0.1)
            s = r.isSet()

        if not self._cancel:
            self._resource_flag = r
            r.set()
            self.info('{} acquired'.format(name))

    @verbose_skip
    @command_register
    def wait(self, name=None, criterion=0):
        self.info('waiting for {} < {}'.format(name, criterion))
        r = self.runner.get_resource(name)

        cnt = 0
        resp = r.read()
        if resp is not None:
            while resp != criterion:

                #only verbose every 10s
                resp = r.read(verbose=cnt % 10 == 0)
                if resp is None:
                    continue

                time.sleep(1)
                cnt += 1
                if cnt > 100:
                    cnt = 0

        self.info('finished waiting')

    @verbose_skip
    @command_register
    def release(self, name=None):

        self.info('release {}'.format(name))
        r = self.runner.get_resource(name)
        r.clear()

    @verbose_skip
    @command_register
    def set_resource(self, name=None, value=1):
        r = self.runner.get_resource(name)
        r.set(value)

#============= EOF ====================================
#    @verbose_skip
#    def _m_open(self, name=None, description=''):
#
#        if description is None:
#            description = '---'
#
#        self.info('opening {} ({})'.format(name, description))
#
#        self._manager_action([('open_valve', (name,), dict(
#                                                      mode='script',
#                                                      description=description
#                                                      ))], protocol=ELPROTOCOL)
#
#    @verbose_skip
#    def close(self, name=None, description=''):
#
#        if description is None:
#            description = '---'
#
#        self.info('closing {} ({})'.format(name, description))
#        self._manager_action([('close_valve', (name,), dict(
#                                                      mode='script',
#                                                      description=description
#                                                      ))], protocol=ELPROTOCOL)
#    def get_context(self):
#        d = super(ExtractionLinePyScript, self).get_context()

#        #=======================================================================
#        #Parameters
#        # this are directly referencable in the script
#        # e.g if OverlapRuns:
#        #    or
#        #    move_to_hole(holeid)
#        #=======================================================================
#
#        d.update(self._context)
#        return d

#    def gosub(self, *args, **kw):
#        kw['analysis_type'] = self.analysis_type
#        kw['_context'] = self._context
#        super(ExtractionLinePyScript, self).gosub(*args, **kw)

#    @verbose_skip
#    def is_open(self, name=None, description=''):
#        self.info('is {} ({}) open?'.format(name, description))
#        result = self._get_valve_state(name, description)
#        if result:
#            return result[0] == True
#
#    @verbose_skip
#    def is_closed(self, name=None, description=''):
#        self.info('is {} ({}) closed?'.format(name, description))
#        result = self._get_valve_state(name, description)
#        if result:
#            return result[0] == False
#
#    def _get_valve_state(self, name, description):
#        return self._manager_action([('open_valve', (name,), dict(
#                                                      mode='script',
#                                                      description=description
#                                                      ))], protocol=ELPROTOCOL)
