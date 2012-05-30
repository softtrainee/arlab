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
from traits.api import HasTraits, Float, Button, Instance, Int, \
     Event, Property, Bool, Any, Enum, on_trait_change, List
from traitsui.api import View, Item, VGroup
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
from numpy import polyfit, linspace, polyval

#============= local library imports  ==========================
from src.managers.manager import Manager
from src.helpers.paths import hidden_dir, co2laser_db_root, co2laser_db, \
    data_dir
import os
import time
from src.graph.graph import Graph
from threading import Thread
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.database.data_warehouse import DataWarehouse
#from src.database.adapters.power_calibration_adapter import PowerCalibrationAdapter
from pyface.timer.do_later import do_later

FITDEGREES = dict(Linear=1, Parabolic=2, Cubic=3)

class PowerCalibrationObject(object):
    coefficients = None

class DummyPowerMeter:
    def read_power_meter(self, setpoint):
        import random
        return setpoint + random.randint(0, 5)

class Parameters(HasTraits):
    pstart = Float(0)
    pstop = Float(100)
    pstep = Float(1)

    sample_delay = Float(1)
    integration_period = Float(1)
    nintegrations = Int(5)
    use_db = Bool(True)
    fit_degree = Enum('Linear', 'Parabolic', 'Cubic')
    view = View(
              Item('pstart', label='Start'),
              Item('pstop', label='Stop'),
              Item('pstep', label='Step'),
              Item('sample_delay'),
              Item('integration_period'),
              Item('nintegrations'),
              Item('fit_degree', label='Fit'),
              Item('use_db')

              )

class PowerCalibrationManager(Manager):
    parameters = Instance(Parameters)

    execute = Event
    execute_label = Property(depends_on='_alive')
    _alive = Bool(False)
    data_manager = None
    graph = None
    db = Any
    coefficients = Property(depends_on='_coefficients')
    _coefficients = List
    save = Button
    def __coefficients_default(self):
        r = []
        if self.parent:
            pc = self.parent.load_power_calibration()
            if pc:
                r = list(pc.coefficients)

        return r

    def _save_fired(self):
        pc = PowerCalibrationObject()
        pc.coefficients = self._coefficients
        self._dump_calibration(pc)

    def _get_coefficients(self):
        return ','.join(['{:0.2f}'.format(c) for c in self._coefficients]) if self._coefficients else ''

    def _validate_coefficients(self, v):
        try:
            return map(float, [c for c in v.split(',')])

        except (ValueError, AttributeError):
            pass

    def _set_coefficients(self, v):
        self._coefficients = v

    def _get_execute_label(self):
        return 'Stop' if self._alive else 'Start'

    def _parameters_default(self):
        return self._load_parameters()

    def _load_parameters(self):
        p = os.path.join(hidden_dir, 'power_calibration')
        pa = None
        if os.path.isfile(p):
            with open(p, 'rb') as f:
                try:
                    pa = pickle.load(f)
                except pickle.PickleError:
                    pass

        if pa is None:
            pa = Parameters()

        return pa

    def _apply_calibration(self):

        if self.confirmation_dialog('Apply Calibration'):
            pc = PowerCalibrationObject()
            pc.coefficients = self._calculate_calibration()
            self._dump_calibration(pc)

    def _dump_calibration(self, pc):
        name = self.parent.name if self.parent else 'foo'
        p = os.path.join(hidden_dir, '{}_power_calibration'.format(name))
        self.info('saving power calibration to {}'.format(p))
        try:
            with open(p, 'wb') as f:
                pickle.dump(pc, f)

        except pickle.PickleError:
            pass

    def _execute_fired(self):
        if self._alive:

            self._alive = False
            if self.parameters.use_db:
                if self.confirmation_dialog('Save to Database'):
                    self._save_to_db()
                    return
                else:
                    self.data_manager.delete_frame()
                    self.data_manager.close()

                self._apply_calibration()

        else:
            self._alive = True
            t = Thread(target=self._execute_power_calibration)
            t.start()

    def _open_graph(self):
        ui = self.graph.edit_traits()
        self.parent.add_window(ui)

    def _execute_power_calibration(self):
        self.graph = g = Graph(window_title='CO2 Power Calibration',
                               container_dict=dict(padding=5)
                               )
        g.new_plot(
                   xtitle='Setpoint (%)',
                   ytitle='Measured Power (W)')
        g.new_series()

        if self.parent is not None:
            do_later(self._open_graph)


        pstop = self.parameters.pstop
        pstep = self.parameters.pstep
        pstart = self.parameters.pstart
        sample_delay = self.parameters.sample_delay
        integration_period = self.parameters.integration_period
        nintegrations = self.parameters.nintegrations

        self.data_manager = dm = H5DataManager()
        if self.parameters.use_db:
            dw = DataWarehouse(root=os.path.join(self.parent.db_root, 'power_calibration'))
            dw.build_warehouse()
            directory = dw.get_current_dir()
        else:
            directory = os.path.join(data_dir, 'power_calibration')

        _dn = dm.new_frame(directory=directory,
                base_frame_name='power_calibration')

        table = dm.new_table('/', 'calibration', table_style='PowerCalibration')

        dev = abs(pstop - pstart)
        sign = 1 if pstart < pstop else -1
        if sign == 1:
            self.graph.set_x_limits(pstart, pstop)
        else:
            self.graph.set_x_limits(pstop, pstart)

        nsteps = int((dev + pstep) / pstep)
        if self.parent is not None:
            apm = self.parent.get_device('analog_power_meter')
        else:
            apm = DummyPowerMeter()

        for i in range(nsteps):
            if not self._alive:
                break

            pi = pstart + sign * i * pstep
            self.info('setting power to {}'.format(pi))
            if self.parent is not None:
                self.parent.set_laser_power(pi, calibration=True)

            time.sleep(sample_delay)
            rp = 0
            for _ in range(nintegrations):
                if not self._alive:
                    break
                if apm is not None:
                    rp += apm.read_power_meter(pi)
                else:
                    rp += 1

                time.sleep(integration_period)

            if not self._alive:
                break

            self._write_data(pi, rp / float(nintegrations), table)

        self._calculate_calibration()
        self._apply_fit()

        if self._alive:
            self._alive = False
            self._save_to_db()
            self._apply_calibration()

    def __alive_changed(self):
        if not self._alive:
            if self.parent is not None:
                self.parent.disable_laser()

    def _save_to_db(self):
        if self.parameters.use_db:
