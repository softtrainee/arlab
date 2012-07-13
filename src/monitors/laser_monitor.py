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
from traits.api import Float

#============= standard library imports ========================
import time
#============= local library imports  ==========================
from monitor import Monitor

NFAILURES = 3
NTRIES = 3
class LaserMonitor(Monitor):
    '''
    '''
    #manager = None
    max_duration = Float(0.1) # in minutes

    gntries = 0
    def _load_hook(self, config):
        '''
        '''

        self.set_attribute(config, 'max_duration',
                           'General', 'max_duration', cast='float', optional=True)



        return True


    def __check_duration(self):
        '''
        '''
        #check max duration
        manager = self.manager
        #self.info('Check duration')

        #max duration in mins convert to secs for comparison
        if time.time() - self.start_time > self.max_duration * 60.0:
            self.warning('Max duration %s (min) exceeded' % self.max_duration)
            manager.emergency_shutoff(reason='Max duration exceeded')


#============= EOF ====================================
