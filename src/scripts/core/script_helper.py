#===============================================================================
# Copyright 2011 Jake Ross
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
from numpy import hstack
import time
from Carbon.Aliases import true
#============= local library imports  ==========================
gintegral = 0
gprev_error = 0
def pid_iteration(error, Kp, Ki, Kd, dt):
    global gintegral, gprev_error

    gintegral += (error * dt)
    derivative = (error - gprev_error) / dt
    output = (Kp * error) + (Ki * gintegral) + (Kd * derivative)
    gprev_error = error
    return output

def smart_equilibrate(*args, **kw):
    ''' 
        smart equilibrate uses a pid loop to adjust the 
        measurement frequency based on setpoint error
    '''
    def update_frequency(error):

        freq = 1 - pid_iteration(error, 0.1, 0, 0, 1)
        if freq <= 0:
            freq = 1

        return freq

    kw['frequnecy'] = None
    kw['freq_hook'] = update_frequency

    return equilibrate(*args, **kw)

def equilibrate(parent, temp_func, setpoint, frequency=None, freq_hook=None, timeout=1, **kw):
    '''
       
    '''
    start = time.time()
    temps = []
    freq = frequency
    while parent.isAlive():
        temp = temp_func()
        if isinstance(temp, tuple):
            temp = temp[0]

        args = check_point(temps, temp, setpoint, **kw)
        temps = args[1]
        if args[0]:
            break

        if frequency is None:
            freq = freq_hook(abs(temp - setpoint))

        time.sleep(1.0 / freq)

        if time.time() - start > timeout * 60.0:
            break

    eq_time = time.time() - start
    return eq_time

def check_point(points, point, setpoint, n=10, mean_tolerance=1.5,
                    std_tolerance=1,
                    mean_check=False,
                    std_check=False,
                    **kw):
    '''

    '''

    points = hstack((points[-n + 1:], [point]))
    if len(points) >= n:

        avg = points.mean()
        stderr = points.std()
        if mean_check:
            #print mean(points),setpoint
            dif = abs(avg - setpoint)
            #bits = (dif < 1.5 or avg >= setpoint)
            bits = dif <= mean_tolerance

        elif std_check:
            bits = stderr < std_tolerance
        else:
            mean_bit = abs(avg - setpoint) < mean_tolerance
            std_bit = stderr < std_tolerance
            bits = (mean_bit and std_bit)

        stats = dict(mean=avg, std=stderr)
        return (bits, points, stats)
    else:
        return (False, points)
#============= EOF ====================================
class Parent:
    def isAlive(self):
        return true

i = 0
def temp_func():
    global i
    t = i
    i += 1
    return t

def test():
    parent = Parent()

    smart_equilibrate(parent, temp_func, 10)

if __name__ == '__main__':
    test()
