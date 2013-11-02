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
from threading import Thread
from traits.api import Int
#============= standard library imports ========================
import zmq
#============= local library imports  ==========================
from src.loggable import Loggable


class Notifier(Loggable):
    port = Int
    _sock = None
    _ping_sock = None

    def _port_changed(self):
        self.setup(self.port)

    def setup(self, port):
        if port:
            context = zmq.Context()
            sock = context.socket(zmq.PUB)
            sock.bind('tcp://*:{}'.format(port))
            self._sock = sock

            self._ping_sock = context.socket(zmq.REP)
            self._ping_sock.bind('tcp://*:{}'.format(port + 1))

            t = Thread(name='ping_replier', target=self._handle_ping)
            t.setDaemon(1)
            t.start()

    def _handle_ping(self):

        sock = self._ping_sock
        poll = zmq.Poller()
        poll.register(self._ping_sock, zmq.POLLIN)

        while self._ping_sock:
            socks = dict(poll.poll(1000))
            if socks.get(sock) == zmq.POLLIN:
                resp = sock.recv()
                if resp == 'ping':
                    sock.send('echo')

    def close(self):
        self._sock.close()
        self._sock = None

        self._ping_sock.close()
        self._ping_sock = None

    def send_notification(self, uuid, tag='RunAdded'):
        msg = '{} {}'.format(tag, uuid)
        self.info('pushing notification - {}'.format(msg))
        self._send(msg)

    def send_console_message(self, msg, tag='ConsoleMessage'):
        msg = '{} {}'.format(tag, msg)
        self.info('push console message - {}'.format(msg))
        self._send(msg)

    def _send(self, msg):
        if self._sock:
            self._sock.send(msg)
        else:
            self.debug('notifier not setup')

#============= EOF =============================================
