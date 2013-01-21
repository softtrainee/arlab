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
from traits.api import Any
from src.pyscripts.pyscript import PyScript, verbose_skip, makeRegistry, \
    makeNamedRegistry
#============= standard library imports ========================
import time
#============= local library imports  ==========================

ELPROTOCOL = 'src.extraction_line.extraction_line_manager.ExtractionLineManager'
command_register = makeRegistry()
named_register = makeNamedRegistry(command_register)

class ValvePyScript(PyScript):
    runner = Any
    def _runner_changed(self):
        self.runner.scripts.append(self)

    def get_command_register(self):
        return command_register.commands.items()

    def gosub(self, *args, **kw):
        kw['runner'] = self.runner
        super(ValvePyScript, self).gosub(*args, **kw)

    @verbose_skip
    @named_register('open')
    def _m_open(self, name=None, description=''):

        if description is None:
            description = '---'

        self.info('opening {} ({})'.format(name, description))

        result = self._manager_action([('open_valve', (name,), dict(
                                                      mode='script',
                                                      description=description
                                                      ))], protocol=ELPROTOCOL)
        if result is not None:
            ok, changed = result[0]
            if changed:
                time.sleep(0.25)

            if not ok:
                self.info('Failed to open valve {} {}'.format(name, description))
                self.cancel()

    @verbose_skip
    @command_register
    def close(self, name=None, description=''):

        if description is None:
            description = '---'

        self.info('closing {} ({})'.format(name, description))
        result = self._manager_action([('close_valve', (name,), dict(
                                                      mode='script',
                                                      description=description
                                                      ))], protocol=ELPROTOCOL)
        if result is not None:
            ok, changed = result[0]
            if changed:
                time.sleep(0.25)
            if not ok:
                self.info('Failed to close valve {} {}'.format(name, description))
                self.cancel()

    @verbose_skip
    @command_register
    def is_open(self, name=None, description=''):
        self.info('is {} ({}) open?'.format(name, description))
        result = self._get_valve_state(name, description)
        if result:
            return result[0] == True

    @verbose_skip
    @command_register
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

#============= EOF =============================================
