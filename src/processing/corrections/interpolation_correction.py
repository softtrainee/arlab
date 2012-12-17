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
from traits.api import HasTraits, Str, List, Any, Instance, Property, cached_property, \
    Event
from traitsui.api import View, Item, TableEditor, EnumEditor, CheckListEditor
import apptools.sweet_pickle as pickle

import os
#============= standard library imports ========================
#============= local library imports  ==========================
from src.paths import paths
from src.database.orms.isotope_orm import meas_AnalysisTable, \
    meas_ExperimentTable, meas_MeasurementTable, gen_AnalysisTypeTable, \
    gen_LabTable
from src.processing.analysis import Analysis
from src.database.records.isotope_record import IsotopeRecord
from src.graph.regression_graph import RegressionGraph, \
    RegressionTimeSeriesGraph, StackedRegressionTimeSeriesGraph
from src.progress_dialog import MProgressDialog

from src.regression.interpolation_regressor import InterpolationRegressor
from src.helpers.traitsui_shortcuts import listeditor
from src.processing.corrections.regression_correction import RegressionCorrection
import time
import datetime
from sqlalchemy.sql.expression import and_

class InterpolationGraph(StackedRegressionTimeSeriesGraph):
    pass

class InterpolationCorrection(HasTraits):
    analyses = List
    kind = Str
    analysis_type = Str
    signal_key = Str
    signal_klass = Any
    db = Any
    graph = Instance(InterpolationGraph)
    fits = List(RegressionCorrection)
    dirty = Event
    predictors = Property(depends_on='dirty')
    _predictors = List
    def dump_fits(self):
        p = os.path.join(paths.hidden_dir, '{}_interpolation_correction_fits'.format(self.kind))
        obj = dict([(di.name, di) for di in self.fits])
        with open(p, 'w') as fp:
            pickle.dump(obj, fp)

    def load_fits(self, isotope_names):
#        fs = [RegressionCorrection(name=ki) for ki in isotope_names]
        cors = dict()
        p = os.path.join(paths.hidden_dir, '{}_interpolation_correction_fits'.format(self.kind))
        if os.path.isfile(p):
            with open(p, 'r') as fp:
                try:
                    cors = pickle.load(fp)
                except pickle.PickleError:
                    pass

        for ki in isotope_names:
            if ki in cors:
                fi = cors[ki]
            else:
                fi = RegressionCorrection(name=ki)

            fi.on_trait_change(self.refresh, 'use')
            fi.on_trait_change(self.refresh_fit, 'fit')
            self.fits.append(fi)

    def refresh_fit(self, obj, name, old, new):
        new = new.lower()
        if new not in ['preceeding', 'bracketing interpolate', 'bracketing average']:
            self.refresh()
        else:
            g = self.graph
            plotid = next((pi for pi, plot in enumerate(g.plots)
                            if plot.y_axis.title == obj.name), None)

            if plotid is not None:
                xs = g.get_data(plotid=plotid)
                ys = g.get_data(axis=1, plotid=plotid)
                es = g.get_data(axis=2, plotid=plotid)
                ip = InterpolationRegressor(xs=xs, ys=ys, yserr=es, kind=new)

                xs = g.get_data(series=4, plotid=plotid)
                ys = ip.predict(xs)
                g.set_data(ys, axis=1, series=4, plotid=plotid)

                g.set_series_visiblity(False, series='fit0', plotid=plotid)
                g.set_series_visiblity(False, series='upper CI0', plotid=plotid)
                g.set_series_visiblity(False, series='lower CI0', plotid=plotid)

            g.redraw()

    def refresh(self):
        self.refresh_graph()

    def load_predictors(self):
        #force load predictors
        _ = self.predictors
        self.refresh_graph()

    def refresh_graph(self):
        graph = self.graph
        graph.clear()

        fits = filter(lambda x:x.use, self.fits)
        fits = reversed(fits)
        for plotid, si in enumerate(fits):
            p = graph.new_plot(padding_right=5,
                           padding_bottom=50,
                           ytitle=si.name,
                           xtitle='Time'
                           )
            p.value_range.tight_bounds = False
            self.add_plot(si.name, si.fit.lower(), plotid)

#        graph.on_trait_change(self._update_interpolation, 'regression_results')
        graph.refresh()

    def add_plot(self, key, fit, plotid):
        ps = self.predictors
        graph = self.graph
        k = '{}{}'.format(key, self.signal_key)
        axs = [ai.timestamp for ai in self.analyses]
        mn = None
        mx = None
        if ps:
            xs, ys = zip(*[(pi.timestamp, self._get_predictor_value(pi, key)) for pi in ps])
            ys, es = zip(*[(yi.nominal_value, yi.std_dev()) for yi in ys])
            mn = min(xs)
            mx = max(xs)
            if fit in ['preceeding', 'bracketing interpolate', 'bracketing average']:
                _, _ = graph.new_series(xs, ys, yer=es,
                                        type='scatter',
                                        fit=False, plotid=plotid)
                reg = InterpolationRegressor(xs=xs, ys=ys, kind=fit)
            else:
                p, s, l = graph.new_series(xs, ys, yer=es, fit=fit, plotid=plotid)
                reg = graph.regressors[plotid]

            ys = reg.predict(axs)
        else:
            ys = []
            for ai in self.analyses:
                if ai.signals.has_key(k):
                    ys.append(ai.signals[k].value)
                else:
                    ys.append(0)
        if mn:
            mn = min(min(axs), mn)
        else:
            mn = min(axs)
        if mx:
            mx = max(max(axs), mx)
        else:
            mx = max(axs)
