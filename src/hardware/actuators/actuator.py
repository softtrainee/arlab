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
#from traits.api import HasTraits, on_trait_change, Str, Int, Float, Button
#from traitsui.api import View, Item, Group, HGroup, VGroup

#============= standard library imports ========================

#============= local library imports  ==========================
#from agilent_gp_actuator import AgilentGPActuator
#from src.hardware.arduino.arduino_gp_actuator import ArduinoGPActuator
#from argus_gp_actuator import ArgusGPActuator

from src.hardware.core.abstract_device import AbstractDevice
PACKAGES = dict(AgilentGPActuator='src.hardware.actuators.agilent_gp_actuator',
              ArduinoGPActuator='src.hardware.arduino.arduino_gp_actuator',
              ArgusGPActuator='src.hardware.actuators.argus_gp_actuator'
              )

class Actuator(AbstractDevice):
    '''
    '''
    _type = None

    def load_additional_args(self, config):
        '''
       
        '''
        #self._cdevice=None
#        if config.has_option('General','subsystem'):
#            # if a subsystem is specified than the physical actuator is part of a larger
#            # subsystem. ex One arduino can have a actuator subsystem and a data logging system
#            #if a subsystem is specified dont want to create our on instance of a GPActuator
#            pass

        self._type = klass = self.config_get(config, 'General', 'type')
        if klass is not None:
            if 'subsystem' in klass:
                pass
            else:
                try:
                    module = __import__(PACKAGES[klass], fromlist=[klass])
                except ImportError, e:
                    self.warning(e)
                    return False

                factory = getattr(module, klass)

                self._cdevice = factory(name=klass,
                                      configuration_dir_name=self.configuration_dir_name)
#                gdict = globals()
#                if class_type in gdict:
#                    self._cdevice = gdict[class_type](name=class_type,
#                                            configuration_dir_name=self.configuration_dir_name
#                                    )
                self._cdevice.load()
                return True

    def open_channel(self, *args, **kw):
        '''
        
        '''

        if self._cdevice is not None:
            return  self._cdevice.open_channel(*args, **kw)
        else:
            return True

    def close_channel(self, *args, **kw):
        '''
            
        '''
        if self._cdevice is not None:
            return self._cdevice.close_channel(*args, **kw)
        else:
            return True

    def get_channel_state(self, *args, **kw):
        '''
           
        '''

        if self._cdevice is not None:
            return self._cdevice.get_channel_state(*args, **kw)

#============= EOF ====================================
