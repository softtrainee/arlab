'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
#from traits.api import HasTraits, on_trait_change,Str,Int,Float,Button
from traitsui.api import View, Item

#============= standard library imports ========================
#============= local library imports  ==========================

from src.hardware.core.core_device import CoreDevice
from src.hardware.core.data_helper import make_bitarray

SET_BITS = '111'
GET_BITS = '110'
SETPOINT_BITS = '00001'
FAULT_BITS = '01000'
COOLANT_BITS = '01001'

FAULTS_TABLE = ['Tank Level Low',
              'Fan Fail',
              None,
              'Pump Fail',
              'RTD open',
              'RTD short',
              None,
              None]
class ThermoRack(CoreDevice):
    '''
    '''
    convert_to_C = True

    scan_func = 'get_coolant_out_temperature'

    #===========================================================================
    # icore device interface
    #===========================================================================
    def set(self, v):
        pass

    def get(self):
#        v = super(ThermoRack, self).get()
        v = CoreDevice.get(self)
        if v is None:
            v = self.get_coolant_out_temperature()

        return v

    def write(self, *args, **kw):
        '''
        '''
        kw['is_hex'] = True
        super(ThermoRack, self).write(*args, **kw)
        CoreDevice.write(self, *args, **kw)

    def ask(self, *args, **kw):
        '''

        '''
        kw['is_hex'] = True
        return super(ThermoRack, self).ask(*args, **kw)


    def set_setpoint(self, v):
        '''
            input temp in c
            
            thermorack whats f
        '''
        if self.convert_to_C:
            v = 9 / 5. * v + 32
        cmd = '%x' % int(SET_BITS + SETPOINT_BITS, 2)

        self.write(cmd)

        data_bits = make_bitarray(int(v * 10), 16)
        high_byte = '%02x' % int(data_bits[:8], 2)
        low_byte = '%02x' % int(data_bits[8:], 2)

        self.write(low_byte)
        self.write(high_byte)

        return cmd, high_byte, low_byte

    def get_setpoint(self):
        '''
        '''
        cmd = '%x' % int(GET_BITS + SETPOINT_BITS, 2)

        resp = self.ask(cmd)
        sp = None
        if not self.simulation and resp is not None:
            sp = self.parse_response(resp, scale=0.1)
        return sp

    def get_faults(self, **kw):
        '''
        '''

        cmd = '%x' % int(GET_BITS + FAULT_BITS, 2)
        resp = self.ask(cmd, **kw)

        if self.simulation:
            resp = '0'

        #parse the fault byte
        fault_byte = make_bitarray(int(resp, 16))
        faults = []
        for i, fault in enumerate(FAULTS_TABLE):
            if fault and fault_byte[7 - i] == '1':
                faults.append(fault)

        return faults

    def get_coolant_out_temperature(self, **kw):
        '''
        '''
        cmd = '%x' % int(GET_BITS + COOLANT_BITS, 2)

        resp = self.ask(cmd)
        if not self.simulation and resp is not None:
            temp = self.parse_response(resp, scale=0.1)
        else:
            temp = self.get_random_value(0, 40)

        return temp

    def parse_response(self, resp, scale=1):
        '''
        '''
        # resp low byte high byte
        #flip to high byte low byte
        #split the response into high and low bytes
        if resp is not None:
            h = resp[2:]
            l = resp[:2]

            resp = int(h + l, 16) * scale
            if self.convert_to_C:
                resp = 5.0 * (resp - 32) / 9.0

        return resp


#===============================================================================
# viewabledevice protocol
#===============================================================================
    def graph_builder(self, g):
        import numpy as np


        super(ThermoRack, self).graph_builder(g)
        x = np.linspace(0, 10, 100)
        g.new_series(x=x,
                     y=np.cos(x)
                     )

    def current_state_view(self):
        v = View(Item('graph', show_label=False, style='custom'))
        return v


#============= EOF ====================================
