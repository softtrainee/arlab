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
#=============standard library imports ========================
#=============local library imports  ==========================
from src.hardware.fusions.fusions_co2_logic_board import FusionsCO2LogicBoard
#from src.monitors.co2_laser_monitor import CO2LaserMonitor
from brightness_pid_manager import BrightnessPIDManager
from fusions_laser_manager import FusionsLaserManager
from src.monitors.fusions_laser_monitor import FusionsLaserMonitor
from src.lasers.laser_managers.power_calibration_manager import PowerCalibrationManager
from src.helpers.paths import co2laser_db
from src.database.adapters.power_calibration_adapter import PowerCalibrationAdapter


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
    monitor_klass = FusionsLaserMonitor

    brightness_meter = Instance(BrightnessPIDManager, ())
    power_calibration_manager = Instance(PowerCalibrationManager)

    def _brightness_meter_default(self):
        mv = self._get_machine_vision()
        return BrightnessPIDManager(parent=self,
                                    machine_vision=mv)

    def _power_calibration_manager_default(self):
        mv = self._get_machine_vision()
        return PowerCalibrationManager(parent=self,
                                       machine_vision=mv,
                                       )

    def get_power_calibration_database(self):
        db = PowerCalibrationAdapter(dbname=co2laser_db,
                                             kind='sqlite')
        db.connect()
        return db

    def set_laser_power(self, rp):
        '''
        '''
        super(FusionsCO2Manager, self).set_laser_power(rp)
        self.info('request power {:0.3f}'.format(rp))
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

