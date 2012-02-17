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
from traits.api import Bool, Float, Str, Constant, Int
from pyface.timer.api import Timer
#============= standard library imports ========================
#============= local library imports  ==========================
from src.hardware.core.core_device import CoreDevice
from src.hardware.core.checksum_helper import computeBCC
STX = chr(2)
ETX = chr(3)
EOT = chr(4)
ENQ = chr(5)
DLE = chr(10)
ANSWER_ADDR = '0002'


class ATLLaserControlUnit(CoreDevice):
    '''
    '''
    _enabled = Bool(False)
    triggered = Bool(False)

    energy = Float(0)
    energymin = Constant(0.0)
    energymax = Constant(15.0)
    update_energy = Float

    hv = Float(11)
    hvmin = Constant(11.0)
    hvmax = Constant(16.0)
    update_hv = Float(11)

    reprate = Float(100)
    repratemin = Constant(100.0)
    repratemax = Constant(300.0)
    update_reprate = Float(100)

    trigger_modes = ['External I',
                      'External II',
                      'Internal'
                      ]
    trigger_mode = Str('External I')
    stablization_modes = ['High Voltage', 'Energy']
    stablization_mode = Str('High Voltage')

    stop_at_low_e = Bool

    cathode = Float(0.0)
    reservoir = Float(0.0)
    missing_pulses = Int(0)
    halogen_filter = Float(0.0)

    laser_head = Float(0.0)
    laser_headmin = Constant(0.0)
    laser_headmax = Constant(7900.0)

    burst = Bool
    nburst = Int(enter_set=True, auto_set=False)
    cburst = Int

    def start_update_timer(self):
        '''
        '''
        self.timer = Timer(1000, self._update_parameters)

    def set_energy(self, v):
        '''
        '''
        pass

    def set_reprate(self, v):
        '''
        '''
        pass

    def set_hv(self, v):
        '''
        '''
        pass

    def trigger_laser(self):
        '''
        '''
        self.start_update_timer()

        self.triggered = True

    def stop_triggering_laser(self):
        '''
        '''
        self.triggered = False

    def laser_on(self):
        '''
        '''
        cmd = self._build_command(11, 0)
        self._send_command(cmd)

        self._enabled = True

    def laser_off(self):
        '''
        '''
        cmd = self._build_command(11, 1)
        self._send_command(cmd)
        self._enabled = False

    def laser_single_shot(self):
        '''
        '''
        cmd = self._build_command(11, 2)
        self._send_command(cmd)

    def laser_run(self):
        '''
        '''
        cmd = self._build_command(11, 3)
        self._send_command(cmd)

    def _update_parameters(self):
        '''
        '''
        formatter = lambda x:x / 10.0
#        read and set energy and pressure as one block
        self._update_parameter_list([('energy', formatter), 'laser_head'], 8, 2)
#        read and set frequency and hv as one block
        self._update_parameter_list(['reprate', ('hv', formatter)], 1001, 2)

#        read and set gas action

    def _anytrait_changed(self, name, value):
        '''

        '''
        if name in ['energy', 'reprate', 'hv']:
            f = getattr(self, 'set_%s' % name)
            self.info('setting %s %s' % (name, value))
            f(value)

            if self.simulation:
                setattr(self, 'update_%s' % name, value)

    def _set_answer_parameters(self, start_addr_value, answer_len):
        '''
        '''

        answer_len = '%04X' % answer_len
        start_addr_value = '%04X' % start_addr_value

        values = [start_addr_value, answer_len]
        cmd = self._build_command(ANSWER_ADDR, values)

        self._send_command(cmd)


    def _build_command(self, start_addr, values):
        '''

        '''

        if isinstance(start_addr, int):
            start_addr = '%04X' % start_addr

        if isinstance(values, int):
            values = ['%04X' % values]

        cmd = start_addr + ''.join(values)
        cmd += ETX
        BCC = computeBCC(cmd)

        cmd = STX + cmd + BCC

        return cmd

    def _send_query(self, s, l):
        '''

        '''

        self._set_answer_parameters(s, l)

        self._start_message()
        r = self.read()
        self.tell(DLE + '1')
        self._end_message()
        return r

    def _send_command(self, cmd):
        '''

        '''
        self._start_message()

        self.ask(cmd)

        self._end_message()

    def _start_message(self):
        '''
        '''
        cmd = 'A' + ENQ
        self.ask(cmd)

    def _end_message(self):
        '''
        '''
        cmd = EOT
        self.ask(cmd)

    def _parse_parameter_answers(self, resp, rstartaddr, answer_len):
        '''
            
        '''
        #split at stx
        rargs = resp.split(STX)
        r, chk = rargs[1].split(ETX)

        #verify checksum
        bcc = computeBCC(r + ETX)
        if int(bcc, 16) != int(chk, 16):
            return

        #r example
        #0005006500000000
        #startaddr, startaddrvalue, ... ,nstartaddr_value

        #remove startaddr and make sure its the one we requested
        startaddr = int(r[:4], 16)
        if rstartaddr != startaddr:
            return

        #trim off start addr
        r = r[4:]
        #ensure len of answers correct
        if answer_len != len(r) / 4:
            return

        args = ()
        for i in range(0, len(r), 4):
            val = r[i:i + 4]
            args += (val,)

        return args

    def _update_parameter_list(self, names, s, l):
        '''
            
        '''
        resp = self._send_query(s, l)

        args = self._parse_parameter_answers(resp, s, l)
        kw = {}
        for n, a in zip(names, args):

            v = int(a, 16)
            if isinstance(n, tuple):
                v = n[1](v)
                n = n[0]

            kw[n] = v
        self.trait_set(**kw)


if __name__ == '__main__':
    from src.helpers.logger_setup import setup
    setup('atl')
    a = ATLLaserControlUnit(name='ATLLaserControlUnit',
                          configuration_dir_name='uv')
    a.bootstrap()
    a.laser_off()
#============= EOF ====================================
