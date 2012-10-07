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
    Str, Trait, cached_property
from traitsui.api import VGroup, HGroup, Item, Group, View, ListStrEditor, \
    InstanceEditor, ListEditor, EnumEditor, Label, Spring
#============= standard library imports ========================

#============= local library imports  ==========================
from src.database.core.database_selector import DatabaseSelector
from src.database.core.base_db_result import DBResult
from src.database.orms.isotope_orm import AnalysisTable

from src.graph.regression_graph import StackedRegressionTimeSeriesGraph
from src.database.isotope_analysis.analysis_summary import AnalysisSummary
from src.database.core.base_results_adapter import BaseResultsAdapter
from src.graph.graph import Graph

from src.graph.stacked_graph import StackedGraph
from src.managers.data_managers.ftp_h5_data_manager import FTPH5DataManager
from traits.trait_errors import TraitError
from src.managers.data_managers.h5_data_manager import H5DataManager

class AnalysisResult(DBResult):
    title_str = 'Analysis'
    window_height = 600
    window_width = 800
    color = 'black'

    sniff_graph = Instance(Graph)
    signal_graph = Instance(StackedRegressionTimeSeriesGraph)
    baseline_graph = Instance(StackedRegressionTimeSeriesGraph)
    peak_center_graph = Instance(Graph)
    peak_hop_graphs = List
#    sniff_graph = Instance(TimeSeriesStackedGraph)
#    signal_graph = Instance(TimeSeriesStackedGraph)
#    baseline_graph = Instance(TimeSeriesStackedGraph)
#    analyzer = Instance(Analyzer)

#    categories = List(['summary', 'signal', 'sniff', 'baseline', 'peak center' ])
    categories = List(['summary', ])#'signal', 'sniff', 'baseline', 'peak center' ])
    selected = Any('signal')
    display_item = Instance(HasTraits)

#    det_keys = None
#    iso_keys = None
#    intercepts = None
    fits = None
    isos = None
    intercepts = None
    baselines = None

    labnumber = Property
    analysis_type = Property
    aliquot = Property

    def __getattr__(self, attr):
        try:
            return getattr(self._db_result, attr)
        except Exception, e:
            pass

#    def _data_manager_factory(self):
#        dm = H5DataManager()
##        dm = FTPH5DataManager(workspace_root='/Users/ross/Sandbox/workspace/foo1')
##        dm.connect('localhost', 'ross', 'jir812', 'Sandbox/ftp/data')
#        return dm

    @cached_property
    def _get_labnumber(self):
#        print 'get aasfd'
        ln = self._db_result.labnumber.labnumber
        if ln == 1:
            ln = 'Blank'
        elif ln == 2:
            ln = 'Air'
        elif ln == 3:
            ln = 'Cocktail'
        elif ln == 4:
            ln = 'Background'

        ln = '{}-{}'.format(ln, self.aliquot)
        return ln

    @cached_property
    def _get_analysis_type(self):
        return self._db_result.measurement.analysis_type.name

    @cached_property
    def _get_aliquot(self):
        return self._db_result.labnumber.aliquot

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
        selected = self.selected
        if selected is not None:

            selected = selected.replace(' ', '_')
#            if selected == 'analyzer':
#                item = self.analyzer
#                info = self.analyzer.edit_traits()
#                if info.result:
#                    self.analyzer.apply_fits()
            if selected == 'summary':
                item = AnalysisSummary(result=self)
            else:
                item = getattr(self, '{}_graph'.format(selected))
            self.trait_set(display_item=item)

    def load_graph(self, graph=None, xoffset=0):

        self.fits = dict()
        self.intercepts = dict()
        self.baselines = dict()

        self.clear()

        dm = self.selector.data_manager
        signals = self._get_table_data(dm, 'signals')
        if signals:

            self.categories.append('signal')
            graph = self._load_stacked_graph(signals)

            for iso, rs in zip(self.isos, graph.regressors):
                self.intercepts[iso] = (rs.coefficients[-1], rs.coefficient_errors[-1])

            self.signal_graph = graph

        sniffs = self._get_table_data(dm, 'sniffs')
        if sniffs:
            self.categories.append('sniff')
            graph = self._load_stacked_graph(sniffs, regress=False)
            self.sniff_graph = graph

        baselines = self._get_table_data(dm, 'baselines')
        if baselines:
            self.categories.append('baseline')
            graph = self._load_stacked_graph(baselines)
            self.baseline_graph = graph
            for iso, rs in zip(self.isos, graph.regressors):
                self.baselines[iso] = (rs.coefficients[-1], rs.coefficient_errors[-1])

        peakcenter = self._get_peakcenter(dm)
        if peakcenter:
            self.categories.append('peak center')
            graph = self._load_peak_center_graph(peakcenter)
            self.peak_center_graph = graph

        self.selected = 'summary'
