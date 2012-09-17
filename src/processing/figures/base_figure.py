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
from traits.api import HasTraits, Instance, Any, List, Bool, Property, \
    cached_property, Button, on_trait_change
from traitsui.api import View, Item, TabularEditor, VSplit, Group, HGroup, VGroup, \
    spring
#============= standard library imports ========================
from tables import openFile
import os
#============= local library imports  ==========================
from src.loggable import Loggable
from src.graph.graph import Graph
from src.processing.analysis import Analysis, AnalysisTabularAdapter
from src.processing.result import Result
from src.processing.plotters.series import Series
from src.processing.series_config import SeriesConfig
from src.processing.processing_selector import ProcessingSelector
from src.helpers.traitsui_shortcuts import listeditor

class BaseFigure(Loggable):
    graph = Instance(Graph)
    analyses = List(Analysis)
    selected_analysis = Any
    workspace = Any

    series_list = List
    show_series = Bool(True)
    db = Any
    selector = None
#    result = Instance(Result, ())

    _debug = True
    series = Instance(Series)

    manage_data = Button
    signal_keys = Property
    isotope_keys = Property

    def refresh(self):
        analyses = self.analyses
        if not analyses:
            return

        graph = self.graph
        try:
            comps = graph.plotcontainer.components
            graph.plotcontainer.remove(*comps)
        except Exception:
            pass

        pl = 70 if self.show_series else 40
        padding = [pl, 10, 0, 30]
        self._refresh(graph, analyses, padding)

    def _refresh(self, graph, analyses, padding):

        seriespadding = padding
        if self.show_series:
            series = Series()
            sks = [(si.label, si.fit) for si in self.series_list if si.show]
            bks = [('{}bs'.format(si.label), si.fit_baseline) for si in self.series_list if si.show_baseline]
            gseries = series.build(analyses, sks, bks, padding=seriespadding)
            if gseries:
                graph.plotcontainer.add(gseries.plotcontainer)

        graph.redraw()

    def load_analyses(self, names, groupids=None, attrs=None):
        if groupids is None:
            groupids = [0 for n in names]
        if attrs is None:
            attrs = [dict() for n in names]

        self.nanalyses = len(names) - 1
        _names = [a.uuid for a in self.analyses]

        #@todo: change to list comp to speed up
        for n, gid, attr in zip(names, groupids, attrs):
            if not n in _names:
                a = self._analyses_factory(n, gid=gid, **attr)
                if a:
                    self.analyses.append(a)
                else:
                    self.warning('could not load {}'.format(n))
            else:
                a = next((a for a in self.analyses if a.uuid == n), None)
                a.gid = gid

        self.nanalyses = -1

        snames = [s.label for s in self.series_list]
        keys = [iso for iso in self.isotope_keys if not iso in snames]
        keys.sort(key=lambda k:k[2:4], reverse=True)
        self.series_list = [SeriesConfig(label=iso, parent=self)
                                for iso in keys]

        self.signal_table_adapter.iso_keys = self.isotope_keys

        signal_keys = self.signal_keys
        signal_keys.sort(key=lambda k:k[2:4], reverse=True)
        bs_keys = [i for i in signal_keys if i.endswith('bs')]
        bs_keys.sort(key=lambda k:k[2:4], reverse=True)
        self.baseline_table_adapter.iso_keys = bs_keys

#===============================================================================
# private
#===============================================================================
    def _update_data(self):
        ps = self.selector
        names = [ri.filename for ri in ps.selected_results if ri.filename != '---']
        attrs = [dict(dbresult=ri._db_result)
                      for ri in ps.selected_results if ri.filename != '---']

        gids = []
        gid = 0
        for ri in ps.selected_results:
            if ri.filename == '---':
                gid += 1
                continue
            gids.append(gid)

        gids = None
        if names:
            self.load_analyses(names, gids, attrs)
            self.refresh()

    def _open_file(self, name):
        p = os.path.join(self.workspace.root, name)

        if os.path.isfile(p):
            return openFile(p)
        else:
            rname = os.path.basename(p)
            if self.repo.isfile(rname):
                self.info('fetching file from repo')
