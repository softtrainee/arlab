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
    spring, Handler
import apptools.sweet_pickle as pickle
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
from src.viewable import ViewableHandler, Viewable
from src.paths import paths
from src.database.core.database_selector import ColumnSorterMixin
from src.displays.rich_text_display import RichTextDisplay
from src.processing.export.csv_exporter import CSVExporter
from src.processing.export.excel_exporter import ExcelExporter

class GraphSelector(HasTraits):
    show_series = Bool(False)
    selections = Property
    @classmethod
    def _item(cls, name, l):
        return Item(name, label=l)
    def _get_selections(self):
        return [self._item('show_series', 'Series')]

    def traits_view(self):
        v = View(VGroup(*self.selections))
        return v

class BaseFigure(Viewable, ColumnSorterMixin):
    graph = Instance(Graph)
    analyses = List(Analysis)
    selected_analysis = Any
    workspace = Any
    repo = Any
    db = Any

    series_configs = List
    show_series = Bool(True)
    selector = None
#    result = Instance(Result, ())

#    _debug = False
    _debug = True
    series = Instance(Series)

    manage_data = Button
    signal_keys = Property
    isotope_keys = Property(depends_on='signal_keys')

    graph_selector = Instance(GraphSelector, ())

    series_klass = Series
    series_config_klass = SeriesConfig

    use_user_series_configs = True
    use_user_graph_selector = True

    results_display = Instance(RichTextDisplay, (),
                               )


    show_results = Button('stats')
    export_csv = Button('csv')
    export_pdf = Button('pdf')
    export_excel = Button('excel')


    def refresh(self):
        self.results_display.clear()
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

        self._refresh_stats()

    def _refresh_stats(self):
        rd = self.results_display
        rd.clear()
        if self.series:
            if self.series.graph:
                tabulate = lambda xs:' '.join(map('{:<10s}'.format,
                                          map('{:0.7f}'.format,
                                              xs)))
#                xx = ['', ' *x', ' *x2', ' *x3']
                for config, reg in zip(self.series_configs,
                                       self.series.graph.regressors):
                    if 'average' in config.fit.lower():
                        h = '          mean          SD          SEM'
                        rd.add_text(h)
                        rd.add_text('{} ={}'.format(config.label,
                                                    '{:<10s}'.format('{:0.7f}'.format(reg.coefficients[0]))))
#                        es = ''.join(map('{:0.7f}'.format, reg.coefficient_errors))
                        es = tabulate(reg.coefficient_errors)
                        es = '{:<10s}'.format(es)
                        rd.add_text('err  =            {}'.format(es))
                    else:
                        h = '          c          x          x2          x3'
                        rd.add_text(h)
#                    cs = reg.coefficients
#                    ss = ' + '.join(map(lambda x:'{:0.7f}{}'.format(*x),
#                                              zip(cs, xx[:len(cs)][::-1])))
                        cs = reg.coefficients
                        cs = cs[::-1]
#                        ss = ' '.join(map('{:<10s}'.format,
#                                          map('{:0.7f}'.format,
#                                              cs)))
                        ce = reg.coefficient_errors
                        ce = ce[::-1]
#                        se = ' '.join(map('{:<10s}'.format,
#                                          map('{:0.7f}'.format,
#                                              ce)))
    ##                    
                        ss = tabulate(cs)
                        se = tabulate(ce)
                        rd.add_text('{} ='.format(config.label) + ss)
                        rd.add_text('err  ='.format(config.label) + se)

    def _get_gids(self, analyses):
        return list(set([(a.gid, True) for a in analyses]))

    def _refresh(self, graph, analyses, padding):
        gs = self.graph_selector

        seriespadding = padding
        if gs.show_series:
            series = self.series_klass()
            sks = [(si.label, si.fit) for si in self.series_configs if si.show]
            bks = [('{}bs'.format(si.label), si.fit_baseline)
                    for si in self.series_configs if si.show_baseline]

            gids = self._get_gids(analyses)
            gseries = series.build(analyses, sks, bks, gids, padding=seriespadding)
            if gseries:
                graph.plotcontainer.add(gseries.plotcontainer)
                series.on_trait_change(self._update_selected_analysis, 'selected_analysis')
            self.series = series
            self.series.graph.on_trait_change(self._refresh_stats, 'regression_results')
        graph.redraw()

    def load_analyses(self, names, groupids=None, attrs=None):
        if groupids is None:
            groupids = [0 for n in names]
        if attrs is None:
            attrs = [dict() for n in names]

        self.nanalyses = len(self.analyses) + len(names) - 1
        _names = [a.uuid for a in self.analyses]

        #@todo: change to list comp to speed up
        for n, gid, attr in zip(names, groupids, attrs):
            if not n in _names:
                a = self._analyses_factory(n, gid=gid, **attr)
                if a:
                    self.info('loading analysis {} groupid={}'.format(a.rid, gid))
                    self.analyses.append(a)
                else:
                    self.warning('could not load {}'.format(n))
            else:
                a = next((a for a in self.analyses if a.uuid == n), None)
                a.gid = gid

        self.nanalyses = -1

        keys = self.isotope_keys
        keys.sort(key=lambda k:k[2:4], reverse=True)
        if not self.series_configs:
            self.series_configs = [self.series_config_klass(label=iso, parent=self)
                                   for iso in keys]
        else:
            #have a series configs list 
            #load any missing isotopes
