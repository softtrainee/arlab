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
from pyface.tasks.task_layout import TaskLayout, Splitter, PaneItem, Tabbed
from pyface.timer.do_later import do_later
from pyface.tasks.action.schema import SToolBar
# from src.processing.tasks.analysis_edit.plot_editor_pane import EditorPane
#============= standard library imports ========================
from itertools import groupby
import cPickle as pickle
#============= local library imports  ==========================
from src.processing.tasks.analysis_edit.analysis_edit_task import AnalysisEditTask
from src.processing.tasks.figures.panes import PlotterOptionsPane, \
    FigureSelectorPane
# from src.ui.gui import invoke_in_main_thread
from src.processing.plotters.ideogram import Ideogram
from src.processing.plotter_options_manager import IdeogramOptionsManager
from src.processing.tasks.figures.actions import SaveFigureAction, \
    OpenFigureAction


class FigureTask(AnalysisEditTask):
    name = 'Figure'
    id = 'pychron.processing.figures'
    plotter_options_pane = Instance(PlotterOptionsPane)
    tool_bars = [SToolBar(
                          SaveFigureAction(),
                          OpenFigureAction(),
                          image_size=(16, 16))]
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
                                         PaneItem('pychron.search.results'),
                                         PaneItem('pychron.search.query'),
                                         orientation='vertical'
                                         )
                          )
#===============================================================================
# task protocol
#===============================================================================
    def prepare_destroy(self):
        if self.active_editor:
            pom = self.active_editor.plotter_options_manager
            pom.close()
        super(FigureTask, self).prepare_destroy()

    def create_dock_panes(self):
        panes = super(FigureTask, self).create_dock_panes()
        self.plotter_options_pane = PlotterOptionsPane()

        self.figure_selector_pane = FigureSelectorPane()
        
        fs = [fi.name for fi in self.manager.db.get_figures()]
        if fs:
            self.figure_selector_pane.trait_set(figures=fs, figure=fs[0])

        return panes + [self.plotter_options_pane,
                        self.figure_selector_pane,
                        ]
#===============================================================================
# grouping
#===============================================================================
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
#             self.unknowns_pane.update_needed = True
            self.unknowns_pane.refresh_needed = True
#===============================================================================
# figures
#===============================================================================
    def new_ideogram(self, ans=None, klass=None, name='Ideo', plotter_kw=None):
        func = self._ideogram_factory
#         func = self.manager.new_ideogram
        if klass is None:
            from src.processing.tasks.figures.figure_editor import IdeogramEditor as klass

        self._new_figure(ans, name, func, klass, plotter_kw)

    def new_spectrum(self, ans=None, klass=None, name='Spec', plotter_kw=None):
        if klass is None:
            from src.processing.tasks.figures.figure_editor import SpectrumEditor as klass

        func = self.manager.new_spectrum
        self._new_figure(ans, name, func, klass, plotter_kw)

    def new_inverse_isochron(self, ans=None, name='Inv. Iso.', plotter_kw=None):
        func = self.manager.new_inverse_isochron
        from src.processing.tasks.figures.figure_editor import InverseIsochronEditor
        klass = InverseIsochronEditor
        self._new_figure(ans, name, func, klass, plotter_kw)

    def new_series(self, ans, klass=None, name='Series',
                   plotter_kw=None
                  ):
        if klass is None:
            from src.processing.tasks.figures.figure_editor import SeriesEditor as klass
        func = self.manager.new_series

        self._new_figure(ans, name, func, klass, plotter_kw)

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
#===============================================================================
# actions
#===============================================================================
    def save_figure(self):
        self._save_figure()

    def open_figure(self):
        self._open_figure()
#===============================================================================
# db persistence
#===============================================================================
    def _open_figure(self, name=None):
        if name is None:
            name = self.figure_selector_pane.figure

        if not name:
            return

        db = self.manager.db

        # get the name of the figure for the user
        fig = db.get_figure(name)
        if not fig:
            return
        # load options

        # load analyses
        items = [self._record_view_factory(ai.analysis) for ai in fig.analyses]
        self.unknowns_pane.items = items



    def _save_figure(self):
        db = self.manager.db
        figure = db.add_figure()
        db.flush()

