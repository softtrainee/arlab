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
from traits.api import Float, Property, Bool, Int, CInt
from traitsui.api import View, Item, HGroup, VGroup, EnumEditor
from pyface.timer.api import Timer

#=============standard library imports ========================
import struct
import binascii
import time
#=============local library imports  ==========================
from kerr_device import KerrDevice

SIGN = ['negative', 'positive']

class KerrMotor(KerrDevice):
    '''
        Base class for motors controller by a kerr microcontroller board
        
    '''
    use_hysteresis = Bool(False)
    hysteresis_value = Int(0)
    velocity = Float
    acceleration = Float
    home_delay = Float
    home_velocity = Float
    home_acceleration = Float
    home_position = Float(0.01)
    min = Float(0)
    max = Float(100)
    steps = Float(137500)
    sign = Float

    enabled = Bool(False)
    timer = None

    data_position = Property(depends_on='_data_position')
    _data_position = Float

    update_position = Float
    nominal_position = Float(0)

    progress = None

    _motor_position = CInt
    doing_hysteresis_correction = False
    def load_additional_args(self, config):
        '''
        '''
        args = [('Motion', 'steps'),
              ('Motion', 'sign'),
              ('Motion', 'velocity'),
              ('Motion', 'acceleration'),

              ('Homing', 'home_delay'),
              ('Homing', 'home_velocity'),
              ('Homing', 'home_acceleration'),
              ('Homing', 'home_position'),
              ('General', 'min'),
              ('General', 'max'),
              ('General', 'nominal_position')

              ]
        for section, key in args:
            self.set_attribute(config, key, section, key, cast='float')

        if config.has_option('Motion', 'hysteresis'):
            self.hysteresis_value = self.config_get(config, 'Motion', 'hysteresis', cast='int')
            self.use_hysteresis = True
        else:
            self.use_hysteresis = False

    def _start_initialize(self, *args, **kw):
        '''
        '''
        self.info('init {}'.format(self.name))
        progress = kw['progress'] if 'progress' in kw else None
        if progress is not None:
            progress.change_message('Initialize {}'.format(self.name))
            self.progress = progress
            progress.increment()


    def _finish_initialize(self):
        '''
        '''
        self._data_position = self.min
        self.update_position = self.min
        if self.sign == -1:
            self._data_position = self.max
            self.update_position = self.max

    def initialize(self, *args, **kw):
        '''
        '''
        self._start_initialize(*args, **kw)
        self._initialize_(*args, **kw)
        self._finish_initialize()
        return True

    def _initialize_(self, *args, **kw):
        '''
        '''

        addr = self.address
        commands = [(addr, '1706', 100, 'stop motor, turn off amp'),
                  (addr, '1800', 100, 'configure io pins'),
                  (addr, 'F6B0042003F401E803FF00E803010101', 100, 'set gains'),
                  (addr, '1701', 100, 'turn on amp'),
                  (addr, '00', 100, 'reset position'),
                  ]
        self._execute_hex_commands(commands)

        self._home_motor(*args, **kw)

    def _home_motor(self, *args, **kw):
        '''
        '''
        progress = None
        if 'progress' in kw:
            progress = kw['progress']
            progress.change_message('Homing {}'.format(self.name))
            progress.increment()
            time.sleep(0.25)

        addr = self.address

        cmd = '94'
        control = 'F6'

        v = self._float_to_hexstr(self.home_velocity)
        a = self._float_to_hexstr(self.home_acceleration)
        move_cmd = ''.join((cmd, control, v, a))


        cmds = [#(addr,home_cmd,10,'=======Set Homing===='),
              (addr, move_cmd, 100, 'Send to Home')]
        self._execute_hex_commands(cmds)


        '''
            this is a hack. Because the home move is in velocity profile mode we cannot use the 0bit of the status byte to 
            determine when the move is complete (0bit indicates when motor has reached requested velocity).
            
            instead we will poll the motor position until n successive positions are equal ie at a limt
        '''

        self.block(4, progress=progress)

        #we are homed and should reset position

        cmds = [(addr, '00', 100, 'reset position')]

        self._execute_hex_commands(cmds)

        #move to the home position
        self._set_data_position(0)

    def block(self, n=3, tolerance=1, progress=None):
        '''
        '''
        fail_cnt = 0
        pos_buffer = []

        if progress is None:
            progress = self.progress

        while not self.parent.simulation:

            pos = self._get_motor_position(verbose=False)

            if progress is not None:
                progress.change_message('{} position = {}'.format(self.name, pos))

            if pos is None:
                fail_cnt += 1
                if fail_cnt > 5:
                    break
                continue

            pos_buffer.append(pos)
            if len(pos_buffer) == n:
                if abs(float(sum(pos_buffer)) / n - pos) < tolerance:
                    break
                else:
                    pos_buffer.pop(0)

        if fail_cnt > 5:
            self.warning('Problem Communicating')

    def _check_status_byte(self, check_bit):
        '''
        return bool 
        check bit =0 False
        check bit =1 True
        '''
        addr = self.address
        cmd = '0E'
        cmd = self._build_command(addr, cmd)
        status_byte = self.ask(cmd, is_hex=True,
                                delay=100,
                                info='get status byte')

        if status_byte == 'simulation':
            status_byte = 'DFDF'

        #2 status bytes were returned ?    
        if len(status_byte) > 4:
            status_byte = status_byte[-4:-2]

        else:
            status_byte = status_byte[:2]

        try:
            status_register = self._check_bits(int(status_byte, 16))
        except Exception, e:
            self.warning('kerr_motor:228 {}'.format(str(e)))
            status_register = []
            if self.timer is not None:
                self.timer.Stop()
        '''
        if X bits is set to one its index will be in the status register
        '''

        return check_bit in status_register

    def _get_motor_position(self, **kw):
        '''
        '''
        addr = self.address
        cmd = '13'
        control = '01'

        cmd = ''.join((cmd, control))
        cmd = (addr, cmd, 100, '')

        pos = self._execute_hex_command(cmd, **kw)

        #trim off status and checksum bits
        if pos is not None:
            pos = pos[2:-2]
            pos = self._hexstr_to_float(pos)