#            print keys
            for i, iso in enumerate(keys):
                se = next((s for s in self.series_configs if s.label == iso), None)
#                print i, iso, se
                if not se:
                    self.series_configs.insert(1, self.series_config_klass(label=iso, parent=self))
                else:
                    se.parent = self

        for i, se in enumerate(self.series_configs):
            se.graphid = i
#        snames = [s.label for s in self.series_configs]
#        keys = [iso for iso in self.isotope_keys if not iso in snames]

        #clone current series list
#        if self.series_configs is not None:
#            series = [si.label for si in self.series_configs]
#            sl = [iso if iso in series else SeriesConfig(label=iso) for iso in keys]
#            for si in sl:
#                si.parent = self
#            self.series_configs = sl
##            for iso in keys:
##                if iso in series:
##                    sl.append(iso)
##                else:
##                    sl.appned
#        else:
#            self.series_configs = [SeriesConfig(label=iso, parent=self)
#                                for iso in keys]

        self.signal_table_adapter.iso_keys = self.isotope_keys

        signal_keys = self.signal_keys
        signal_keys.sort(key=lambda k:k[2:4], reverse=True)
        bs_keys = [i for i in signal_keys if i.endswith('bs')]
        bs_keys.sort(key=lambda k:k[2:4], reverse=True)

        self.baseline_table_adapter.iso_keys = bs_keys

#===============================================================================
# viewable
#===============================================================================
    def closed(self, ok):
        self._dump_series_configs()
        self._dump_graph_selector()

    def opened(self):
        if self.use_user_series_configs:
            self._load_series_configs()
        if self.use_user_graph_selector:
            self._load_graph_selector()
#===============================================================================
# persistence
#===============================================================================
    def _get_series_config_path(self):
        return os.path.join(paths.hidden_dir, 'series_config')

    def _get_graph_selector_path(self):
        return os.path.join(paths.hidden_dir, 'graph_selector')

    def _load_graph_selector(self):
        p = self._get_graph_selector_path()
        obj = self._load_obj(p)
        if obj is not None:
            self.graph_selector = obj

    def _load_series_configs(self):
        p = self._get_series_config_path()
        obj = self._load_obj(p)
        if obj:
            for si in obj:
                si.parent = self
            self.series_configs = obj

    def _dump_graph_selector(self):
        p = self._get_graph_selector_path()
        self._dump_obj(self.graph_selector, p)

    def _dump_series_configs(self):
        p = self._get_series_config_path()
        self._dump_obj(self.series_configs, p)

    def _dump_obj(self, obj, p):
        try:
            with open(p, 'wb') as f:
                pickle.dump(obj, f)
        except Exception, e :
            print e

    def _load_obj(self, p):
        try:

            with open(p, 'rb') as f:
                obj = pickle.load(f)
                return obj
        except Exception, e:
            print e
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

#        self.refresh()
#        self.refresh()
#===============================================================================
# handlers
#===============================================================================
    def _update_selected_analysis(self, new):
        self.selected_analysis = new

    @on_trait_change('analyses[]')
    def _analyses_changed(self):
#        print len(self.analyses), self.nanalyses
        if len(self.analyses) > self.nanalyses:
            print 'refreshing analysis change'
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
            ps.edit_traits()

            self.selector = ps
            if self._debug:
                ps.selected_results = [i for i in ps.selector.results[2:6] if i.analysis_type != 'blank']

        else:
            self.selector.show()

        self._update_data()
    def _show_results_fired(self):
        self.results_display.edit_traits()

    def _export_csv_fired(self):
        self.info('exporting to csv')
        self._export(CSVExporter)

    def _export_excel_fired(self):
        self.info('exporting to csv')
        self._export(ExcelExporter)

    def _export_pdf_fired(self):
        self.info('exporting to pdf')
#        self._export(pdfExporter)

    def _export(self, klass):
        exp = klass(figure=self)
        exp.export(path='/Users/ross/Sandbox/aaaaaaaaaexporttest.xls')
