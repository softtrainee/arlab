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
        self.ask('4;')
        
    def power_off(self):
        '''
        '''
        self.ask('5;')
        
    def set_intensity(self, v):
        '''
        '''
        self.ask('6,{};'.format(int(v)))
#    def power_on(self):
##        self._communicator.digital_write(self.power_pin,
##                           1
##                           )
#        
#        
#    def digital_read(self):
#        self._communicator.digital_read()
#============= EOF ====================================
