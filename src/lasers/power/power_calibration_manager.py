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
from traitsui.api import View, Item, VGroup, Group
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
from numpy import polyfit, linspace, polyval, poly1d
from scipy import optimize
from threading import Event as TEvent
from threading import Thread
#============= local library imports  ==========================
from src.managers.manager import Manager
from src.paths import paths
import os
import time
from src.graph.graph import Graph
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.database.data_warehouse import DataWarehouse
#from src.database.adapters.power_calibration_adapter import PowerCalibrationAdapter
from pyface.timer.do_later import do_later
from src.hardware.analog_power_meter import AnalogPowerMeter
import random

FITDEGREES = dict(Linear=1, Parabolic=2, Cubic=3)

class PowerCalibrationObject(object):
    coefficients = None
    bounds = None

    def get_calibrated_power(self, rp):
        if self.bounds:
            for c, b in zip(self.coefficients, self.bounds):
                if b[0] < rp <= b[1]:
                    break
            else:
                closest = 0
                min_d = 1000
                for i, b in enumerate(self.bounds):
                    d = min(abs(b[0] - rp), abs(b[1] - rp))
                    if d < min_d:
                        closest = i
                c = self.coefficients[closest]
        else:
            c = self.coefficients

        #say y=ax+b (watts=a*power_percent+b)
        #calculate x for a given y
        #solvers solve x for y=0
        #we want x for y=power, therefore
        #subtract the requested power from the intercept coeff (b)
        #find the root of the polynominal

        if c is not None and len(c):
            c[-1] -= rp
            power = optimize.newton(poly1d(c), 1)
            c[-1] += rp
        else:
            power = rp
        return power, c


#class DummyPowerMeter:
#    def read_power_meter(self, setpoint):
#        import random
#        return setpoint + random.randint(0, 5)

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
              Item('use_db'),
              )

class PowerCalibrationManager(Manager):
    parameters = Instance(Parameters)
    check_parameters = Instance(Parameters)

    execute = Event
    execute_check = Event
    execute_check_label = Property(depends_on='_check_alive')
    _check_alive = Bool(False)

    execute_label = Property(depends_on='_alive')
    _alive = Bool(False)
    data_manager = None
    graph = None
    db = Any
    coefficients = Property(depends_on='_coefficients')
    _coefficients = List
    save = Button

    power_meter = Instance(AnalogPowerMeter)
#    def configure_power_meter_fired(self):
#        if self.parent is not None:
#            apm = self.parent.get_device('analog_power_meter')
#            apm.edit_traits(kind='modal')
    graph_cnt = 0
    def _execute_power_calibration_check(self):
        '''
        
        '''
        g = Graph()
        g.new_plot()
        g.new_series()
        g.new_series(x=[0, 100], y=[0, 100], line_style='dash')
        do_later(self._open_graph, graph=g)

        self._stop_signal = TEvent()
        callback = lambda pi, r: None
        self._iterate(self.check_parameters,
                      g, False, callback)

    def _execute_power_calibration(self):
        gc = self.graph_cnt
        cnt = '' if not gc else gc
        self.graph_cnt += 1

        name = self.parent.name if self.parent else 'Foo'

        self.graph = g = Graph(window_title='{} Power Calibration {}'.format(name, cnt),
                               container_dict=dict(padding=5),
                               window_x=500 + gc * 25,
                               window_y=25 + gc * 25
                               )
        g.new_plot(
                   xtitle='Setpoint (%)',
                   ytitle='Measured Power (W)')
        g.new_series()

        if self.parent is not None:
            do_later(self._open_graph)

        self.data_manager = dm = H5DataManager()
        if self.parameters.use_db:
            dw = DataWarehouse(root=os.path.join(self.parent.db_root, 'power_calibration'))
            dw.build_warehouse()
            directory = dw.get_current_dir()
        else:
            directory = os.path.join(paths.data_dir, 'power_calibration')

        _dn = dm.new_frame(directory=directory,
                base_frame_name='power_calibration')

        table = dm.new_table('/', 'calibration', table_style='PowerCalibration')
        callback = lambda p, r, t: self._write_data(p, r, t)
        self._stop_signal = TEvent()
        self._iterate(self.parameters,
                      self.graph, True,
                      callback, table)

        self._calculate_calibration()
        self._apply_fit()

        if self._alive:
            self._alive = False
            self._save_to_db()
            self._apply_calibration()

    def _iterate(self, params, graph,
                 is_calibrating, callback, *args):
        pstop = params.pstop
        pstep = params.pstep
        pstart = params.pstart
        sample_delay = params.sample_delay
        integration_period = params.integration_period
        nintegrations = params.nintegrations

        dev = abs(pstop - pstart)
        sign = 1 if pstart < pstop else -1
        if sign == 1:
            graph.set_x_limits(pstart, pstop)
        else:
            graph.set_x_limits(pstop, pstart)

        apm = self.power_meter
#        if self.parent is not None:
#            apm = self.parent.get_device('analog_power_meter')
#        else:
#            apm = DummyPowerMeter()
        if self.parent is not None:
            self.parent.enable_laser()

        nsteps = int((dev + pstep) / pstep)
        for i in range(nsteps):