#        self.analyzer = Analyzer(analysis=self)
#        self.analyzer.fits = [AnalysisParams(fit='linear', name=k) for k in keys]
    def clear(self):
        self.baselines = dict()
        self.categories = ['summary']

    def get_peakhop_graphs(self):
        return [getattr(self, tr) for tr in self.traits()
                    if tr.endswith('_graph') and
                        not tr in ['signal_graph', 'sniff_graph', 'baseline_graph',
                              'peak_center_graph'
                              ]]

    def _load_stacked_graph(self, data, det=None, regress=True):
        if regress:
#            klass = StackedTimeSeriesRegressionGraph
            klass = StackedRegressionTimeSeriesGraph
        else:
            klass = StackedGraph

        graph = self._graph_factory(klass, width=700)
        gkw = dict()

        isos = [vi[1] for vi in data.itervalues()]
        isos = sorted(isos, key=lambda k: int(k[2:]))
        self.isos = isos

        def get_data(k):
            try:
                return data[k]
            except KeyError:
                return next((di for di in data.itervalues() if di[1] == k), None)

        i = 0
#        for i, iso in enumerate(isos):
        for iso in isos:
            try:
                di, _iso, fi, (xs, ys) = get_data(iso)
            except ValueError:
                continue

            try:
                cfit = self.fits[iso]
                if cfit is None:
                    self.fits[iso] = fi
            except KeyError:
                self.fits[iso] = fi

            gkw['ytitle'] = '{} ({})'.format(di if det is None else det, iso)
            skw = dict()
            if regress:
                skw['fit'] = fi
#
            graph.new_plot(**gkw)
            graph.new_series(xs, ys, plotid=i,
                             type='scatter', marker='circle',
                             marker_size=1.25,
                             **skw)
#            graph.set_series_label(key, plotid=i)
            mi = min(xs)
            ma = max(xs)
            graph.set_x_limits(min=mi, max=ma, pad='0.1', plotid=i)
            params = dict(orientation='right' if i % 2 else 'left',
                          axis_line_visible=False
                          )
            graph.set_axis_traits(i, 'y', **params)
            i += 1

        return graph

#    def _get_peakhop_signals(self, dm):
#        return self._get_table_data(dm, grp)
#        return self._get_peakhop(dm, 'signals')

#    def _get_peakhop_baselines(self, dm):
#        return self._get_peakhop(dm, 'baselines')

#    def _get_peakhop(self, dm, name):
#        grp = dm.get_group('peakhop_{}'.format(name))
#        peakhops = dict()
#        if grp is not None:
#            for di in dm.get_groups(grp):
#                peakhop = dict()
#                for ti in dm.get_tables(di):
#                    data = zip(*[(r['time'], r['value']) for r in ti.iterrows()])
#                    try:
#                        fit = ti.attrs.fit
#                    except AttributeError:
#                        fit = None
#                    peakhop[ti._v_name] = [di._v_name, ti._v_name, fit, data]
#    #                p[ti._v_nam] = [ti._v_name, fit, data]
#                peakhops[di._v_name] = peakhop
#
#        return peakhops

