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
#============= standard library imports ========================
#============= local library imports  ==========================

class BaseTasksApplication(TasksApplication, Loggable):
    uis = List

    def open_view(self, obj, **kw):
        info = obj.edit_traits(**kw)
        self.uis.append(info)

    def exit(self):
        import copy
        uis = copy.copy(self.uis)
        for ui in uis:
            try:
                ui.dispose(abort=True)
            except AttributeError:
                pass

        super(BaseTasksApplication, self).exit()
#============= EOF =============================================
