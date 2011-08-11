#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from src.hardware.arduino.arduino_valve_actuator import ArduinoValveActuator

from actuator import Actuator
class ValveController(Actuator):
    def get_open_indicator_state(self, *args, **kw):
        '''
            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        if self._cdevice is not None:
            return self._cdevice.get_open_indicator_state(*args, **kw)
    def get_closed_indicator_state(self, *args, **kw):
        '''
            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        if self._cdevice is not None:
            return self._cdevice.get_close_indicator_state(*args, **kw)
    def get_hard_lock_indicator_state(self, *args, **kw):
        '''
            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        if self._cdevice is not None:
            return self._cdevice.get_hard_lock_indicator_state(*args, **kw)
#============= EOF ====================================
