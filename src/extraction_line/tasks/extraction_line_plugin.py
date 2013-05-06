#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import List, Instance
from src.envisage.tasks.base_task_plugin import BaseTaskPlugin
from envisage.ui.tasks.task_factory import TaskFactory
#============= standard library imports ========================
#============= local library imports  ==========================
from src.extraction_line.extraction_line_manager import ExtractionLineManager
from src.extraction_line.tasks.extraction_line_task import ExtractionLineTask

class ExtractionLinePlugin(BaseTaskPlugin):
    id = 'pychron.extraction_line.plugin'

    managers = List(contributes_to='pychron.hardware.managers')

    manager = Instance(ExtractionLineManager)
    def _manager_default(self):
        from src.helpers.parsers.initialization_parser import InitializationParser
        ip = InitializationParser()
        try:
            plugin = ip.get_plugin('ExtractionLine', category='hardware')
            mode = ip.get_parameter(plugin, 'mode')
#            mode = plugin.get('mode')
        except AttributeError:
            # no epxeriment plugin defined
            mode = 'normal'

        elm = ExtractionLineManager(mode=mode)
        elm.bind_preferences()
        return elm

    def _managers_default(self):
        '''
        '''
        return [
                dict(
                     name='extraction_line',
                     manager=self.manager),
                ]

    def _tasks_default(self):
        ts = [TaskFactory(id='pychron.extraction_line',
                         factory=self._factory)]
        return ts

    def _factory(self):

        t = ExtractionLineTask(manager=self.manager)

#        print self.application.get_service()
        return t

#============= EOF =============================================
