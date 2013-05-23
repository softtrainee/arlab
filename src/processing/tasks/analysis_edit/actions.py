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
from traits.api import HasTraits
from traitsui.api import View, Item
from pyface.tasks.action.task_action import TaskAction
from pyface.tasks.task_window_layout import TaskWindowLayout
#============= standard library imports ========================
#============= local library imports  ==========================

class BlankEditAction(TaskAction):
    name = 'Blanks...'
    accelerator = 'Ctrl+B'
    def perform(self, event):
        _id = 'pychron.analysis_edit'
        task = self.task
        if not task.id == _id:
            # search other windows
            app = task.window.application
            for win in app.windows:
                if win.active_task.id == _id:
                    win.activate()
                    break
            else:
                win = app.create_window(TaskWindowLayout(_id))
            win.open()
            task = win.active_task

        task.new_blank()
#============= EOF =============================================
