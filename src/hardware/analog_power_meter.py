#===============================================================================
# Copyright 2011 Jake Ross
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================

#=============enthought library imports=======================
from traits.api import Float, Enum
from traitsui.api import View, Item
#=============standard library imports ========================

#=============local library imports  ==========================
from adc.adc_device import ADCDevice

class AnalogPowerMeter(ADCDevice):
    '''
    '''
    watt_range = Enum(0.03, 0.1, 0.3, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000)
    voltage_range = Float(5.0)

    def load_additional_args(self, config):
        super(AnalogPowerMeter, self).load_additional_args(config)
        self.set_attribute(config, 'voltage_range', 'General', 'voltage', cast='float')

    def traits_view(self):
        v = View(Item('watt_range', label='Watt Range'),
                 Item('voltage_range', label='ADC range'),
                 buttons=['OK', 'Cancel']
                 )
        return v

    def _scan_(self, *args):
        '''
        '''

        r = self._cdevice._scan_()

        self.stream_manager.record(r, self.name)

    def read_power_meter(self, *args, **kw):
        '''
        '''
        return self.read_voltage(**kw) * self.watt_range / self.voltage_range
#============= EOF ==============================================
