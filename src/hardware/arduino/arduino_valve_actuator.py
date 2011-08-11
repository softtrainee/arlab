#============= enthought library imports =======================
#from traits.api import HasTraits, on_trait_change,Str,Int,Float,Button
#from traitsui.api import View,Item,Group,HGroup,VGroup

#============= standard library imports ========================

#============= local library imports  ==========================
from arduino_gp_actuator import ArduinoGPActuator
class ArduinoValveActuator(ArduinoGPActuator):
    def get_open_indicator_state(self, obj):
        '''
            @type obj: C{str}
            @param obj:
        '''
        pass
    def get_closed_indicator_state(self, obj):
        '''
            @type obj: C{str}
            @param obj:
        '''
        pass
    def get_hard_lock_indicator_state(self, obj):
        '''
            @type obj: C{str}
            @param obj:
        '''
        cmd = 'A%s' % obj.name
        return self.ask(cmd, verbose = False) == '1'
#============= EOF ====================================
