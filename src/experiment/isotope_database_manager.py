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
from traits.api import HasTraits, Instance
from apptools.preferences.preference_binding import bind_preference
#============= standard library imports ========================
#============= local library imports  ==========================
from src.database.adapters.isotope_adapter import IsotopeAdapter
from src.managers.manager import Manager
from src.ui.progress_dialog import myProgressDialog


class IsotopeDatabaseManager(Manager):
    db = Instance(IsotopeAdapter)
    def __init__(self, bind=True, *args, **kw):
        super(IsotopeDatabaseManager, self).__init__(*args, **kw)
        if bind:
            self.bind_preferences()

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

    def bind_preferences(self):
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

        if not self.db.connect():
            self.warning_dialog('Not Connected to Database {}'.format(self.db.url))
            self.db = None

    def _db_default(self):
        return self._db_factory()

    def _db_factory(self):
        db = IsotopeAdapter(application=self.application)
        return db

    def _load_analyses(self, ans, func=None):
        progress = self._open_progress(len(ans))
        for ai in ans:
            msg = 'loading {}'.format(ai.record_id)
            progress.change_message(msg)

            if func:
                func(ai)
            else:
                ai.load_isotopes()

            progress.increment()

    def _open_progress(self, n):
        pd = myProgressDialog(max=n - 1, size=(550, 15))
        pd.open()
        return pd
#============= EOF =============================================
