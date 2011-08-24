#============= enthought library imports =======================
#from traitsui.api import View,Item,Group,HGroup,VGroup

#============= standard library imports ========================

#============= local library imports  ==========================

from src.hardware.arduino.arduino_gp_actuator import ArduinoGPActuator
from src.hardware.arduino.arduino_valve_actuator import ArduinoValveActuator
from src.hardware.arduino.arduino_fiber_light_module import ArduinoFiberLightModule
from subsystem import Subsystem

class ArduinoSubsystem(Subsystem):
    def load_additional_args(self, config):
        '''

        '''



        modules = self.config_get(config, 'General', 'modules')

        if modules is not None:
            for m in modules.split(','):
                _class_ = 'Arduino{}'.format(m)
                gdict = globals()
                if _class_ in gdict:
                    module = gdict[_class_](name = _class_,
                                            configuration_dir_name = self.configuration_dir_name
                                    )
                    module.load()
                    module._communicator = self._communicator
                    self.modules[m] = module
        return True

#============= EOF ====================================
