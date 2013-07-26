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


#============= enthought library imports =======================
#============= standard library imports ========================
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_, not_
from datetime import datetime, timedelta
#============= local library imports  ==========================
from src.experiment.isotope_database_manager import IsotopeDatabaseManager
from src.processing.plotter_options_manager import IdeogramOptionsManager, \
    SpectrumOptionsManager, InverseIsochronOptionsManager
from src.database.orms.isotope_orm import meas_AnalysisTable, \
    meas_MeasurementTable, gen_AnalysisTypeTable, gen_LabTable, gen_SampleTable, \
    gen_MassSpectrometerTable, gen_ExtractionDeviceTable, meas_ExtractionTable
from src.processing.analysis import Analysis
from src.processing.tasks.analysis_edit.fits import Fit
from src.processing.plotters.spectrum import Spectrum
from src.processing.plotters.ideogram import Ideogram
from src.processing.plotters.inverse_isochron import InverseIsochron
from src.processing.plotters.series import Series


class Processor(IsotopeDatabaseManager):
    def load_series(self, analysis_type, ms, ed, weeks=0, days=0, hours=0):
        db = self.db
        sess = db.get_session()
        q = sess.query(meas_AnalysisTable)
        q = q.join(meas_MeasurementTable)
        q = q.join(meas_ExtractionTable)
        q = q.join(gen_AnalysisTypeTable)
        q = q.join(gen_MassSpectrometerTable)
        q = q.join(gen_ExtractionDeviceTable)
#         q = q.join(gen_LabTable)

        d = datetime.today()
        today = datetime.today()  # .date()#.datetime()
        d = d - timedelta(hours=hours, weeks=weeks, days=days)
        attr = meas_AnalysisTable.analysis_timestamp
        q = q.filter(and_(attr <= today, attr >= d))
        q = q.filter(gen_AnalysisTypeTable.name == analysis_type)
        q = q.filter(gen_MassSpectrometerTable.name == ms)

        if ed:
#             ed = ed.capitalize()
#             print ed
            q = q.filter(gen_ExtractionDeviceTable.name == ed)

        return self._make_analyses_from_query(q)


    def load_sample_analyses(self, labnumber, sample, aliquot=None):
        db = self.db
        sess = db.get_session()
        q = sess.query(meas_AnalysisTable)
        q = q.join(gen_LabTable)
        q = q.join(gen_SampleTable)

        q = q.filter(gen_SampleTable.name == sample)
        if aliquot is not None:
            q = q.filter(meas_AnalysisTable.aliquot == aliquot)

        if sample=='FC-2':
            q=q.filter(gen_LabTable.identifier==labnumber)
            
#        q = q.limit(10)
        return self._make_analyses_from_query(q)

    def _make_analyses_from_query(self, q):
        ans = None
        try:
            ans = q.all()
        except Exception, e:
            import traceback
            traceback.print_exc()

        if ans:
            ans = self.make_analyses(ans)
            return ans

    def auto_blank_fit(self, irradiation, level, kind):
        if kind == 'preceeding':
            '''
            1. supply a list of labnumbers/ supply level and extract labnumbers (with project minnabluff)
            2. get all analyses for the labnumbers
            3. sort analyses by run date
            4. calculate blank
                1. preceeding/bracketing
                    get max 2 predictors
                
                2. fit
                    a. group analyses by run date 
                    b. get n predictors based on group date
            5. save blank
            '''
            db = self.db
            level = db.get_irradiation_level(irradiation, level)

            labnumbers = [pi.labnumber for pi in level.positions
                            if pi.labnumber.sample.project.name in ('j', 'Minna Bluff', 'Mina Bluff')]
            ans = [ai
                    for ln in labnumbers
                        for ai in ln.analyses
                        ]
            pd = self.open_progress(n=len(ans))
            for ai in ans:
                self.preceeding_blank_correct(ai, pd=pd)
            db.commit()

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

    def _find_analyses(self, ms, post, delta, atype, step=0.5, maxtries=10, **kw):
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
        if isinstance(post, float):
            post = datetime.datetime.fromtimestamp(post)

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

    def find_associated_analyses(self, analysis):
        ms = analysis.spectrometer
        post = analysis.timestamp

        delta = -2
        atype = 'blank_{}'.format(analysis.analysis_type)
        br = self._find_analyses(ms, post, delta, atype)

        delta = 2
        ar = self._find_analyses(ms, post, delta, atype)

        return br + ar

    def preceeding_blank_correct(self, analysis, keys=None, pd=None):
        from src.regression.interpolation_regressor import InterpolationRegressor
        if not isinstance(analysis, Analysis):
            analysis = self.make_analyses([analysis])[0]
            analysis.load_isotopes()

        msg = 'applying preceeding blank for {}'.format(analysis.record_id)
        if pd is not None:
            pd.change_message(msg)
            pd.increment()

        self.info(msg)
        ms = analysis.spectrometer
        post = analysis.timestamp

        delta = -2
        atype = 'blank_{}'.format(analysis.analysis_type)
        br = self._find_analyses(ms, post, delta, atype)

        br = self.make_analyses(br[-1:])
        br[0].load_isotopes()
