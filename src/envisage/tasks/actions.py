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
from traits.api import HasTraits, on_trait_change, Any
from traitsui.api import View, Item
from pyface.action.action import Action
from pyface.tasks.task_window_layout import TaskWindowLayout
from pyface.tasks.action.task_action import TaskAction
#============= standard library imports ========================
#============= local library imports  ==========================
# class DefaultAction(Action):
#    def _get_experimentor(self, event):
#        return self._get_service(event, 'src.experiment.experimentor.Experimentor')
#
#    def _get_service(self, event, name):
#        app = event.task.window.application
#        return app.get_service(name)
#
#    def _open_editor(self, event, task_id):
#        application = event.task.window.application
#        for wi in application.windows:
#            if wi.active_task.id == task_id:
#                wi.activate()
#                break
#        else:
#            win = application.create_window(TaskWindowLayout(task_id))
#            win.open()

# class GenericNewAction(DefaultAction):
#    name = 'New'
#    accelerator = 'Ctrl+N'
#    def perform(self, event):
#        task = event.task
#        if hasattr(task, 'new'):
#            task.new()
#        else:
#            manager = self._get_experimentor(event)
#            if manager.verify_database_connection(inform=True):
#    #        if manager.verify_credentials():
#                if manager.load():
#                    self._open_editor(event, 'pychron.experiment')

# class GenericOpenAction(DefaultAction):
#    name = 'Open...'
#    accelerator = 'Ctrl+O'
#    def perform(self, event):
#        task = event.task
#        if hasattr(task, 'open'):
#            task.open()
#        else:
#            # default is to open experiment
#            manager = self._get_experimentor(event)
#            if manager.verify_database_connection(inform=True):
#    #        if manager.verify_credentials():
#                if manager.load():
#                    if manager.load_experiment_queue(saveable=True):
#                        self._open_editor(event, 'pychron.experiment')
class ResetLayoutAction(TaskAction):
    name = 'Reset Layout'
    def perform(self, event):
        self.task.window.reset_layout()


class MinimizeAction(TaskAction):
    name = 'Minimize'
    accelerator = 'Ctrl+m'
    def perform(self, event):
        app = self.task.window.application
        app.active_window.control.showMinimized()

class RaiseAction(TaskAction):
    window = Any
    style = 'toggle'
    def perform(self, event):
        self.window.activate()
        self.checked = True

    @on_trait_change('window:deactivated')
    def _on_deactivate(self):
        self.checked = False

class RaiseUIAction(TaskAction):
    style = 'toggle'
    def perform(self, event):
#        self.ui.control.activate()
        self.checked = True

class GenericSaveAction(TaskAction):
    name = 'Save'
    accelerator = 'Ctrl+S'
    def perform(self, event):
        task = self.task
#        task = event.task
        if hasattr(task, 'save'):
            task.save()
#        else:
#            manager = self._get_experimentor(event)
#            manager.save_experiment_queues()


class GenericSaveAsAction(TaskAction):
    name = 'Save As...'
    accelerator = 'Ctrl+Shift+S'
    def perform(self, event):
        task = self.task
        if hasattr(task, 'save_as'):
            task.save_as()

class GenericFindAction(TaskAction):
    accelerator = 'Ctrl+F'
    name = 'Find...'
    def perform(self, event):
        task = self.task
        if hasattr(task, 'find'):
            task.find()

# class GenericReplaceAction(TaskAction):
#    pass
#        else:
#            manager = self._get_experimentor(event)
#            manager.save_as_experiment_queues()

#============= EOF =============================================
