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
from pyface.tasks.task_layout import TaskLayout, Splitter, PaneItem, Tabbed, \
    HSplitter
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
# from src.processing.plotters.ideogram import Ideogram
from src.processing.plotter_options_manager import IdeogramOptionsManager
from src.processing.tasks.figures.actions import SaveFigureAction, \
    OpenFigureAction
from src.processing.tasks.browser.browser_task import BaseBrowserTask
from src.processing.tasks.browser.panes import BrowserPane
from src.codetools.simple_timeit import timethis

import weakref

from .editors.spectrum_editor import SpectrumEditor
from .editors.isochron_editor import InverseIsochronEditor
from .editors.ideogram_editor import IdeogramEditor
from src.processing.tasks.figures.figure_editor import FigureEditor
from src.processing.tasks.figures.editors.series_editor import SeriesEditor

class FigureTask(AnalysisEditTask, BaseBrowserTask):
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
                          left=HSplitter(
                                    PaneItem('pychron.browser'),
                                    Splitter(
                                         Tabbed(
                                                PaneItem('pychron.analysis_edit.unknowns'),
                                                PaneItem('pychron.processing.figures.plotter_options')
                                                ),
                                         Tabbed(
                                                PaneItem('pychron.analysis_edit.controls'),
                                                PaneItem('pychron.processing.editor'),
                                                ),
                                         orientation='vertical'
                                         )
                                    ),

#                           right=Splitter(
#                                          PaneItem('pychron.search.results'),
#                                          PaneItem('pychron.search.query'),
#                                          orientation='vertical'
#                                          )
                          )
#===============================================================================
# task protocol
#===============================================================================

    def prepare_destroy(self):
        for ed in self.editor_area.editors:
            if isinstance(ed, FigureEditor):
                pom = ed.plotter_options_manager
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
                        BrowserPane(model=self)
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
    def new_ideogram(self, ans=None, klass=None, tklass=None,
                     name='Ideo', plotter_kw=None):

        if klass is None:
            klass = IdeogramEditor

        if tklass is None:
            from src.processing.tasks.tables.editors.laser_table_editor \
                import LaserTableEditor as tklass

        self._new_figure(ans, name, klass, tklass)

    def new_spectrum(self, ans=None, klass=None,
                     tklass=None,
                     name='Spec', plotter_kw=None):
        if klass is None:
            klass = SpectrumEditor

        if tklass is None:
            from src.processing.tasks.tables.editors.laser_table_editor \
                import LaserTableEditor as tklass

        self._new_figure(ans, name, klass, tklass)

    def new_inverse_isochron(self, ans=None, name='Inv. Iso.',
                             klass=None, tklass=None, plotter_kw=None):
        if klass is None:
            klass = InverseIsochronEditor

        if tklass is None:
            from src.processing.tasks.tables.editors.laser_table_editor \
                import LaserTableEditor as tklass

        feditor = self._new_figure(ans, name, klass, tklass,
                                   add_iso=False)

    def new_series(self, ans=None, name='Series',
                             klass=None, tklass=None, plotter_kw=None):
        if klass is None:
            klass = SeriesEditor

        if tklass is None:
            from src.processing.tasks.tables.editors.laser_table_editor \
                import LaserTableEditor as tklass

        feditor = self._new_figure(ans, name, klass, tklass,
                                   add_iso=False)


#         func = self.manager.new_inverse_isochron
#         from src.processing.tasks.figures.figure_editor import InverseIsochronEditor
#         klass = InverseIsochronEditor
#         self._new_figure(ans, name, func, klass, plotter_kw)

#     def new_series(self, ans, klass=None, name='Series',
#                    plotter_kw=None
#                   ):
#         if klass is None:
#             from src.processing.tasks.figures.figure_editor import SeriesEditor as klass
#         func = self.manager.new_series
#
#         self._new_figure(ans, name, func, klass, plotter_kw)
#
#         editor = self.active_editor
#         refiso = ans[0]
# #         editor._unknowns = ans
#         editor.trait_set(_unknowns=ans,
#                          unknowns=ans,
#                          trait_change_notify=False)
# #         editor.unknowns = ans
#         editor.tool.load_fits(refiso.isotope_keys,
#                               refiso.isotope_fits
#                               )
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
    def _new_figure(self, ans, name, klass, tklass=None, add_iso=True):
#         comp, plotter = None, None
        # new figure editor
        editor = klass(
                       name=name,
                       processor=self.manager,
                       )

