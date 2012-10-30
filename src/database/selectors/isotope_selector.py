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
from traits.api import Int, Property
#from traits.api import HasTraits, Any, List, String, \
#    Float, Bool, Int, Instance, Property, Dict, Enum, on_trait_change, \
#    Str, Trait, cached_property
#from traitsui.api import VGroup, HGroup, Item, Group, View, ListStrEditor, \
#    InstanceEditor, ListEditor, EnumEditor, Label, Spring
#============= standard library imports ========================

#============= local library imports  ==========================
from src.database.core.database_selector import DatabaseSelector
#from src.database.core.base_db_result import DBResult
from src.database.orms.isotope_orm import meas_AnalysisTable

#from src.graph.regression_graph import StackedRegressionTimeSeriesGraph, \
#    StackedRegressionGraph
#from src.database.isotope_analysis.analysis_summary import AnalysisSummary
from src.database.core.base_results_adapter import BaseResultsAdapter
#from src.graph.graph import Graph

#from src.graph.stacked_graph import StackedGraph
from src.managers.data_managers.ftp_h5_data_manager import FTPH5DataManager
#from traits.trait_errors import TraitError
from src.managers.data_managers.h5_data_manager import H5DataManager
#from src.database.isotope_analysis.blanks_summary import BlanksSummary
#from src.experiment.identifier import convert_identifier, convert_labnumber, \
#    convert_shortname
#from src.database.isotope_analysis.fit_selector import FitSelector
from src.database.records.isotope_record import IsotopeRecord





class IsotopeResultsAdapter(BaseResultsAdapter):
    columns = [
#               ('ID', 'rid'),
               ('Labnumber', 'labnumber'),
               ('Aliquot', 'aliquot'),
               ('Date', 'rundate'),
               ('Time', 'runtime')
               ]
    font = 'monospace'
#    rid_width = Int(50)
    labnumber_width = Int(90)
    aliquot_width = Int(90)
    rundate_width = Int(90)
    runtime_width = Int(90)
    aliquot_text = Property
    def _get_aliquot_text(self, trait, item):
        a = self.item.aliquot
        s = self.item.step
        return '{}{}'.format(a, s)
#        return '1'
#    width = Int(50)

class IsotopeAnalysisSelector(DatabaseSelector):
    title = 'Recall Analyses'
    orm_path = 'src.database.orms.isotope_orm'

    query_table = meas_AnalysisTable
    record_klass = IsotopeRecord

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
        q = sess.query(meas_AnalysisTable)
        q = q.order_by(meas_AnalysisTable.id.desc())
        q = q.filter(meas_AnalysisTable.status != -1)

        if 'filter_str' in kw:
#            print kw['filter_str']
            q = q.filter(kw['filter_str'])

        if 'limit' in kw:
            q = q.limit(kw['limit'])

        records = q.all()
        records.reverse()
        return records
#        return q.all()


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

