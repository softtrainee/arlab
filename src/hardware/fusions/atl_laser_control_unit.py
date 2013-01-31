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



#============= enthought library imports =======================
from traits.api import Bool, Float, Str, Constant, Int
from pyface.timer.api import Timer
#============= standard library imports ========================
#============= local library imports  ==========================
from src.hardware.core.core_device import CoreDevice
from src.hardware.core.checksum_helper import computeBCC
import time
STX = chr(2)
ETX = chr(3)
EOT = chr(4)
ENQ = chr(5)
DLE = chr(16)
ANSWER_ADDR = '0002'


class ATLLaserControlUnit(CoreDevice):
    '''
    '''
    energy_readback = Float
    pressure_readback=Float
    _timer = None
#    _enabled = Bool(False)
#    triggered = Bool(False)
#
#    energy = Float(0)
#    energymin = Constant(0.0)
#    energymax = Constant(15.0)
#    update_energy = Float
#
#    hv = Float(11)
#    hvmin = Constant(11.0)
#    hvmax = Constant(16.0)
#    update_hv = Float(11)
#
#    reprate = Float(100)
#    repratemin = Constant(100.0)
#    repratemax = Constant(300.0)
#    update_reprate = Float(100)
#
#    trigger_modes = ['External I',
#                      'External II',
#                      'Internal'
#                      ]
#    trigger_mode = Str('External I')
#    stablization_modes = ['High Voltage', 'Energy']
#    stablization_mode = Str('High Voltage')
#
#    stop_at_low_e = Bool
#
#    cathode = Float(0.0)
#    reservoir = Float(0.0)
#    missing_pulses = Int(0)
#    halogen_filter = Float(0.0)
#
#    laser_head = Float(0.0)
#    laser_headmin = Constant(0.0)
#    laser_headmax = Constant(7900.0)
#
#    burst = Bool
#    nburst = Int(enter_set=True, auto_set=False)
#    cburst = Int

    def start_update_timer(self):
        '''
        '''
        self.stop_update_timer()
        self._timer = Timer(1000, self._update_parameters)

    def stop_update_timer(self):
        if self._timer:
            self._timer.Stop()

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

#    def trigger_laser(self):
#        '''
#        '''
#        self.start_update_timer()
#
#        self.triggered = True
#
#    def stop_triggering_laser(self):
#        '''
#        '''
#        self.triggered = False

    def laser_on(self):
        '''
        '''
#        self.start_update_timer()
        cmd = self._build_command(11, 1)
        self._send_command(cmd)
#        self.ask('A'+ENQ)
        self._enabled = True

    def laser_off(self):
        '''
        '''
        cmd = self._build_command(11, 0)
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
        self.start_update_timer()

        cmd = self._build_command(11, 3)
        self._send_command(cmd)

    def laser_stop(self):
        self.stop_update_timer()

        cmd = self._build_command(11, 1)
        self._send_command(cmd)


#===============================================================================
# gas handling
#===============================================================================
    def do_auto_vac(self):
#        self.start_auto_vac()
        #wait until idle
        while 1:
            time.sleep(0.5)
            if self.is_idle():
                break
            
    def start_auto_vac(self):
        cmd = self._build_command(14, 11)
        self._send_command(cmd)
        
    def start_auto_gas_exchange(self):

        cmd = self._build_command(14, 11)
        self._send_command(cmd)

    def set_to_idle(self):
        cmd = self._build_command(14, 11)
        self._send_command(cmd)
    
    def is_idle(self):
        status=self.get_gas_status()
        if status is not None:
            istatus=int(status, 16)
            return istatus==0
        #print 'is idle',status, len(status)
           
    def get_gas_status(self):
        r=self._send_query(13, 1)
        return r
        
    def open_valve(self, addr):
        self.info('open valve {}'.format(addr))
        cmd = STX
        self._send_command(cmd)
        
    def close_valve(self, addr):
        self.info('close valve {}'.format(addr))
    
    def _clean_response(self, r):
        handshake=r[:4]
        if handshake=='a'+DLE+'0'+STX:
            chksum=computeBCC(r[4:-1])
            if chr(chksum)==r[-1]:
                return r[8:-2]
            
    def _parse_response(self,resp, l):
        
        if len(resp)==l*4:
            return [int(resp[i:i+4], 16) for i in range(0, len(resp)-3, 4)]
                
        
    def _update_parameters(self):
#        '''
#        '''
        #energy and pressure_readback
        vs=self._send_query(8, 2, verbose=False)
