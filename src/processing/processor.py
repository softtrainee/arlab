#===============================================================================
# Copyright 2013 Jake Ross
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
from src.experiment.isotope_database_manager import IsotopeDatabaseManager
from src.processing.plotter_options_manager import IdeogramOptionsManager
import datetime
from src.database.orms.isotope_orm import meas_AnalysisTable, \
    meas_MeasurementTable, gen_AnalysisTypeTable
from sqlalchemy.sql.expression import and_
from sqlalchemy.orm.exc import NoResultFound
from src.processing.analysis import Analysis

#============= enthought library imports =======================
# from traits.api import HasTraits, List, Instance, on_trait_change, Any, DelegatesTo
# from traitsui.api import View, Item
# from src.experiment.isotope_database_manager import IsotopeDatabaseManager
# from src.graph.graph import Graph
# from src.processing.plotter_options_manager import IdeogramOptionsManager
# from src.database.records.isotope_record import IsotopeRecord
# from src.processing.analysis import Analysis, Marker
# from src.processing.search.selector_manager import SelectorManager
# from src.processing.search.search_manager import SearchManager
# from src.ui.progress_dialog import myProgressDialog
# from src.ui.gui import invoke_in_main_thread
# import threading
# from pyface.progress_dialog import ProgressDialog
# import time
#============= standard library imports ========================
#============= local library imports  ==========================
class Processor(IsotopeDatabaseManager):
    def refit_isotopes(self, analysis, pd=None, fits=None, keys=None, verbose=False):
        if not isinstance(analysis, Analysis):
            analysis = self.make_analyses([analysis])[0]

        analysis.load_isotopes()

        dbr = analysis.dbrecord
        if keys is None:
            keys = [iso.molecular_weight.name for iso in dbr.isotopes
                                if iso.kind == 'signal']

        '''
            if spectrometer is map use all linear
            
            if spectrometer is Jan or Obama
                if counts >150 use parabolic
                else use linear
        '''
        if fits is None:
            if analysis.mass_spectrometer in ('pychron obama', 'pychron jan', 'jan', 'obama'):
                n = 0
                if keys:
                    n = analysis.isotopes[keys[0]].xs.shape[0]

                if n >= 150:
                    fits = ['parabolic', ] * len(keys)
                else:
                    fits = ['linear', ] * len(keys)

            else:
                fits = ['linear', ] * len(keys)

        db = self.db

        if not dbr.selected_histories:
            db.add_selected_histories(dbr)
            db.flush()

        msg = 'fitting isotopes for {}'.format(analysis.record_id)
        if pd is not None:
            pd.change_message(msg)
        self.debug(msg)
        dbhist = db.add_fit_history(dbr)
        for key, fit in zip(keys, fits):
            dbiso_baseline = next((iso for iso in dbr.isotopes
                          if iso.molecular_weight.name == key and iso.kind == 'baseline'), None)
            if dbiso_baseline:
                if verbose:
                    self.debug('{} {}'.format(key, fit))

                vv = analysis.isotopes[key]
                baseline = vv.baseline
                if not baseline:
                    continue

                v, e = baseline.value, baseline.error
                db.add_fit(dbhist, dbiso_baseline, fit='average_sem', filter_outliers=True,
                           filter_outlier_std_devs=2)
                db.add_isotope_result(dbiso_baseline, dbhist, signal_=float(v), signal_err=float(e))

                dbiso = next((iso for iso in dbr.isotopes
                          if iso.molecular_weight.name == key and iso.kind == 'signal'), None)
                if dbiso:
                    vv = analysis.isotopes[key]
                    v, e = vv.value, vv.error

                    db.add_fit(dbhist, dbiso, fit=fit, filter_outliers=True,
                               filter_outlier_std_devs=2)
                    db.add_isotope_result(dbiso, dbhist, signal_=float(v), signal_err=float(e))

        if pd is not None:
            pd.increment()

    def _find_analyses(self, ms, post, delta, atype, step=100, maxtries=10, **kw):
        if delta < 0:
            step = -step

        for i in range(maxtries):
            rs = self._filter_analyses(ms, post, delta + i * step, 5, atype, **kw)
            if rs:
                return rs
        else:
            return []

    def _filter_analyses(self, ms, post, delta, lim, at, filter_hook=None):
        '''
            ms= spectrometer 
            post= timestamp
            delta= time in hours
            at=analysis type
            
            if delta is negative 
            get all before post and after post-delta

            if delta is post 
            get all before post+delta and after post
        '''
        sess = self.db.get_session()
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
                          meas_AnalysisTable.analysis_timestamp >= a,
                          meas_AnalysisTable.analysis_timestamp <= b,
                          ))

        if filter_hook:
            q = filter_hook(q)
        q = q.limit(lim)

        try:
            return q.all()
        except NoResultFound:
            pass

    def preceeding_blank_correct(self, analysis, keys=None):
        from src.regression.interpolation_regressor import InterpolationRegressor
        if not isinstance(analysis, Analysis):
            analysis = self.make_analyses([analysis])[0]
            analysis.load_isotopes()

        ms = analysis.spectrometer
        post = analysis.timestamp
        delta = -1
        atype = 'blank_{}'.format(analysis.analysis_type)
        br = self._find_analyses(ms, post, delta, atype)

        br = self.make_analyses(br)
        self.load_analyses(br)

        if keys is None:
            keys = analysis.isotope_keys


        for key in keys:
            r_xs, r_ys, r_es = [(ai.timestamp, ai.isotopes[key].value, ai.isotopes[key].error) for ai in br
                                                    if key in ai.isotopes]

            reg = InterpolationRegressor(xs=r_xs,
                                     ys=r_ys,
                                     yserr=r_es,
                                     kind='preceeding')
            print key, reg.predict(post)
