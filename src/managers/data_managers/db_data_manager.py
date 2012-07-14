#===============================================================================
# Copyright 2011 Jake Ross
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
from traits.api import Instance, Button
from traitsui.api import View, Item
from src.managers.manager import Manager

#============= standard library imports ========================

#============= local library imports  ==========================
from src.database.core.database_adapter import DatabaseAdapter
class DBDataManager(Manager):
    database = Instance(DatabaseAdapter)

    #host = DelegatesTo('database')
    #dbname = DelegatesTo('database')
    #password = DelegatesTo('database')
    #user = DelegatesTo('database')
    #kind = DelegatesTo('database')
    #connected = DelegatesTo('database')
    #use_db = DelegatesTo('database')
    importbutton = Button('Import')
    def _importbutton_fired(self):
        self._import_()

    def _import_(self):
        pass


    def traits_view(self):

        v = View(Item('importbutton', show_label=False),
                 Item('database', style='custom', show_label=False)
                 )
        return v



#============= EOF ====================================
