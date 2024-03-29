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
from traits.api import List
#============= standard library imports ========================
import time
from numpy import linspace
#============= local library imports  ==========================
from src.pyscripts.pyscript import verbose_skip, makeRegistry
from src.lasers.laser_managers.ilaser_manager import ILaserManager
# from src.lasers.laser_managers.extraction_device import ILaserManager
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
    info_color = 'red'
    snapshot_paths = List

    def get_command_register(self):
        cm = super(ExtractionLinePyScript, self).get_command_register()
        return command_register.commands.items() + cm

    def _post_execute_hook(self):
        # remove ourselves from the script runner
        if self.runner:
            self.runner.scripts.remove(self)

    def _cancel_hook(self):
        if self._resource_flag:
            self._resource_flag.clear()

    def set_default_context(self):
        '''
            provide default values for all the properties exposed in the script
        '''
        self.info('%%%%%%%%%%%%%%%%%%%%%%% setting default context')

        self.setup_context(analysis_type='',
                           position='',
                           pattern='',
                           extract_device='',
                           extract_value=0,
                           extract_units='',
                           tray='',
                           ramp_rate='',
                           duration=0,
                           cleanup=0,
                           run_identifier='default_runid'
                           )
#===============================================================================
# properties
#===============================================================================
    @property
    def pattern(self):
        return self.get_context()['pattern']

    @property
    def analysis_type(self):
        return self.get_context()['analysis_type']
#
    @property
    def extract_device(self):
        return self.get_context()['extract_device']
#
    @property
    def tray(self):
        return self.get_context()['tray']
#
    @property
    def position(self):
        '''
            if position is 0 return None
        '''
        pos = self.get_context()['position']
        if pos:
            return pos
#
    @property
    def extract_value(self):
        return self.get_context()['extract_value']

    @property
    def extract_units(self):
        return self.get_context()['extract_units']
#===============================================================================
# commands
#===============================================================================
    @verbose_skip
    @command_register
    def snapshot(self, format_str=''):
        if format_str == '':
            format_str = '{}'

        name = format_str.format(self.run_identifier)

        ps = self._manager_action(['take_snapshot', (name,), {}],
                             name=self.extract_device,
                             protocol=ILaserManager)
        if ps:
            self.snapshot_paths.append(ps[0])

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
                                       protocol=ILaserManager,
#                                       protocol='src.lasers.laser_managers.laser_manager.IExtractionDevice',
                                       name=self.extract_device)
        if not success:
            self.info('{} move to position failed'.format(self.extract_device))
        else:
            self.info('move to position suceeded')
        return True


    @verbose_skip
    @command_register
    def set_motor_lock(self, name='', value=''):
        if name and value is not '':
            l = 'YES' if value else 'NO'
            self.info('set motor lock to {}'.format(name, l))
            self._manager_action([('set_motor_lock', (name, value), {})],
                                 protocol=ILaserManager,
                                 name=self.extract_device)

    @verbose_skip
    @command_register
    def set_motor(self, name='', value=''):
        if name and value is not '':
            self.info('set motor {} to {}'.format(name, value))
            self._manager_action([('set_motor', (name, value), {})],
                                 protocol=ILaserManager,
                                 name=self.extract_device)


    @verbose_skip
    @command_register
    def move_to_position(self, position=''):
        if position == '':
            position = self.position

        if position:
            position_ok = True
            if isinstance(position, (list, tuple)):
                position_ok = all(position)
        else:
            position_ok = False

        if position_ok:
#            print self.extract_device, 'asdfasfdasdf'
            self.info('{} move to position {}'.format(self.extract_device, position))
            success = self._manager_action([('move_to_position', (position,), {})
                                            ],
#                                          protocol='src.lasers.laser_managers.laser_manager.ILaserManager',
                                          protocol=ILaserManager,
                                          name=self.extract_device
                                          )
            if not success:
                self.info('{} move to position failed'.format(self.extract_device))
            else:
                self.info('move to position suceeded')
                return True
        else:
            self.info('move not required. position is None')
            return True

    @verbose_skip
    @command_register
    def execute_pattern(self, pattern='', block=False):
        if pattern == '':
            pattern = self.pattern

        st = time.time()
        # set block=True to wait for pattern completion
        self._manager_action([('execute_pattern', (pattern,), {'block':block})],
                             name=self.extract_device,
                              protocol=ILaserManager)

        return time.time() - st

    @verbose_skip
    @command_register
    def set_tray(self, tray=''):
        if tray == '':
            tray = self.tray

        self.info('set tray to {}'.format(tray))
        result = self._manager_action([('set_stage_map', (tray,), {})
                                        ],
                                      protocol=ILaserManager,
                                      name=self.extract_device
                                      )
        return result

    @verbose_skip
    @command_register
    def moving_extract(self, value='', name=''):
        '''
            p=Point
            l=Trace path in continuous mode
            s=Trace path in step mode
            d=Drill point
            r=raster polygon
        '''

        if name == '':
            name = self.position
        if value == '':
            value = self.extract_value

        name = name.lower()
        self.move_to_position(name)

        if name.startswith('p'):
            self.extract(value)
        elif name.startswith('l'):
            self.trace_path(value, name)
        elif name.startswith('s'):
            self.trace_path(value, name, kind='step')
        elif name.startswith('d'):
            self.drill_point(value, name)

    @verbose_skip
    @command_register
    def drill_point(self, value='', name=''):
        if name == '':
            name = self.position

        if value == '':
            value = self.extract_value

        self._manager_action([('drill_point', (value, name,), {})],
                             protocol=ILaserManager,
                             name=self.extract_device)

    @verbose_skip
    @command_register
    def trace_path(self, name='', value='', kind='continuous'):
        if name == '':
            name = self.position

        if value == '':
            value = self.extract_value

        self._manager_action([('trace_path', (value, name, kind), {})],
                             protocol=ILaserManager,
                             name=self.extract_device)

    @verbose_skip
    @command_register
    def extract(self, power='', units=''):
        if power == '':
            power = self.extract_value
        if units == '':
            units = self.extract_units

        self.info('extract sample to {} ({})'.format(power, units))
        self._manager_action([('extract', (power,), {'units':units})],
                             protocol=ILaserManager,
                             name=self.extract_device)

    @verbose_skip
    @command_register
    def end_extract(self):
        self._manager_action([('end_extract', (), {})],
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
            self._sleep(1)
            s = r.isSet()

        if not self._cancel:
            self._resource_flag = r
            r.set()
            self.info('{} acquired'.format(name))

    @verbose_skip
    @command_register
    def wait(self, name=None, criterion=0):
        self.info('waiting for {} = {}'.format(name, criterion))
        r = self.runner.get_resource(name)

        cnt = 0
        resp = r.read()
        if resp is not None:
            while resp != criterion:
                time.sleep(1)

                # only verbose every 10s
                resp = r.read(verbose=cnt % 10 == 0)
                if resp is None:
                    continue

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

    @verbose_skip
    @command_register
    def enable(self):
        return self._manager_action([('enable_device', (), {})],
                             protocol=ILaserManager,
                             name=self.extract_device)
    @verbose_skip
    @command_register
    def disable(self):
        return self._manager_action([('disable_device', (), {})],
                             protocol=ILaserManager,
                             name=self.extract_device)
    @verbose_skip
    @command_register
    def prepare(self):
        return self._manager_action([('prepare', (), {})],
                             protocol=ILaserManager,
                             name=self.extract_device)

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
