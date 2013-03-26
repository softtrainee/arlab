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
from traitsui.api import View, Item, TableEditor
from apptools.preferences.preference_binding import bind_preference
#============= standard library imports ========================
#============= local library imports  ==========================
from src.database.adapters.isotope_adapter import IsotopeAdapter
from src.managers.manager import Manager


class IsotopeDatabaseManager(Manager):
    db = Instance(IsotopeAdapter)
    def bind_preferences(self):
        if self.db is None:
            self.db = self._db_factory()

        prefid = 'pychron.experiment'

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

#        if not self.db.connect():
#            self.warning_dialog('Not Connected to Database {}'.format(self.db.url))
#            self.db = None
    def _db_default(self):
        return self._db_factory()

    def _db_factory(self):
        db = IsotopeAdapter(application=self.application)
        return db
#============= EOF =============================================