#            self._motor_position = pos
            return pos

    def _set_motor_position_(self, pos, hysteresis=0):
        '''
        '''
        self._motor_position = pos + hysteresis
        #============pos is in mm===========
        addr = self.address
        cmd = 'D4'
        control = '97'

        position = self._float_to_hexstr(pos)

        v = self._float_to_hexstr(self.velocity)
        a = self._float_to_hexstr(self.acceleration)
        cmd = ''.join((cmd, control, position, v, a))
        cmd = (addr, cmd, 100, 'setting motor steps {}'.format(pos))

        self._execute_hex_command(cmd)

    def _update_position(self):
        '''
        '''

        if not self._check_status_byte(0):
            self.enabled = False

        else:
            if self.use_hysteresis and not self.doing_hysteresis_correction:
                    #move to original desired position
                    self._set_motor_position_(self._motor_position - self.hysteresis_value)
                    self.doing_hysteresis_correction = True
            else:
                self.enabled = True
                if self.timer is not None:

                    self.timer.Stop()
                    self.update_position = self._data_position

        if not self.enabled:
            pos = self._get_motor_position()
            if pos is not None:
                pos /= (self.steps * (1 - self.home_position))

                if self.sign == -1:
                    pos = 1 - pos
                pos *= (self.max - self.min)

                pos = max(min(self.max, pos), self.min)

                self.update_position = pos

    def _get_data_position(self):
        '''
        '''
        return  self._data_position
#        return float('%0.3f' % self._data_position)

    def _set_data_position(self, pos):
        '''
           
            this is a better solution than al deinos (mass spec) for handling positioning of a 
            linear drive.  Al sets the focused position from 0-100. this means if you change the drive sign
            (in affect changing the homing position +tive or -tive) you also have to change the focused position 
            
            example 
            drive sign =-1
            home pos= 99
            
            drive sign =1
            home pos = 1
            
            this seems wrong. the solution that follows sets the focused position in % distance from home
            
            focus_beam_pos=0.01 #1%
            dr_sign=1
            
            #normalize the input value to 1
            pos=pos/(max-min)  
            
            if dr_sign==-1:
                pos=1-pos
            
            #scale pos to the total number of motor steps ** minus the focused position in motor steps **
            focus_pos_msteps=motor_steps*focus_pos
            
            pos_msteps= (motor_steps-focus_pos_msteps) * pos
            
            
            @todo: may need a way to account for hystersis/backlash
            
            for zoom drive a few steps past desired position then back to desired position
            this takes out any lash in the gears
            
        '''
        self.info('setting motor in data space {:0.3f}'.format(float(pos)))
        if self._data_position != pos:

            self._data_position = pos

            pos /= float((self.max - self.min))
            if self.sign == -1.0:
                pos = 1 - pos

            npos = int((1 - self.home_position) * self.steps * pos)
            hysteresis = 0
            if self._motor_position < npos:
                #means we are going forward
                if self.use_hysteresis:
                    self.doing_hysteresis_correction = False
                    hysteresis = self.hysteresis_value

            self._set_motor_position_(npos, hysteresis)

            if not self.parent.simulation:
                self.timer = Timer(250, self._update_position)
            else:
                self.update_position = self._data_position

    def _float_to_hexstr(self, f, endianness='little'):
        '''
        '''
        fmt = '%sI' % ('<' if endianness == 'little' else '>')
        return binascii.hexlify(struct.pack(fmt, int(f)))

    def _hexstr_to_float(self, h, endianness='little'):
        '''
        '''
        fmt = '%sI' % ('<' if endianness == 'little' else '>')
        try:
            return struct.unpack(fmt, h.decode('hex'))[0]
        except:
            pass

    def traits_view(self):
        '''
        '''
        return View(VGroup(
                           HGroup('min', 'max', label='Limits', show_border=True),
                           VGroup('velocity', 'acceleration', Item('sign', editor=EnumEditor(values={'negative':-1, 'positive':1})), label='Move', show_border=True),
                           VGroup('home_velocity', 'home_acceleration', 'focal_position', label='Home', show_border=True)
                           )
                    )
#============= EOF ====================================
