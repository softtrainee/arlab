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



#from traits.api import HasTraits, Str, String, Button, List, Any, Long, Event, \
#    Date, Time, Instance, Dict, DelegatesTo, Property
#from traitsui.api import View, Item, TabularEditor, EnumEditor, \
#    HGroup, VGroup, Group, spring
#from traitsui.tabular_adapter import TabularAdapter
#
#from datetime import datetime, timedelta
#import os

from .database_adapter import DatabaseAdapter
from src.database.selectors.power_map_selector import PowerMapSelector
from src.database.orms.power_map_orm import PowerMapTable, PowerMapPathTable
#from src.database.selectors.bakeout_selector import BakeoutDBSelector
#from src.helpers.datetime_tools import  get_date
#from src.loggable import Loggable
#from src.bakeout.bakeout_graph_viewer import BakeoutGraphViewer



class PowerMapAdapter(DatabaseAdapter):
    test_func = None
    selector_klass = PowerMapSelector
    path_table = PowerMapPathTable
#==============================================================================
#    getters
#==============================================================================

    def get_powermaps(self, join_table=None, filter_str=None):
        try:
            if isinstance(join_table, str):
                join_table = globals()[join_table]

            q = self._get_query(PowerMapTable, join_table=join_table,
                                 filter_str=filter_str)
            return q.all()
        except Exception, e:
            print e

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


#======== EOF ================================

