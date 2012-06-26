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
#============= standard library imports ========================
#============= local library imports  ==========================
from src.database.adapters.database_adapter import PathDatabaseAdapter
from src.database.orms.bakeout_orm import BakeoutTable, ControllerTable, BakeoutPathTable
from src.database.selectors.bakeout_selector import BakeoutDBSelector
from src.paths import paths


class BakeoutAdapter(PathDatabaseAdapter):
    test_func = None
    selector_klass = BakeoutDBSelector
    path_table = BakeoutPathTable
#==============================================================================
#    getters
#==============================================================================

    def get_bakeouts(self, **kw):
        return self._get_items(BakeoutTable, globals(), **kw)
#=============================================================================
#   adder
#=============================================================================
    def add_bakeout(self, commit=False, **kw):
        b = self._add_timestamped_item(BakeoutTable, commit, **kw)
        return b

    def add_controller(self, bakeout, commit=False, **kw):
        c = ControllerTable(**kw)
        bakeout.controllers.append(c)
        if commit:
            self.commit()
        return c


if __name__ == '__main__':
    db = BakeoutAdapter(dbname=paths.bakeout_db,
                            kind='sqlite')
    db.connect()

    dbs = BakeoutDBSelector(_db=db)
    dbs.load_recent()
    dbs.configure_traits()
#    print db.get_bakeouts(join_table='ControllerTable',
#                    filter_str='ControllerTable.script="---"'
#                    )


#============= EOF =============================================
