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

#=============enthought library imports=======================
from traits.api import Button, DelegatesTo, Instance
import apptools.sweet_pickle as pickle
#=============standard library imports ========================
import os
#=============local library imports  ==========================
from src.hardware.fusions.fusions_co2_logic_board import FusionsCO2LogicBoard
#from src.monitors.co2_laser_monitor import CO2LaserMonitor
from brightness_pid_manager import BrightnessPIDManager
from fusions_laser_manager import FusionsLaserManager
from src.monitors.fusions_laser_monitor import FusionsLaserMonitor
from src.paths import paths
from src.monitors.fusions_co2_laser_monitor import FusionsCO2LaserMonitor

from traits.api import HasTraits
from numpy import polyval

class PowerMeterCalibration(object):
    _coefficients = None
    def get_watts(self, m):
        coeffs = self._coefficients
        if coeffs:
            return polyval(coeffs, m)

class FusionsCO2Manager(FusionsLaserManager):
    '''
    '''
    name = 'FusionsCO2'
    id = 'pychron.fusions.co2'
    configuration_dir_name = 'co2'
    launch_profile = Button
    launch_step = Button

    request_power = DelegatesTo('logic_board')
    request_powermin = DelegatesTo('logic_board')
    request_powermax = DelegatesTo('logic_board')

    monitor_name = 'co2_laser_monitor'
    monitor_klass = FusionsCO2LaserMonitor

    brightness_meter = Instance(BrightnessPIDManager, ())
    dbname = paths.co2laser_db
    db_root = paths.co2laser_db_root

    power_meter_calibration = None

    def finish_loading(self):
        super(FusionsCO2Manager, self).finish_loading()
        self.load_power_meter_calibration()

    def load_power_meter_calibration(self):
        p = os.path.join(paths.hidden_dir,
                         '{}.power_meter_calibration'.format(self.name))
        if os.path.isfile(p):
            self.info('loading power meter calibration: {}'.format(p))
            try:
                with open(p, 'rb') as f:
                    c = pickle.load(f)
                    if isinstance(c, PowerMeterCalibration):
                        self.power_meter_calibration = c
            except (OSError, pickle.PickleError):
                pass

    def dump_power_meter_calibration(self):
        p = os.path.join(paths.hidden_dir,
                         '{}.power_meter_calibration'.format(self.name))
        self.info('dumping power meter calibration to {}'.format(p))
        try:
            with open(p, 'wb') as f:
                pickle.dump(self.power_meter_calibration, f)
        except (OSError, pickle.PickleError):
            pass

    def _brightness_meter_default(self):
        mv = self._get_machine_vision()
        return BrightnessPIDManager(parent=self,
                                    machine_vision=mv)

    def _set_laser_power_hook(self, rp):
        '''
        '''
        self.logic_board._set_laser_power_(rp)

        if self.data_manager:
            with self._data_manager_lock:
                tab = self.data_manager.get_table('internal', 'Power')
                if tab:
                    tab.attrs.request_power = rp

    def get_laser_watts(self):
        w = self.logic_board.read_power_meter()

        #convert to watts
        #no calibration of logic board currently available
        #will have to simple normalize to 100

        if w is not None:
            if self.power_meter_calibration is not None:
                w = self.power_meter_calibration.get_watts(w)
            else:
                w = w / 255. * 100

        return w

    def _logic_board_default(self):
        '''
        '''
        b = FusionsCO2LogicBoard(name='co2logicboard',
                                 configuration_dir_name='co2')
        return b

    def _stage_manager_default(self):
        '''
        '''
        args = dict(name='co2stage',
                            configuration_dir_name='co2',
                             parent=self)

        return self._stage_manager_factory(args)

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    from src.initializer import Initializer


    logging_setup('fusions co2')
    f = FusionsCO2Manager()
    f.use_video = True
    f.record_brightness = True
    ini = Initializer()

    a = dict(manager=f, name='FusionsCO2')
    ini.add_initialization(a)
    ini.run()
#    f.bootstrap()
    f.configure_traits()

#    def show_streams(self):
#        '''
#        '''
#
#
#        if not self.streaming:
#
#        tc = self.temperature_controller
#        pyro = self.pyrometer
#        tm = self.temperature_monitor
#        apm = self.analog_power_meter
#        avaliable_streams = [apm]
#        self._show_streams_(avaliable_streams)

#        
#    def get_menus(self):
#        '''
#        '''
#        m = super(FusionsCO2Manager, self).get_menus()
#
#
#
#        m += [('Calibration', [
#                               dict(name = 'Power Profile', action = 'launch_power_profile'),
#                                  ]
#                                ),
#
#                ]
#        return m
#============= EOF ====================================

