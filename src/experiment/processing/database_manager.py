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
from src.database.adapters.isotope_adapter import IsotopeAdapter
from src.loggable import Loggable
from src.managers.manager import Manager
#============= standard library imports ========================
#============= local library imports  ==========================
class DatabaseManager(Manager):
    db = Instance(IsotopeAdapter)
    def _db_factory(self):
        db = IsotopeAdapter(username='root',
                            password='Argon',
                            kind='mysql',
                            name='isotopedb_dev'
                            )

        return db
    def _db_default(self):
        db = self._db_factory()
        return db

#============= EOF =============================================
