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
from traits.api import List
from src.loggable import Loggable
from envisage.ui.tasks.tasks_application import TasksApplication
from pyface.tasks.task_window_layout import TaskWindowLayout
from src.globals import globalv
from src.hardware.core.i_core_device import ICoreDevice
#============= standard library imports ========================
#============= local library imports  ==========================

class BaseTasksApplication(TasksApplication, Loggable):
    uis = List
    def start(self):
        if globalv.open_logger_on_launch:
            self._load_state()
            self.get_task('pychron.logger')
#             win = self.create_window(TaskWindowLayout('pychron.logger',
#                                                       ),
#                                      )
#             win.open()
        return super(BaseTasksApplication, self).start()

    def get_task(self, tid, activate=False):
        for win in self.windows:
            if win.active_task:
                if win.active_task.id == tid:
                    if tid:
                        win.activate()
                    break
        else:
            win = self.create_window(TaskWindowLayout(tid))
            win.open()

        return win.active_task

    def open_task(self, tid):
        return self.get_task(tid, True)

    def open_view(self, obj, **kw):
        info = obj.edit_traits(**kw)
        self.uis.append(info)

    def exit(self):

        self._cleanup_services()

        import copy
        uis = copy.copy(self.uis)
        for ui in uis:
            try:
                ui.dispose(abort=True)
            except AttributeError:
                pass

        super(BaseTasksApplication, self).exit()

    def _cleanup_services(self):
        for si in self.get_services(ICoreDevice):
            si.close()



#============= EOF =============================================
