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
    Event, Float
from traitsui.api import View, Item
import apptools.sweet_pickle as pickle
from chaco.array_data_source import ArrayDataSource

#============= standard library imports ========================
from sqlalchemy.sql.expression import and_
import os
from numpy import  asarray
import datetime
#============= local library imports  ==========================
from src.paths import paths
from src.database.orms.isotope_orm import meas_AnalysisTable, \
    meas_ExperimentTable, meas_MeasurementTable, gen_AnalysisTypeTable
from src.processing.analysis import Analysis
from src.database.records.isotope_record import IsotopeRecord
from src.graph.regression_graph import StackedRegressionGraph
# from src.progress_dialog import myProgressDialog

from src.regression.interpolation_regressor import InterpolationRegressor
from src.helpers.traitsui_shortcuts import listeditor
from src.processing.corrections.regression_correction import RegressionCorrection

from src.graph.error_bar_overlay import ErrorBarOverlay
from src.helpers.datetime_tools import convert_timestamp
from src.regression.mean_regressor import MeanRegressor
from src.regression.ols_regressor import OLSRegressor
from apptools.preferences.preference_binding import bind_preference
from src.ui.progress_dialog import myProgressDialog

class InterpolationGraph(StackedRegressionGraph):
    pass

class InterpolationCorrection(HasTraits):
    analyses = List
    kind = Str
    analysis_type = Str
    isotope_name = Str
#    signal_key = Str
    isotope_klass = Any
    graph = Instance(InterpolationGraph)
    fits = List(RegressionCorrection)
    dirty = Event
    predictors = Property(depends_on='dirty')
    _predictors = List

    db = Any

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

        fs = []
        for ki in isotope_names:
            if ki in cors:
                fi = cors[ki]
            else:
                fi = RegressionCorrection(name=ki)

            fs.append(fi)

        self.fits = fs
        for fi in fs:
            fi.on_trait_change(self.refresh_graph, 'use')
            fi.on_trait_change(self.refresh_fit, 'fit')

    def refresh_fit(self, obj, name, old, new):
        new = new.lower()
        if new not in ['preceeding', 'bracketing interpolate', 'bracketing average']:
            self.refresh_graph()
        else:
            g = self.graph
            plotid = next((pi for pi, plot in enumerate(g.plots)
                            if plot.y_axis.title == obj.name), None)

            if plotid is not None:
                predictor = g.plots[plotid].plots['data0'][0]
                xs = predictor.index.get_data()
                ys = predictor.value.get_data()
                es = predictor.yerror.get_data()
                ip = InterpolationRegressor(xs=xs, ys=ys, yserr=es, kind=new)

                interpolated = g.plots[plotid].plots['plot4'][0]
                xs = interpolated.index.get_data()
                ys = ip.predict(xs)
                es = ip.predict_error(xs)
                interpolated.value.set_data(ys)
                interpolated.yerror.set_data(es)

                g.set_series_visiblity(False, series='fit0', plotid=plotid)
                g.set_series_visiblity(False, series='upper CI0', plotid=plotid)
                g.set_series_visiblity(False, series='lower CI0', plotid=plotid)

                self.sync_analyses(ys, es, obj.name)

            g.redraw()

    def refresh(self):
        self.refresh_graph()

    def load_predictors(self):
        # force load predictors
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

        graph.on_trait_change(self._update_interpolation, 'regression_results')
        graph.refresh()

    def normalize(self, xs, start):
        xs = asarray(xs)
        xs.sort()
        xs -= start

        # scale to hours
        xs = xs / (60.*60.)
        return xs

    def add_plot(self, key, fit, plotid):
        graph = self.graph
