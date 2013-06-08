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
from pyface.action.action import Action
from pyface.tasks.task_window_layout import TaskWindowLayout
from pyface.tasks.action.task_action import TaskAction
#============= standard library imports ========================
#============= local library imports  ==========================
class ProcessorAction(Action):
    def _get_processor(self, event):
        app = event.task.window.application
        processor = app.get_service('src.processing.processor.Processor')
        return processor

class EquilibrationInspectorAction(Action):
    name = 'Equilibration Inspector...'
    def perform(self, event):
        from src.processing.utils.equil import EquilibrationInspector

        eq = EquilibrationInspector()
        eq.refresh()
        app = event.task.window.application
        app.open_view(eq)







class IdeogramAction(ProcessorAction):
    name = 'Ideogram'
    def perform(self, event):

        task = event.task
        if not task.id == 'pychron.processing.figures':
            app = task.window.application
            win = app.create_window(TaskWindowLayout(
                                               'pychron.processing.figures'
                                               )
                              )
            win.open()
            task = win.active_task

        task.new_ideogram()

class SpectrumAction(ProcessorAction):
    name = 'Spectrum'
    accelerator = 'Ctrl+D'
    def perform(self, event):

        task = event.task
        if not task.id == 'pychron.processing':
            app = task.window.application
            win = app.create_window(TaskWindowLayout(
                                               'pychron.processing'
                                               )
                              )
            win.open()
            task = win.active_task

        task.new_spectrum()


class RecallAction(ProcessorAction):
    name = 'Recall'
    accelerator = 'Ctrl+R'
    def perform(self, event):

        task = event.task
        if not task.id == 'pychron.recall':
            app = task.window.application
            win = app.create_window(TaskWindowLayout(
                                               'pychron.recall'
                                               )
                              )
            win.open()
            task = win.active_task
        else:
            task.window.activate()


class LabnumberEntryAction(Action):
    name = 'Labnumber Entry'
    accelerator = 'Ctrl+Shift+l'

    task_id = 'pychron.labnumber_entry'

    def perform(self, event):
        task = event.task
        if not task.id == 'pychron.entry':
            app = task.window.application
            win = app.create_window(TaskWindowLayout(
                                               'pychron.entry'
                                               )
                              )
            win.open()
        else:
            task.window.activate()



#============= EOF =============================================
