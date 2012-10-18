#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import List, Event
from traitsui.api import View, Item, TableEditor
from traitsui.menu import Action
#============= standard library imports ========================
import os

#============= local library imports  ==========================
from src.experiment.processing.figures.base_figure import BaseFigure
from src.paths import paths
from src.viewable import ViewableHandler
from src.experiment.processing.plotters.fit_series import FitSeries


class FitSeriesFigureHandler(ViewableHandler):
    def on_apply(self, info):
        if info.object.apply():
            info.ui.dispose()


class FitSeriesFigure(BaseFigure):
    _name = ''
    fit_analyses = List
    apply_event = Event
    series_klass = FitSeries
#    use_user_series_configs = False
    def _manage_data_fired(self):
        db = self.db
        db.connect()
        if self.selector is None:
            db.selector_factory()
            from src.experiment.processing.processing_selector import ProcessingSelector
            ps = ProcessingSelector(db=self.db)
            ps.selector.style = 'panel'
            ps.on_trait_change(self._update_data, 'update_data')
#            ps.edit_traits()

            self.selector = ps
#            if self._debug:
#            a =

            ps.selected_results = [
#                                   ps.selector.results[-7],
                                   ps.selector.results[-6],
                                   ps.selector.results[-2]]
#            ps.selected_results = [i for i in ps.selector.results[-5:-3] if i.analysis_type != 'blank']

        else:
            self.selector.show()

        self._update_data()

    def _get_load_keywords(self):
        return {'ispredictor':True}

    def _get_analyses(self):
        return sorted(self._analyses + self.fit_analyses, key=lambda x: x.timestamp)

    def _check_refresh(self):
        if self._analyses or self.fit_analyses:
            return True

    def _add_analysis(self, a, ispredictor=False):
#        print ispredictor, a
        if ispredictor:
            self._analyses.append(a)
        else:
            a.bgcolor = 'blue'
            self.fit_analyses.append(a)

    def _refresh(self, graph, analyses, padding):
        gs = self.graph_selector

        seriespadding = padding
        if gs.show_series:
            series = self.series_klass()
            series.analyses = self.analyses

            sks = [(si.label, si.fit) for si in self.series_configs if si.show]
            bks = [('{}bs'.format(si.label), si.fit_baseline)
                    for si in self.series_configs if si.show_baseline]

            gids = self._get_gids(analyses)
            gseries = series.build(analyses,
                                   sks, bks, gids,
                                   padding=seriespadding)

            gids = self._get_gids(self.fit_analyses)
            gseries = series.build(self.fit_analyses, sks, bks, gids,
                         graph=gseries,
#                         analyses=,
                         new_plot=False,
                         regress=False,
                         padding=seriespadding,
                         )
            if gseries:
                graph.plotcontainer.add(gseries.plotcontainer)
                series.on_trait_change(self._update_selected_analysis, 'selected_analysis')
            self.series = series
            self.series.graph.on_trait_change(self._refresh_stats, 'regression_results')

        graph.redraw()

    def _get_series_config_path(self):
        return os.path.join(paths.hidden_dir, '{}_series_config'.format(self._name))

    def _get_graph_selector_path(self):
        return os.path.join(paths.hidden_dir, '{}_graph_selector'.format(self._name))

    def apply(self):
        if not self.dirty:
            self.warning_dialog('No series set')
            return False
        self.info('applying {} series'.format(self._name))
        self.apply_event = True
        return True

    def _get_buttons(self):
        return [Action(name='Apply',
                       action='on_apply'), 'Cancel']

    def _get_handler(self):
        return FitSeriesFigureHandler

    def close(self, isok):
        r = True
        if self.dirty:
            r = self.confirmation_dialog('Sure you want to close with out saving')
        return r

#    def _get_gids(self, analyses):
#        gids = list(set([(a.gid, True) for a in analyses]))
#        gids = [(g, True if i == 0 else False) for i, (g, _) in enumerate(gids)]
#        return gids

    @property
    def fit_series(self):
        return [si for si in self.series_configs if si.show and si.fit != '---']

    @property
    def dirty(self):
        return next((s for s in self.fit_series), None)
#============= EOF =============================================