#        return reg.predict(ant)

    def recall(self):
        pass
#        if self.db:
#            if self.db.connect():
# #                ps = self.search_manager
# #                ps.selected = None
#                self.db.selector.load_last(n=100)
#
# #                return [self._record_factory(si) for si in ps.selector.records[-1:]]
#                info = ps.edit_traits(view='modal_view')
#    #            print info.result
#                if info.result:
# #                    ans = [self._record_factory(si) for si in ps.selector.selected]
#    #                self._load_analyses(ans)
#                    return ps.selector.selected

    def new_ideogram(self, ans, plotter_options=None):
        '''
            return a plotcontainer
        '''
        from src.processing.plotters.ideogram import Ideogram

        probability_curve_kind = 'cumulative'
        mean_calculation_kind = 'weighted_mean'
        data_label_font = None
        metadata_label_font = None
 #        highlight_omitted = True
        display_mean_indicator = True
        display_mean_text = True

        p = Ideogram(
 #                     db=self.db,
 #                     processing_manager=self,
                     probability_curve_kind=probability_curve_kind,
                     mean_calculation_kind=mean_calculation_kind
                     )
        options = dict(
                       title='',
                       data_label_font=data_label_font,
                       metadata_label_font=metadata_label_font,
                       display_mean_text=display_mean_text,
                       display_mean_indicator=display_mean_indicator,
                       )

        if plotter_options is None:
            pom = IdeogramOptionsManager()
            plotter_options = pom.plotter_options

        if ans:
            self.analyses = ans
            gideo = p.build(ans, options=options,
                            plotter_options=plotter_options)
            if gideo:
                gideo, _plots = gideo

            return gideo





#===============================================================================
# corrections
#===============================================================================
    def add_history(self, analysis, kind):
        dbrecord = analysis.dbrecord
        db = self.db

        # new history
        func = getattr(db, 'add_{}_history'.format(kind))
        history = func(dbrecord, user=db.save_username)
#        history = db.add_blanks_history(dbrecord, user=db.save_username)

        # set analysis' selected history
        sh = db.add_selected_histories(dbrecord)
        setattr(sh, 'selected_{}'.format(kind), history)
#        sh.selected_blanks = history
        return history

    def apply_fixed_correction(self, history, isotope, value, error, correction_name):
        func = getattr(self.db, 'add_{}'.format(correction_name))
        func(history, isotope=isotope, use_set=False,
             user_value=value, user_error=error)

    def apply_fixed_value_correction(self, phistory, history, fit_obj, correction_name):
        db = self.db
        if phistory:
            bs = getattr(phistory, correction_name)
            bs = reversed(bs)
            prev = next((bi for bi in bs if bi.isotope == fit_obj.name), None)
            if prev:
                uv = prev.user_value
                ue = prev.user_error
                func = getattr(db, 'add_{}'.format(correction_name))
                func(history,
                      isotope=prev.isotope,
                      fit=prev.fit,
                      user_value=uv,
                      user_error=ue
                      )

    def apply_correction(self, history, analysis, fit_obj, predictors, kind):
        func = getattr(self, '_apply_{}_correction'.format(kind))
        func(history, analysis, fit_obj, predictors)

    def _apply_blanks_correction(self, history, analysis, fit_obj, predictors):
        ss = analysis.isotopes[fit_obj.name]

        item = self.db.add_blanks(history,
                    isotope=fit_obj.name,
                    user_value=float(ss.blank.value),
                    user_error=float(ss.blank.error),
                    fit=fit_obj.fit)

