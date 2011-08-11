
#=============enthought library imports=======================

#=============standard library imports ========================

#=============local library imports  ==========================
from analog_digital_converter import AnalogDigitalConverter, AgilentADC, OmegaADC, KeithleyADC
from src.hardware.core.abstract_device import AbstractDevice
from src.hardware.core.streamable import Streamable

class ADCDevice(AbstractDevice, Streamable):
    scan_func = 'read_voltage'
    def load_additional_args(self, config):
        '''

        '''
        adc = self.config_get(config, 'General', 'adc')
        if adc is not None:
            gdict = globals()
            if adc in gdict:
                self._cdevice = gdict[adc](name = adc,
                                              configuration_dir_name = self.configuration_dir_name
                            )
                self._cdevice.load()
                return True

    def read_voltage(self, **kw):
        '''
        '''
        v = 1
        if self._cdevice is not None:
            v = self._cdevice.read_device(**kw)

        return v
