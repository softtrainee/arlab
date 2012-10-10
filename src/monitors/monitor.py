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
from threading import Thread, Event
import time
#============= local library imports  ==========================
#from src.config_loadable import ConfigLoadable
#from src.managers.manager import Manager
from src.config_loadable import ConfigLoadable
from pyface.message_dialog import warning

class Monitor(ConfigLoadable):
    '''
    '''
    sample_delay = Float(5)
    manager = None
    _monitoring = False
    _invalid_checks = None
    _stop_signal = None

    def is_monitoring(self):
        return self._monitoring

    def load(self):
        config = self.get_configuration()
        self.set_attribute(config, 'sample_delay',
                           'General', 'sample_delay', cast='float', optional=False)

        self._load_hook(config)
        self._invalid_checks = []

    def _load_hook(self, *args):
        pass

    def stop(self):
        '''
        '''
        self._stop_signal.set()
#        self.kill = True
        self.info('Stop monitor')
        self._monitoring = False

    def warning(self, msg):
        '''
            override loggable warning to issue a warning dialog
        '''
        super(Monitor, self).warning(msg)
        warning(None, msg)

    def monitor(self):
        '''
        '''
        if not self._monitoring:
            self._monitoring = True
            self.info('Starting monitor')
            self._stop_signal = Event()
            t = Thread(target=self._monitor_, args=(self._stop_signal,))
    #        self.kill = False
            t.start()

    def reset_start_time(self):
        '''
        '''
        self.start_time = time.time()

    def _monitor_(self, stop_signal):
        '''
        '''
        #load before every monitor call so that changes to the config file
        #are incorpoated
        self.load()

        if self.manager is not None:
            #clear error
            self.manager.error_code = None

            self.gntries = 0
            self.reset_start_time()
            funcs = [getattr(self, h) for h in dir(self)
                     if '_fcheck' in h and h not in self._invalid_checks]
            while not stop_signal.isSet():
                for fi in funcs:
                    fi()
                    if stop_signal.isSet():
                        break

                #sleep before running monitor again
                time.sleep(self.sample_delay)
#============= EOF ====================================
#    def _monitor_(self, stop_signal):
#        '''
#        '''
#        #load before every monitor call so that changes to the config file
#        #are incorpoated
#        self.load()
#
#        if self.manager is not None:
#            self.gntries = 0
#            self.reset_start_time()
#            cnt = 0
#            while not stop_signal.isSet():
#                '''
#                    double checks executed twice for every check
#                '''
#                for h in dir(self):
#                    if '_doublecheck' in h and h not in self._invalid_checks:
#                        func = getattr(self, h)
#                        func()
#                        if stop_signal.isSet():
#                            break
#
#                if cnt % 2 == 0:
#                    for h in dir(self):
#                        if '_check' in h and h not in self._invalid_checks:
#                            func = getattr(self, h)
#                            func()
#                            if stop_signal.isSet():
#                                break
#
#                cnt += 1
#                if cnt == 100:
#                    cnt = 0
#                #sleep before running monitor again
#                time.sleep(self.sample_delay / 2.0)
