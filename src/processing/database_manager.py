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

class DatabaseManager(Manager):
    db = Instance(IsotopeAdapter)
    def __init__(self, *args, **kw):
        super(DatabaseManager, self).__init__(*args, **kw)
        if self.application:
            self.bind_preferences()

    def bind_preferences(self):
        try:
#            bind_preference(self, 'username', 'envisage.ui.workbench.username')
            bind_preference(self.db, 'save_username', 'envisage.ui.workbench.username')
            prefid = 'pychron.experiment'
            bind_preference(self.db, 'kind', '{}.db_kind'.format(prefid))
            if self.db.kind == 'mysql':
                bind_preference(self.db, 'host', '{}.db_host'.format(prefid))
                bind_preference(self.db, 'username', '{}.db_username'.format(prefid))
                bind_preference(self.db, 'password', '{}.db_password'.format(prefid))

            bind_preference(self.db, 'name', '{}.db_name'.format(prefid))
        except (AttributeError, NameError):
            pass

    def _db_factory(self):
        db = IsotopeAdapter(username='massspec',
                            password='DBArgon',
                            kind='mysql',
                            name='isotopedb_dev',
                            host='129.138.12.131'
                            )
        db = IsotopeAdapter(username='root',
                            password='Argon',
                            kind='mysql',
                            name='isotopedb_dev',
                            application=self.application
                            )

        return db

    def _db_default(self):
        db = self._db_factory()
        return db

#============= EOF =============================================