#            if not self._alive:
#                break
            if self._stop_signal.isSet():
                break

            pi = pstart + sign * i * pstep
            self.info('setting power to {}'.format(pi))
            time.sleep(sample_delay)
            if self.parent is not None:
                self.parent.set_laser_power(pi, use_calibration=not is_calibrating)
                if not is_calibrating:
                    pi = self.parent._calibrated_power

                rp = 0
                for _ in range(nintegrations):
    #                if not self._alive:
    #                    break
                    if self._stop_signal.isSet():
                        break

                    if apm is not None:
                        rp += apm.read_power_meter(pi)

                    time.sleep(integration_period)
            else:
                n = 10
                rp = pi + n * random.random() - n / 2

#            if not self._alive:
#                break
            if self._stop_signal.isSet():
                break

            graph.add_datum((pi, rp), do_after=1)
            callback(pi, rp / float(nintegrations), *args)


            #calculate slope and intercept of data

        x = graph.get_data()
        y = graph.get_data(axis=1)
        coeffs = polyfit(x, y, 1)


#            self._write_data(pi, , table)


    def _get_parameters_path(self, name):
        p = os.path.join(paths.hidden_dir, 'power_calibration_{}'.format(name))
        return p

    def _load_parameters(self, p):
        pa = None
        if os.path.isfile(p):
            with open(p, 'rb') as f:
                try:
                    pa = pickle.load(f)
                except (pickle.PickleError, EOFError):
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
        p = os.path.join(paths.hidden_dir, '{}_power_calibration'.format(name))
        self.info('saving power calibration to {}'.format(p))
        try:
            with open(p, 'wb') as f:
                pickle.dump(pc, f)

        except pickle.PickleError:
            pass

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
        return self._coefficients

    def _open_graph(self, graph=None):
        if graph is None:
            graph = self.graph

        ui = graph.edit_traits()
        if self.parent:
            self.parent.add_window(ui)

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
#===============================================================================
# handlers
#===============================================================================
    @on_trait_change('parameters:fit_degree')
    def update_graph(self):
        self._calculate_calibration()
        self._apply_fit(new=False)

    def __alive_changed(self):
        if not self._alive:
            if self.parent is not None:
                self.parent.disable_laser()

    def _save_fired(self):
        pc = PowerCalibrationObject()
        pc.coefficients = self._coefficients
        self._dump_calibration(pc)

    def _execute_check_fired(self):
        if self._check_alive:
            self._stop_signal.set()
            self._check_alive = False
        else:
            self._check_alive = True
            t = Thread(target=self._execute_power_calibration_check)
            t.start()

    def _execute_fired(self):
        if self._alive:
            self._stop_signal.set()
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

    def kill(self):
        super(PowerCalibrationManager, self).kill()
        if self.initialized:
            for n in ['parameters', 'check_parameters']:
                with open(self._get_parameters_path(n),
                          'wb') as f:
                    pickle.dump(getattr(self, n), f)
#            with open(self._get_parameters_path('parameters'),
#                      'wb') as f:
#                pickle.dump(self.check_parameters, f)

    def traits_view(self):

        self.graph_cnt = 0

        v = View(
                 VGroup(

                        Group(
                                Group(
                                      self._button_factory('execute', align='right'),
                                      Item('parameters', show_label=False, style='custom'),
                                      label='Calculate'
                                      ),
                                Group(
                                      self._button_factory('execute_check', align='right'),
                                      Item('check_parameters', show_label=False, style='custom'),
                                      label='Check'
                                      ),
                                layout='tabbed',
                                show_border=True,
                                label='Setup'
                                ),
                 VGroup(Item('coefficients'),
                        self._button_factory('save', align='right'),
                        show_border=True,
                        label='Set Calibration'
                        ),
                 VGroup(
                        Item('power_meter', style='custom', show_label=False),
                            show_border=True,
                            label='Power Meter')
                 ),

                 handler=self.handler_klass,
                 title='Power Calibration',
                 id='pychron.power_calibration_manager',
                 resizable=True
                 )
        return v

    def _get_execute_label(self):
        return 'Stop' if self._alive else 'Start'

    def _get_execute_check_label(self):
        return 'Stop' if self._alive else 'Start'

    def _get_coefficients(self):
        return ','.join(['{:0.2f}'.format(c) for c in self._coefficients]) if self._coefficients else ''

    def _validate_coefficients(self, v):
        try:
            return map(float, [c for c in v.split(',')])

        except (ValueError, AttributeError):
            pass

    def _set_coefficients(self, v):
        self._coefficients = v


    def _parameters_default(self):
        p = self._get_parameters_path('parameters')
        return self._load_parameters(p)

    def _check_parameters_default(self):
        p = self._get_parameters_path('check_parameters')
        return self._load_parameters(p)

    def __coefficients_default(self):
        r = []
        if self.parent:
            pc = self.parent.load_power_calibration()
            if pc:
                if pc.coefficients:
                    r = list(pc.coefficients)

        return r

    def _power_meter_default(self):
        if self.parent is not None:
            apm = self.parent.get_device('analog_power_meter')
        else:
            apm = AnalogPowerMeter()
        return apm

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('pcm')
    pac = PowerCalibrationManager()
    pac.configure_traits()
#============= EOF =============================================
