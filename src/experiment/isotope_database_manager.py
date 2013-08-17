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
from traits.api import HasTraits, Instance, String, Property, Event, \
    cached_property
from apptools.preferences.preference_binding import bind_preference
#============= standard library imports ========================
#============= local library imports  ==========================
from src.database.adapters.isotope_adapter import IsotopeAdapter
from src.managers.manager import Manager
from src.ui.progress_dialog import myProgressDialog
from src.database.records.isotope_record import IsotopeRecord, IsotopeRecordView
from src.processing.analysis import Analysis, NonDBAnalysis
# from src.constants import NULL_STR
# from src.ui.gui import invoke_in_main_thread


class IsotopeDatabaseManager(Manager):
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

        if connect and not self.db.connect(warn=warn):
            self.db = None

    def isConnected(self):
        if self.db:
            return self.db.connected

    def load(self):
        return self.populate_default_tables()

    def populate_default_tables(self):
        self.debug('populating default tables')
        db = self.db
        if self.db:
            if db.connect(force=False):
                from src.database.defaults import load_isotopedb_defaults
                load_isotopedb_defaults(db)
                return True

    def verify_database_connection(self, inform=True):
        if self.db is not None:
            if self.db.connect(force=True):
                self.db.flush()
                self.db.reset()
                return True
        elif inform:
            self.warning_dialog('Not Database available')

    def bind_preferences(self, connect=False):
        if self.db is None:
            self.db = self._db_factory()

        prefid = 'pychron.experiment'
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

    def make_analyses(self, ans, **kw):
        if ans:
            return [self._record_factory(ai, **kw) for ai in ans]

    def load_analyses(self, ans, **kw):
        self._load_analyses(ans, **kw)

    def get_level(self, level, irradiation=None):
        if irradiation is None:
            irradiation = self.irradiation

        return self.db.get_irradiation_level(irradiation, level)

    def _record_factory(self, pi, **kw):
        if isinstance(pi, (Analysis, NonDBAnalysis)):
            return pi

        if isinstance(pi, IsotopeRecordView):
            rec = self.db.get_analysis(pi.uuid, key='uuid')
            kw.update(dict(graph_id=pi.graph_id,
                           group_id=pi.group_id))
            pi = rec

        rec = IsotopeRecord(_dbrecord=pi, **kw)
        a = Analysis(isotope_record=rec)
#        a.load_isotopes()
        return a

    def _db_default(self):
        return self._db_factory()

    def _db_factory(self):
        db = IsotopeAdapter(application=self.application)
        return db

    def _load_analyses(self, ans, func=None):
        if not ans:
            return

        if func is None:
            def func(x):
                if hasattr(x, 'load_isotopes'):
                    x.load_isotopes()

        if len(ans) == 1:
            func(ans[0])

        else:
            progress = self._open_progress(len(ans))
            for ai in ans:
                msg = 'loading {}'.format(ai.record_id)
                progress.change_message(msg)
                self.debug(msg)

                func(ai)
                progress.increment()

    def open_progress(self, n=2):
        return self._open_progress(n)

    def _open_progress(self, n):

        pd = myProgressDialog(max=n - 1, size=(550, 15))
        pd.open()
        return pd

#===============================================================================
# property get/set
#===============================================================================
    @cached_property
    def _get_irradiations(self):
#         self.irradiation = NULL_STR
#        r = ['NM-Test', 'NM-100', 'NM-200']
#         r = [NULL_STR] +
        r = []
        if self.db:
            r = [str(ri.name) for ri in self.db.get_irradiations()
                            if ri.name]

            if r and not self.irradiation:
                self.irradiation = r[0]

        return r

    @cached_property
    def _get_levels(self):

#         self.level = NULL_STR
        r = []
        if self.db:
            irrad = self.db.get_irradiation(self.irradiation)
            if irrad:
    #             r = [NULL_STR] + sorted([str(ri.name) for ri in irrad.levels])
                r = sorted([str(ri.name) for ri in irrad.levels
                                            if ri.name])
                if r and not self.level:
                    self.level = r[0]
    #            if r and not self.level:

        return r
#============= EOF =============================================