#         for ai in self.unknowns_pane.items:
        for ai in self.active_editor.plotter.analyses:
            dban = ai.dbrecord
            aid = ai.record_id
            if dban:
                db.add_figure_analysis(figure, dban,
                                       status=ai.temp_status and ai.status,
                                       graph=ai.graph_id,
                                       group=ai.group_id,
                                       )
                self.debug('adding analysis {} to figure'.format(aid))
            else:
                self.debug('{} not in database'.format(aid))

        po = self.active_editor.plotter_options_manager.plotter_options
        refg = self.active_editor.plotter.graphs[0]
        r = refg.plots[0].index_mapper.range
        xbounds = '{}, {}'.format(r.low, r.high)
        ys = []
        for pi in refg.plots:
            r = pi.value_mapper.range
            ys.append('{},{}'.format(r.low, r.high))

        ybounds = '|'.join(ys)

        blob = pickle.dumps(po)
        db.add_figure_preference(figure,
                                 xbounds=xbounds,
                                 ybounds=ybounds,
                                 options_pickle=blob)
        db.commit()
#===============================================================================
#
#===============================================================================
    def _new_figure(self, ans, name, func, klass, plotter_kw):
        comp, plotter = None, None
        editor = klass(
#                        component=comp,
#                        plotter=plotter,
                       name=name,
                       processor=self.manager,
                       make_func=func
                       )

        editor._suppress_rebuild = True
        self.plot_editor_pane.component = comp
        self._open_editor(editor)

        if ans:
            if plotter_kw is None:
                plotter_kw = {}
            comp, plotter = func(ans, **plotter_kw)
            editor.plotter = plotter
            editor.component = comp

            editor._unknowns = ans
            self.unknowns_pane.items = ans
        editor._suppress_rebuild = False



#     @on_trait_change('active_editor:plotter:recall_event')
#     def _recall(self, new):
#         print new



    def _get_unique_group_id(self):
        gids = {i.group_id for i in self.unknowns_pane.items}
        return max(gids) + 1

    def _get_selected_indices(self):
        items = self.unknowns_pane.items
        return [items.index(si) for si in self.unknowns_pane.selected]

    def _group_by(self, key):
        if self.active_editor:
            items = self.unknowns_pane.items
            items = sorted(items, key=key)
            for i, (_, analyses) in enumerate(groupby(items, key=key)):
                idxs = [items.index(ai) for ai in analyses]
                self.active_editor.set_group(idxs, i, refresh=False)

#             self.unknowns_pane.update_needed = True
            self.unknowns_pane.refresh_needed = True
            self.active_editor.rebuild(refresh_data=False)

    def _ideogram_factory(self, ans, plotter_options=None):
        probability_curve_kind = 'cumulative'
        mean_calculation_kind = 'weighted_mean'
        data_label_font = None
        metadata_label_font = None
#        highlight_omitted = True
        display_mean_indicator = True
        display_mean_text = True

        p = Ideogram(
#                     db=self.db,
#                     processing_manager=self,
                     probability_curve_kind=probability_curve_kind,
                     mean_calculation_kind=mean_calculation_kind
                     )
        options = dict(
                       title='',
                       data_label_font=data_label_font,
                       metadata_label_font=metadata_label_font,
                       display_mean_text=display_mean_text,
                       display_mean_indicator=display_mean_indicator,
                       )

        if plotter_options is None:
            pom = IdeogramOptionsManager()
            plotter_options = pom.plotter_options

        if ans:
#             self.analyses = ans
            gideo = p.build(ans, options=options,
                            plotter_options=plotter_options)
            if gideo:
                gideo, _plots = gideo

            return gideo, p


#===============================================================================
# handlers
#===============================================================================

    @on_trait_change('plotter_options_pane:pom:plotter_options:[+, aux_plots:+]')
    def _options_update(self, name, new):
        if name == 'initialized':
            return

        do_later(self.active_editor.rebuild)
#         self.active_editor.rebuild()
        self.active_editor.dirty = True

    def _active_editor_changed(self):
        if self.active_editor:
            self.plotter_options_pane.pom = self.active_editor.plotter_options_manager

        super(FigureTask, self)._active_editor_changed()
#============= EOF =============================================
