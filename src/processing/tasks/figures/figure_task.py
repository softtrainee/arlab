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
from traits.api import HasTraits, on_trait_change, Instance, List
from traitsui.api import View, Item
from src.processing.tasks.analysis_edit.analysis_edit_task import AnalysisEditTask
from pyface.tasks.task_layout import TaskLayout, Splitter, PaneItem
from src.processing.tasks.figures.plotter_options_pane import PlotterOptionsPane
from src.processing.tasks.analysis_edit.plot_editor_pane import EditorPane
#============= standard library imports ========================
#============= local library imports  ==========================

class FigureTask(AnalysisEditTask):
    id = 'pychron.processing.figures'
    plotter_options_pane = Instance(PlotterOptionsPane)

    def _default_layout_default(self):
        return TaskLayout(
                          id='pychron.analysis_edit',
                          left=Splitter(
                                     PaneItem('pychron.analysis_edit.unknowns'),
                                     PaneItem('pychron.processing.figures.plotter_options'),
                                     PaneItem('pychron.analysis_edit.controls'),
                                     PaneItem('pychron.processing.editor'),
                                     orientation='vertical'
                                     ),

                          right=Splitter(
                                         PaneItem('pychron.search.query'),
                                         orientation='vertical'
                                         )
                          )

    def create_dock_panes(self):
        panes = super(FigureTask, self).create_dock_panes()
        self.plotter_options_pane = PlotterOptionsPane()
        return panes + [self.plotter_options_pane,
                        ]

    def new_ideogram(self, ans=None, name='Ideo'):

        from src.processing.tasks.figures.figure_editor import IdeogramEditor
        func = self.manager.new_ideogram
        klass = IdeogramEditor
        self._new_figure(ans, name, func, klass)

    def new_spectrum(self, ans, name='Spec'):
        from src.processing.tasks.figures.figure_editor import SpectrumEditor
        func = self.manager.new_spectrum
        klass = SpectrumEditor
        self._new_figure(ans, name, func, klass)

    def _new_figure(self, ans, name, func, klass):
        comp = None
        if ans:
            self.unknowns_pane.items = ans
            comp = func(ans)

        editor = klass(component=comp,
                       name=name,
                       processor=self.manager,
                       make_func=func
                       )
        self.plot_editor_pane.component = comp
        self._open_editor(editor)

    def _active_editor_changed(self):
        if self.active_editor:
            self.plotter_options_pane.pom = self.active_editor.plotter_options_manager

        super(FigureTask, self)._active_editor_changed()

    @on_trait_change('plotter_options_pane:pom:plotter_options:[+, aux_plots:+]')
    def _options_update(self, name, new):
        if name == 'initialized':
            return

        self.active_editor.rebuild()
#        po = self.plotter_options_pane.pom.plotter_options
#        comp = self.active_editor.make_func(ans=ans, plotter_options=po)
#        self.active_editor.component = comp
#============= EOF =============================================
