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
from envisage.ui.tasks.task_factory import TaskFactory
#============= standard library imports ========================
#============= local library imports  ==========================

from src.envisage.tasks.base_task_plugin import BaseTaskPlugin

#from src.processing.tasks.browser.browser_task import BrowserTask
from src.system_monitor.tasks.system_monitor_task import SystemMonitorTask


class SystemMonitorPlugin(BaseTaskPlugin):
    def _service_offers_default(self):
        #process_so = self.service_offer_factory(
        #    protocol=Processor,
        #    factory=self._processor_factory)
        return []

    def start(self):
        pass

    def _task_factory(self):
        return SystemMonitorTask()

    def _my_task_extensions_default(self):
        return []

    def _tasks_default(self):
        return [TaskFactory(name='System Monitor',
                            id='pychron.system_monitor',
                            factory=self._task_factory)]

    def _preferences_panes_default(self):
        return []

        #============= EOF =============================================