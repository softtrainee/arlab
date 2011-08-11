#=============enthought library imports=======================
from traits.api import Float
#=============standard library imports ========================

#=============local library imports  ==========================
from adc.adc_device import ADCDevice
class PyrometerTemperatureMonitor(ADCDevice):
    '''
    '''
    resistance = Float
    amps_max = Float
    amps_min = Float
    pyrometer_min = Float
    pyrometer_max = Float
    def load_additional_args(self, config):
        '''
            @type config: C{str}
            @param config:
        '''
        for s, k in [('General', 'resistance'),
                    ('General', 'amps_max'),
                    ('General', 'amps_min'),
                    ('General', 'pyrometer_min'),
                    ('General', 'pyrometer_max')]:
            self.set_attribute(config, k, s, k, cast = 'float')
#            

        return True

    def _scan_(self, *args, **kw):
        '''

        '''
        vi = self._cdevice._scan_(*args, **kw)
        #print r
        #r=self.convert_voltage_temp(r/1000.0)
        #print r
        amps = vi / (1000 * self.resistance)
        temp = amps / (self.amps_max - self.amps_min) * (self.pyrometer_max - self.pyrometer_min) + self.pyrometer_min

        self.stream_manager.record(temp, self.name)

    def convert_voltage_temp(self, volt):
        '''
          
        '''

        #convert volts to current
        amps = volt / self.resistance

        #convert current to temperature
        return ((amps / (self.amps_max - self.amps_min)) * (self.pyrometer_max - self.pyrometer_min)) + self.pyrometer_min