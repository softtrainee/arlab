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
from threading import Event
import time

from PySide.QtCore import QThread
#============= local library imports  ==========================
class Timer(QThread):
    def __init__(self, period, func, delay=0, *args, **kw):
        super(Timer, self).__init__()
        self._period = period / 1000.0
        self._func = func
        self._flag = Event()

        self._delay = delay / 1000.0
        self._args = args
        self._kwargs = kw

        self.start()

    def run(self):
#         p = self._period
        func = self._func
        flag = self._flag
        args = self._args
        kwargs = self._kwargs
        delay = self._delay

        if delay:
            flag.wait(delay)

        while not flag.isSet():
#            if t is not None:
#                ww = self._period - (time.time() - t) - 0.005
#
#            w = max(0, ww)

            st = time.time()
            func(*args, **kwargs)
#            ct=time.time()
#            print p - ct - st, ct, st
#            print max(0, p - time.time() + st), p,
            flag.wait(max(0, self._period - time.time() + st))

#            t = time.time()
    def stop(self):
        self.Stop()

    def Stop(self):
        self._flag.set()

    def IsRunning(self):
        return not self._flag.is_set()

    def set_interval(self, v):
        self._period = v
#============= EOF =====================================
