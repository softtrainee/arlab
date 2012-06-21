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
from traits.api import Int, Float

#============= standard library imports ========================
#import time
#============= local library imports  ==========================
#from monitor import Monitor
from src.monitors.laser_monitor import LaserMonitor

NFAILURES = 3
NTRIES = 3
class FusionsLaserMonitor(LaserMonitor):
    '''
    '''
    manager = None
#    sample_delay = Int(5)
    max_duration = Float(60) # in minutes

    max_coolant_temp = Float(25)

    gntries = 0
    def load_additional_args(self, config):
        '''
        '''
        super(FusionsLaserMonitor, self).load_additional_args(self)
        self.set_attribute(config, 'max_coolant_temp',
                       'General', 'max_coolant_temp', cast='float', optional=True)

    def __check_interlocks(self):
        '''
        '''
        #check laser interlocks
        manager = self.manager
        self.info('Check laser interlocks')
        for i in range(NTRIES):
            interlocks = manager.logic_board.check_interlocks()

            if interlocks:
                inter = ' '.join(interlocks)
                self.warning(inter)
                manager.emergency_shutoff(reason=inter)
                break
            else:
                self.info('interlocks OK')
                break

        if i == NTRIES - 1:
            #failed checking interlocks 
            self.gntries += 1
            if self.gntries > NFAILURES:
                manager.emergency_shutoff(reason='failed checking interlocks')

    def __check_coolant_temp(self):
        '''
        '''
        manager = self.manager

        self.info('Check laser coolant temperature')
        ct = manager.get_coolant_temperature(verbose=False)
        if ct is None:
#            self._invalid_checks.append('_FusionsLaserMonitor__check_coolant_temp')
#            pass
            self._chiller_unavailable()
        elif ct > self.max_coolant_temp:
            self.warning('Laser coolant over temperature {:0.2f}'.format(ct))
            manager.emergency_shutoff(reason='Coolant over temp {:0.2f}'.format(ct))
        else:
            self.info('laser coolant temperature= {:0.2f}'.format(ct))

    def __check_coolant_status(self):
        manager = self.manager
        self.info('Check laser coolant status')

        status = manager.get_coolant_status()
        if not status:
            self.info('no coolant errors')
        elif status is None:
            self._chiller_unavailable()
        else:
            status = ','.join(status) if isinstance(status, list) else status
            reason = 'Laser coolant error {}'.format(status)
            self.warning(reason)
            manager.emergency_shutoff(reason=reason)

    def _chiller_unavailable(self):
        reason = 'Laser chiller not available'
        self.manager.emergency_shutoff(reason=reason)
        self.warning(reason)
#============= EOF ====================================
