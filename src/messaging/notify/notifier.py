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
from traits.api import Int
#============= standard library imports ========================
import zmq
#============= local library imports  ==========================
from src.loggable import Loggable


class Notifier(Loggable):
    port = Int
    _sock = None

    def _port_changed(self):
        self.setup(self.port)

    def setup(self, port):
        if port:
            context = zmq.Context()
            sock = context.socket(zmq.PUB)
            sock.bind('tcp://*:{}'.format(port))
            self._sock = sock

            # delay to allow publ sock to get setup
            #time.sleep(0.1)

    def close(self):
        self._sock.close()
        self._sock = None

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