#    def _get_sniffs(self, dm):
#        return self._get_table_data(dm, 'sniffs')
#
#    def _get_baselines(self, dm):
#        return self._get_table_data(dm, 'baselines')

    def _get_peakcenter(self, dm):

        ti = dm.get_table('peakcenter', '/')
        if ti is not None:
            try:
                center = ti.attrs.center_dac
            except AttributeError:
                center = 0

            try:
                pcsignals = [ti.attrs.low_signal, ti.attrs.high_signal]
                pcdacs = [ti.attrs.low_dac, ti.attrs.high_dac]
            except AttributeError:
                pcsignals = []
                pcdacs = []

            return ([(r['time'], r['value']) for r in  ti.iterrows()], center, pcdacs, pcsignals)

    def _get_table_data(self, dm, grp):
        ds = dict()
        try:
            isogrps = dm.get_groups(grp)
        except Exception, e:
            print 'get table data', e
            return

        for ig in isogrps:
            for ti in dm.get_tables(ig):
                name = ti.name
                data = zip(*[(r['time'], r['value']) for r in ti.iterrows()])

                iso = ig._v_name
                try:
                    iso = ti.attrs.isotope
                except AttributeError:
                    pass

                fit = None
                try:
                    fit = ti.attrs.fit
                except AttributeError, e:
                    pass
#                print 'nn', name, ig._v_name
                ds[name] = [ti._v_name, iso, fit, data]

        return ds

    def _load_peak_center_graph(self, data):
        xs = []
        ys = []
        if data:
            xsys, center_dac, pcdacs, pcsignals = data
            xs, ys = zip(*xsys)

        graph = self._graph_factory()
        graph.container_dict = dict(padding=[10, 0, 30, 10])
        graph.clear()

        title = ''
        graph.new_plot(title='{}'.format(title),
                       xtitle='DAC (V)',
                       ytitle='Intensity (fA)',
                       )

        graph.new_series(
                         x=xs, y=ys,
                         type='scatter', marker='circle',
                         marker_size=1.25
                         )
        graph.new_series(
                         x=pcdacs,
                         y=pcsignals,
                         type='scatter', marker='circle',
                         marker_size=2
                         )
        graph.add_vertical_rule(center_dac)

#        graph.plots[0].value_range.tight_bounds = False
        if xs:
            graph.set_x_limits(min=min(xs), max=max(xs))
        return graph

class IsotopeResultsAdapter(BaseResultsAdapter):
    columns = [
#               ('ID', 'rid'),
               ('Labnumber', 'labnumber'),
               ('Date', 'rundate'),
               ('Time', 'runtime')
               ]
    font = 'monospace'
    rid_width = Int(50)
    labnumber_width = Int(90)
    rundate_width = Int(90)
    runtime_width = Int(90)
#    width = Int(50)

class IsotopeAnalysisSelector(DatabaseSelector):
    title = 'Recall Analyses'
    orm_path = 'src.database.orms.isotope_orm'

    query_table = AnalysisTable
    result_klass = AnalysisResult

    tabular_adapter = IsotopeResultsAdapter
#    multi_graphable = Bool(True)

#    def _load_hook(self):
#        jt = self._join_table_parameters
#        if jt:
#            self.join_table_parameter = str(jt[0])
#    def _selected_changed(self):
#        print self.selected
    def set_data_manager(self, kind, **kw):
        if kind == 'FTP':
            dm = FTPH5DataManager(**kw)
        else:
            dm = H5DataManager(**kw)

        self.data_manager = dm

    def _get_selector_records(self, **kw):
        sess = self._db.get_session()
        q = sess.query(AnalysisTable)
#        q = q.order_by(AnalysisTable.id.desc())
        q = q.filter(AnalysisTable.status != -1)
        return q.all()


#        return self._db.get_analyses(**kw)

#    def _get__join_table_parameters(self):
#        dv = self._db.get_devices()
#        return list(set([di.name for di in dv if di.name is not None]))



#        f = lambda x:[str(col)
#                           for col in x.__table__.columns]
#        params = f(b)
#        return list(params)
#        return

