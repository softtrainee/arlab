#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from src.loggable import Loggable
import random

def signal_generator(mid, ncycles, npts, rlow = 0, rhigh = 5):
    '''
        @type ncycles: C{str}
        @param ncycles:

        @type npts: C{str}
        @param npts:

        @type rlow: C{str}
        @param rlow:

        @type rhigh: C{str}
        @param rhigh:
    '''
    x = []
    y = []
    c = 0
    while c < ncycles:
        p = 0
        while p < npts:
            x = c + p / 30.0
            y = mid + random.randint(rlow, rhigh) / 5000.0

            yield x, y
            p += 1

        c += 1
        if c == ncycles:
            c = 0

signal_generators = dict()
for k, m in [('l2', 0.000154), ('l1', 0.0043159), ('ax', 0.0009083), ('h1', 0.0664872), ('h2', 0.5071873)]:
    signal_generators[k] = signal_generator(m, 6, 10)

class Spectrometer(Loggable):
    def move_to_mass(self, mass, detector = 'ax'):
        '''
            @type mass: C{str}
            @param mass:

            @type detector: C{str}
            @param detector:
        '''
        self.info('moving %s to mass %0.3f' % (detector, mass))

    def get_signal(self, detector):
        '''
            @type detector: C{str}
            @param detector:
        '''
        return signal_generators[detector].next()

#============= views ===================================
#============= EOF ====================================
