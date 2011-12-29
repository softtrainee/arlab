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

#=============enthought library imports=======================

#=============standard library imports ========================

#=============local library imports  ==========================
#from analog_digital_converter import AnalogDigitalConverter, AgilentADC, OmegaADC, KeithleyADC
from src.hardware.core.abstract_device import AbstractDevice
#from src.hardware.core.streamable import Streamable

class ADCDevice(AbstractDevice):
    scan_func = 'read_voltage'
    def load_additional_args(self, config):
        '''

        '''
        adc = self.config_get(config, 'General', 'adc')
        if adc is not None:
            module = __import__('src.hardware.adc.analog_digital_converter', fromlist=[adc])
            factory = getattr(module, adc)

            self._cdevice = factory(name=adc,
                                          configuration_dir_name=self.configuration_dir_name
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
