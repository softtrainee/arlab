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
from threading import Lock, Thread, Condition
import time
from Queue import Queue, Empty
from src.helpers.logger_setup import add_console
from src.loggable import Loggable

#============= local library imports  ==========================


class RS485Scheduler(Loggable):
    '''
        this class should be used when working with multiple rs485 devices on the same port. 
        
        it uses a simple lock and sleep cycle to avoid collision on the data lines
        
        when setting up the devices use device.set_scheduler to set the shared scheduler
        
    '''

#    collision_delay = Float(125)
    collision_delay = Float(25)

    def __init__(self, *args, **kw):
        super(RS485Scheduler, self).__init__(*args, **kw)
#        self._lock = Lock()
        self._condition = Condition()
        self._command_queue = Queue()
        self._buffer = Queue()

        consumer = Consumer(self._command_queue,
                            self._condition,
                            self.collision_delay)
        consumer.start()

    def schedule(self, func, args=None, kwargs=None):
        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = dict()

        _cond = self._condition
        _cond.acquire()

        self._command_queue.put((func, args, kwargs, self._buffer))
        _cond.notify()
        _cond.release()

        try:
            r = self._buffer.get(timeout=1)
        except Empty:
            r = None
        #self.debug('asked {} got {}'.format(args, r))
        return r


class Consumer(Thread):

    def __init__(self, q, cond, cd):
        Thread.__init__(self)
        self._q = q
        self.logger = add_console(name='consumer')
        self.cond = cond
        self.cd = cd

    def run(self):
        while 1:
            self.cond.acquire()
            while self._q.empty():
                self.cond.wait(timeout=0.05)

            st = time.time()
            func, args, kwargs, buf = self._q.get()
            r = func(*args, **kwargs)

            buf.put(r)

            self.cond.release()
#            time.sleep(max(0.0001, self.cd / 1000. - (time.time() - st) - 0.001))



#============= EOF ====================================
