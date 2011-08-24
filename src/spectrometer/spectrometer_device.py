#============= enthought library imports =======================
from traits.api import  Any, DelegatesTo
#from traitsui.api import View, Item, Group, HGroup, VGroup

#============= standard library imports ========================

#============= local library imports  ==========================
from src.loggable import Loggable

class SpectrometerDevice(Loggable):
    microcontroller = Any

    simulation = DelegatesTo('microcontroller')
    def finish_loading(self):
        pass



#============= EOF =============================================
