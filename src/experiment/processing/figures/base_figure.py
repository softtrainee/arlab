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
    cached_property, Button, on_trait_change, Str
from traitsui.api import View, Item, TabularEditor, VSplit, Group, HGroup, VGroup, \
    spring, Handler
#import apptools.sweet_pickle as pickle
from pyface.timer.do_later import do_later
#============= standard library imports ========================
#from tables import openFile
import cPickle as pickle
import os

#============= local library imports  ==========================
#from src.loggable import Loggable
from src.graph.graph import Graph
from src.experiment.processing.analysis import Analysis, AnalysisTabularAdapter
from src.experiment.processing.plotters.series import Series
from src.experiment.processing.series_config import SeriesConfig, RatioConfig
from src.experiment.processing.processing_selector import ProcessingSelector
from src.helpers.traitsui_shortcuts import listeditor
from src.viewable import ViewableHandler, Viewable
from src.paths import paths
from src.database.core.database_selector import ColumnSorterMixin
from src.displays.rich_text_display import RichTextDisplay
from src.experiment.processing.export.csv_exporter import CSVExporter
from src.experiment.processing.export.excel_exporter import ExcelExporter
from src.experiment.processing.figures.figure_store import FigureStore
from src.initializer import MProgressDialog

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

def sort_keys(func):
    def decorator(cls):
        import re
        key = lambda x: re.sub('\D', '', x)
        keys = func(cls)
        return sorted(keys, key=key)

    return decorator

class BaseFigure(Viewable, ColumnSorterMixin):
    graph = Instance(Graph)
    analyses = Property(
#                        depends_on='_analyses'
                        )
    _analyses = List#(Analysis)
    selected_analysis = Any
#    workspace = Any
#    repo = Any
    db = Any
    username = Str

    series_configs = List
    ratio_configs = List
    selector = None
#    result = Instance(Result, ())

#    _debug = False
    _debug = True
    series = Instance(Series)

    manage_data = Button
    custom_query = Button
    signal_keys = Property
    isotope_keys = Property(depends_on='signal_keys')

    graph_selector = Instance(GraphSelector, ())

    series_klass = Series
    series_config_klass = SeriesConfig
    ratio_config_klass = RatioConfig

    use_user_series_configs = True
    use_user_ratio_configs = True
    use_user_graph_selector = True

    results_display = Instance(RichTextDisplay, (),
                               )

    show_results = Button('stats')
    export_csv = Button('csv')
    export_pdf = Button('pdf')
    export_excel = Button('excel')
    store = Button('store')
    load_button = Button('load')

    def _check_refresh(self):
        if self._analyses:
            return True


    def refresh(self, caller=None):

        print 'refresh called from {}'.format(caller)

        self.results_display.clear()

        analyses = self._analyses

        if not self._check_refresh():
            return

        graph = self.graph
        try:
            comps = graph.plotcontainer.components
            graph.plotcontainer.remove(*comps)
        except Exception:
            pass

        pl = 70 if self.graph_selector.show_series else 40
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
                header = lambda hs: '          ' + ''.join(map('{:<10s}'.format, hs))

                for config, reg in zip(self.series_configs,
                                       self.series.graph.regressors):
                    if 'average' in config.fit.lower():
                        rd.add_text(header(['mean', 'SD', 'SEM']))
                        rd.add_text('{} ={}'.format(config.label,
                                                    '{:<10s}'.format('{:0.7f}'.format(reg.coefficients[0]))))
#                        es = ''.join(map('{:0.7f}'.format, reg.coefficient_errors))
                        es = tabulate(reg.coefficient_errors)
                        es = '{:<10s}'.format(es)
                        rd.add_text('err  =            {}'.format(es))
                    else:

                        rd.add_text(header(['c', 'x', 'x2', 'x3']))
#                    cs = reg.coefficients
#                    ss = ' + '.join(map(lambda x:'{:0.7f}{}'.format(*x),
#                                              zip(cs, xx[:len(cs)][::-1])))
                        cs = reg.coefficients
                        if cs is not None:
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

    def _get_group_ids(self, analyses):
        return list(set([a.group_id for a in analyses]))
