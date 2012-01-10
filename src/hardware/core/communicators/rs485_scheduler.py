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
#============= enthought library imports =======================
from traits.api import HasTraits, Float

#============= standard library imports ========================
from threading import Lock
import time

#============= local library imports  ==========================


class RS485Scheduler(HasTraits):
    '''
        this class should be used when working with multiple rs485 devices on the same port. 
        
        it uses a simple lock and sleep cycle to avoid collision on the data lines
        
        when setting up the devices use device.set_scheduler to set the shared scheduler
        
    '''

#    collision_delay = Float(125)
    collision_delay = Float(25)

    def __init__(self, *args, **kw):
        super(RS485Scheduler, self).__init__(*args, **kw)
        self._lock = Lock()

    def schedule(self, func, args=None, kwargs=None):
        with self._lock:
        #self._lock.acquire()
            if args is None:
                args = tuple()
            if kwargs is None:
                kwargs = dict()

#            time.sleep(self.collision_delay / 1000.0)
            r = func(*args, **kwargs)
            time.sleep(self.collision_delay / 1000.0)
            #self._lock.release()
            #print args,kwargs, r
            return r

#============= EOF ====================================
