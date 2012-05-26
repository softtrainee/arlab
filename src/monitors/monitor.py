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
from traits.api import Int
#============= standard library imports ========================
from threading import Thread
import time
#============= local library imports  ==========================
#from src.config_loadable import ConfigLoadable
#from src.managers.manager import Manager
from src.config_loadable import ConfigLoadable

class Monitor(ConfigLoadable):
    '''
    '''
    sample_delay = Int(10)
    manager = None
    #parent = None
    kill = False
    _invalid_checks = None
    def load(self):
        config = self.get_configuration()
        self.set_attribute(config, 'sample_delay',
                           'General', 'sample_delay', cast='int', optional=True)
        self._load_hook(config)
        self._invalid_checks = []
    def _load_hook(self, *args):
        pass

    def stop(self):
        '''
        '''
        self.kill = True
        self.info('Stop monitor')

    def monitor(self):
        '''
        '''
        self.info('Starting monitor')
        t = Thread(target=self._monitor_)
        self.kill = False
        t.start()

    def reset_start_time(self):
        '''
        '''
        self.start_time = time.time()
#    def _monitor_(self):
#        '''
#        '''
#        raise NotImplementedError
    def _monitor_(self):
        '''
        '''
        #load before every monitor call so that changes to the config file
        #are incorpoated
        self.load()

        if self.manager is not None:
            self.gntries = 0
            self.reset_start_time()

            while not self.kill:
                #execute check hooks
                '''
                    does the order in which the check hooks are executed matter?
                    
                '''
                for h in dir(self):
                    '''
                        methods are prefaced with the class name
                        _LaserMonitor__check_duration
                    '''
                    if '__check' in h and h not in self._invalid_checks:
                        func = getattr(self, h)
                        func()
                        if self.kill:
                            break
                #sleep before running monitor again
                time.sleep(self.sample_delay)
#============= EOF ====================================
