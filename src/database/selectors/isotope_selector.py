#===============================================================================
# Copyright 2011 Jake Ross
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
from traits.api import HasTraits, Any, List, String, \
    Float, Bool, Int, Instance, Property, Dict, Enum, on_trait_change, \
    Str, Trait
from traitsui.api import VGroup, HGroup, Item, Group, View, ListStrEditor, \
    InstanceEditor, ListEditor, EnumEditor, Label, Spring
#============= standard library imports ========================

#============= local library imports  ==========================
from src.database.core.db_selector import DBSelector
from src.graph.time_series_graph import TimeSeriesStackedGraph
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.database.core.base_db_result import DBResult
from src.database.orms.isotope_orm import AnalysisTable

from src.graph.regression_graph import StackedTimeSeriesRegressionGraph
from src.database.isotope_analysis.analyzer import Analyzer
from src.database.isotope_analysis.analysis_summary import AnalysisSummary
from src.database.core.base_results_adapter import BaseResultsAdapter

class AnalysisResult(DBResult):
    title_str = 'Analysis'
    window_height = 600
    window_width = 650

    sniff_graph = Instance(StackedTimeSeriesRegressionGraph)
    signal_graph = Instance(StackedTimeSeriesRegressionGraph)
    baseline_graph = Instance(StackedTimeSeriesRegressionGraph)
#    sniff_graph = Instance(TimeSeriesStackedGraph)
#    signal_graph = Instance(TimeSeriesStackedGraph)
#    baseline_graph = Instance(TimeSeriesStackedGraph)
    analyzer = Instance(Analyzer)

    categories = List(['summary', 'signal', 'sniff', 'baseline', 'analyzer'])
    selected = Any('signal')
    display_item = Instance(HasTraits)

    iso_keys = None
    intercepts = None

    @property
    def labnumber(self):
        return self._db_result.labnumber

    def traits_view(self):
        info = self._get_info_grp()
        info.label = 'Info'
        grp = HGroup(
                        Item('categories', editor=ListStrEditor(
                                                                editable=False,
                                                                operations=[],
                                                                selected='selected'
                                                                ),
                             show_label=False,
                             width=0.10
                             ),
                        Item('display_item', show_label=False, style='custom'),
                        )

        return self._view_factory(grp)

    def _selected_changed(self):
        if self.selected is not None:

            if self.selected == 'analyzer':
                item = self.analyzer
#                info = self.analyzer.edit_traits()
#                if info.result:
#                    self.analyzer.apply_fits()
            elif self.selected == 'summary':
                item = AnalysisSummary(age=10.0,
                                       error=0.01,
                                       result=self
                                       )
                item.age = 12

            else:
                item = getattr(self, '{}_graph'.format(self.selected))
            self.trait_set(display_item=item)

    def load_graph(self, graph=None, xoffset=0):
        keys, sniffs, signals, baselines = self._get_data()

        self.iso_keys = keys

#        signals = [('a', ([1, 2, 3, 4, 5],
#                  [1, 2, 3, 3.5, 5])
#                  )]

        graph = self._load_graph(signals)

        self.intercepts = [3.3, ] * len(keys)

        self.signal_graph = graph
        self.display_item = graph

        graph = self._load_graph(sniffs)
        self.sniff_graph = graph

        graph = self._load_graph(baselines)
        self.baseline_graph = graph

#        self.selected = 'analyzer'

        self.analyzer = Analyzer(analysis=self)
#        self.analyzer.fits = [AnalysisParams(fit='linear', name=k) for k in keys]

    def _load_graph(self, data):
        graph = self._graph_factory(klass=StackedTimeSeriesRegressionGraph)

        gkw = dict(xtitle='Time',
                       padding=[50, 50, 40, 40],
                       panel_height=50,
                       )

        for i, (key, (xs, ys)) in enumerate(data):
            gkw['ytitle'] = key

            graph.new_plot(**gkw)
            graph.new_series(xs, ys, plotid=i)
#            graph.set_series_label(key, plotid=i)

            params = dict(orientation='right' if i % 2 else 'left',
                          axis_line_visible=False
                          )
            graph.set_axis_traits(i, 'y', **params)

        return graph

    def _get_table_data(self, dm, grp):
        return [(ti.name, zip(*[(r['time'], r['value']) for r in ti.iterrows()]))
              for ti in dm.get_tables(grp)]

    def _get_data(self):
        dm = self._data_manager_factory()
        dm.open_data(self._get_path())

        sniffs = []
        signals = []
        baselines = []
        keys = []
        if isinstance(dm, H5DataManager):

            sniffs = self._get_table_data(dm, 'sniffs')
            signals = self._get_table_data(dm, 'signals')
            baselines = self._get_table_data(dm, 'baselines')
            if sniffs or signals or baselines:
                self._loadable = True
                keys = set(zip(*sniffs)[0] if sniffs else [] +
                           zip(*signals)[0] if signals else [] +
                           zip(*baselines)[0] if baselines else []
                           )
        return keys, sniffs, signals, baselines


class IsotopeResultsAdapter(BaseResultsAdapter):
    columns = [('ID', 'rid'),
               ('Labnumber', 'labnumber'),
               ('Date', 'rundate'),
               ('Time', 'runtime')
               ]

class IsotopeAnalysisSelector(DBSelector):
    title = 'Recall Analyses'

    parameter = String('AnalysisTable.rundate')
    query_table = AnalysisTable
    result_klass = AnalysisResult

    tabular_adapter = IsotopeResultsAdapter
#    multi_graphable = Bool(True)

#    def _load_hook(self):
#        jt = self._join_table_parameters
#        if jt:
#            self.join_table_parameter = str(jt[0])

    def _get_selector_records(self, **kw):
        return self._db.get_analyses(**kw)

#    def _get__join_table_parameters(self):
#        dv = self._db.get_devices()
#        return list(set([di.name for di in dv if di.name is not None]))



#        f = lambda x:[str(col)
#                           for col in x.__table__.columns]
#        params = f(b)
#        return list(params)
#        return

#============= EOF =============================================
