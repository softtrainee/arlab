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
from traits.api import Any
#============= standard library imports ========================

#============= local library imports  ==========================
from src.pyscripts.pyscript import PyScript, verbose_skip
from src.lasers.laser_managers.laser_manager import ILaserManager
import time
ELPROTOCOL = 'src.extraction_line.extraction_line_manager.ExtractionLineManager'

class ExtractionLinePyScript(PyScript):
    runner = Any
    _resource_flag = None
    runtype = None
    heat_device = None
    heat_value = None
    heat_units = None
    duration = None

    def _runner_changed(self):
        self.runner.scripts.append(self)

    def _post_execute_hook(self):
        #remove ourselves from the script runner
        if self.runner:
            self.runner.scripts.remove(self)

    def _cancel_hook(self):
        if self._resource_flag:
            self._resource_flag.clear()

    def get_script_commands(self):
        cmds = [('open', '_m_open'), 'close',
                 'acquire', 'release',
                 'wait', 'set_resource',
                 'move_to_position',
                 'heat',
                 'end_heat',
                 'is_open', 'is_closed',
                 ]
        return cmds

    def get_context(self):
        d = super(ExtractionLinePyScript, self).get_context()

        #=======================================================================
        #Parameters
        # this are directly referencable in the script
        # e.g if OverlapRuns:
        #    or
        #    move_to_hole(holeid)
        #=======================================================================

#        d['holeid'] = 123
#        d['OverlapRuns'] = True
        d['runtype'] = self.runtype
        d['duration'] = self.duration
        d['heat_value'] = self.heat_value
        d['heat_units'] = self.heat_units
        return d

    def gosub(self, *args, **kw):
        kw['runtype'] = self.runtype
        super(ExtractionLinePyScript, self).gosub(*args, **kw)

    @verbose_skip
    def is_open(self, name=None, description=''):

        self.info('is {} ({}) open?'.format(name, description))
        result = self._get_valve_state(name, description)
        if result:
            return result[0] == True

    @verbose_skip
    def is_closed(self, name=None, description=''):
        self.info('is {} ({}) closed?'.format(name, description))
        result = self._get_valve_state(name, description)
        if result:
            return result[0] == False

    def _get_valve_state(self, name, description):
        return self._manager_action([('open_valve', (name,), dict(
                                                      mode='script',
                                                      description=description
                                                      ))], protocol=ELPROTOCOL)

    @verbose_skip
    def move_to_position(self, position=0):
        self.info('move to position {}'.format(position))
        result = self._manager_action([('move_to_position', (position,), {})
                                        ],
                                      protocol=ILaserManager,
                                      name=self.heat_device
                                      )

#    @verbose_skip
#    def set_stage_map(self, mapname=None):
#        self.info('set stage map to {}, using position correction={}'.format(mapname))
#        result = self._manager_action([('set_stage_map', (mapname), {})
#                                        ],
#                                      protocol=ILaserManager,
#                                      name=self.heat_device
#                                      )
#        self.report_result(result)

    @verbose_skip
    def heat(self, power=None):
        if power is None:
            power = self.heat_value
        self.info('heat sample to power {}'.format(power))
        self._manager_action([('enable_laser', (), {}),
                                       ('set_laser_power', (power,), {})
                                       ],
                                      protocol=ILaserManager,
                                      name=self.heat_device
                             )
    def end_heat(self):
        self._manager_action([('disable_laser', (), {})],
                             protocol=ILaserManager,
                             name=self.heat_device
                             )

    @verbose_skip
    def _m_open(self, name=None, description=''):
#        if self._syntax_checking or self._cancel:
#            return
        if description is None:
            description = '---'

        self.info('opening {} ({})'.format(name, description))

        self._manager_action([('open_valve', (name,), dict(
                                                      mode='script',
                                                      description=description
                                                      ))], protocol=ELPROTOCOL)

    @verbose_skip
    def close(self, name=None, description=''):
#        if self._syntax_checking or self._cancel:
#            return

        if description is None:
            description = '---'

        self.info('closing {} ({})'.format(name, description))
#        self._manager_action('close_valve',
#                             protocol=ELPROTOCOL,
#                             description=name, mode='script')
        self._manager_action([('close_valve', (name,), dict(
                                                      mode='script',
                                                      description=description
                                                      ))], protocol=ELPROTOCOL)

    @verbose_skip
    def acquire(self, name=None):

#        if self._syntax_checking or self._cancel:
#            return

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
    def wait(self, name=None, criterion=0):
        self.info('waiting for {} < {}'.format(name, criterion))
        r = self.runner.get_resource(name)

        resp = r.read()
        if resp is not None:
            while resp != criterion:
                resp = r.read()
                if resp is None:
                    continue

                time.sleep(1)

        self.info('finished waiting')

    @verbose_skip
    def release(self, name=None):
#        if self._syntax_checking or self._cancel:
#            return

        self.info('release {}'.format(name))
        r = self.runner.get_resource(name)
        r.clear()

    @verbose_skip
    def set_resource(self, name=None, value=1):
        r = self.runner.get_resource(name)
        r.set(value)

#============= EOF ====================================
