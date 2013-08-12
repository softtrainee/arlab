#===============================================================================
# Copyright 2013 Jake Ross
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

#============= standard library imports ========================
#============= local library imports  ==========================

from src.ui.thread import Thread
from Queue import Queue, Empty

class ConsumerMixin(object):
    def setup_consumer(self, func=None, buftime=None, auto_start=True):
        self._consume_func = func
        self._buftime = buftime  # ms
        self._consumer_queue = Queue()
        self._consumer = Thread(target=self._consume)
        self._should_consume = True
        if auto_start:
            self._consumer.start()

    def start(self):
        if self._consumer:
            self._consumer.start()

    def stop(self):
        if self._consumer:
            self._should_consume = False

    def add_consumable(self, v):
        self._consumer_queue.put(v)

    def _consume(self):
        bt = self._buftime
        if bt:
            bt = bt / 1000.
        else:
            bt = 1

        def get_func():
            q = self._consumer_queue
            v = None
            while 1:
                try:
                    v = q.get(timeout=bt)
                except Empty:
                    break

            return v

        cfunc = self._consume_func

        while 1:
            v = get_func()
            if v:
                if cfunc:
                    cfunc(v)
                elif isinstance(v, tuple):
                    func, a = v
                    func(a)

            if not self._should_consume:
                break

#============= EOF =============================================