#        ys = reg.predict(xs)

        #sync the analysis' signals
        for yi, ai in zip(ys, self.analyses):
            if k in ai.signals:
                sig = ai.signals[k]
                sig.value = yi
            else:
                sig = self.signal_klass(value=yi)
                ai.signals[k] = sig

        graph.new_series(axs, ys, fit=False, type='scatter', plotid=plotid)
        graph.set_x_limits(mn, mx, pad='0.1', plotid=plotid)

    def _get_predictor_value(self, pi, key):
        return pi.get_corrected_intercept(key)

    def _predictor_factory(self, predictor):
        if not isinstance(predictor, Analysis):
            predictor = Analysis(isotope_record=IsotopeRecord(_dbrecord=predictor))
        return predictor

    def _find_predictors(self, analysis):
        sess = self.db.get_session()

#        q = sess.query(meas_AnalysisTable)
#        q = q.join(gen_LabTable)
#        q = q.filter(gen_LabTable.labnumber == -1)
#        return q.all()[:10]

        exp = analysis.experiment
        if exp is  None:
            '''
                analysis doesnt belong to an experiment
                get kind_analyses before and after analysis rundate and runtime
            '''
            post = analysis.timestamp
            dt = datetime.datetime.fromtimestamp(post)
            win = datetime.timedelta(hours=6)
            udt = dt + win
            ldt = dt - win

            q = sess.query(meas_AnalysisTable)
            q = q.join(meas_MeasurementTable)
            q = q.join(gen_AnalysisTypeTable)

            q = q.order_by(meas_AnalysisTable.rundate.desc())
            q = q.order_by(meas_AnalysisTable.runtime.desc())

            if self.kind == 'blanks':
                at = 'blank_{}'.format(analysis.analysis_type)
            else:
                at = self.analysis_type

            q = q.filter(and_(
                              gen_AnalysisTypeTable.name == at,
                              meas_AnalysisTable.rundate >= ldt.date(),
                              meas_AnalysisTable.runtime > ldt.time(),
                              meas_AnalysisTable.rundate <= udt.date(),
                              meas_AnalysisTable.runtime < udt.time(),
                              meas_AnalysisTable.id != analysis.id))
        else:
            '''
                find all kind_analyses in this analysis' experiment
            '''
            q = sess.query(meas_AnalysisTable)
            q = q.join(meas_ExperimentTable)
            q = q.join(meas_MeasurementTable)
            q = q.join(gen_AnalysisTypeTable)
            q = q.filter(and_(gen_AnalysisTypeTable.name == self.kind,
                              meas_ExperimentTable.id == exp.id,
                              meas_AnalysisTable.id != analysis.id))

#            q = q.filter(meas_ExperimentTable.id == exp.id)
#            q = q.filter(meas_AnalysisTable.id != analysis.id)

        return q.all()



#===============================================================================
# propert get/set
#===============================================================================
    @cached_property
    def _get_predictors(self):
        ps = self._predictors
        if not ps:
            ps = [
              self._predictor_factory(predictor)
              for a in self.analyses
                  for predictor in self._find_predictors(a)]

        if ps:
            #filter duplicates
            pp = []
            uuids = []
            for pi in ps:
                if pi.uuid in uuids:
                    continue
                else:
                    uuids.append(pi.uuid)
                    pp.append(pi)

            n = len(pp)
            progress = MProgressDialog(max=n, size=(550, 15))
            progress.open()
            progress.center()

            for pi in pp:
                msg = 'loading {}'.format(pi.record_id)
                progress.change_message(msg)
                pi.load_age()
                progress.increment()
            return pp
#===============================================================================
# handlers
#===============================================================================
    def _update_interpolation(self, regressors):
        pass
#        if not self.fit.lower() in ['preceeding', 'bracketing interpolate', 'bracketing average']:
#            if regressors:
#                g = self.graph
#                reg = regressors[0]
#                xs = g.get_data(series=4)
#                ys = reg.predict(xs)
#                g.set_data(ys, axis=1, series=4)
#
#    def _fit_changed(self):
#        g = self.graph
#        fi = self.fit.lower()
#        if fi in ['preceeding', 'bracketing interpolate', 'bracketing average']:
#            xs = g.get_data()
#            ys = g.get_data(axis=1)
#            es = g.get_data(axis=2)
#            ip = InterpolationRegressor(xs=xs, ys=ys, yserr=es, kind=fi)
#
#            xs = g.get_data(series=4)
#            ys = ip.predict(xs)
#            g.set_data(ys, axis=1, series=4)
#
#            g.set_series_visiblity(False, series='fit0')
#            g.set_series_visiblity(False, series='upper CI0')
#            g.set_series_visiblity(False, series='lower CI0')
#
#            g.redraw()
#        else:
#            g.set_fit(self.fit)
#
#            g.set_series_visiblity(True, series='fit0')
#            g.set_series_visiblity(True, series='upper CI0')
#            g.set_series_visiblity(True, series='lower CI0')
#
#            g.refresh()

    def traits_view(self):
        v = View(Item('graph',
                      height=500,
                      width=600,
                      show_label=False, style='custom'),
                 listeditor('fits')
                 )
        return v

    def _graph_default(self):
        g = InterpolationGraph(container_dict=dict(padding=5))
        return g

    def _correction_factory(self, name):
        fi = RegressionCorrection(name=name)
        fi.on_trait_change(self.refresh, 'use')
        fi.on_trait_change(self.refresh_fit, 'fit')
        return fi

class DetectorIntercalibrationInterpolationCorrection(InterpolationCorrection):
    def _get_predictor_value(self, pi, key):
        v = (pi.get_corrected_intercept('Ar40') / pi.get_corrected_intercept('Ar36'))
        if key == 'IC':
            v /= 295.5
        return  v

    def load_fits(self, names):
        for ri in ['IC', 'Ar40/Ar36']:
            self.fits.append(self._correction_factory(ri))

#============= EOF =============================================
