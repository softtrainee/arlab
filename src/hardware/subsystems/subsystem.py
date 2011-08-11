#============= enthought library imports =======================
from traits.api import Dict

#============= standard library imports ========================

#============= local library imports  ==========================

#============= views ===================================
#============= EOF ====================================
from src.hardware.core.core_device import CoreDevice
class Subsystem(CoreDevice):
    '''
    '''
    #dictionary of arduino subsystem module classes 
    #ex ArduinoGPActuator
    modules = Dict

    def get_module(self, key):
        '''
        '''
        mods = self.modules
        if key in  mods:
            return mods[key]
        else:
            self.warning('{} not available'.format(key))