#        self.load_analyses(br)

        if keys is None:
            keys = analysis.isotope_keys

        kind = 'blanks'
        history = self.add_history(analysis, kind)

        fit = 'preceeding'
        for key in keys:
            predictors = [ai for ai in br if key in ai.isotopes]
            if predictors:
                r_xs, r_y = zip(*[(ai.timestamp, ai.isotopes[key].baseline_corrected_value()
                                          )
                                        for ai in predictors])
                r_ys, r_es = zip(*[(yi.nominal_value, yi.std_dev) for yi in r_y])
                reg = InterpolationRegressor(xs=r_xs,
                                         ys=r_ys,
                                         yserr=r_es,
                                         kind=fit)

                fit_obj = Fit(name=key, fit=fit)
                v, e = reg.predict(post), reg.predict_error(post)
                analysis.set_blank(key, v[0], e[0])
                self.apply_correction(history, analysis, fit_obj, predictors, kind)
            else:
                self.warning('no preceeding blank for {}'.format(analysis.record_id))

    def recall(self):
        pass
#===============================================================================
# figures
#===============================================================================
    def new_series(self, ans, options=None, plotter_options=None):
        if ans:
            p = Series()
            gseries = p.build(ans, options=options,
                              plotter_options=plotter_options)
            return gseries, p

    def new_ideogram(self, ans, plotter_options=None):
        '''
            return a plotcontainer
        '''

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
#             self.analyses = ans
            gideo = p.build(ans, options=options,
                            plotter_options=plotter_options)
            if gideo:
                gideo, _plots = gideo

            return gideo, p

    def new_spectrum(self, ans, plotter_options=None):

        p = Spectrum()

        if plotter_options is None:
            pom = SpectrumOptionsManager()
            plotter_options = pom.plotter_options

        options = {}

        self._plotter_options = plotter_options
        if ans:
#             self.analyses = ans
            gspec = p.build(ans, options=options,
                            plotter_options=plotter_options)
            if gspec:
                gspec, _plots = gspec

            return gspec, p

    def new_inverse_isochron(self, ans, plotter_options=None):
        p = InverseIsochron()

        if plotter_options is None:
            pom = InverseIsochronOptionsManager()
            plotter_options = pom.plotter_options

        options = {}

        self._plotter_options = plotter_options
        if ans:
#             self.analyses = ans
            giso = p.build(ans, options=options,
                            plotter_options=plotter_options)
            if giso:
                return giso.plotcontainer
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


        '''
            the blanks_editor may have set a temporary blank
            use that instead of the saved blank
        '''
        if hasattr(ss, 'temporary_blank'):
            blank = ss.temporary_blank
        else:
            blank = ss.blank

        item = self.db.add_blanks(history,
                    isotope=fit_obj.name,
                    user_value=float(blank.value),
                    user_error=float(blank.error),
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
