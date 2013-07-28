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

from src.mv.machine_vision_manager import MachineVisionManager
import time
from src.mv.lumen_detector import LumenDetector
#============= standard library imports ========================
#============= local library imports  ==========================
class PID(object):
    _integral_err = 0
    _prev_err = 0
    Kp = 0.25
    Ki = 0.0001
    Kd = 0
    def get_value(self, error, dt):
        self._integral_err += (error * dt)
        derivative = (error - self._prev_err) / dt
        output = (self.Kp * error) + (self.Ki * self._integral_err) + (self.Kd * derivative)
        self._prev_err = error
        return output

class Degasser(MachineVisionManager):
    _period = 0.1
    def degas(self, lumens, duration):
        '''
            degas for duration trying to maintain
            lumens
        '''
        self._detector = LumenDetector()
        dt = self._period
        pid = PID()
        st = time.time()
        while time.time() - st < duration:
            cl = self._get_current_lumens()
            err = lumens - cl
            out = pid.get_value(err, dt)

            self._set_power(out)
            time.sleep(dt)

    def _set_power(self, pwr):
        if self.laser_manager:
            self.laser_manager.set_laser_power(pwr)

    def _get_current_lumens(self):
        src = self.new_image_frame()
        return self._detector.get_value(src)

#============= EOF =============================================
