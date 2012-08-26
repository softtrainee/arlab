#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import Any, Event, Property, Bool
#from traitsui.api import View, Item, spring, ButtonEditor, HGroup
#============= standard library imports ========================
#============= local library imports  ==========================
from src.loggable import Loggable
from threading import Thread
#from src.spectrometer.spectrometer import Spectrometer

class SpectrometerTask(Loggable):
    spectrometer = Any
    execute = Event
    execute_label = Property(depends_on='_alive')
    _alive = Bool

    reference_detector = Any

    def _get_execute_label(self):
        return 'Stop' if self.isAlive() else 'Start'

    def isAlive(self):
        return self._alive

    def stop(self):
        self._alive = False

    def _execute_fired(self):
        if self.isAlive():
            self.stop()
            self._end()
        else:
            self._alive = True
            t = Thread(name='magnet_scan', target=self._execute)
            t.start()

    def _execute(self):
        pass


#============= EOF =============================================
