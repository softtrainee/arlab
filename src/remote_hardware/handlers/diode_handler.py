#============= enthought library imports =======================
#from traits.api import HasTraits, on_trait_change, Str, Int, Float, Button
#from traitsui.api import View, Item, Group, HGroup, VGroup

#============= standard library imports ========================

#============= local library imports  ==========================
from laser_handler import LaserHandler

class DiodeHandler(LaserHandler):
    manager_name = 'Diode'
    def SetLaserPower(self, manager, data):
        result = 'OK'
        #manager.set_laser_power(data)
        return result

#============= views ===================================
#============= EOF ====================================
