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
from traits.api import Instance, String, Property, Event, \
    cached_property
from apptools.preferences.preference_binding import bind_preference
#============= standard library imports ========================
#============= local library imports  ==========================
from src.database.adapters.isotope_adapter import IsotopeAdapter
from src.managers.manager import Manager
from src.ui.progress_dialog import myProgressDialog
# from src.database.records.isotope_record import IsotopeRecord, IsotopeRecordView
from src.database.records.isotope_record import IsotopeRecordView
# from src.processing.analysis import Analysis, NonDBAnalysis
from src.codetools.simple_timeit import simple_timer, timethis
from src.processing.analyses.analysis import DBAnalysis, Analysis
from src.loggable import Loggable
from src.database.orms.isotope.meas import meas_AnalysisTable
from src.experiment.utilities.identifier import make_runid
# from src.constants import NULL_STR
# from src.ui.gui import invoke_in_main_thread


class IsotopeDatabaseManager(Loggable):
    db = Instance(IsotopeAdapter)

    irradiation = String
    level = String

    irradiations = Property(depends_on='saved, updated')
    levels = Property(depends_on='irradiation, saved, updated')

    saved = Event
    updated = Event


    def __init__(self, bind=True, connect=True, warn=True, *args, **kw):
        super(IsotopeDatabaseManager, self).__init__(*args, **kw)

        if bind:
            try:
                self.bind_preferences()
            except AttributeError, e:
                self.debug('bind exception. {}'.format(e))

                #         if connect and not self.db.connect(warn=warn):
        if connect:
            self.db.connect(warn=warn)

            #             self.db = None

    def isConnected(self):
        if self.db:
            return self.db.connected

    def load(self):
        self.populate_default_tables()
        return True

    def populate_default_tables(self):
        self.debug('populating default tables')
        db = self.db
        if self.db:
            if db.connect(force=False):
                from src.database.defaults import load_isotopedb_defaults

                load_isotopedb_defaults(db)
                self.debug('defaults finished')
                return True

    def verify_database_connection(self, inform=True):
        if self.db is not None:
            if self.db.connect(force=True):
                return True
                #                 self.db.flush()
                #                 self.db.reset()
        elif inform:
            self.warning_dialog('Not Database available')

    def bind_preferences(self, connect=False):
        if self.db is None:
            self.db = self._db_factory()

        prefid = 'pychron.database'
        try:
            bind_preference(self, 'username', '{}.username'.format(prefid))
            #        bind_preference(self, 'repo_kind', '{}.repo_kind'.format(prefid))

            #        if self.repo_kind == 'FTP':
            #            bind_preference(self.repository, 'host', '{}.ftp_host'.format(prefid))
            #            bind_preference(self.repository, 'username', '{}.ftp_username'.format(prefid))
            #            bind_preference(self.repository, 'password', '{}.ftp_password'.format(prefid))
            #            bind_preference(self.repository, 'remote', '{}.repo_root'.format(prefid))

            bind_preference(self.db, 'kind', '{}.db_kind'.format(prefid))
            if self.db.kind == 'mysql':
                bind_preference(self.db, 'host', '{}.db_host'.format(prefid))
                bind_preference(self.db, 'username', '{}.db_username'.format(prefid))
                bind_preference(self.db, 'password', '{}.db_password'.format(prefid))

            bind_preference(self.db, 'name', '{}.db_name'.format(prefid))
        except AttributeError:
            pass

    def filter_analysis_tag(self, ans, exclude):
        if not isinstance(exclude, (list, tuple)):
            exclude = (exclude,)

        return filter(lambda x: not x.tag in exclude, ans)

    def make_analysis(self, ai):
        return self.make_analyses((ai,))[0]

    def make_analyses(self, ans, calculate_age=False,
                      unpack=False,
                      exclude=None, **kw):
        if exclude:
            ans = self.filter_analysis_tag(ans, exclude)

        if not ans:
            return []

        with self.db.session_ctx():
            if ans:
                progress = None

                dbans = filter(lambda x: isinstance(x, DBAnalysis), ans)
                nodbans = filter(lambda x: not isinstance(x, DBAnalysis), ans)
                if nodbans:
                    n = len(ans)
                    if n > 1:
                        progress = self._open_progress(n)

                    #if progress:
                    #    progress.on_trait_change(self._progress_closed, 'closed')

                    #rs = []
                    uuids = [a.uuid for a in dbans]
                    for ai in ans:
                        r = self._analysis_factory(ai,
                                                   progress=progress,
                                                   calculate_age=calculate_age,
                                                   unpack=unpack,
                                                   **kw)
                        if r is not None:
                            #rs.append(r)
                            if r.uuid not in uuids:
                                dbans.append(r)
                                uuids.append(r.uuid)

                    #dbans.extend(rs)

                    if progress:
                        progress.on_trait_change(self._progress_closed,
                                                 'closed', remove=True)

                return dbans

    def get_level(self, level, irradiation=None):
        if irradiation is None:
            irradiation = self.irradiation

        return self.db.get_irradiation_level(irradiation, level)

    def open_progress(self, n=2):
        return self._open_progress(n)

    #===============================================================================
    # private
    #===============================================================================
    def _load_analyses(self, ans, func=None, progress=None, unpack=True):

        if not ans:
            return

        if func is None:
        #             @simple_timer('load')
            def func(x):
            #                 x.load_isotopes(unpack=unpack)
                x.calculate_age()

        if len(ans) == 1:
            func(ans[0])

        else:
            if progress:
                def f(ai, msg):
                    progress.change_message(msg)
                    func(ai)
                    progress.increment()
            else:
                def f(ai, msg):
                    func(ai)

            for ai in ans:
                msg = 'loading {}'.format(ai.record_id)
                #                 self.debug(msg)
                f(ai, msg)

    def _open_progress(self, n):

        pd = myProgressDialog(max=n - 1,
                              size=(550, 15))
        pd.open()
        pd.on_trait_change(self._progress_closed, 'closed')
        return pd

    def _progress_closed(self):
        if self.application:
            win = self.application.windows[-1]
            win.activate()

    def _add_arar(self, meas_analysis, analysis):

        db = self.db
        with db.session_ctx() as sess:
            hist = db.add_arar_history(meas_analysis)
            #a, e=age.nominal_value, age.std_dev
            d = dict()
            attrs = ['k39', 'ca37', 'cl36', 'rad40',
                     'Ar40', 'Ar39', 'Ar38', 'Ar37', 'Ar36']

            for a in attrs:
                v = getattr(analysis, a)
                ek = '{}_err'.format(a)
                d[a] = float(v.nominal_value)
                d[ek] = float(v.std_dev)

            age_scalar = analysis.arar_constants.age_scalar
            d['age_err_wo_j'] = analysis.age_error_wo_j * age_scalar

            age = analysis.age
            d['age'] = age.nominal_value * age_scalar
            d['age_err'] = age.std_dev * age_scalar

            db.add_arar(hist, **d)

            meas_analysis.selected_histories.selected_arar = hist
            sess.commit()
            #hist.selected=analysis.selected_histories
            #analysis.selected_histories.selected_arar=hist

    def _analysis_factory(self, rec, progress=None,
                          calculate_age=False,
                          unpack=False,
                          exclude=None, **kw):
        graph_id = 0
        group_id = 0

        if isinstance(rec, (Analysis, DBAnalysis)):
            if progress:
                progress.increment()

            return rec

        else:
            atype = None
            if isinstance(rec, meas_AnalysisTable):
                rid = make_runid(rec.labnumber.identifier, rec.aliquot, rec.step)
                atype = rec.measurement.analysis_type.name

            elif hasattr(rec, 'record_id'):
                rid = rec.record_id
            else:
                rid = id(rec)

            if hasattr(rec, 'group_id'):
                group_id = rec.group_id

            if hasattr(rec, 'graph_id'):
                graph_id = rec.graph_id

            if atype is None:
                atype = rec.analysis_type

            def func(r):
                meas_analysis = self.db.get_analysis_uuid(r.uuid)

                ai = DBAnalysis(group_id=group_id,
                                graph_id=graph_id)
                if atype in ('unknown', 'cocktail'):
                    ai.sync_arar(meas_analysis)

                    if calculate_age:
                        ai.sync(meas_analysis, unpack=True)
                        ai.calculate_age(force=True)
                    elif not ai.persisted_age:
                        ai.sync(meas_analysis, unpack=True)
                        ai.calculate_age()
                        self._add_arar(meas_analysis, ai)
                    #elif calculate_age:
                    #    ai.sync(meas_analysis, unpack=True)
                    #    ai.calculate_age(force=True)
                    else:
                        ai.sync(meas_analysis, unpack=unpack)

                else:
                    ai.sync(meas_analysis, unpack=unpack)

                return ai

            if progress:
                show_age = calculate_age and atype in ('unknown', 'cocktail')
                m = 'calculating age' if show_age else ''
                msg = 'loading {}. {}'.format(rid, m)
                progress.change_message(msg)
                #a = timethis(func, args=(rec,), msg='make analysis')
                a = func(rec)
                progress.increment()
            else:
                a = func(rec)

            return a

    def _db_factory(self):

        db = IsotopeAdapter(application=self.application)
        return db

    #===============================================================================
    # property get/set
    #===============================================================================
    @cached_property
    def _get_irradiations(self):
    #         self.irradiation = NULL_STR
    #        r = ['NM-Test', 'NM-100', 'NM-200']
    #         r = [NULL_STR] +
        r = []
        db = self.db
        if db and db.connected:
            with db.session_ctx():
            #             with self.db.session_() as sess:
                r = [str(ri.name) for ri in db.get_irradiations()
                     if ri.name]

            if r and not self.irradiation:
                self.irradiation = r[0]

        return r

    @cached_property
    def _get_levels(self):

    #         self.level = NULL_STR
        r = []
        if self.db and self.db.connected:

            with self.db.session_ctx():
                irrad = self.db.get_irradiation(self.irradiation)
                if irrad:
                    r = sorted([str(ri.name) for ri in irrad.levels
                                if ri.name])
                    if r and not self.level:
                        self.level = r[0]

        return r

    #===============================================================================
    # handlers
    #===============================================================================
    def _irradiation_changed(self):
        self.level = ''

    #===============================================================================
    # defaults
    #===============================================================================
    def _db_default(self):
        return self._db_factory()

#============= EOF =============================================