#        return list(set([(a.group_id + offset, True) for a in analyses]))

    def _refresh(self, graph, analyses, padding):
        gs = self.graph_selector

        seriespadding = padding
        if gs.show_series:
            sks = [(si.label, si.fit) for si in self.series_configs if si.show]
            bks = [('{}bs'.format(si.label), si.fit_baseline)
                    for si in self.series_configs if si.show_baseline]
            rks = [(si.label, si.fit) for si in self.ratio_configs if si.show]
            group_ids = self._get_group_ids(analyses)

            keys = sks + bks + rks
            epts = None
            if self.series:
                epts = self.series.get_excluded_points(keys, group_ids)

            series = self.series_klass()
            series.analyses = self._analyses
            gseries = series.build(analyses, sks, bks, rks, group_ids,
                                   seriespadding)

            if gseries:
                graph.plotcontainer.add(gseries.plotcontainer)
                series.on_trait_change(self._update_selected_analysis, 'selected_analysis')
                series.set_excluded_points(epts, keys, group_ids)

            self.series = series
            self.series.graph.on_trait_change(self._refresh_stats, 'regression_results')

        graph.redraw()

    def _add_analysis(self, a, **kw):
        self._analyses.append(a)

    def load_analyses(self, names, groupids=None, attrs=None,
                      set_series_configs=True,
                      **kw):

        analyses = self._analyses
        if groupids is None:
            groupids = [0 for n in names]
        if attrs is None:
            attrs = [dict() for n in names]

        _names = [a.uuid for a in analyses]
#        rnames = []
#        if exclusive:
        rnames = list(set(_names) - set(names))

        newnames = list(set(names) - set(_names))
        n = len(analyses) - len(rnames) + len(newnames) - 1

#===============================================================================
#     serial load
#===============================================================================
        pd = MProgressDialog(max=n + 1, size=(550, 15))
        import wx
        pd.open()
        (w, h) = wx.DisplaySize()
        (ww, _hh) = pd.control.GetSize()
        pd.control.MoveXY(w / 2 - ww + 275, h / 2 + 150)

        for n, group_id, attr in zip(names, groupids, attrs):
            if not n in _names:
                a = self._analysis_factory(n, **attr)
#                a.group_id = group_id
                if a:
                    msg = 'loading analysis {} groupid={} graphid={}'.format(a.dbrecord.record_id,
                                                                  group_id,
                                                                  a.graph_id)
                    pd.change_message(msg)
                    self.info(msg)
                    self._add_analysis(a, **kw)
                else:
                    self.warning('could not load {}'.format(n))
            else:
                a = next((a for a in analyses if a.uuid == n), None)

            #dbrecord must be set before setting group_id
            a.group_id = group_id

            pd.increment()
#===============================================================================
# 
#===============================================================================

        #remove analyses not in names
        self._analyses = [ai for ai in analyses if ai.uuid not in rnames]
#        print self._analyses
        self.nanalyses = -1

        keys = self.isotope_keys
        keys.sort(key=lambda k:k[2:4], reverse=True)
        if not self.series_configs and set_series_configs:
            self.series_configs = [self.series_config_klass(label=iso, figure=self)
                                   for iso in keys]
        else:
            #have a series configs list 
            #load any missing isotopes
#            print keys
            for i, iso in enumerate(keys):
                se = next((s for s in self.series_configs if s.label == iso), None)
#                print i, iso, se
                if not se:
                    self.series_configs.insert(1, self.series_config_klass(label=iso,
                                                                           figure=self))
                else:
                    se.figure = self

        for i, se in enumerate(self.series_configs):
            se.graphid = i

        rkeys = ['Ar40/Ar36', ]
        if not self.series_configs and set_series_configs:
            self.ratio_configs = [self.ratio_config_klass(label=ri,
                                                        figure=self) for ri in rkeys]
        else:
            #have a series configs list 
            #load any missing isotopes
#            print keys
            for i, iso in enumerate(rkeys):
                se = next((s for s in self.ratio_configs if s.label == iso), None)
#                print i, iso, se
                if not se:
                    self.ratio_configs.insert(1, self.ratio_config_klass(label=iso,
                                                                           figure=self))
                else:
                    se.figure = self

        signal_keys = self.signal_keys
        signal_keys.sort(key=lambda k:k[2:4], reverse=True)
        bs_keys = [i for i in signal_keys if i.endswith('bs')]
        bs_keys.sort(key=lambda k:k[2:4], reverse=True)

