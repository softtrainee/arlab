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
from traits.api import Instance, List, Any, Bool, on_trait_change, Button
from traitsui.api import View, Item, Group, VSplit, HGroup, VGroup, spring, \
    InstanceEditor, ListEditor
from src.graph.graph import Graph
from src.processing.analysis import Analysis, AnalysisTabularAdapter
from traitsui.editors.tabular_editor import TabularEditor
#============= standard library imports ========================
from tables import openFile
import os
#============= local library imports  ==========================
from src.processing.plotters.api import Ideogram, InverseIsochron, Spectrum, Series
from src.processing.processing_selector import ProcessingSelector
from src.loggable import Loggable
from result import Result
from series_config import SeriesConfig


#@todo: graph baseline series when show baseline fires

#@todo: sort signals ar40,ar39, ar40-baseline,ar39-baseline

class Figure(Loggable):
    graph = Instance(Graph)
    analyses = List(Analysis)
    selected_analysis = Any
    workspace = Any

    series = List
    serieskeys = List
    _serieskeys = List

    nanalyses = -1

    manage_data = Button
    show_ideo = Bool(True)
#    show_isochron = Bool(True)
#    show_spectrum = Bool(True)
    show_series = Bool(True)

#    show_ideo = Bool(False)
    show_isochron = Bool(False)
    show_spectrum = Bool(False)
#    show_series = Bool(True)

    db = Any
    selector = None
    result = Instance(Result, ())


    def refresh(self):
        graph = self.graph

        self.result = Result()
        result = self.result
        analyses = self.analyses
        if not analyses:
            return

        try:
            comps = graph.plotcontainer.components
            graph.plotcontainer.remove(*comps)
        except Exception:
            pass

        pl = 70 if self.show_series else 40
        padding = [pl, 10, 0, 30]
        specpadding = padding
        ideopadding = padding
        isopadding = padding
        seriespadding = padding

        if self.show_ideo:
            ig = Ideogram()
            gideo = ig.build(analyses, padding=ideopadding)
            if gideo:
                graph.plotcontainer.add(gideo.plotcontainer)
                result.add(ig)

        if self.show_spectrum:
            spectrum = Spectrum()
            gspec = spectrum.build(analyses, padding=specpadding)
            if gspec:
                graph.plotcontainer.add(gspec.plotcontainer)

        if self.show_isochron:
            isochron = InverseIsochron()
            giso = isochron.build(analyses, padding=isopadding)
            if giso:
                graph.plotcontainer.add(giso.plotcontainer)

        if self.show_series:
            series = Series()
            sks = [(si.label, si.fit) for si in self.series if si.show]
            bks = [('{}bs'.format(si.label), si.fit_baseline) for si in self.series if si.show_baseline]
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

        keys = []
        for ai in self.analyses:
            keys += ai.signals.keys()

        iso_keys = list(set(keys))

        iso_keys.sort(key=lambda k:int(k[2:4]), reverse=True)

        snames = [s.label for s in self.series]
        for iso in iso_keys:
            if iso.endswith('bs'):
                continue
            s = SeriesConfig(label=iso)
            if not iso in snames:
                self.series.append(s)
                s.on_trait_change(self._refresh_graph, 'show')
                s.on_trait_change(self._refresh_graph, 'fit')
                s.on_trait_change(self._refresh_graph, 'show_baseline')
                s.on_trait_change(self._refresh_graph, 'fit_baseline')

        self.nanalyses = -1
        self.table_adapter.iso_keys = iso_keys

    def _open_file(self, name):
        p = os.path.join(self.workspace.root, name)
        if os.path.isfile(p):
            return openFile(p)

    @property
    def ages(self):
        return [a.age for a in self.analyses]
#===============================================================================
# handlers
#===============================================================================
    @on_trait_change('analyses[]')
    def _analyses_changed(self):
        if len(self.analyses) > self.nanalyses:
            self.refresh()

    @on_trait_change('show_ideo,show_isochron,show_spectrum,show_series')
    def _refresh_graph(self):
        self.refresh()

    def _manage_data_fired(self):
#        db = self.db
#        db.connect()
#        if self.selector is None:
#            db.selector_factory()
#            ps = ProcessingSelector(db=self.db)
#            ps.selector.style = 'panel'
#            ps.on_trait_change(self._update_data, 'update_data')
#            ps.edit_traits()
#
#            self.selector = ps
#        else:
#            self.selector.show()

        self._update_data()

    def _update_data(self):
#        self.result = Result()/
#        ps = self.selector
#        names = [ri.filename for ri in ps.selected_results if ri.filename != '---']
#        attrs = [dict(rid='{}-{}'.format(ri.labnumber, ri.aliquot))
#                      for ri in ps.selected_results if ri.filename != '---']
##        for ri in ps.selected_results:
##            print ri
##            print ri.labnumber, ri.aliquot, 'sadffffffff'
#
#        gids = []
#        gid = 0
#        for ri in ps.selected_results:
#            if ri.filename == '---':
#                gid += 1
#                continue
#            gids.append(gid)

        names = ['B-1.h5', 'e4ee06da-a342-4144-aaff-ace8592d586b.h5', '5682288f-870f-4243-9835-34a5031b5eba.h5']
        attrs = [dict(rid='blank-0') for n in names]
        gids = None
        if names:
            self.load_analyses(names, gids, attrs)
            self.refresh()
#===============================================================================
# factories
#===============================================================================
    def _analyses_factory(self, n, **kw):

        df = self._open_file(n)
        if df:
            a = Analysis(uuid=n,
                         **kw)
            a.load_from_file(df)
            return a

    def _graph_factory(self, klass=None, **kw):
        g = Graph(container_dict=dict(kind='h', padding=10,
                                      bgcolor='red',
                                      spacing=10,
                                      ))
        return g
#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        graph_grp = Item('graph', show_label=False, style='custom',
                         height=0.7
                         )
        infogrp = Item('result',
                       show_label=False, style='custom')

        self.table_adapter = ta = AnalysisTabularAdapter()
        datagrp = Group(Item('analyses',
                      show_label=False,
                       height=0.3,
                      editor=TabularEditor(adapter=ta,
                                           column_clicked='object.column_clicked',
                                           selected='object.selected_analysis',
                                           editable=False, operations=['delete'])
                       ),
                       label='Data',
                       )

        tb = HGroup(
                  spring,
                  Item('manage_data', show_label=False),
                  )
        gcntrlgrp = HGroup(
                           VGroup(
                                  Item('show_ideo', label='Ideogram'),
                                  Item('show_isochron', label='Isochron'),
                                  Item('show_spectrum', label='Spectrum'),
                                  Item('show_series', label='Series')
                                  ),

                                 Item(
                                      'series',
                                      show_label=False,
                                      editor=ListEditor(mutable=False,
                                                        style='custom',
                                                        editor=InstanceEditor()
                                                        ),
                                      width=200
                                      ),
                            label='Graph'
                           )
        cntrl_grp = VGroup(tb,
                           Group(
                                 infogrp,
                                 gcntrlgrp,
                                 datagrp,
                                 layout='tabbed')
                           )
        v = View(
                 VSplit(graph_grp,
                        cntrl_grp),
                 resizable=True,
                 width=0.5,
                 height=0.75,
                 title=' '
                 )
        return v
#===============================================================================
# defaults
#===============================================================================
    def _graph_default(self):
        return self._graph_factory()



#============= EOF =============================================
