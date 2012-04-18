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
import time

class PIDObject(object):
    Kp = 0.25
    Ki = 0
    Kd = 0
    _prev_time = 0
    _integral_err = 0
    _prev_err = 0

    def iterate(self, error, dt):

        self._integral_err += (error * dt)
        derivative = (error - self._prev_err) / dt
        output = (self.Kp * error) + (self.Ki * self._integral_err) + (self.Kd * derivative)
        self._prev_err = error

        return output

    def get_value(self, err):
        if self._prev_time is None:
            self._prev_time = time.time()

        ct = time.time()
        dt = ct - self._prev_time
        self._prev_time = ct

        return self.iterate(err, dt)

#======== EOF ================================================================
