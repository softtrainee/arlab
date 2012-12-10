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
from traits.api import HasTraits, Str, List, Any, Instance
from traitsui.api import View, Item, TableEditor
from src.database.orms.isotope_orm import meas_AnalysisTable, \
    meas_ExperimentTable, meas_MeasurementTable, gen_AnalysisTypeTable, \
    gen_LabTable
from src.processing.analysis import Analysis
from src.database.records.isotope_record import IsotopeRecord
from src.graph.regression_graph import RegressionGraph, \
    RegressionTimeSeriesGraph
from src.progress_dialog import MProgressDialog
#============= standard library imports ========================
#============= local library imports  ==========================

class InterpolationGraph(RegressionTimeSeriesGraph):
    pass

class InterpolationCorrection(HasTraits):
    analyses = List
    kind = Str
    db = Any
    graph = Instance(InterpolationGraph)
    def load_predictors(self):

        ps = [
              self._predictor_factory(predictor)
              for a in self.analyses[:1]
                  for predictor in self._get_predictors(a)]
        if ps:
            n = len(ps)
            progress = MProgressDialog(max=n, size=(550, 15))
            progress.open()
            progress.center()

            for pi in ps:
                msg = 'loading {}'.format(pi.record_id)
                progress.change_message(msg)
                pi.load_age()
                progress.increment()

            graph = self.graph
            graph.new_plot()
            xs, ys = zip(*[(pi.timestamp, pi.get_corrected_intercept('Ar40')) for pi in ps])
            ys, es = zip(*[(yi.nominal_value, yi.std_dev()) for yi in ys])

            graph.new_series(xs, ys, fit='linear')
            reg = graph.regressors[0]

            xs = [ai.timestamp for ai in self.analyses]
            ys = [reg.predict(xi) for xi in xs]
            graph.new_series(xs, ys, fit=False, type='scatter')

    def _predictor_factory(self, predictor):
        a = Analysis(dbrecord=IsotopeRecord(_dbrecord=predictor))
        return a

    def _get_predictors(self, analysis):
        sess = self.db.get_session()
#        exp = analysis.dbrecord.experiment
#
        q = sess.query(meas_AnalysisTable)
        q = q.join(gen_LabTable)
        q = q.filter(gen_LabTable.labnumber == -1)
#        q = q.join(meas_ExperimentTable)
#        q = q.join(meas_MeasurementTable)
#        q = q.join(gen_AnalysisTypeTable)
#        q = q.filter(gen_AnalysisTypeTable.name == self.kind)
#        q = q.filter(meas_ExperimentTable.id == exp.id)
#        q = q.filter(meas_AnalysisTable.id != analysis.id)
        return q.all()[:10]

    def traits_view(self):
        v = View(Item('graph',
                      height=500,
                      show_label=False, style='custom'))
        return v

    def _graph_default(self):
        g = InterpolationGraph(container_dict=dict(padding=5))
        return g
#============= EOF =============================================
