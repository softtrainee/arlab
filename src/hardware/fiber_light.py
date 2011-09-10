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
from traits.api import Range, Event, Bool, on_trait_change, Property

#============= standard library imports ========================

#============= local library imports  ==========================
from src.hardware.arduino.arduino_fiber_light_module import ArduinoFiberLightModule
from src.hardware.core.abstract_device import AbstractDevice

class FiberLight(AbstractDevice):
    '''
        G{classtree}
    '''
    intensity = Range(0, 100.0, mode='slider')
    power = Event
    power_label = Property(depends_on='state')
    state = Bool
    def load_additional_args(self, config):
        '''
            @type config: C{str}
            @param config:
        '''
        n = self.config_get(config, 'General', 'control_module')

        self._cdevice = None
        if n is not None:
            if 'subsystem' in n:
                pass
            else:
                gdict = globals()
                if n in gdict:
                    self._cdevice = gdict[n](name=n,
                                 configuration_dir_name=self.configuration_dir_name
                                 )
                    self._cdevice.load()
            return True

    def power_on(self):
        '''
        '''
        if self._cdevice is not None:
            self._cdevice.power_on()
            self.state = True

    def power_off(self):
        '''
        '''
        if self._cdevice is not None:
            self._cdevice.power_off()
            self.state = False

    @on_trait_change('intensity')
    def set_intensity(self):
        '''
        '''
        if self._cdevice is not None:
            self._cdevice.set_intensity(self.intensity / 100 * 255)

    @on_trait_change('power')
    def power_fired(self):
        '''
        '''
        if self.state:
            self.power_off()
        else:
            self.power_on()
    def _get_power_label(self):
        '''
        '''
        if self.state:
            s = 'OFF'
        else:
            s = 'ON'
        return s
#============= EOF ====================================
