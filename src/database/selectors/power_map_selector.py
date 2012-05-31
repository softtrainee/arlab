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
from traits.api import String
#============= standard library imports ========================
import os
import csv
#============= local library imports  ==========================
from .db_selector import DBSelector
from src.database.orms.power_map_orm import PowerMapTable
from src.database.selectors.base_db_result import DBResult


class PowerMapResult(DBResult):
    title_str = 'PowerMap'
    resizable = False
    def load_graph(self, *args, **kw):
        data = os.path.join(self.directory, self.filename)
        from src.data_processing.power_mapping.power_map_processor import PowerMapProcessor
        pmp = PowerMapProcessor()
        if data.endswith('.h5'):
            reader = self._data_manager_factory()
            reader.open_data(data)
        else:
            with open(data, 'r') as f:
                reader = csv.reader(f)
                #trim off header
                reader.next()
        self.graph = pmp.load_graph(reader)
        self.graph.width = 625
        self.graph.height = 500


class PowerMapSelector(DBSelector):
    parameter = String('PowerMapTable.rundate')

    result_klass = PowerMapResult
    query_table = PowerMapTable


    def _get_selector_records(self, **kw):
        return self._db.get_powermaps(**kw)

#============= EOF =============================================
