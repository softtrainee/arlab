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
from traits.api import Instance, List
from pyface.tasks.action.schema import SToolBar
from pyface.tasks.task_layout import TaskLayout, Splitter, PaneItem
#============= standard library imports ========================
#============= local library imports  ==========================
from src.processing.tasks.analysis_edit.panes import ControlsPane
from src.processing.tasks.figures.figure_editor import FigureEditor
from src.processing.tasks.figures.figure_task import FigureTask
from src.processing.tasks.figures.panes import PlotterOptionsPane
from src.system_monitor.tasks.actions import AddSystemMonitorAction
from src.system_monitor.tasks.connection_spec import ConnectionSpec
from src.system_monitor.tasks.panes import ConnectionPane, AnalysisPane
from src.system_monitor.tasks.system_monitor_editor import SystemMonitorEditor

from traitsui.api import View, Item, EnumEditor


class SystemMonitorTask(FigureTask):
    name = 'System Monitor'

    tool_bars = [SToolBar(AddSystemMonitorAction(),
                          image_size=(16, 16)),
                 SToolBar(
                     image_size=(16, 16))]

    connection_pane = Instance(ConnectionPane)
    controls_pane = Instance(ControlsPane)
    unknowns_pane = Instance(AnalysisPane)
    connections = List
    connection = Instance(ConnectionSpec)

    #def prepare_destroy(self):
    #    pass

    def add_system_monitor(self):
        self._editor_factory()

    def get_connection_view(self):
        v = View(Item('connection',
                      editor=EnumEditor(name='connections')),
                 kind='livemodal',
                 buttons=['OK', 'Cancel'],
                 width=300,
                 title='Choose System')
        return v

    def _editor_factory(self):
        #ask user for system
        info = self.edit_traits(view='get_connection_view')

        if info.result and self.connection:
            editor = SystemMonitorEditor(processor=self.manager,
                                         conn_spec=self.connection)
            editor.start()
            self._open_editor(editor)
            if editor:
                editor.sub_refresh()

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

    def _make_connections(self):
        app = self.window.application
        connections = app.preferences.get('pychron.sys_mon.favorites')
        cs = []
        for ci in eval(connections):
            n, sn, h, p = ci.split(',')
            cc = ConnectionSpec(system_name=sn,
                                host=h, port=int(p))
            cs.append(cc)
        self.connections = cs

    def activated(self):
        self._make_connections()
        self._editor_factory()

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