#         self.plot_editor_pane.component = None


        if not ans:
            ans = self.unknowns_pane.items

        if ans:
            editor.unknowns = ans
            self.unknowns_pane.items = ans

#             comp, plotter = func(ans)
#             editor.plotter = plotter
#             editor.component = comp
#
        self._open_editor(editor)

        if tklass:
            # open table
            teditor = self._new_table(ans, name, tklass)
            if teditor:
                editor.associated_editors.append(weakref.ref(teditor)())

        if add_iso:
            # open associated isochron
            ieditor = self._new_associated_isochron(ans, name)
            if ieditor:
                editor.associated_editors.append(weakref.ref(ieditor)())

        # activate figure editor
        self.editor_area.activate_editor(editor)
        return editor

    def _new_associated_isochron(self, ans, name):
        name = '{}-isochron'.format(name)
        editor = InverseIsochronEditor(name=name,
                                       processor=self.manager
                                       )
        return self._add_editor(editor, ans)
#         if ans:
#             ed = next((e for e in self.editor_area.editors
#                         if e.name == editor.name))
#             if not ed:
#                 editor.items = ans
#                 self.editor_area.add_editor(editor)
#
#         return editor

    def _new_table(self, ans, name, klass):
        name = '{}-table'.format(name)
        editor = klass(name=name)
        return self._add_editor(editor, ans)

    def _add_editor(self, editor, ans):
        ed = None
        if ans:
            if isinstance(editor, FigureEditor):
                editor.unknowns = ans
            else:
                editor.items = ans

            ed = next((e for e in self.editor_area.editors
                        if e.name == editor.name), None)

        if not ed:
            self.editor_area.add_editor(editor)
        else:
            editor = None

        return editor

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
#             print 'asdfsdfsadfsd'
            self.active_editor.rebuild(refresh_data=False)

#     def _ideogram_factory(self, ans, plotter_options=None):
#         probability_curve_kind = 'cumulative'
#         mean_calculation_kind = 'weighted_mean'
#         data_label_font = None
#         metadata_label_font = None
# #        highlight_omitted = True
#         display_mean_indicator = True
#         display_mean_text = True
#
#         p = Ideogram(
# #                     db=self.db,
# #                     processing_manager=self,
#                      probability_curve_kind=probability_curve_kind,
#                      mean_calculation_kind=mean_calculation_kind
#                      )
#         options = dict(
#                        title='',
#                        data_label_font=data_label_font,
#                        metadata_label_font=metadata_label_font,
#                        display_mean_text=display_mean_text,
#                        display_mean_indicator=display_mean_indicator,
#                        )
#
#         if plotter_options is None:
#             pom = IdeogramOptionsManager()
#             plotter_options = pom.plotter_options
#
#         if ans:
# #             self.analyses = ans
#             gideo = p.build(ans, options=options,
#                             plotter_options=plotter_options)
#             if gideo:
#                 gideo, _plots = gideo
#
#             return gideo, p


#===============================================================================
# handlers
#===============================================================================
#     @on_trait_change('plotter_options_pane:pom:plotter_options:aux_plots:x_error')
#     def _update_x_error(self):


    @on_trait_change('plotter_options_pane:pom:plotter_options:[+, aux_plots:+]')
    def _options_update(self, name, new):
        if name == 'initialized':
            return
#         print 'asdfsdf'
        self.active_editor.rebuild(refresh_data=False)
#         do_later(self.active_editor.rebuild, refresh_data=False)
#         self.active_editor.rebuild()
        self.active_editor.dirty = True

    def _active_editor_changed(self):
        if self.active_editor:
#             if hasattr(self.active_editor, 'plotter_options_manager'):
            if isinstance(self.active_editor, FigureEditor):
                self.plotter_options_pane.pom = self.active_editor.plotter_options_manager

        super(FigureTask, self)._active_editor_changed()

    #===========================================================================
    # browser protocol
    #===========================================================================
    def _dclicked_sample_changed(self, new):
        for sa in self.selected_sample:

            ans = self._get_sample_analyses(sa)
#             ans = man.make_analyses(ans)
            self.unknowns_pane.items = ans

#             sam = next((si
#                         for si in self.active_editor.items
#                             if si.sample == sa.name), None)
#             if sam is None:
#                 man = self.manager
#                 ans = self._get_sample_analyses(sa)
#                 ans = man.make_analyses(ans)
#============= EOF =============================================
