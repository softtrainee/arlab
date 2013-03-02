from traits.api import Int
import time
from src.hardware.core.core_device import CoreDevice

class AgilentUnit(CoreDevice):
    slot = Int
    trigger_count = Int
    def load_additional_args(self, config):

        self.slot = self.config_get(config, 'General', 'slot', cast='int', default=1)
        self.trigger_count = self.config_get(config, 'General', 'trigger_count', cast='int', default=1)


    def _trigger(self, verbose=False):
        '''
        '''
        self.ask('ABORT', verbose=verbose)
        #time.sleep(0.05)
        self.tell('INIT', verbose=verbose)
#        time.sleep(0.1)

    def _wait(self, n=1000, verbose=False):
        if self.simulation:
            return True

        for _ in range(1000):
            if self._points_available(verbose=verbose):
                return True
            time.sleep(0.025)
        else:
            self.warning('not points in memory')

    def _points_available(self, verbose=False):
        resp = self.ask('DATA:POINTS?', verbose=verbose)
        if resp is not None:
            return int(resp)

#    def read_device(self, **kw):
#        '''
#        '''
#        #resp = super(AgilentADC, self).read_device()
##        resp = AnalogDigitalConverter.read_device(self)
##        if resp is None:
#        self._trigger()
#        
#        #wait unit points in memory
#        while not self._points_available():
#            time.sleep(0.001)
#            

#        resp = self.ask('DATA:POINTS?')
#        if resp is not None:
#            n = float(resp)
#            resp = 0
#            if n > 0:
#                resp = self.ask('DATA:REMOVE? {}'.format(float(n)))
#                resp = self._parse_response_(resp)
#
#            #self.current_value = resp
#            self.read_voltage = resp
#        return resp
