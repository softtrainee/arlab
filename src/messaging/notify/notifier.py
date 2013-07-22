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
from traits.api import HasTraits
from traitsui.api import View, Item
from src.loggable import Loggable
import zmq
#============= standard library imports ========================
#============= local library imports  ==========================

class Notifier(Loggable):
    def setup(self):
        context = zmq.Context()
        sock = context.socket(zmq.PUB)
        sock.bind('tcp://*:8100')
        self._sock = sock

    def send_notification(self, msg):
        self._sock.send(msg)
#============= EOF =============================================
