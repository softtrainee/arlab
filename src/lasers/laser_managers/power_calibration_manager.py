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
from traits.api import HasTraits, Float, Instance, Int, Event, Property, Bool
from traitsui.api import View, Item
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
from numpy import polyfit

#============= local library imports  ==========================
from src.managers.manager import Manager
from src.helpers.paths import hidden_dir, co2laser_db_root, co2laser_db
import os
import time
from src.graph.graph import Graph
from threading import Thread
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.database.data_warehouse import DataWarehouse
from src.database.adapters.power_calibration_adapter import PowerCalibrationAdapter

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

    view = View(
              Item('pstart', label='Start'),
              Item('pstop', label='Stop'),
              Item('pstep', label='Step'),
              Item('sample_delay'),
              Item('integration_period'),
              Item('nintegrations'),
              Item('use_db')

              )

class PowerCalibrationManager(Manager):
    parameters = Instance(Parameters)

    execute = Event
    execute_label = Property(depends_on='_alive')
    _alive = Bool(False)
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

        print pa
        if pa is None:
            pa = Parameters()

        return pa

    def _execute_fired(self):
        if self._alive:
            self._alive = False

            self._end(True)

        else:
            self._alive = True
    #        self.graph.edit_traits()
            t = Thread(target=self._execute_power_calibration)
            t.start()
    #        self._execute_power_calibration()

    def _execute_power_calibration(self):
        self.graph = g = Graph(window_title='CO2 Power Calibration')
        g.new_plot()
        g.new_series()
        g.show()

        pstop = self.parameters.pstop
        pstep = self.parameters.pstep
        pstart = self.parameters.pstart
        sample_delay = self.parameters.sample_delay
        integration_period = self.parameters.integration_period
        nintegrations = self.parameters.nintegrations

        self.data_manager = dm = H5DataManager()

        dw = DataWarehouse(root=os.path.join(co2laser_db_root, 'power_calibration'))
#                           os.path.join(data_dir, base_dir))
        dw.build_warehouse()

        _dn = dm.new_frame(directory=dw.get_current_dir(),
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
                self.parent.set_laser_power(pi)

            time.sleep(sample_delay)
            rp = 0
            for _ in range(nintegrations):
                if not self._alive:
                    break
                rp += apm.read_power_meter(pi)
                time.sleep(integration_period)

            if not self._alive:
                break

            self._write_data(pi, rp / float(nintegrations), table)

        self._calculate_calibration()

        self._end(False)

    def _end(self, user_kill):
        if self.parameters.use_db:
            save_to_db = True
            if user_kill:
                save_to_db = self.confirmation_dialog('Save to Database')

            if save_to_db:
                db = PowerCalibrationAdapter(dbname=co2laser_db,
                                             kind='sqlite')
                db.connect()
                r = db.add_calibration_record()
                p = self.data_manager.get_current_path()
                db.add_calibration_path(r, p)
                db.commit()
                db.close()

            else:
                self.data_manager.delete_frame()

        self.data_manager.close()
        self._alive = False

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

        print polyfit(xs, ys, 1)

    def kill(self):
        super(PowerCalibrationManager, self).kill()
        p = os.path.join(hidden_dir, 'power_calibration')
        with open(p, 'wb') as f:
            pickle.dump(self.parameters, f)


    def traits_view(self):
        v = View(self._button_factory('execute'),
                 Item('parameters', show_label=False, style='custom'),
                 handler=self.handler_klass

                 )
        return v

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('pcm')
    p = PowerCalibrationManager()
    p.configure_traits()
#============= EOF =============================================
