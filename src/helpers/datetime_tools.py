import time
import math
from datetime import datetime
ISO_FORMAT_STR = "%Y-%m-%d %H:%M:%S"
def time_generator(start = None):
    if start is None:
        start = time.time()
    while 1:
        yield time.time() - start

def current_time_generator(start):
    '''
    '''
    yt = start
    prev_time = 0
    i = 0
    while(1):

        current_time = time.time()
        if prev_time != 0:
            interval = current_time - prev_time
            yt += interval

        yield(yt)
        prev_time = current_time
        i += 1


def generate_timestamp(resolution = 'seconds'):
    '''
    '''
    ti = time.time()
    millisecs = math.modf(ti)[0] * 1000
    if resolution == 'seconds':
        r = '{}'.format(time.strftime(ISO_FORMAT_STR))
    else:
        r = '{}{:0.5f}'.format(time.strftime(ISO_FORMAT_STR), millisecs)
    return r

def generate_datestamp():
    return time.strftime('%Y-%m-%d')

def get_datetime(timestamp):
    if isinstance(timestamp, float):
        d = datetime.fromtimestamp(timestamp)
    else:
        d = datetime.strptime(timestamp, ISO_FORMAT_STR)
    return d

def convert_timestamp(timestamp):
    t = get_datetime(timestamp)
    return time.mktime(t.timetuple()) + 1e-6 * t.microsecond
