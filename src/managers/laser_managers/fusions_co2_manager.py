'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

#=============enthought library imports=======================
from traits.api import Button, DelegatesTo, Instance
#=============standard library imports ========================
#=============local library imports  ==========================

from fusions_laser_manager import FusionsLaserManager
from src.hardware.fusions.fusions_co2_logic_board import FusionsCO2LogicBoard
from src.monitors.co2_laser_monitor import CO2LaserMonitor
from src.managers.laser_managers.brightness_pid_manager import BrightnessPIDManager
#from hardware.analog_digital_converter import AgilentADC
#from hardware.newport_esp301_motioncontroller import ESPMotionController
#from src.helpers import paths


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
    monitor_klass = CO2LaserMonitor

    brightness_meter = Instance(BrightnessPIDManager, ())

    def _brightness_meter_default(self):
#        mv = None
#        if hasattr(self.stage_manager, 'machine_vision_manager'):
#            mv = self.stage_manager.machine_vision_manager
        mv = self._get_machine_vision()
        print 'mac', mv
        return BrightnessPIDManager(parent=self,
                                    machine_vision=mv)

    def set_laser_power(self, rp):
        '''
        '''
        super(FusionsCO2Manager, self).set_laser_power(rp)
        self.info('request power {:0.3f}'.format(rp))
        self.logic_board._set_laser_power_(rp)

    def get_laser_watts(self):
        w = self.logic_board.read_power_meter()

        #convert to watts
        #no calibration of logic board currently available
        #will have to simple normalize to 100

        if w is not None:
            w = w / 255. * 100

        return w

#    def _monitor_factory(self):
#        '''
#        '''
#        return CO2LaserMonitor

#    def monitor_factory(self):
#        lm = self.monitor
#        if lm is None:
#            lm = self._monitor_factory()(manager = self,
#                            configuration_dir_name = paths.monitors_dir,
#                            name = 'co2_laser_monitor')
#            #lm.bootstrap()
#        return lm

    def _logic_board_default(self):
        '''
        '''
        b = FusionsCO2LogicBoard(name='co2logicboard',
                                 configuration_dir_name='co2')
        return b

    def _stage_manager_default(self):
        '''
        '''
#        print 'afasdf'
        args = dict(name='co2stage',
                            configuration_dir_name='co2',
                             parent=self)

        return self._stage_manager_factory(args)


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