#        self.signal_table_adapter.iso_keys = self.isotope_keys
#        self.baseline_table_adapter.iso_keys = bs_keys

        self.refresh(caller='load analyses')
#===============================================================================
# viewable
#===============================================================================
    def closed(self, ok):
        self._dump_series_configs()
        self._dump_ratio_configs()
        self._dump_graph_selector()

    def opened(self):
        if self.use_user_series_configs:
            self._load_series_configs()

        if self.use_user_ratio_configs:
            self._load_ratio_configs()

        if self.use_user_graph_selector:
            self._load_graph_selector()

#===============================================================================
# persistence
#===============================================================================
    def _get_series_config_path(self):
        return os.path.join(paths.hidden_dir, 'series_config')

    def _get_ratio_config_path(self):
        return os.path.join(paths.hidden_dir, 'ratio_config')

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
                si.figure = self
            self.series_configs = obj

    def _load_ratio_configs(self):
        p = self._get_ratio_config_path()
        obj = self._load_obj(p)
        if obj:
            for si in obj:
                si.figure = self
            self.ratio_configs = obj

    def _dump_graph_selector(self):
        p = self._get_graph_selector_path()
        self._dump_obj(self.graph_selector, p)

    def _dump_series_configs(self):
        p = self._get_series_config_path()
        self._dump_obj(self.series_configs, p)

    def _dump_ratio_configs(self):
        p = self._get_ratio_config_path()
        self._dump_obj(self.ratio_configs, p)

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
            print 'ddd', p
            print e
#===============================================================================
# private
#===============================================================================
    def _update_data(self):
        def do():
            ps = self.selector
            try:
                names, attrs, group_ids = zip(*[(ri.filename, dict(dbrecord=ri), ri.group_id)
                                          for ri in ps.selected_records
                                            if ri.path.strip()

                                            ])

                if names:
                    self.load_analyses(names, attrs=attrs, groupids=group_ids, **self._get_load_keywords())
            except ValueError, e:
                print e

        do_later(do)

    def _get_load_keywords(self):
        return {}

#===============================================================================
# handlers
#===============================================================================
    def _update_selected_analysis(self, new):
        self.selected_analysis = new

#    @on_trait_change('_analyses[]')
#    def _analyses_changed(self):
##        print len(self.analyses), self.nanalyses
#        if len(self._analyses) > self.nanalyses:
#            self.refresh(caller='analyses_changed')

    @on_trait_change('graph_selector:show_series')
    def _refresh_graph(self, obj, name, old, new):
        self.refresh(caller='show_series')

    def _create_custom_function(self):
        p = os.path.join(paths.custom_queries_dir, 'get_irradiation_position.txt')
        sql = open(p, 'r').read()
        code = compile(sql, '<string>', 'exec')
        #namespace to execute query in
        ctx = dict(sess=self.db.get_session(),
                   )
        exec code in ctx
        return ctx['query']

    def _custom_query_fired(self):
        db = self.db
        db.connect()
#        if self.selector is None:
        ps = ProcessingSelector(db=self.db)
        self.selector = ps
        ps.selector.style = 'panel'
        ps.on_trait_change(self._update_data, 'update_data')
#            ps.selector.load_last(n=200)
#        sess = db.get_session()

        #=======================================================================
        # custom
        #=======================================================================
        try:
            query = self._create_custom_function()
            recs = query()

            from src.database.records.isotope_record import IsotopeRecord
            recs = [IsotopeRecord(_dbrecord=ri,
                                  selector=ps.selector
                                  ) for ri in recs]
            ps.selected_records = recs

            gs = ps._group_by_labnumber()
            for ri in ps.selected_records:
                ri.group_id = gs.index(ri.labnumber)
#            ps.show()
        except Exception, e:
            self.warning_dialog('Custom Query failed {}'.format(e))
            print 'custom query exception', e

        #=======================================================================
        # 
        #=======================================================================

#        self.selector.show()
        self._update_data()

    def _manage_data_fired(self):
        db = self.db
        db.connect()
#        import time
#        st = time.clock()
        if self.selector is None:
#            db.selector_factory()
            ps = ProcessingSelector(db=self.db)
            ps.selector.style = 'panel'
            ps.on_trait_change(self._update_data, 'update_data')
#            ps.selector.load_recent()
            ps.selector.load_last(n=200)
#            ps._analysis_type_changed()
#            ps.edit_traits()
            self.selector = ps
