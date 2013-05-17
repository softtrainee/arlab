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
from pyface.tasks.task_layout import PaneItem, TaskLayout, Splitter
#============= standard library imports ========================
#============= local library imports  ==========================
from src.envisage.tasks.base_task import BaseManagerTask
from src.experiment.tasks.experiment_panes import AnalysesPane, \
    ExperimentFactoryPane, StatsPane, ControlsPane, ConsolePane, ExplanationPane
from pyface.tasks.task_window_layout import TaskWindowLayout

class ExperimentEditorTask(BaseManagerTask):

    def _menu_bar_factory(self, menus=None):
        return super(ExperimentEditorTask, self)._menu_bar_factory(menus=menus)

    def _default_layout_default(self):
        return TaskLayout(
                          left=PaneItem('pychron.experiment.factory'),
                          right=Splitter(
                                         PaneItem('pychron.experiment.stats'),
                                        PaneItem('pychron.experiment.explanation'),
                                         orientation='vertical'
                                         ),
                          bottom=PaneItem('pychron.experiment.console'),
                          top=PaneItem('pychron.experiment.controls')
                          )
    def prepare_destroy(self):
        self.manager.stop_file_listener()

    def create_central_pane(self):
        return AnalysesPane(model=self.manager)

    def create_dock_panes(self):
        return [
                ExperimentFactoryPane(model=self.manager.experiment_factory),
                StatsPane(model=self.manager),
                ControlsPane(model=self.manager.executor),
                ConsolePane(model=self.manager.executor),
                ExplanationPane(),
                ]

#===============================================================================
# generic actions
#===============================================================================
    def open(self):
        path = self.open_file_dialog()
        if path:
            manager = self.manager
            if manager.verify_database_connection(inform=True):
#        if manager.verify_credentials():
                if manager.load():
                    if manager.load_experiment_queue(saveable=True):
                        self._open_editor()

    def _open_editor(self):
        application = self.window.application
#        application = event.task.window.application
        for wi in application.windows:
            if wi.active_task.id == self.task_id:
                wi.activate()
                break
        else:
            win = application.create_window(TaskWindowLayout(self.task_id))
            win.open()
#============= EOF =============================================
