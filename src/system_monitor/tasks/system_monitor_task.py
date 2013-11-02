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
from PySide.QtCore import Qt
from pyface.timer.do_later import do_later
from traits.api import Instance, List
from pyface.tasks.action.schema import SToolBar
from pyface.tasks.task_layout import TaskLayout, Splitter, PaneItem, Tabbed
#============= standard library imports ========================
#============= local library imports  ==========================
from src.envisage.tasks.pane_helpers import ConsolePane
from src.processing.tasks.analysis_edit.panes import ControlsPane
from src.processing.tasks.analysis_edit.plot_editor_pane import PlotEditorPane
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
    console_pane = Instance(ConsolePane)

    connections = List
    connection = Instance(ConnectionSpec)

    def prepare_destroy(self):
        for e in self.editor_area.editors:
            if isinstance(e, SystemMonitorEditor):
                e.stop()

    #def add_ideogram(self):
    #    editor=IdeogramEditor()
    #    self._open_editor(editor)
    #    return editor
    #
    #def add_spectrum(self):
    #    editor=SpectrumEditor()
    #    self._open_editor(editor)
    #    return editor


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

    def tab_editors(self, *args):
        def func(control, a, b):
            control.tabifyDockWidget(a, b)

        self._layout_editors(func, *args)

    def split_editors(self, *args):
        def func(control, a, b):
            control.splitDockWidget(a, b, Qt.Horizontal)

        self._layout_editors(func, *args)

    def _layout_editors(self, func, aidx, bidx):
        ea = self.editor_area
        control = ea.control
        widgets = control.get_dock_widgets()
        if widgets:
            try:
                a, b = widgets[aidx], widgets[bidx]
                func(control, a, b)
            except IndexError:
                pass

    def _editor_factory(self):
        self.connection = self.connections[1]
        #ask user for system
        #info = self.edit_traits(view='get_connection_view')
        if 1:
        #if info.result and self.connection:
            editor = SystemMonitorEditor(processor=self.manager,
                                         conn_spec=self.connection,
                                         task=self)
            editor.start()
            self._open_editor(editor)
            if editor:
                do_later(editor.run_added_handler)

            return editor

    def _active_editor_changed(self):
        if self.active_editor:
            if self.controls_pane:
                tool = None
                if hasattr(self.active_editor, 'tool'):
                    tool = self.active_editor.tool

                self.controls_pane.tool = tool
            if isinstance(self.active_editor, FigureEditor):
                self.plotter_options_pane.pom = self.active_editor.plotter_options_manager
            if isinstance(self.active_editor, SystemMonitorEditor):
                self.console_pane.console_display = self.active_editor.console_display
                self.connection_pane.conn_spec = self.active_editor.conn_spec

            if self.unknowns_pane:
                if hasattr(self.active_editor, 'unknowns'):
                    #print self.active_editor, len(self.active_editor.unknowns)
                    #self.unknowns_pane._no_update=True
                    self.unknowns_pane.items = self.active_editor.unknowns
                    #self.unknowns_pane._no_update=False

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
        self.add_system_monitor()

        self.new_ideogram(add_table=False, add_iso=False)
        #self.active_editor.unknowns=[]

        self.activate_editor(self.editor_area.editors[0])

    def _default_layout_default(self):
        return TaskLayout(
            left=Splitter(
                Splitter(
                    PaneItem('pychron.sys_mon.connection'),
                    PaneItem('pychron.analysis_edit.controls'),
                    orientation='vertical'),
                PaneItem('pychron.sys_mon.analyses'),
                orientation='horizontal'),
            right=Tabbed(PaneItem('pychron.console'),
                         PaneItem('pychron.plot_editor')))

    def create_dock_panes(self):
        self.connection_pane = ConnectionPane()
        self.controls_pane = ControlsPane()
        self.unknowns_pane = AnalysisPane()
        self.plotter_options_pane = PlotterOptionsPane()
        self.plot_editor_pane = PlotEditorPane()

        self.console_pane = ConsolePane()

        return [self.connection_pane,
                self.controls_pane,
                self.unknowns_pane,
                self.plotter_options_pane,
                self.console_pane,
                self.plot_editor_pane
        ]


#============= EOF =============================================
