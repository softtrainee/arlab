#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import CInt
#============= standard library imports ========================
#============= local library imports  ==========================
from src.hardware.kerr.kerr_step_motor import KerrStepMotor
import time
from src.hardware.core.data_helper import make_bitarray
'''
    status byte
    0 1 2 3 4 5 6 7
  1 0 0 0 0 0 0 0 1
  
 18 0 0 0 1 0 0 1 0
 
 0= moving
 1= comm err
 2= amp enable output signal is HIGH
 3= power sense input signal is HIGH
 4= at speed
 5= vel prof mode
 6= trap prof mode
 7= home in progress
 
'''
class KerrCircularStepMotor(KerrStepMotor):
    min = CInt
    max = CInt
    
        
       
#            pos = self.discrete_positions[self.discrete_position]
#            self._set_motor_position_(int(self.discrete_position))

#    def _build_parameters(self):
#        cmd = '56'
#        op = (int(self._assemble_options_byte(), 2), 2)#'00001111'
#        mps = (1, 2)
#        rcl = (self.run_current, 2)
#        hcl = (self.hold_current, 2)
#        tl = (0, 2)
#
#        hexfmt = lambda a: '{{:0{}x}}'.format(a[1]).format(a[0])
#        bs = [cmd ] + map(hexfmt, [op, mps, rcl, hcl, tl])
##        print bs,''.join(bs)
#        return ''.join(bs)

    def _initialize_(self, *args, **kw):
        addr = self.address
        commands = [
                    (addr, '1706', 100, 'stop motor, turn off amp'),
#                    (addr, '1804', 100, 'configure io pins'),
                    (addr, self._build_parameters(), 100, 'set parameters'),
                    (addr, '1701', 100, 'turn on amp'),
                    (addr, '00', 100, 'reset position')
                    ]
        self._execute_hex_commands(commands)
#        time.sleep(5)
#        self._execute_hex_commands([(addr, '1706', 100, 'stop motor, turn off amp')])

        self._home_motor(*args, **kw)

    def _home_motor(self, *args, **kw):
        #start moving
        progress = self.progress
        if progress is not None:
            progress = kw['progress']
            progress.increase_max()
            progress.change_message('Homing {}'.format(self.name))
            progress.increment()

        addr = self.address

        cmd = '34'
#        control = 'F6' #'11110110'
        control = '{:02x}'.format(int('10010110',2))
#        v = self._float_to_hexstr(self.home_velocity)
#        a = self._float_to_hexstr(self.home_acceleration)
        v = '{:02x}'.format(int(self.home_velocity))
        a = '{:02x}'.format(int(self.home_acceleration))

        move_cmd = ''.join((cmd, control, v, a))

        cmds = [#(addr,home_cmd,10,'=======Set Homing===='),
              (addr, move_cmd, 100, 'Send to Limit')]
        self._execute_hex_commands(cmds)
        #poll proximity switch
        while 1:
            time.sleep(0.05)
            if self._get_proximity_limit():
                break

        #stop moving when proximity limit set
        cmds = [(addr, '1707', 100, 'Stop motor'), #leave amp on
                (addr, '00', 100, 'Reset Position')]
        self._execute_hex_commands(cmds)
        
        #start moving
        self._set_motor_position_(1000)
        
        #poll proximity switch
        while 1:
            time.sleep(0.05)
            if not self._get_proximity_limit():
                break
        cmds = [(addr, '1707', 100, 'Stop motor'), #leave amp on
                (addr, '00', 100, 'Reset Position')]
        self._execute_hex_commands(cmds)
        #define homing options
        #stop abruptly on home signal
        home_control_byte = self._load_home_control_byte()
        home_cmd = '19{:02x}'.format(home_control_byte)
        cmds = [(addr, home_cmd, 100, 'Set home options')]
        self._execute_hex_commands(cmds)

        #start moving
        self._set_motor_position_(1000)

        #wait until home signal is set.
        while 1:
            time.sleep(0.05)
            lim = self._read_limits()
            if int(lim[2]) == 1:
                break

        #motor is stopped 
        #reset pos
        self._execute_hex_commands([(addr, '00', 100, 'Reset Position')])

    def _read_limits(self):
        cb = '00001000'
        inb = self.read_status(cb, verbose=False)
        inb = inb[2:-2]
        if inb:
            #resp_byte consists of input_byte
            ba = make_bitarray(int(inb, 16))#, self._hexstr_to_float(rb)
            return ba

    def _get_proximity_limit(self):
        ba = self._read_limits()
        return int(ba[4])

    def _load_home_control_byte(self):
        '''
           control byte
                7 6 5 4 3 2 1 0
            97- 1 0 0 1 0 1 1 1
            0=capture home on limit1
            1=capture home on limit2
            2=turn motor off on home
            3=capture home on home
            4=stop abruptly
            5=stop smoothly
            6,7=not used- clear to 0
        '''

        return int('00011000', 2)

    

#============= EOF =============================================
#            
#    def _load_trajectory_controlbyte(self):
#        '''
#           control byte
#                7 6 5 4 3 2 1 0
#            97- 1 0 0 1 0 1 1 1
#            
#            0=load pos
#            1=load vel
#            2=load acce
#            3=load pwm
#            4=enable servo
#            5=profile mode 0=trap 1=vel
#            6=direction trap mode 0=abs 1=rel vel mode 0=for. 1=back
#            7=start motion now
#            
#        '''
#        return '{:02x}'.format(int('10000111', 2))
#
#    def _get_velocity(self):
#        speed = self._velocity #in um/sec
#        res = 0.5
#        steprate = speed / res
#        result = round(steprate / 25)
#        result = min(max(1, result), 250)
#        print 'calcualtes velocity', result
#        return result
