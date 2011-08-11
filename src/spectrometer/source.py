#============= enthought library imports =======================
from traits.api import  Float
#from traitsui.api import View, Item, Group, HGroup, VGroup

#============= standard library imports ========================

#============= local library imports  ==========================
from src.spectrometer.spectrometer_device import SpectrometerDevice

class Source(SpectrometerDevice):
    nominal_hv = Float(4500)
    current_hv = Float(4500)

    def read_hv(self):
        r = self.microcontroller.ask('GetHighVoltage')
        try:
            r = float(r)
        except:
            r = self.nominal_hv

        self.current_hv = r
        return r
#============= EOF =============================================
