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
from traits.api import HasTraits, on_trait_change, Instance, List, Dict
from traitsui.api import View, Item
from pyface.tasks.task_layout import TaskLayout, Splitter, PaneItem, Tabbed
from src.processing.tasks.figures.plotter_options_pane import PlotterOptionsPane
from src.processing.tasks.figures.figure_task import FigureTask
from src.processing.tasks.figures.figure_editor import IdeogramEditor, \
    SpectrumEditor, AutoIdeogramEditor, AutoSpectrumEditor, AutoSeriesEditor
from src.processing.tasks.figures.auto_figure_panes import AutoFigureControlPane
# from src.processing.tasks.analysis_edit.plot_editor_pane import EditorPane
#============= standard library imports ========================
#============= local library imports  ==========================

class AutoFigureTask(FigureTask):
    name = 'AutoFigure'
    id = 'pychron.processing.auto_figure'
    plotter_options_pane = Instance(PlotterOptionsPane)
    _cached_samples = None
    _cached = Dict
    def _default_layout_default(self):
        return TaskLayout(
                          id='pychron.analysis_edit',
                          left=Splitter(
                                     Tabbed(
                                            PaneItem('pychron.analysis_edit.unknowns'),
                                            PaneItem('pychron.processing.figures.plotter_options')
                                            ),
                                     Tabbed(
                                            PaneItem('pychron.analysis_edit.controls'),
                                            PaneItem('pychron.processing.editor'),
                                            PaneItem('pychron.processing.auto_figure_controls')
                                            ),
                                     orientation='vertical'
                                     ),

                          right=Splitter(
                                         PaneItem('pychron.search.query'),
                                         orientation='vertical'
                                         )
                          )

    def refresh_plots(self, last_run):
        '''
            if last run is part of a step heat experiment
            plot spectrum for list sample/aliquot
            
            if last run is blank, air, cocktail 
            plot a series
        '''

        if last_run.analysis_type == 'unknown':
            sample = last_run.sample
            if sample:

                if last_run.extract_group:
                    aliquot = last_run.aliquot
                    self.plot_sample_spectrum(sample, aliquot)
                else:
                    self.plot_sample_ideogram(sample)

        else:
            ms = last_run.mass_spectrometer
            ed = last_run.extract_device
            at = last_run.analysis_type
            ln = last_run.labnumber
            editor = self._get_editor(AutoSeriesEditor)
            if editor: 
                afc = editor.auto_figure_control
                days,hours=afc.days,afc.hours
            else:
                days,hours=1,0
                
            
                
                
            self.plot_series(ln,at, ms, ed,
                             days=days, hours=hours)

    def _unique_analyses(self, ans):
        if ans:
            items = self.unknowns_pane.items
            if items:
                uuids = [ai.uuid for ai in items]
                ans = [ui for ui in ans if ui.uuid not in uuids]
        return ans

    def plot_series(self, ln=None, at=None, ms=None, ed=None, **kw):
        '''
            switch to series editor
        '''
        
        if ln is None:
            ln = self._cached['ln']
        if at is None:
            at = self._cached['analysis_type']
        if ms is None:
            ms = self._cached['ms']
        if ed is None:
            ed = self._cached['ed']

        self._cached['ln'] = ln
        self._cached['analysis_type'] = at
        self._cached['ms'] = ms
        self._cached['ed'] = ed

        klass = AutoSeriesEditor
        editor = self._get_editor(klass)
        if editor and editor.labnumber ==ln:
            unks = self.manager.load_series(at, ms, ed,
                                            **kw)
            nunks = self._unique_analyses(unks)
            if nunks:
                self.unknowns_pane.items.extend(nunks)

        else:
            unks = self.manager.load_series(at, ms, ed,
                                            **kw)
            self.manager.load_analyses(unks)
            self.new_series(unks, klass, name=ln)
            self.active_editor.labnumber=ln
            self.active_editor.show_series('Ar40')

    def _get_editor(self, klass):
        return next((editor for editor in self.editor_area.editors
                        if isinstance(editor, klass)), None)

    def plot_sample_spectrum(self, sample, aliquot):
        self.debug('auto plot sample spectrum sample={} aliquot={}'.format(sample, aliquot))
        klass = AutoSpectrumEditor
        editor = self._get_editor(klass)
        if editor:
            unks = self.manager.load_sample_analyses(sample, aliquot)
            nunks = self._unique_analyses(unks)
            if nunks:
                self.unknowns_pane.items.extend(nunks)

        else:
            unks = self.manager.load_sample_analyses(sample, aliquot)
            self.manager.load_analyses(unks)
            self.new_spectrum(unks, klass)
        self.group_by_aliquot()

    def plot_sample_ideogram(self, sample):
        self.debug('auto plot sample ideogram {}'.format(sample))
        klass = AutoIdeogramEditor
        editor = self._get_editor(klass)
        if editor:

            unks = self.manager.load_sample_analyses(sample)
            nunks = self._unique_analyses(unks)
            if nunks:
                self.unknowns_pane.items.extend(nunks)

        else:
            unks = self.manager.load_sample_analyses(sample)
            self.manager.load_analyses(unks)
            self.new_ideogram(unks, klass)

        if self.active_editor.auto_figure_control.group_by_labnumber:
            self.group_by_labnumber()

        if self.active_editor.auto_figure_control.group_by_aliquot:
            self.group_by_aliquot()

    def create_dock_panes(self):
        panes = super(AutoFigureTask, self).create_dock_panes()

        self.auto_figure_control_pane = AutoFigureControlPane()
        return panes + [self.auto_figure_control_pane]
#         self.plotter_options_pane = PlotterOptionsPane()
#         return panes + [self.plotter_options_pane,
#                         ]

    def _active_editor_changed(self):
        if self.active_editor:
            self.auto_figure_control_pane.auto_control = self.active_editor.auto_figure_control

        super(AutoFigureTask, self)._active_editor_changed()

    @on_trait_change('''active_editor:auto_figure_control:[group_by_aliquot,
group_by_labnumber]''')
    def _update_group_by_aliquot(self, name, new):
        if new:
            if name == 'group_by_aliquot':
                self.group_by_aliquot()
            else:
                self.group_by_labnumber()
        else:
            self.clear_grouping()

    @on_trait_change('active_editor:auto_figure_control:[hours, days]')
    def _update_series_limits(self, name, new):
        self.unknowns_pane.items = []
        self.plot_series(**{name:new})

#     @on_trait_change('active_editor:plotter:recall_event')
#     def _recall(self, new):
#         print new

    @on_trait_change('plotter_options_pane:pom:plotter_options:[+, aux_plots:+]')
    def _options_update(self, name, new):
        if name == 'initialized':
            return

        self.active_editor.rebuild(refresh_data=False)

#        po = self.plotter_options_pane.pom.plotter_options
#        comp = self.active_editor.make_func(ans=ans, plotter_options=po)
#        self.active_editor.component = comp
#============= EOF =============================================
