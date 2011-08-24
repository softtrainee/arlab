#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================

from src.hardware.core.arduino_core_device import ArduinoCoreDevice
'''

'''
class ArduinoFiberLightModule(ArduinoCoreDevice):
    def power_on(self):
        '''
        '''
        self.ask('o')
    def power_off(self):
        '''
        '''
        self.ask('f')
    def set_intensity(self, v):
        '''
            @type v: C{str}
            @param v:
        '''
        self.ask('i %03i' % v)
#    def power_on(self):
##        self._communicator.digital_write(self.power_pin,
##                           1
##                           )
#        
#        
#    def digital_read(self):
#        self._communicator.digital_read()
#============= EOF ====================================
