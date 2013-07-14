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
from pyface.tasks.task_layout import TaskLayout, Splitter, PaneItem, Tabbed
from src.processing.tasks.figures.plotter_options_pane import PlotterOptionsPane
from itertools import groupby
# from src.processing.tasks.analysis_edit.plot_editor_pane import EditorPane
#============= standard library imports ========================
#============= local library imports  ==========================

class FigureTask(AnalysisEditTask):
    name = 'Figure'
    id = 'pychron.processing.figures'
    plotter_options_pane = Instance(PlotterOptionsPane)

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
                                            ),
                                     orientation='vertical'
                                     ),

                          right=Splitter(
                                         PaneItem('pychron.search.query'),
                                         orientation='vertical'
                                         )
                          )

    def prepare_destroy(self):
        if self.active_editor:
            pom = self.active_editor.plotter_options_manager
            pom.close()

    def create_dock_panes(self):
        panes = super(FigureTask, self).create_dock_panes()
        self.plotter_options_pane = PlotterOptionsPane()
        return panes + [self.plotter_options_pane,
                        ]

    def group_by_aliquot(self):
        key = lambda x: x.aliquot
        self._group_by(key)

    def group_by_labnumber(self):
        key = lambda x: x.labnumber
        self._group_by(key)

    def group_selected(self):
        if self.unknowns_pane.selected:
            self.active_editor.set_group(
                                         self._get_selected_indices(),
                                         self._get_unique_group_id())
    def _get_selected_indices(self):
        items = self.unknowns_pane.items
        return [items.index(si) for si in self.unknowns_pane.selected]

    def clear_grouping(self):
        '''
            if selected then set selected group_id to 0
            else set all to 0
        '''
        if self.active_editor:
            sel = self.unknowns_pane.selected
            if sel:
                idx = self._get_selected_indices()
            else:
                idx = range(len(self.unknowns_pane.items))

            self.active_editor.set_group(idx, 0)
            self.unknowns_pane.update_needed = True

    def _group_by(self, key):
        if self.active_editor:
            items = self.unknowns_pane.items
            items = sorted(items, key=key)
            for i, (_, analyses) in enumerate(groupby(items, key=key)):
                idxs = [items.index(ai) for ai in analyses]
                self.active_editor.set_group(idxs, i, refresh=False)

#             self.unknowns_pane.update_needed = True
            self.active_editor.rebuild(refresh_data=False)

    def _get_unique_group_id(self):
        gids = {i.group_id for i in self.unknowns_pane.items}
        return max(gids) + 1

    def new_ideogram(self, ans=None, klass=None, name='Ideo'):
        func = self.manager.new_ideogram
        if klass is None:
            from src.processing.tasks.figures.figure_editor import IdeogramEditor as klass

        self._new_figure(ans, name, func, klass)

    def new_spectrum(self, ans=None, klass=None, name='Spec'):
        if klass is None:
            from src.processing.tasks.figures.figure_editor import SpectrumEditor as klass

        func = self.manager.new_spectrum
        self._new_figure(ans, name, func, klass)

    def new_inverse_isochron(self, ans=None, name='Inv. Iso.'):
        func = self.manager.new_inverse_isochron
        from src.processing.tasks.figures.figure_editor import InverseIsochronEditor
        klass = InverseIsochronEditor
        self._new_figure(ans, name, func, klass)

#     def _save_file(self, path):
#         self.active_editor.save_file(path)
    def new_series(self, ans, klass=None, name='Series'):

#         from src.processing.tasks.series.series_editor import SeriesEditor
#         editor = SeriesEditor(name='Series',
#                               processor=self.manager,
#                               unknowns=ans
#                               )
#         editor.unknowns = self.unknowns_pane.items
#         self._open_editor(editor)
#         self.series_editor_count += 1
        if klass is None:
            from src.processing.tasks.figures.figure_editor import SeriesEditor as klass
        func = self.manager.new_series

        self._new_figure(ans, name, func, klass)

        editor = self.active_editor
        refiso = ans[0]
#         editor._unknowns = ans
        editor.trait_set(_unknowns=ans,
                         unknowns=ans,
                         trait_change_notify=False)
#         editor.unknowns = ans
        editor.tool.load_fits(refiso.isotope_keys,
                            refiso.isotope_fits
                            )

    def _new_figure(self, ans, name, func, klass):
        comp, plotter = None, None
        if ans:
            comp, plotter = func(ans)

            editor = klass(
                           component=comp,
                           plotter=plotter,
                           name=name,
                           processor=self.manager,
                           make_func=func
                           )

            self.plot_editor_pane.component = comp
            self._open_editor(editor)

            editor._unknowns = ans
            editor._suppress_rebuild = True
            self.unknowns_pane.items = ans
            editor._suppress_rebuild = False

    def _active_editor_changed(self):
        if self.active_editor:
            self.plotter_options_pane.pom = self.active_editor.plotter_options_manager

        super(FigureTask, self)._active_editor_changed()

    @on_trait_change('active_editor:plotter:recall_event')
    def _recall(self, new):
        print new

    @on_trait_change('plotter_options_pane:pom:plotter_options:[+, aux_plots:+]')
    def _options_update(self, name, new):
        if name == 'initialized':
            return

        self.active_editor.rebuild()
        self.active_editor.dirty = True

#        po = self.plotter_options_pane.pom.plotter_options
#        comp = self.active_editor.make_func(ans=ans, plotter_options=po)
#        self.active_editor.component = comp
#============= EOF =============================================
