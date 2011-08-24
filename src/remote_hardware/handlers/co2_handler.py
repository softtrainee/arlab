#============= enthought library imports =======================
#from traits.api import HasTraits, on_trait_change, Str, Int, Float, Button
#from traitsui.api import View, Item, Group, HGroup, VGroup

#============= standard library imports ========================

#============= local library imports  ==========================
from laser_handler import LaserHandler

class Co2Handler(LaserHandler):
    manager_name = 'CO2'
    def SetLaserPower(self, manager, data):
        result = 'OK'
        try:
            data = float(data)
            manager.set_laser_power(data)
        except TypeError:
            result = 'Invalid power value {}'.format(data)

        return result

#============= views ===================================
#============= EOF ====================================
