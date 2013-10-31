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
from traits.api import Instance
from pyface.tasks.action.schema import SToolBar
from pyface.tasks.task_layout import TaskLayout, Splitter, PaneItem
#============= standard library imports ========================
#============= local library imports  ==========================
from src.processing.tasks.analysis_edit.panes import ControlsPane
from src.processing.tasks.figures.figure_editor import FigureEditor
from src.processing.tasks.figures.figure_task import FigureTask
from src.processing.tasks.figures.panes import PlotterOptionsPane
from src.system_monitor.tasks.actions import AddSystemMonitorAction
from src.system_monitor.tasks.panes import ConnectionPane, AnalysisPane
from src.system_monitor.tasks.system_monitor_editor import SystemMonitorEditor


class SystemMonitorTask(FigureTask):
    name = 'System Monitor'

    tool_bars = [SToolBar(AddSystemMonitorAction(),
                          image_size=(16, 16)),
                 SToolBar(
                     image_size=(16, 16))]

    connection_pane = Instance(ConnectionPane)
    controls_pane = Instance(ControlsPane)
    unknowns_pane = Instance(AnalysisPane)

    def prepare_destroy(self):
        pass

    def add_system_monitor(self):
        editor = self._editor_factory()
        self._open_editor(editor)

    def _editor_factory(self):
        editor = SystemMonitorEditor(processor=self.manager)
        editor.start()

        return editor

    def _active_editor_changed(self):
        if self.active_editor:

            self.connection_pane.conn_spec = self.active_editor.conn_spec

            if self.controls_pane:
                tool = None
                if hasattr(self.active_editor, 'tool'):
                    tool = self.active_editor.tool

                self.controls_pane.tool = tool

        if isinstance(self.active_editor, FigureEditor):
            self.plotter_options_pane.pom = self.active_editor.plotter_options_manager


    def _prompt_for_save(self):
        """
            dont save just close
        """
        return True

    def activated(self):
        editor = self._editor_factory()
        self._open_editor(editor)

        editor.sub_refresh_plots()
        #db=self.manager.db
        #with db.session_ctx():
        #    ans=db.selector.get_last(5)
        #
        #    ans=self.manager.make_analyses(ans)
        #    editor.unknowns=ans

    def _default_layout_default(self):
        return TaskLayout(
            left=Splitter(
                Splitter(
                    PaneItem('pychron.sys_mon.connection'),
                    PaneItem('pychron.analysis_edit.controls'),
                    orientation='vertical'),
                PaneItem('pychron.sys_mon.analyses'),
                orientation='horizontal'))

    def create_dock_panes(self):
        self.connection_pane = ConnectionPane()
        self.controls_pane = ControlsPane()
        self.unknowns_pane = AnalysisPane()
        self.plotter_options_pane = PlotterOptionsPane()

        return [self.connection_pane,
                self.controls_pane,
                self.unknowns_pane,
                self.plotter_options_pane
        ]


#============= EOF =============================================
