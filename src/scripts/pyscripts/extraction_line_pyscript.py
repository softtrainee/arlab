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
from traits.api import Any
#============= standard library imports ========================

#============= local library imports  ==========================
from src.scripts.pyscripts.pyscript import PyScript
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
        self.runner.scripts.remove(self)

    def _cancel_hook(self):
        if self._resource_flag:
            self._resource_flag.clear()

    def _get_help_hook(self):
        return HTML_HELP

    def _get_commands(self):
        cmds = super(ExtractionLinePyScript, self)._get_commands()
        cmds += [('open', '_m_open'), 'close',
                 'acquire', 'release'
                 ]
        return cmds

    def _m_open(self, vname):
        if self._syntax_checking or self._cancel:
            return

        self.info('opening {}'.format(vname))
        result = self._manager_action('open_valve', vname, mode='script')
        self.report_result(result)

    def close(self, vname):
        if self._syntax_checking or self._cancel:
            return

        self.info('closing {}'.format(vname))
        self._manager_action('close_valve', vname, mode='script')

    def acquire(self, resource):

        if self._syntax_checking or self._cancel:
            return

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

    def release(self, resource):
        if self._syntax_checking or self._cancel:
            return

        self.info('release {}'.format(resource))
        r = self.runner.get_resource(resource)
        r.clear()

#============= EOF ====================================
