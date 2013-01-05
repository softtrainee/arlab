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
from traits.api import HasTraits, Property, cached_property
#from traitsui.api import View, Item, TableEditor
from src.database.records.database_record import DatabaseRecord
#============= standard library imports ========================
import os
#============= local library imports  ==========================

class SQLiteRecord(DatabaseRecord):
    path = Property

    @cached_property
    def _get_path(self):
        if self.dbrecord.path:
            root = self.dbrecord.path.root
            name = self.dbrecord.path.filename
            return os.path.join(root, name)
#============= EOF =============================================
