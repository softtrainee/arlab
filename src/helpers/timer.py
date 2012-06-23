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
#============= standard library imports ========================
from threading import Thread, Event
import time
#============= local library imports  ==========================
class Timer(Thread):
    def __init__(self, period, func, *args, **kw):
        super(Timer, self).__init__()
        self._period = period / 1000.0
        self._func = func
        self._flag = Event()

        self._args = args
        self._kwargs = kw
        self.start()

    def run(self):
        t = None
        ww = self._period
        while not self._flag.isSet():
            if t is not None:
                ww = self._period - (time.time() - t) - 0.005
            w = max(0, ww)
            self._func(*self._args, **self._kwargs)
            self._flag.wait(w)
            t = time.time()

    def Stop(self):
        self._flag.set()

    def IsRunning(self):
        return not self._flag.is_set()
#============= EOF =====================================
