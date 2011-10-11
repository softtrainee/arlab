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
#=============enthought library imports=======================
#=============standard library imports ========================
from numpy import random, char

#=============local library imports  ==========================
CRLF = chr(13)
from src.hardware.core.core_device import CoreDevice
class MicroIonController(CoreDevice):
    scan_func = 'get_pressures'
    def load_additional_args(self, config, *args, **kw):
        self.address = self.config_get(config, 'General', 'address', optional=False)
        return True
    
    def graph_builder(self, g):
        CoreDevice.graph_builder(self, g, **{'show_legend':True})
        g.new_series()
        g.set_series_label('IG')
        
        g.new_series()
        g.set_series_label('CG1', series=1)

        g.new_series()
        g.set_series_label('CG2', series=2)
        
    def get_pressures(self):
        b = self.get_convectron_b_pressure()
        a = self.get_convectron_a_pressure()
        ig = self.get_ion_pressure()
        
        return ig, a, b
        #return self.get_convectron_a_pressure()

    def set_degas(self, state):
        key = 'DG'
        value = 'ON' if state else 'OFF'
        cmd = self._build_command(key, value)
        r = self.ask(cmd)
        r = self._parse_response(r)
        return r

    def get_degas(self):
        key = 'DGS'
        cmd = self._build_command(key)
        r = self.ask(cmd)
        r = self._parse_response(r)
        return r

    def get_ion_pressure(self):
        name = 'IG'
        return self._get_pressure(name)

    def get_convectron_a_pressure(self):
        name = 'CG1'
        return self._get_pressure(name)

    def get_convectron_b_pressure(self):
        name = 'CG2'
        return self._get_pressure(name)

    def set_ion_gauge_state(self, state):
        key = 'IG1'
        value = 'ON' if state else 'OFF'
        cmd = self._build_command(key, value)
        r = self.ask(cmd)
        r = self._parse_response(r)
        return r

    def get_process_control_status(self, channel=None):
        key = 'PCS'

        cmd = self._build_command(key, channel)

        r = self.ask(cmd)
        r = self._parse_response(r)

        if channel is None:
            if r is None:
                #from numpy import random,char
                r = random.randint(0, 2, 6)
                r = ','.join(char.array(r))

            r = r.split(',')
        return r

    def _get_pressure(self, name):
        key = 'DS'
        cmd = self._build_command(key, name)

        r = self.ask(cmd)
        r = self._parse_response(r)
        return r

    def _build_command(self, key, value=None):

        #prepend key with our address
        #example of new string formating 
        #see http://docs.python.org/library/string.html#formatspec
        key = '#{}{}'.format(self.address, key)
        if value is not None:
            args = (key, value, CRLF)
        else:
            args = (key, CRLF)
        c = ' '.join(args)

        return  c

    def _parse_response(self, r):
        if self.simulation or r is None:
            r = self.get_random_value(0, 10)

        return r

ON = True
OFF = False
import unittest
class tester(unittest.TestCase):
    def setUp(self):
        self._controller = MicroIonController()
        self._controller.bootstrap()
    def testSetDegas(self):

        cmd = self._controller.set_degas(ON)
        self.assertEqual(cmd, 'DG ON ' + CRLF)

        cmd = self._controller.set_degas(OFF)
        self.assertEqual(cmd, 'DG OFF ' + CRLF)

    def testGetDegas(self):
        cmd = self._controller.get_degas()
        self.assertEqual(cmd, 'DGS ' + CRLF)

    def testGetPressure(self):
        cmd = self._controller.get_ion_pressure()
        self.assertEqual(cmd, 'DS IG ' + CRLF)

        cmd = self._controller.get_convectron_a_pressure()
        self.assertEqual(cmd, 'DS CG1 ' + CRLF)

        cmd = self._controller.get_convectron_b_pressure()
        self.assertEqual(cmd, 'DS CG2 ' + CRLF)

    def testSetPower(self):

        cmd = self._controller.set_ion_gauge_state(ON)
        self.assertEqual(cmd, 'IG1 ON ' + CRLF)

        cmd = self._controller.set_ion_gauge_state(OFF)
        self.assertEqual(cmd, 'IG1 OFF ' + CRLF)

    def testProcessControl(self):
        cmd = self._controller.get_process_control_status(channel=1)
        self.assertEqual(cmd, 'PCS 1 ' + CRLF)

        cmd = self._controller.get_process_control_status(channel=None)
        self.assertEqual(cmd, 'PCS ' + CRLF)



if __name__ == '__main__':
    m = MicroIonController(name='micro_ion_controller')
    m.bootstrap()
    m.scan()
#============= EOF ====================================
