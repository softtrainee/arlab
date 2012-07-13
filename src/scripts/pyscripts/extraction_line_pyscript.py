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
from src.scripts.pyscripts.pyscript import PyScript, verbose_skip
HTML_HELP = '''
<tr>
    <td>open</td>
    <td>valvekey</td>
    <td>Open a valve</td>
    <td>open('B')</td>
</tr>
<tr>
    <td>close</td>
    <td>valvekey</td>
    <td>close a valve</td>
    <td>close('B')</td>
</tr>
'''



class ExtractionLinePyScript(PyScript):
    runner = Any
    _resource_flag = None

    def _runner_changed(self):
        self.runner.scripts.append(self)

    def _post_execute_hook(self):
        #remove ourselves from the script runner
        if self.runner:
            self.runner.scripts.remove(self)

    def _cancel_hook(self):
        if self._resource_flag:
            self._resource_flag.clear()

    def _get_help_hook(self):
        return HTML_HELP

    def get_commands(self):
        cmds = super(ExtractionLinePyScript, self).get_commands()
        cmds += [('open', '_m_open'), 'close',
                 'acquire', 'release',

                 'move_to_hole', 'heat_sample'

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

        d['holeid'] = 123
        d['OverlapRuns'] = True
        return d


    def move_to_hole(self, holeid):
        self.info('move to hole {}'.format(holeid))

        man_protocol = 'src.lasers.laser_managers.fusions_co2_manager.FusionsCO2Manager'
        result = self._manager_action('move_to_hole', manager=man_protocol)
        self.report_result(result)

    def heat_sample(self, pwr, duration):
        self.info('heat sample to power {}, {}'.format(pwr, duration))
        man_protocol = 'src.lasers.laser_managers.fusions_co2_manager.FusionsCO2Manager'
        self._manager_action([('enable_laser', (), {}),
                                       ('set_laser_power', (pwr,), {})
                                       ], manager=man_protocol)
        self.sleep(duration)
        self._manager_action('disable_laser', manager=man_protocol)

    @verbose_skip
    def _m_open(self, vname):
#        if self._syntax_checking or self._cancel:
#            return

        self.info('opening {}'.format(vname))

        self._manager_action('open_valve', None, description=vname, mode='script')

    @verbose_skip
    def close(self, vname):
#        if self._syntax_checking or self._cancel:
#            return

        self.info('closing {}'.format(vname))
        self._manager_action('close_valve', None, description=vname, mode='script')

    @verbose_skip
    def acquire(self, resource):

#        if self._syntax_checking or self._cancel:
#            return

        if self.runner is None:
            return

        self.info('acquire {}'.format(resource))
        r = self.runner.get_resource(resource)

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
            self.info('{} acquired'.format(resource))

    @verbose_skip
    def release(self, resource):
#        if self._syntax_checking or self._cancel:
#            return

        self.info('release {}'.format(resource))
        r = self.runner.get_resource(resource)
        r.clear()

#============= EOF ====================================
