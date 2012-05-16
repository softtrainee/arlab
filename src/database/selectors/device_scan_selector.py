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
#============= local library imports  ==========================
from src.database.selectors.db_selector import DBSelector, DBResult
from src.database.orms.device_scan_orm import ScanTable

from src.graph.time_series_graph import TimeSeriesGraph

class ScanResult(DBResult):
    title_str = 'Device Scan Record'
    request_power = Float

    def load_graph(self):

        g = TimeSeriesGraph()
        dm = self._data_manager_factory()

        g.new_plot()

        s1 = dm.get_table('scan1', 'scans')
        xi, yi = zip(*[(r['time'], r['value']) for r in s1.iterrows()])
        g.new_series(xi, yi)

        self.graph = g

    def _load_hook(self, dbr):
        #load the datamanager to set _none_loadable flag
        self._data_manager_factory()

class DeviceScanSelector(DBSelector):
    parameter = String('ScanTable.rundate')
    date_str = 'rundate'
    query_table = 'ScanTable'
    result_klass = ScanResult

    def _get__parameters(self):

        b = ScanTable

        f = lambda x:[str(col)
                           for col in x.__table__.columns]
        params = f(b)
        return list(params)

    def _get_selector_records(self, **kw):
        return self._db.get_scans(**kw)


#============= EOF =============================================