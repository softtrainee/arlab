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
from traits.api import String, Float, Enum, Str
from traitsui.api import Item, HGroup, VGroup
#============= standard library imports ========================
import os
from numpy import linspace, polyval, polyfit
#============= local library imports  ==========================
from src.database.selectors.db_selector import DBSelector
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.database.orms.power_calibration_orm import PowerCalibrationTable
from src.database.selectors.base_db_result import DBResult

FITDEGREE = dict(Linear=1, Parabolic=2, Cubic=3)
class PowerCalibrationResult(DBResult):
    title_str = 'PowerCalibrationRecord'
    request_power = Float
    exportable = True
    fit = Enum('Linear', 'Parabolic', 'Cubic')
    coeffs = Str

    def _fit_changed(self):
        g = self.graph
        x = g.get_data()
        y = g.get_data(axis=1)

        coeffs, x, y = self._calculate_fit(x, y)
        self._set_coeffs(coeffs)

        g.set_data(x, series=1)
        g.set_data(y, series=1, axis=1)
        g.redraw()

    def _get_graph_item(self):
        g = super(PowerCalibrationResult, self)._get_graph_item()
#        g.height = 1.0
#        g.springy = True
        return VGroup(
                         HGroup(Item('fit', show_label=False),
                             Item('coeffs', style='readonly'),
#                             spring
                             ),
                      g,
#                      springy=True,
#                      label='Graph'
                      )

    def _calculate_fit(self, x, y, deg=None):
        if deg is None:
            deg = FITDEGREE[self.fit]

        rxi = linspace(min(x), max(x), 500)
        coeffs = polyfit(x, y, deg)
        ryi = polyval(coeffs, rxi)

        return coeffs, rxi, ryi

    def load_graph(self, *args, **kw):

        g = self._graph_factory()
        dm = self.data_manager
        calibration = dm.get_table('calibration', '/')
        g.new_plot(xtitle='Setpoint (%)',
                   ytitle='Measured Power (W)',
                   padding=[50, 10, 10, 40]
                   )

        xi, yi = zip(*[(r['setpoint'], r['value']) for r in calibration.iterrows()])
        g.new_series(xi, yi)

        coeffs, rxi, ryi = self._calculate_fit(xi, yi)
        self._set_coeffs(coeffs)
        g.new_series(rxi, ryi)

#        self.summary = 'coeffs ={}'.format(', '.join(['{:0.3f}'.format(c) for c in coeffs]))

        self.graph = g

    def _set_coeffs(self, coeffs):
        alpha = 'abcde'
        self.coeffs = ', '.join(['{}={:0.3f}'.format(a, c) for a, c in zip(alpha, coeffs)])

    def _load_hook(self, dbr):
        data = os.path.join(self.directory, self.filename)
        dm = H5DataManager()
        if os.path.isfile(data):
            dm.open_data(data)

        self.data_manager = dm


class PowerCalibrationSelector(DBSelector):
    parameter = String('PowerCalibrationTable.rundate')
    query_table = PowerCalibrationTable
    result_klass = PowerCalibrationResult

    def _get_selector_records(self, **kw):
        return self._db.get_calibration_records(**kw)

#============= EOF =============================================
