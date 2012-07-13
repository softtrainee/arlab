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
from traits.api import String, Float, Bool, Int
from traitsui.api import VGroup, HGroup, Item
#============= standard library imports ========================
from numpy import array
#============= local library imports  ==========================
from src.database.selectors.db_selector import DBSelector
from src.database.orms.device_scan_orm import ScanTable
from src.graph.time_series_graph import TimeSeriesGraph
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.database.selectors.base_db_result import DBResult


class ScanResult(DBResult):
    title_str = 'Device Scan Record'
    request_power = Float
    downsample = Int(0)
    def _get_graph_item(self):
        g = super(ScanResult, self)._get_graph_item()
#        g.height = 1.0
#        g.springy = True
        return VGroup(
                         HGroup(Item('downsample'),
#                             Item('coeffs', style='readonly'),
#                             spring
                             ),
                      g,
#                      springy=True,
#                      label='Graph'
                      )

    def _downsample_changed(self):
        g = self.graph
        x, y = self._get_data()
        g.downsample(x, y, max(1, self.downsample))


    def load_graph(self, graph=None, xoffset=0):

        if graph is None:
            graph = self._graph_factory(klass=TimeSeriesGraph)
            graph.new_plot(xtitle='Time',
                       ytitle='Value',
                       padding=[40, 10, 10, 40]
                       )

        xi, yi = self._get_data()
        if xi is not None:
            graph.new_series(array(xi) + xoffset, yi)

        self.graph = graph

        return max(xi)

    def _get_data(self):
        dm = self._data_manager_factory()
        dm.open_data(self._get_path())
        xi = None
        yi = None
        if isinstance(dm, H5DataManager):
            s1 = dm.get_table('scan1', 'scans')
            if s1 is not None:
                xi, yi = zip(*[(r['time'], r['value']) for r in s1.iterrows()])
            else:
                self._loadable = False
        else:
            da = dm.read_data()
            if da is not None:
                xi, yi = da
        return xi, yi
#    def _load_hook(self, dbr):
#        #load the datamanager to set _none_loadable flag
#        self._data_manager_factory()

class DeviceScanSelector(DBSelector):
    parameter = String('ScanTable.rundate')
    query_table = ScanTable
    result_klass = ScanResult
    join_table_col = String('name')
    join_table = String('DeviceTable')
    multi_graphable = Bool(True)

    def _load_hook(self):
        jt = self._join_table_parameters
        if jt:
            self.join_table_parameter = str(jt[0])

    def _get_selector_records(self, **kw):
        return self._db.get_scans(**kw)

    def _get__join_table_parameters(self):
        dv = self._db.get_devices()
        return list(set([di.name for di in dv if di.name is not None]))



#        f = lambda x:[str(col)
#                           for col in x.__table__.columns]
#        params = f(b)
#        return list(params)
#        return

#============= EOF =============================================