#        vs=self._send_query(30, 2, verbose=False)
        if vs is not None:
            vs=self._parse_response(vs, 2)
            if vs is not None:
                self.energy_readback=vs[0]/10.
                self.pressure_readback=vs[1]
                
        
#        formatter = lambda x:x / 10.0
#        read and set energy and pressure_readback as one block
#        self._update_parameter_list([('energy_readback', formatter)], 8, 1)
##        read and set frequency and hv as one block
#        self._update_parameter_list(['reprate', ('hv', formatter)], 1001, 2)

#        read and set gas action

#    def _anytrait_changed(self, name, value):
#        '''
#
#        '''
#        if name in ['energy', 'reprate', 'hv']:
#            f = getattr(self, 'set_%s' % name)
#            self.info('setting %s %s' % (name, value))
#            f(value)
#
#            if self.simulation:
#                setattr(self, 'update_%s' % name, value)

    def _set_answer_parameters(self, start_addr_value, answer_len, verbose=True):
        '''
        '''

        answer_len = '{:04X}'.format(answer_len)
        start_addr_value = '{:04X}'.format(start_addr_value)

        values = [start_addr_value, answer_len]
        cmd = self._build_command(ANSWER_ADDR, values)

        self._send_command(cmd,verbose=verbose)


    def _build_command(self, start_addr, values):
        '''

        '''

        if isinstance(start_addr, int):
            start_addr = '{:04X}'.format(start_addr)

        if isinstance(values, int):
            values = ('{:04X}'.format(values),)

        cmd = start_addr + ''.join(values)
        cmd += ETX
        BCC = computeBCC(cmd)

        cmd = STX + cmd + chr(BCC)

        return cmd

    def _send_query(self, s, l, verbose=True):
        '''

        '''

        self._set_answer_parameters(s, l,verbose=verbose)
        
        #=self.ask('A'+ENQ, nchars=(l+1)*4+6)
#        self._start_message()
        n=(l+1)*4+6
        cmd='a'+ENQ
#        print 'n',n
        r=self.ask(cmd, nchars=n, verbose=verbose)
#        r = self.read(nchars=n)
        self.tell(DLE + '1',verbose=verbose)
        self._end_message(verbose=verbose)
        return self._clean_response(r)

    def _send_command(self, cmd, verbose=True):
        '''
        '''
        self._start_message(verbose=verbose)
        self.ask(cmd, read_terminator=DLE + '1', verbose=verbose)
        self._end_message(verbose=verbose)

    def _start_message(self, verbose=True):
        '''
        '''
        cmd = 'A' + ENQ
        self.ask(cmd, read_terminator=DLE + '0', verbose=verbose)

    def _end_message(self,verbose=True):
        '''
        '''
        cmd = EOT
        self.tell(cmd,verbose=verbose)

#    def _parse_parameter_answers(self, resp, rstartaddr, answer_len):
#        '''
#        '''
#        #split at stx
#        rargs = resp.split(STX)
#        r, chk = rargs[1].split(ETX)
#
#        #verify checksum
#        bcc = computeBCC(r + ETX)
#        if int(bcc, 16) != int(chk, 16):
#            return
#
#        #r example
#        #0005006500000000
#        #startaddr, startaddrvalue, ... ,nstartaddr_value
#
#        #remove startaddr and make sure its the one we requested
#        startaddr = int(r[:4], 16)
#        if rstartaddr != startaddr:
#            return
#
#        #trim off start addr
#        r = r[4:]
#        #ensure len of answers correct
#        if answer_len != len(r) / 4:
#            return
#
#        args = ()
#        for i in range(0, len(r), 4):
#            val = r[i:i + 4]
#            args += (val,)
#
#        return args

#    def _update_parameter_list(self, names, s, l):
#        '''
#            
#        '''
#        resp = self._send_query(s, l)
#        if resp is not None:
#            args = self._parse_parameter_answers(resp, s, l)
#    #        kw = dict()
#            for n, a in zip(names, args):
#                v = int(a, 16)
#                if isinstance(n, tuple):
#                    v = n[1](v)
#                    n = n[0]
#                self.trait_set(n=v)
#            kw[n] = v
#        self.trait_set(**kw)


if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('atl')
    a = ATLLaserControlUnit(name='ATLLaserControlUnit',
                          configuration_dir_name='uv')
    a.bootstrap()
    a.laser_off()
#============= EOF ====================================