#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        top = self._get_top_group()
        bot = self._get_bottom_group()
        export = HGroup(spring, 'export_csv', 'export_excel', 'export_pdf', show_labels=False,
                        enabled_when='analyses'
                        )
        tb = HGroup(
#                    spring,
                    export,
#                    Item('export_csv', show_label=False),
#                    Item('export_excel', show_label=False),
#                    Item('export_pdf', show_label=False),
                    Item('show_results', show_label=False),
                       Item('manage_data', show_label=False),
                       )
        bottom = VGroup(tb, bot)

        v = View(VSplit(top, bottom),
                 resizable=True,
                 width=0.5,
                 height=0.8,
                 title=' '
                 )
        v.buttons = self._get_buttons()
        v.handler = self._get_handler()
        return v


    def _get_buttons(self):
        return []

    def _get_handler(self):
        return ViewableHandler

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
        grp, ta = self._analyses_table_factroy('Signals')
        self.signal_table_adapter = ta
        return grp

#        self.signal_table_adapter = ta = AnalysisTabularAdapter()
#        sgrp = Group(Item('analyses',
#                      show_label=False,
##                       height=0.3,
#                      editor=TabularEditor(adapter=ta,
#                                           column_clicked='object.column_clicked',
#                                           selected='object.selected_analysis',
#                                           editable=False,
##                                            operations=['delete']
#                                            )
#                       ),
#                       label='Signals',
#                       )
#        return sgrp

    def _get_baselines_group(self):
        grp, ta = self._analyses_table_factroy('Baselines')
        self.baseline_table_adapter = ta
        return grp

#        self.baseline_table_adapter = ta = AnalysisTabularAdapter()
#        baselinegrp = Group(Item('analyses',
#                                 show_label=False,
##                                 height=0.3,
#                                 editor=TabularEditor(adapter=ta,
#                                           selected='object.selected_analysis',
#                                           editable=False,
#                                           )
#                       ),
#                       label='Baselines',
#                       )
#        return baselinegrp

    def _get_graph_edit_group(self):
        g = HGroup(Item('graph_selector', style='custom', show_label=False),
                 listeditor('series_configs',
                            height=125,
                            width=200),
                 label='Graph'
                 )
        return g
#    def _get_graph_edit_group(self):
#        gs = self._get_graph_shows()
#        g = HGroup(VGroup(*gs),
#                 listeditor('series_configs', width=200),
#                 label='Graph'
#                 )
#        return g
#
#    def _get_graph_shows(self):
#        return [Item('show_series', label='Series')]
#===============================================================================
# factories
#===============================================================================
    def _analyses_factory(self, n, **kw):

#        df = self._open_file(n)
#        if df:
        a = Analysis(uuid=n,
                     repo=self.repo,
                     workspace=self.workspace,
                     ** kw)

        #need to call both load from file and database
        if a.load_from_file(n):
            a.load_from_database()
            a.load_age()
            return a

    def _graph_factory(self, klass=None, **kw):
        g = Graph(container_dict=dict(kind='h', padding=10,
                                      bgcolor='lightgray',
                                      spacing=10,
                                      ))
        return g

    def _analyses_table_factroy(self, name):
        ta = AnalysisTabularAdapter()
        grp = Group(Item('analyses',
                                 show_label=False,
                                 height=0.3,
                                 editor=TabularEditor(adapter=ta,
                                           editable=False,
                                           column_clicked='object.column_clicked',
                                           selected='object.selected_analysis',
                                           )
                       ),
                       label=name,
                       )
        return grp, ta
#===============================================================================
# defaults
#===============================================================================
    def _graph_default(self):
        return self._graph_factory()

    def _results_display_default(self):
        r = RichTextDisplay(default_size=10,
                            default_color='black',
                            width=290,
                            selectable=True,
                            id='stats_display.{}'.format(self.workspace.name)
                            )
        r.title = '{} Stats'.format(self.workspace.name)
#        r.title = ''.format(self)
        return r
#===============================================================================
# property get/set
#===============================================================================
    def _get_isotope_keys(self):
        excks = ['bs', 'bl', 'bg']
        def exc(ki):
            f = lambda ei: ki.endswith(ei)
            return sum(map(f, excks)) > 0

        keys = self.signal_keys
        return [ki for ki in keys if not exc(ki)]
#        exc=lambda x: i.endswith('bs') or i.endswith
#        return [i for i in keys if not (i.endswith('bs') or i.endswith('bl'))]

    def _get_signal_keys(self):
        keys = [ki for ai in self.analyses
                    for ki in ai.signals.keys()]

        return sorted(list(set(keys)), key=lambda x:int(x[2:4]), reverse=True)
#============= EOF =============================================
