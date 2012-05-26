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
from numpy import linspace, polyval, polyfit
#============= local library imports  ==========================
from src.database.selectors.db_selector import DBSelector, DBResult
from src.graph.graph import Graph
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.database.orms.power_calibration_orm import PowerCalibrationTable

class PowerCalibrationResult(DBResult):
    title_str = 'PowerCalibrationRecord'
    request_power = Float
    exportable = False

    def load_graph(self):

        g = Graph()
        dm = self.data_manager
        calibration = dm.get_table('calibration', '/')
        g.new_plot(xtitle='Setpoint (%)',
                   ytitle='Measured Power (W)'
                   )

        xi, yi = zip(*[(r['setpoint'], r['value']) for r in calibration.iterrows()])
        g.new_series(xi, yi)

        rxi = linspace(min(xi), max(xi), 500)
        coeffs = polyfit(xi, yi, 1)
        ryi = polyval(coeffs, rxi)

        g.new_series(rxi, ryi)

        self.summary = 'coeffs ={}'.format(', '.join(['{:0.3f}'.format(c) for c in coeffs]))

        self.graph = g

    def _load_hook(self, dbr):
        data = os.path.join(self.directory, self.filename)
        dm = H5DataManager()
        if os.path.isfile(data):
            dm.open_data(data)

        self.data_manager = dm


class PowerCalibrationSelector(DBSelector):
    parameter = String('PowerCalibrationTable.rundate')
    date_str = 'rundate'
    query_table = 'PowerCalibrationTable'
    result_klass = PowerCalibrationResult

    def _get__parameters(self):

        b = PowerCalibrationTable

        f = lambda x:[str(col)
                           for col in x.__table__.columns]
        params = f(b)
        return list(params)

    def _get_selector_records(self, **kw):
        return self._db.get_calibration_records(**kw)

#============= EOF =============================================
