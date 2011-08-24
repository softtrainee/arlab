#============= enthought library imports =======================

#============= standard library imports ========================
from numpy import hstack, std, mean
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

    equilibrate(*args, **kw)

def equilibrate(parent, temp_func, setpoint, frequency = None, freq_hook = None, timeout = 1, **kw):
    '''
        @type temp_func: C{str}
        @param temp_func:

        @type setpoint: C{str}
        @param setpoint:

        @type frequency: C{str}
        @param frequency:

        @type **kw: C{str}
        @param **kw:
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

def check_point(points, point, setpoint, n = 10, mean_tolerance = 1.5,
                    std_tolerance = 1,
                    mean_check = False,
                    std_check = False,
                    **kw):
    '''
        @type point: C{str}
        @param point:

        @type setpoint: C{str}
        @param setpoint:

        @type n: C{str}
        @param n:

        @type mean_tolerance: C{str}
        @param mean_tolerance:

        @type : C{str}
        @param :
    '''

    points = hstack((points[-n + 1:], [point]))
    if len(points) >= n:

        avg = mean(points)
        stderr = std(points)
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

        stats = dict(mean = avg, std = stderr)
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