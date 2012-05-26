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
from traits.api import String, Float
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.database.selectors.db_selector import DBSelector
from src.database.orms.power_orm import PowerTable
from src.graph.graph import Graph
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.database.selectors.base_db_result import RIDDBResult
from src.database.selectors.base_results_adapter import RIDResultsAdapter


class PowerResult(RIDDBResult):
    title_str = 'PowerRecord'
    request_power = Float

    def load_graph(self):

        g = Graph()
        dm = self.data_manager
        internal = dm.get_table('internal', 'Power')
        brightness = dm.get_table('brightness', 'Power')
        g.new_plot()
        if internal is not None:
            xi, yi = zip(*[(r['time'], r['value']) for r in internal.iterrows()])
            g.new_series(xi, yi)
        if brightness is not None:
            xb, yb = zip(*[(r['time'], r['value']) for r in brightness.iterrows()])
            g.new_series(xb, yb)

        self.graph = g

    def _load_hook(self, dbr):
        data = os.path.join(self.directory, self.filename)
        dm = H5DataManager()
        if os.path.isfile(data):
            dm.open_data(data)

            tab = dm.get_table('internal', 'Power')
            if tab is not None:
                if hasattr(tab.attrs, 'request_power'):
                    self.summary = 'request power ={}'.format(tab.attrs.request_power)
            self.runid = str(dbr.rid)

        self.data_manager = dm

class PowerSelector(DBSelector):
    parameter = String('PowerTable.rundate')
    date_str = 'rundate'
    query_table = 'PowerTable'
    result_klass = PowerResult
    tabular_adapter = RIDResultsAdapter
    def _get__parameters(self):

        b = PowerTable

        f = lambda x:[str(col)
                           for col in x.__table__.columns]
        params = f(b)
        return list(params)

    def _get_selector_records(self, **kw):
        return self._db.get_power_records(**kw)


#============= EOF =============================================
