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
from src.hardware.kerr.kerr_motor import KerrMotor
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
class KerrStepMotor(KerrMotor):
    min = CInt
    max = CInt

    def _build_parameters(self):

        cmd = '56'
        op = (int('00001011', 2), 2)
        mps = (1, 2)
        rcl = (150, 2)
        hcl = (20, 2)
        tl = (0, 2)

        hexfmt = lambda a: '{{:0{}x}}'.format(a[1]).format(a[0])
        bs = [cmd ] + map(hexfmt, [op, mps, rcl, hcl, tl])
        return ''.join(bs)

    def _initialize_(self, *args, **kw):
        addr = self.address
        commands = [
                    (addr, '1706', 100, 'stop motor, turn off amp'),
                    (addr, self._build_parameters(), 100, 'set parameters'),
                    (addr, '1701', 100, 'turn on amp'),
                    (addr, '00', 100, 'reset position')
                    ]
        self._execute_hex_commands(commands)
        
        self._set_motor_position_(100)
#        self._home_motor(*args, **kw)
    
    def _home_motor(self, *args, **kw):
        '''
        '''
        progress = self.progress
        if progress is not None:
            progress = kw['progress']
            progress.increase_max()
            progress.change_message('Homing {}'.format(self.name))
            progress.increment()

        addr = self.address

        cmd = '94'
        control = 'F6'

        v = self._float_to_hexstr(self.home_velocity)
        a = self._float_to_hexstr(self.home_acceleration)
        print self.home_acceleration
        move_cmd = ''.join((cmd, control, v, a))

        cmds = [#(addr,home_cmd,10,'=======Set Homing===='),
              (addr, move_cmd, 100, 'Send to Home')]
        self._execute_hex_commands(cmds)


        '''
            this is a hack. Because the home move is in velocity profile mode we cannot use the 0bit of the status byte to 
            determine when the move is complete (0bit indicates when motor has reached requested velocity).
            
            instead we will poll the motor position until n successive positions are equal ie at a limt
        '''

#        self.block(4, progress=progress)
#
#        #we are homed and should reset position
#
#        cmds = [(addr, '00', 100, 'reset position')]
#
#        self._execute_hex_commands(cmds)
#        
    def _load_trajectory_controlbyte(self):
        '''
           control byte
                7 6 5 4 3 2 1 0
            97- 1 0 0 1 0 1 1 1
            
            0=load pos
            1=load vel
            2=load acce
            3=load pwm
            4=enable servo
            5=profile mode 0=trap 1=vel
            6=direction trap mode 0=abs 1=rel vel mode 0=for. 1=back
            7=start motion now
            
        '''
        return '{:02x}'.format(int('10000111', 2))

    def _get_velocity(self):
        speed = self._velocity #in um/sec
        res = 0.5
        steprate = speed / res
        result = round(steprate / 25)
        result = min(max(1, result), 250)
        print 'calcualtes velocity', result
        return result

#============= EOF =============================================