#            db = PowerCalibrationAdapter(dbname=co2laser_db,
#                                         kind='sqlite')
            db = self.db
            db.connect()
            r = db.add_calibration_record()
            db.add_path(r, self.data_manager.get_current_path())
            db.commit()
            db.close()
        self.data_manager.close()

    def _write_data(self, pi, rp, table):
        self.graph.add_datum((pi, rp), do_after=1)

        row = table.row
        row['setpoint'] = pi
        row['value'] = rp
        row.append()
        table.flush()

    def _calculate_calibration(self):
        xs = self.graph.get_data()
        ys = self.graph.get_data(axis=1)

        deg = FITDEGREES[self.parameters.fit_degree]

        coeffs = polyfit(xs, ys, deg)
        self._coefficients = list(coeffs)

    def _apply_fit(self, new=True):
        xs = self.graph.get_data()

        x = linspace(min(xs), max(xs), 500)
        y = polyval(self._coefficients, x)
        g = self.graph
        if new:
            g.new_series(x, y)
        else:
            g.set_data(x, series=1)
            g.set_data(y, series=1, axis=1)
            g.redraw()

    @on_trait_change('parameters:fit_degree')
    def update_graph(self):
        self._calculate_calibration()
        self._apply_fit(new=False)

    def kill(self):
        super(PowerCalibrationManager, self).kill()
        if self.initialized:
            with open(os.path.join(hidden_dir, 'power_calibration'),
                      'wb') as f:
                pickle.dump(self.parameters, f)

    def traits_view(self):
        v = View(self._button_factory('execute'),
                 Item('parameters', show_label=False, style='custom'),
                 VGroup(Item('coefficients'),
                        Item('save', show_label=False),
                        show_border=True,
                        label='Set Calibration'
                        ),

                 handler=self.handler_klass,
                 title='Power Calibration',
                 id='pychron.power_calibration_manager',
                 resizable=True
                 )
        return v

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('pcm')
    pac = PowerCalibrationManager()
    pac.configure_traits()
#============= EOF =============================================