#                out = open(p, 'wb')
                self.repo.retrieveFile(rname, p)
                return openFile(p)
            else:
                self.warning('{} is not a file'.format(name))
#===============================================================================
# handlers
#===============================================================================
    def _update_selected_analysis(self, new):
        self.selected_analysis = new

    @on_trait_change('analyses[]')
    def _analyses_changed(self):
        if len(self.analyses) > self.nanalyses:
            self.refresh()

    @on_trait_change('show_series')
    def _refresh_graph(self, obj, name, old, new):
        self.refresh()

    def _manage_data_fired(self):
        db = self.db
        db.connect()
        if self.selector is None:
            db.selector_factory()
            ps = ProcessingSelector(db=self.db)
            ps.selector.style = 'panel'
            ps.on_trait_change(self._update_data, 'update_data')
#            ps.edit_traits()

            self.selector = ps
            if self._debug:
                ps.selected_results = [ps.selector.results[-1]]
        else:
            self.selector.show()

        self._update_data()
#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        top = self._get_top_group()
        bot = self._get_bottom_group()
        tb = HGroup(spring,
                       Item('manage_data', show_label=False),
                       )
        bottom = VGroup(tb, bot)
        v = View(VSplit(top, bottom),
                 resizable=True,
                 width=0.5,
                 height=0.8,
                 title=' '
                 )
        return v

    def _get_top_group(self):
        graph_grp = Item('graph', show_label=False, style='custom',
                         height=0.7
                         )
        return graph_grp

    def _get_bottom_group(self):

        grps = [
              self._get_graph_edit_group(),
              self._get_signals_group(),
              self._get_baselines_group(),
              ]

        g = Group(*grps,
                  layout='tabbed')

        return g

    def _get_signals_group(self):
        self.signal_table_adapter = ta = AnalysisTabularAdapter()
        sgrp = Group(Item('analyses',
                      show_label=False,
                       height=0.3,
                      editor=TabularEditor(adapter=ta,
                                           column_clicked='object.column_clicked',
                                           selected='object.selected_analysis',
                                           editable=False, operations=['delete'])
                       ),
                       label='Signals',
                       )
        return sgrp

    def _get_baselines_group(self):
        self.baseline_table_adapter = ta = AnalysisTabularAdapter()
        baselinegrp = Group(Item('analyses',
                                 show_label=False,
                                 height=0.3,
                                 editor=TabularEditor(adapter=ta,
                                           editable=False,
                                           )
                       ),
                       label='Baselines',
                       )
        return baselinegrp

    def _get_graph_edit_group(self):
        gs = self._get_graph_shows()
        g = HGroup(VGroup(*gs),
                 listeditor('series_list', width=200),
                 label='Graph'
                 )
        return g

    def _get_graph_shows(self):
        return [Item('show_series', label='Series')]
#===============================================================================
# factories
#===============================================================================
    def _analyses_factory(self, n, **kw):

        df = self._open_file(n)
        if df:
            a = Analysis(uuid=n,
                         **kw)

            #need to call both load from file and database
            a.load_from_file(df)
            a.load_from_database()

            return a

    def _graph_factory(self, klass=None, **kw):
        g = Graph(container_dict=dict(kind='h', padding=10,
                                      bgcolor='red',
                                      spacing=10,
                                      ))
        return g
#===============================================================================
# defaults
#===============================================================================
    def _graph_default(self):
        return self._graph_factory()

#===============================================================================
# property get/set
#===============================================================================
    def _get_isotope_keys(self):
        keys = self.signal_keys
        return [i for i in keys if not (i.endswith('bs') or i.endswith('bl'))]

    def _get_signal_keys(self):
        keys = [ki for ai in self.analyses
                    for ki in ai.signals.keys()]
        return list(set(keys))
#============= EOF =============================================
