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

#============= standard library imports ========================
#============= local library imports  ==========================

from src.database.selectors.power_map_selector import PowerMapSelector
from src.database.orms.power_map_orm import PowerMapTable, PowerMapPathTable
from src.database.adapters.database_adapter import DatabaseAdapter


class PowerMapAdapter(DatabaseAdapter):
    test_func = None
    selector_klass = PowerMapSelector
    path_table = PowerMapPathTable
#==============================================================================
#    getters
#==============================================================================

    def get_powermaps(self, **kw):
        return self._get_items(PowerMapTable, globals(), **kw)

#=============================================================================
#   adder
#=============================================================================
    def add_powermap(self, commit=False, **kw):
#        b = PowerMapTable(**kw)
        b = self._add_timestamped_item(PowerMapTable, commit, **kw)
        return b

if __name__ == '__main__':
    db = PowerMapAdapter(dbname='co2laserdb',
                            password='Argon')
    db.connect()

    dbs = PowerMapSelector(_db=db)
    dbs.load_recent()
#    dbs._execute_()
    dbs.configure_traits()
#    print db.get_bakeouts(join_table='ControllerTable',
#                    filter_str='ControllerTable.script="---"'
#                    )


#============= EOF =============================================