#        k = '{}{}'.format(key, self.signal_key)
        ps = self.predictors
        axs = [ai.timestamp for ai in self.analyses]

        xs, ys, mn, mx, reg = None, None, None, None, None
        scatter = None
        if ps:
            xs, ys = zip(*[(pi.timestamp, self._get_predictor_value(pi, key)) for pi in ps])

            start = min(min(axs), min(xs))

            # normalize to earliest
            oxs = asarray(map(convert_timestamp, xs[:]))
            xs = self.normalize(xs, start)
            axs = self.normalize(axs, start)

            ys, es = zip(*[(yi.value, yi.error) for yi in ys])
            mn = min(xs)
            mx = max(xs)

            if fit in ['preceeding', 'bracketing interpolate', 'bracketing average']:
                reg = InterpolationRegressor(xs=xs, ys=ys, kind=fit)
                scatter, _p = graph.new_series(xs, ys,
                                        display_index=ArrayDataSource(data=oxs),
                                        yerror=ArrayDataSource(data=es),
                                        type='scatter',
                                        fit=False,
                                        plotid=plotid)
                ays = reg.predict(axs)
                aes = reg.predict_error(axs)

            else:
                _p, scatter, _l = graph.new_series(xs, ys,
                                           display_index=ArrayDataSource(data=oxs),
                                           yerror=ArrayDataSource(data=es),
                                           fit=fit,
                                           plotid=plotid)
                if fit.startswith('average'):
                    reg = MeanRegressor(xs=xs, ys=ys, yserr=es)
                else:
                    reg = OLSRegressor(xs=xs, ys=ys, yserr=es, fit=fit)
                ays = reg.predict(axs)
                aes = reg.predict_error(axs)


            ebo = ErrorBarOverlay(component=scatter,
                                  orientation='y')
            scatter.overlays.insert(0, ebo)

        else:
            axs = self.normalize(axs, min(axs))
            ays = []
            aes = []
            for ai in self.analyses:
                if ai.isotopes.has_key(key):
                    ays.append(ai.isotopes[key].value)
                    aes.append(ai.isotopes[key].error)
                else:
                    ays.append(0)
                    aes.append(0)

        # sync the analysis' signals
#        self.sync_analyses(ays, aes, key)

        # display the predicted values
        ss, _ = graph.new_series(axs,
                                ays,
                                yerror=ArrayDataSource(aes),
                                fit=False,
                                type='scatter',
                                plotid=plotid,
                                )

        ebo = ErrorBarOverlay(component=ss,
                              orientation='y')
        if scatter:
            scatter.overlays.insert(0, ebo)
        else:
            ss.overlays.insert(0, ebo)

        if mn is not None:
            mn = min(min(axs), mn)
        else:
            mn = min(axs)
        if mx is not None:
            mx = max(max(axs), mx)
        else:
            mx = max(axs)

        graph.set_x_limits(mn, mx, pad='0.1', plotid=plotid)

    def sync_analyses(self, ays, aes, k):
        for yi, ei, ai in zip(ays, aes, self.analyses):
            if k in ai.isotopes:
                sig = ai.isotopes[k]

                if self.isotope_name == 'blank':
                    sig = sig.blank
                elif self.isotope_name == 'background':
                    sig = sig.background
                sig.value = yi
                sig.error = ei
            else:
                sig = self.isotope_klass(value=yi, error=ei)
                if self.isotope_name == 'blank':
                    ai.isotopes[k].blank = sig
                elif self.isotope_name == 'background':
                    ai.isotopes[k].background = sig

    def _get_predictor_value(self, pi, key):
        return pi.get_corrected_value(key)

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

        '''
            if kind is blanks then look for all blank_kind analyses
            e.g if analysis is an unknown look for blank_unknown
            
        '''
        if self.kind == 'blanks':
            atype = 'blank_{}'.format(analysis.analysis_type)
        else:
            atype = self.analysis_type

        exp = analysis.experiment
        if exp is  None:
            '''
                analysis doesnt belong to an experiment
                get kind_analyses before and after analysis rundate and runtime
            '''
            def filter_analyses(post, delta, lim, at):
                '''
                    post= timestamp
                    delta= time in hours
                    at=analysis type
                    
                    if delta is negative 
                    get all before post and after post-delta

                    if delta is post 
                    get all before post+delta and after post
                '''
                q = sess.query(meas_AnalysisTable)
                q = q.join(meas_MeasurementTable)
                q = q.join(gen_AnalysisTypeTable)

                win = datetime.timedelta(hours=delta)
                dt = post + win
                if delta < 0:
                    a, b = dt, post
                else:
                    a, b = post, dt

                q = q.filter(and_(
                                  gen_AnalysisTypeTable.name == at,
                                  meas_AnalysisTable.id != analysis.id,
                                  meas_AnalysisTable.analysis_timestamp >= a,
                                  meas_AnalysisTable.analysis_timestamp <= b,
                                  ))
                q = q.limit(lim)
                return q.all()

            def find_analyses(post, delta, atype, step=100, maxtries=10):
                if delta < 0:
                    step = -step

                for i in range(maxtries):
                    rs = filter_analyses(post, delta + i * step, 3, atype)
                    if rs:
                        return rs
                else:
                    return []

            pi = analysis.timestamp
            pi = datetime.datetime.fromtimestamp(pi)

            br = find_analyses(pi, -60, atype)
            ar = find_analyses(pi, 60, atype, maxtries=1)  # dont search forward was much as backward
