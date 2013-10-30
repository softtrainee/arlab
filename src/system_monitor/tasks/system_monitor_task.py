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
from traits.api import Instance, on_trait_change
from pyface.tasks.action.schema import SToolBar
from pyface.tasks.task_layout import TaskLayout, Splitter, PaneItem
#============= standard library imports ========================
#============= local library imports  ==========================
from src.envisage.tasks.editor_task import BaseEditorTask
from src.processing.tasks.analysis_edit.panes import ControlsPane
from src.system_monitor.tasks.actions import AddSystemMonitorAction
from src.system_monitor.tasks.panes import ConnectionPane
from src.system_monitor.tasks.system_monitor_editor import SystemMonitorEditor


class SystemMonitorTask(BaseEditorTask):
    name = 'System Monitor'

    tool_bars = [SToolBar(AddSystemMonitorAction(),
                          image_size=(16, 16)),
                 SToolBar(
                     image_size=(16, 16))]

    connection_pane = Instance(ConnectionPane)
    controls_pane = Instance(ControlsPane)

    def add_system_monitor(self):
        editor = SystemMonitorEditor()
        self._open_editor(editor)

    def _active_editor_changed(self):
        if self.active_editor:

            self.connection_pane.system_name = self.active_editor.system_name
            self.connection_pane.dbconn_spec = self.active_editor.dbconn_spec

            if self.controls_pane:
                tool = None
                if hasattr(self.active_editor, 'tool'):
                    tool = self.active_editor.tool

                self.controls_pane.tool = tool

    @on_trait_change('connection_pane:system_name')
    def _handle_system_name(self, new):
        if self.active_editor:
            self.active_editor.system_name = new

    def _prompt_for_save(self):
        """
            dont save just close
        """
        return True

    def activated(self):
        editor = SystemMonitorEditor()
        self._open_editor(editor)

    def _manager_default(self):
        return

    def _default_layout_default(self):
        return TaskLayout(
            left=Splitter(
                PaneItem('pychron.sys_mon.connection'),
                PaneItem('pychron.analysis_edit.controls'),
                orientation='vertical'),
        )

    def create_dock_panes(self):
        self.connection_pane = ConnectionPane()
        self.controls_pane = ControlsPane()
        return [self.connection_pane,
                self.controls_pane
        ]


#============= EOF =============================================
