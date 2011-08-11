#=============enthought library imports=======================

#=============standard library imports ========================

#=============local library imports  ==========================
from adc.adc_device import ADCDevice

class AnalogPowerMeter(ADCDevice):
    '''
    '''
    range = 1.0
    voltage_range = 5.0

    def _scan_(self, *args):
        '''
        '''

        r = self._cdevice._scan_()

        self.stream_manager.record(r, self.name)

    def read_power_meter(self, **kw):
        '''
        '''
        return self.read_voltage(**kw) * self.range / self.voltage_range
#============= EOF ==============================================