#============= EOF =============================================
#    
#    def _load_graph(self, data, fit=None, regress=True, keys=None, setiso=False):
#        if keys is None:
#            keys = self.det_keys
#        if regress:
#            klass = StackedTimeSeriesRegressionGraph
#        else:
#            klass = StackedGraph
#        graph = self._graph_factory(klass=klass, width=700)
#
#        gkw = dict(xtitle='Time',
#                       padding=[50, 50, 40, 40],
#                       panel_height=50,
#                       )
##        get_data = lambda k: next((d[3] for d in data if d[0] == k), None)
##        print data
##        print data.keys()
#        print 'load graph'
#        for i, key in enumerate(keys):
##            print data[key]
#            try:
#                iso, fi, (xs, ys) = data[key]
#            except KeyError:
#                continue
#
#            gkw['ytitle'] = '{} ({})'.format(key, iso)
#
#            skw = dict()
#            if regress:
#                if fit is None:
#                    fit = fi
#                if fit:
#                    skw['fit_type'] = fit
#
#            graph.new_plot(**gkw)
#            graph.new_series(xs, ys, plotid=i,
#                             type='scatter', marker='circle',
#                             marker_size=1.25,
#                             **skw)
##            graph.set_series_label(key, plotid=i)
#
#            params = dict(orientation='right' if i % 2 else 'left',
#                          axis_line_visible=False
#                          )
#            graph.set_axis_traits(i, 'y', **params)
#
#
#        return graph
#

#
#    def _get_data(self):
#        dm = self._data_manager_factory()
#        dm.open_data(self._get_path())
#
#        sniffs = []
#        signals = []
#        baselines = []
#        keys = []
##        isos = []
##        fits = []
#        peakcenter = None
#        if isinstance(dm, H5DataManager):
#
#            sniffs = self._get_table_data(dm, 'sniffs')
#            signals = self._get_table_data(dm, 'signals')
#            baselines = self._get_table_data(dm, 'baselines')
#
#            if sniffs or signals or baselines:
#                self._loadable = True
#                keys = list(set(
#                           sniffs.keys() if sniffs else [] +
#                           signals.keys() if signals else [] +
#                           baselines.keys() if baselines else []
#                           ))
#
##                isos = list(set(
##                           [v[0]  for v in sniffs.values()] if sniffs else [] +
##                           [v[0] for v in signals.values()] if signals else [] +
##                           [v[0] for v in baselines.values()] if baselines else []
##                           ))
##
##                fits = list(signals.values()[1])
#
##            if sniffs or signals or baselines:
##                self._loadable = True
##                keys = list(set(zip(*sniffs)[0] if sniffs else [] +
##                           zip(*signals)[0] if signals else [] +
##                           zip(*baselines)[0] if baselines else []
##                           ))
##                isos = list(set(zip(*sniffs)[1] if sniffs else [] +
##                           zip(*signals)[1] if signals else [] +
##                           zip(*baselines)[1] if baselines else []
##                           ))
##                fits = list(zip(*signals)[2]) if signals else []
#
#
#
##                print zip(*sniffs)[0]
##                print zip(*signals)[0]
##                print zip(*baselines)[0]
##                print keys
#            grp = dm.get_group('peakhop')
#            peakhop = dict()
#            for di in dm.get_groups(grp):
#                p = dict()
#                for ti in dm.get_tables(di):
#                    data = zip(*[(r['time'], r['value']) for r in ti.iterrows()])
#                    try:
#                        fit = ti.attrs.fit
#                    except AttributeError:
#                        fit = None
#                    p[ti._v_name] = [ti._v_name, fit, data]
#                peakhop[di._v_name] = p
#
#            ti = dm.get_table('peakcenter', '/')
#            if ti is not None:
#                try:
#                    center = ti.attrs.center_dac
#                except AttributeError:
#                    center = 0
#
#                try:
#                    pcsignals = [ti.attrs.low_signal, ti.attrs.high_signal]
#                    pcdacs = [ti.attrs.low_dac, ti.attrs.high_dac]
#                except AttributeError:
#                    pcsignals = []
#                    pcdacs = []
#
#                peakcenter = ([(r['time'], r['value']) for r in  ti.iterrows()], center, pcdacs, pcsignals)
##        print keys
##        print sniffs
#        return keys, sniffs, signals, baselines, peakhop, peakcenter