#            print len(br), len(ar)
            return br + ar

        else:
            '''
                find all kind_analyses in this analysis' experiment
            '''
            q = sess.query(meas_AnalysisTable)
            q = q.join(meas_ExperimentTable)
            q = q.join(meas_MeasurementTable)
            q = q.join(gen_AnalysisTypeTable)
            q = q.filter(and_(gen_AnalysisTypeTable.name == atype,
                              meas_ExperimentTable.id == exp.id,
                              meas_AnalysisTable.id != analysis.record_id))

        return q.all()

#===============================================================================
# property get/set
#===============================================================================
    @cached_property
    def _get_predictors(self):
        ps = self._predictors
        if not ps:
            ps = [
              self._predictor_factory(predictor)
              for a in self.analyses
                  for predictor in self._find_predictors(a)]

        pp = []

        if ps:
            # filter duplicates
            uuids = []
            for pi in ps:
                if pi.uuid in uuids:
                    continue
                else:
                    uuids.append(pi.uuid)
                    pp.append(pi)

            n = len(pp)
            progress = myProgressDialog(max=n, size=(550, 15))
            progress.open()
            progress.center()

            for pi in pp:
                msg = 'loading {}'.format(pi.record_id)
                progress.change_message(msg)
                pi.initialize()
                progress.increment()

        return pp
#===============================================================================
# handlers
#===============================================================================
    def _update_interpolation(self, regressors):
        g = self.graph
        if g.plots:
            si = g.plots[0].plots['plot4'][0]
#            i = 0
            for reg, fi in zip(regressors, self.fits):
                if not fi.use:
                    continue

                if not fi.fit.lower() in ['preceeding', 'bracketing interpolate', 'bracketing average']:
#                    reg = regressors[i]
                    xs = si.index.get_data()
                    ys = reg.predict(xs)
                    es = reg.predict_error(xs, error_calc='sd')
                    si.value.set_data(ys)

                    self.sync_analyses(ys, es, fi.name)

                    if hasattr(si, 'yerror'):
                        si.yerror.set_data(es)
#                i += 1

            g.redraw()

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
    normalization_factor = Float

    def __init__(self, *args, **kw):
        super(DetectorIntercalibrationInterpolationCorrection, self).__init__(*args, **kw)
        bind_preference(self, 'normalization_factor', 'pychron.experiment.constants.Ar40_Ar36_atm')
        print self.normalization_factor

    def _get_predictor_value(self, pi, key):
        v = (pi.get_corrected_value('Ar40') / pi.get_corrected_value('Ar36'))
        if key == 'IC':
            v /= self.normalization_factor
        return  v

    def load_fits(self, names):
        for ri in ['IC', 'Ar40/Ar36']:
            self.fits.append(self._correction_factory(ri))

#============= EOF =============================================