#        ps = self.interpolation_correction.predictors
        if predictors:
            for pi in predictors:
                self.db.add_blanks_set(item, pi.dbrecord)
#
# class Processor2(IsotopeDatabaseManager):
#    count = 0
#    selector_manager = Instance(SelectorManager)
#    search_manager = Instance(SearchManager)
#    active_editor = Any
#    analyses = List
#    component = Any
#    _plotter_options = Any
#
# #    @on_trait_change('''options_manager:plotter_options:[+, aux_plots:+]
# # ''')
# #    def _options_update(self, name, new):
# #        print name, new, len(self.analyses), self
# #        if self.analyses:
# #            comp = self.new_ideogram(ans=self.analyses)
# # #            self.component = comp
# #            if comp:
# #                self.active_editor.component = comp
#    def recall(self):
#        if self.db:
#            if self.db.connect():
#                ps = self.search_manager
#                ps.selected = None
#                ps.selector.load_last(n=100)
#
# #                return [self._record_factory(si) for si in ps.selector.records[-1:]]
#                info = ps.edit_traits(view='modal_view')
#    #            print info.result
#                if info.result:
#                    ans = [self._record_factory(si) for si in ps.selector.selected]
#    #                self._load_analyses(ans)
#                    return ans
#
#    def find(self):
#        if self.db.connect():
#            ps = self.search_manager
#            ps.selected = None
#            ps.selector.load_last(n=20)
#            self.open_view(ps)
#
#    def _gather_data(self):
#        d = self.selector_manager
#        if self.db:
#            if self.db.connect():
#                info = d.edit_traits(kind='livemodal')
#                if info.result:
#                    ans = [self._record_factory(ri)
#                                for ri in d.selected_records
#                                    if not isinstance(ri, Marker)]
#
#                    self._load_analyses(ans)
#                    return ans
#
#    def new_spectrum(self, plotter_options=None, ans=None):
#        from src.processing.plotters.spectrum import Spectrum
#
#        p = Spectrum()
#        if ans is None:
#            ans = self._gather_data()
#
#        if plotter_options is None:
#            plotter_options = self._plotter_options
#
#        options = {}
#
#        self._plotter_options = plotter_options
#        if ans:
#            self.analyses = ans
#            gideo = p.build(ans, options=options,
#                            plotter_options=plotter_options)
#            if gideo:
#                gideo, _plots = gideo
#
#            return gideo
#
#    def new_ideogram(self, plotter_options=None, ans=None):
#        '''
#            return a plotcontainer
#        '''
#        from src.processing.plotters.ideogram import Ideogram
#
# #        g = self._window_factory()
#
#        probability_curve_kind = 'cumulative'
#        mean_calculation_kind = 'weighted_mean'
#        data_label_font = None
#        metadata_label_font = None
# #        highlight_omitted = True
#        display_mean_indicator = True
#        display_mean_text = True
#        title = 'Foo'  # .format(self.count)
# #        self.count += 1
#        p = Ideogram(
# #                     db=self.db,
# #                     processing_manager=self,
#                     probability_curve_kind=probability_curve_kind,
#                     mean_calculation_kind=mean_calculation_kind
#                     )
#
# #        plotter_options = self.options_manager.plotter_options
# #        ps = self._build_aux_plots(plotter_options.get_aux_plots())
#        options = dict(
# #                       aux_plots=ps,
# #                       use_centered_range=plotter_options.use_centered_range,
# #                       centered_range=plotter_options.centered_range,
# #                       xmin=plotter_options.xmin,
# #                       xmax=plotter_options.xmax,
# #                       xtitle_font=xtitle_font,
# #                       xtick_font=xtick_font,
# #                       ytitle_font=ytitle_font,
# #                       ytick_font=ytick_font,
#                       data_label_font=data_label_font,
#                       metadata_label_font=metadata_label_font,
#                       title=title,
#                       display_mean_text=display_mean_text,
#                       display_mean_indicator=display_mean_indicator,
#                       )
#
#        if ans is None:
#            ans = self._gather_data()
#
#        if plotter_options is None:
#            plotter_options = self._plotter_options
#
#        self._plotter_options = plotter_options
#        if ans:
#            self.analyses = ans
#            gideo = p.build(ans, options=options,
#                            plotter_options=plotter_options)
#            if gideo:
#                gideo, _plots = gideo
#
#            return gideo
#
#
#
#
#
##===============================================================================
# # defaults
##===============================================================================
#    def _selector_manager_default(self):
#        db = self.db
#        d = SelectorManager(db=db)
#        return d
#
#    def _search_manager_default(self):
#        db = self.db
#        d = SearchManager(db=db)
#        if not db.connected:
#            db.connect()
#        return d
#============= EOF =============================================
