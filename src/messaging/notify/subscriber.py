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
from threading import Thread, Event

from traits.api import Str, Int, Callable, List
import zmq

from src.loggable import Loggable


#============= standard library imports ========================
#============= local library imports  ==========================

class Subscriber(Loggable):
    host = Str
    port = Int
    callback = Callable

    _stop_signal = None
    _subscriptions = List
    was_listening = False

    def connect(self, timeout=None):
        context = zmq.Context()
        sock = context.socket(zmq.SUB)

        url = self._get_url()
        sock.connect(url)
        self._sock = sock
        return self._check_server_availability(url, timeout, context=context)


    def _get_url(self):
        h, p = self.host, self.port
        return 'tcp://{}:{}'.format(h, p)

    def check_server_availability(self, timeout=1, verbose=True):
        url = self._get_url()
        return self._check_server_availability(url, timeout=timeout, verbose=verbose)

    def _check_server_availability(self, url, timeout=3, context=None, verbose=True):
        ret = True
        if timeout:
            if context is None:
                context = zmq.Context()

            alive_sock = context.socket(zmq.REQ)
            alive_sock.connect(url)

            poll = zmq.Poller()
            poll.register(alive_sock, zmq.POLLIN)
            request = 'ping'
            alive_sock.send(request)
            socks = dict(poll.poll(timeout * 1000))
            if not socks.get(alive_sock) == zmq.POLLIN:
                if verbose:
                    self.warning('subscription server at {} not available'.format(url))
                alive_sock.setsockopt(zmq.LINGER, 0)
                alive_sock.close()
                poll.unregister(alive_sock)
                ret = False

        return ret

    def subscribe(self, f, cb, verbose=False):
        sock = self._sock
        sock.setsockopt(zmq.SUBSCRIBE, f)
        self._subscriptions.append((f, cb, verbose))

    def is_listening(self):
        return self._stop_signal and not self._stop_signal.is_set()

    def listen(self):
        self.info('starting subscription')
        self.was_listening = True

        self._stop_signal = Event()
        t = Thread(target=self._listen)
        t.setDaemon(True)
        t.start()

    def stop(self):
        self.debug('stopping')
        if self._stop_signal:
            self._stop_signal.set()
            self.was_listening = False

    def _listen(self):
        sock = self._sock
        while not self._stop_signal.is_set():
            resp = sock.recv()
            self.debug('raw notification {}'.format(resp))
            for si, cb, verbose in self._subscriptions:
                if resp.startswith(si):
                    resp = resp.split(si)[-1].strip()
                    if verbose:
                        self.info('received notification {}'.format(resp))
                    cb(resp)
                    break

        self.debug('no longer listening {}'.format(self._stop_signal.is_set()))

#============= EOF =============================================