#            if self._debug:

            ps.selected_records = [i for i in ps.selector.records if i.labnumber in [57740, 57741,
                                                                                      57743, 57742, 57745
                                                                                     ]]
#            for pi in ps.selected_records:
#                if pi.labnumber == 57741:
##                    pi.group_id = 1
#                    pi.graph_id = 1
            ps.selected_records = ps.selected_records[::5]
#            print len(ps.selected_records)
#            ps.selected_records = [i for i in ps.selector.records[-20:] if i.analysis_type != 'blank']
#            print 'get results time', time.clock() - st
        else:
            self.selector.show()

#        st = time.clock()
        self._update_data()
#        print 'update time', time.clock() - st

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

    def _store_fired(self):
        name = 'staore1'
        p = os.path.join(self.workspace.root, 'store', name)
        d = os.path.dirname(p)
        if not os.path.isdir(d):
            os.mkdir(d)

        st = FigureStore(p, self)
        st.dump()

    def _load_button_fired(self):
        name = 'staore1'
        p = os.path.join(self.workspace.root, 'store', name)
        st = FigureStore(p, self)
        st.load()

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
                    Item('store', show_label=False,),
                    Item('load_button', show_label=False,),
#                    Item('export_csv', show_label=False),
#                    Item('export_excel', show_label=False),
#                    Item('export_pdf', show_label=False),
                    Item('show_results', show_label=False),
                    Item('manage_data', show_label=False),
                    Item('custom_query', show_label=False),
                    )
        bottom = VGroup(tb, bot)

        v = View(VSplit(top, bottom),
                 resizable=True,
                 width=0.5,
                 height=800,
#                 height=0.8,
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
#              self._get_signals_group(),
#              self._get_baselines_group(),
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
                 listeditor('ratio_configs'),
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

    def _analysis_factory(self, n, dbrecord=None, **kw):

        a = Analysis(uuid=n,
#                     repo=self.repo,
#                     workspace=self.workspace,
                     dbrecord=dbrecord,
                     **kw)
        #need to call both load from file and database
#        if not a.load_from_file(n):
#            return

#        if self.db.connect():
#            sess = self.db.get_session()
#            from src.database.orms.isotope_orm import AnalysisPathTable
#            from src.database.orms.isotope_orm import AnalysisTable
#            q = sess.query(AnalysisTable)
#            q = q.join(AnalysisPathTable)
#            q = q.filter(AnalysisPathTable.filename == n)
#            dbr = q.one()

#            selector = self.db.new_selector()
#            selector.data_manager = H5DataManager(repository=self.repo)
#            dbrecord = selector.record_klass(_dbrecord=dbr, selector=selector)
#        if dbrecord and dbrecord.loadable:

#            a.dbrecord = dbrecord

#                a.load_from_file(n)
        if a.load_age():
            return a

    def _graph_factory(self, klass=None, **kw):
        g = Graph(container_dict=dict(kind='h', padding=0,
                                      bgcolor='lightgray',
                                      spacing=0,
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
#                            id='stats_display'
#                            id='stats_display.{}'.format(self.workspace.name)
                            )
#        r.title = '{} Stats'.format(self.workspace.name)
#        r.title = ''.format(self)
        return r
#===============================================================================
# property get/set
#===============================================================================
    def _get_analyses(self):
        return self._analyses

    def _set_analyses(self, v):
        self._analyses = v

    def _get_isotope_keys(self):
        excks = ['bs', 'bl', 'bg']
        def exc(ki):
            f = lambda ei: ki.endswith(ei)
            return sum(map(f, excks)) > 0

        keys = self.signal_keys
        return [ki for ki in keys if not exc(ki)]
#        exc=lambda x: i.endswith('bs') or i.endswith
#        return [i for i in keys if not (i.endswith('bs') or i.endswith('bl'))]

    @sort_keys
    def _get_signal_keys(self):
        keys = list(set([ki for ai in self._analyses
                    for ki in ai.signals.keys()]))
        return keys
#        return sorted(list(set(keys)), key=lambda x:int(x[2:4]), reverse=True)

#    def _sort_keys(self, keys, reverse=True):
#        import re
#        key = lambda x: re.sub('\D', '', x)
#        return sorted(list(set(keys)), key=key, reverse=reverse)

#============= EOF =============================================
