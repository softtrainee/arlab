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
from traitsui.api import View, Item, HGroup, VGroup, EnumEditor, RangeEditor, Label
from pyface.timer.api import Timer

#=============standard library imports ========================
import struct
import binascii
#=============local library imports  ==========================
from kerr_device import KerrDevice
from src.hardware.core.data_helper import make_bitarray
import time
from globals import globalv

SIGN = ['negative', 'positive']

class KerrMotor(KerrDevice):
    '''
        Base class for motors controller by a kerr microcontroller board
        
    '''
    use_initialize = Bool(True)
    use_hysteresis = Bool(False)
    hysteresis_value = Int(0)

    velocity = Property
    _velocity = Float
    acceleration = Float
    home_delay = Float
    home_velocity = Float
    home_acceleration = Float
    home_position = Float(0)
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

    def _build_gains(self):
        '''
            F6  B004 2003 F401 E803 FF 00 E803 01 01 01
            cmd p    d    i    il   ol cl el   sr db sm
        '''
        p = (45060, 4)
        i = (8195, 4)
        d = (62465, 4)
        il = (59395, 4)
        ol = (255, 2)
        cl = (0, 2)
        el = (59395, 4)
        sr = (1, 2)
        db = (1, 2)
        sm = (1, 2)

        hexfmt = lambda a: '{{:0{}x}}'.format(a[1]).format(a[0])
        return ''.join(['F6'] + map(hexfmt, [p, d, i, il, ol, cl, el, sr, db, sm]))

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

        if config.has_option('General', 'initialize'):
            self.use_initialize = self.config_get(config, 'General', 'initialize', cast='boolean')

    def _start_initialize(self, *args, **kw):
        '''
        '''
        self.info('init {}'.format(self.name))

#        progress = kw['progress'] if 'progress' in kw else None
#        if progress is not None:
#            progress.change_message('Initialize {}'.format(self.name))
#            self.progress = progress
#            progress.increment()

    def _update_position_changed(self):
        try:
            self.progress.change_message('{} position = {}'.format(self.name, self.update_position))
        except AttributeError:
            #self.progress is None
            pass

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
        try:
            self.progress = kw['progress']
        except KeyError:
            pass

        self._start_initialize(*args, **kw)
        self._initialize_(*args, **kw)
        self._finish_initialize()

        if self.nominal_position:
            move_to_nominal = True
            if not globalv.ignore_initialization_questions:

                move_to_nominal = self.confirmation_dialog('Would you like to set the {} motor to its nominal pos of {}'.format(self.name.upper(), self.nominal_position))

            if move_to_nominal:
                #move to the home position
                self._set_data_position(self.nominal_position)
                self.block(4, progress=self.progress)

        #remove reference to progress
        self.progress = None
        self.enabled = True

        return True

    def _clear_bits(self):
        cmd = (self.address, '0b', 100, 'clear bits')
        self._execute_hex_command(cmd)

    def _initialize_(self, *args, **kw):
        '''
        '''

        addr = self.address
        commands = [(addr, '1706', 100, 'stop motor, turn off amp'),
                  (addr, '1800', 100, 'configure io pins'),
                  (addr, self._build_gains(), 100, 'set gains'),
                  (addr, '1701', 100, 'turn on amp'),
                  (addr, '00', 100, 'reset position'),
                  (addr, '0b', 100, 'clear bits')
                  ]
        self._execute_hex_commands(commands)

        self._home_motor(*args, **kw)

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

    def block(self, n=3, tolerance=1, progress=None):
        '''
        '''
        fail_cnt = 0
        pos_buffer = []

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
            time.sleep(0.05)

        if fail_cnt > 5:
            self.warning('Problem Communicating')

    def read_status(self, cb, verbose=True):
        if isinstance(cb, str):
            cb = '{:02x}'.format(int(cb, 2))

        addr = self.address
        cb = '13{}'.format(cb)
        cmd = self._build_command(addr, cb)
        status_byte = self.ask(cmd, is_hex=True,
                                delay=100,
                                nbytes=3,
                                verbose=verbose,
                                info='get status byte')
        return status_byte

    def read_defined_status(self, verbose=True):

        addr = self.address
        cmd = '0E'
        cmd = self._build_command(addr, cmd)
        status_byte = self.ask(cmd, is_hex=True,
                                delay=100,
                                nbytes=2,
                                info='get defined status',
                                verbose=verbose
                                )
        return status_byte

    def _moving(self, verbose=True):
        status_byte = self.read_defined_status(verbose=verbose)

        if status_byte == 'simulation':
            status_byte = 'DFDF'

        status_register = map(int, make_bitarray(int(status_byte[:2], 16)))
        return not status_register[7]

#    def _check_status_byte(self, check_bit):
#        '''
#        return bool 
#        check bit =0 False
#        check bit =1 True
#        '''
#        status_byte = self.read_defined_status()
#
#        if status_byte == 'simulation':
#            status_byte = 'DFDF'
#
#        status_register=map(int,make_bitarray(int(status_byte[:2], 16)))
#        print status_register
#        #2 status bytes were returned ?    
#        if len(status_byte) > 4:
#            status_byte = status_byte[-4:-2]
#
#        else:
#            status_byte = status_byte[:2]
#
#        try:
#            status_register = self._check_bits(int(status_byte, 16))
#        except Exception, e:
#            self.warning('kerr_motor:228 {}'.format(str(e)))
#            status_register = []
#            if self.timer is not None:
#                self.timer.Stop()
#        '''
#        if X bits is set to one its index will be in the status register
#        '''
#
#        return check_bit in status_register

    def _get_motor_position(self, **kw):
        '''
        '''
        addr = self.address
        cmd = '13'
        control = '01'

        cmd = ''.join((cmd, control))
        cmd = (addr, cmd, 100, '')

        pos = self._execute_hex_command(cmd, nbytes=6, **kw)

        #trim off status and checksum bits
        if pos is not None:
            pos = pos[2:-2]
            pos = self._hexstr_to_float(pos)
#            self._motor_position = pos
            return pos

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

        return '{:02x}'.format(int('10010111', 2))

    def _set_motor_position_(self, pos, hysteresis=0):
        '''
        '''
        self._motor_position = pos + hysteresis
        #============pos is in mm===========
        addr = self.address
        cmd = 'D4'
        control = self._load_trajectory_controlbyte()
        position = self._float_to_hexstr(pos)
        v = self._float_to_hexstr(self.velocity)
        a = self._float_to_hexstr(self.acceleration)
#        print cmd, control, position, v, a
        cmd = ''.join((cmd, control, position, v, a))
        cmd = (addr, cmd, 100, 'setting motor steps {}'.format(pos))

        self._execute_hex_command(cmd)

    def _update_position(self):
        '''
        '''

        if self._moving(verbose=False):
            self.enabled = False

#        if not self._check_status_byte(0):
#            self.enabled = False

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
            pos = self._get_motor_position(verbose=False)
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
            
        
            drive a few steps past desired position then back to desired position
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
#                time.sleep(0.250)
                self.timer = Timer(400, self._update_position)
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
        except Exception, e:
            print e

    def control_view(self):
        return View(Label(self.name),
                    Item('data_position', show_label=False,
                         editor=RangeEditor(mode='slider',
                                            low_name='min',
                                            high_name='max')
                         ),
                    Item('update_position', show_label=False,
                         editor=RangeEditor(mode='slider',
                                            format='%0.3f',
                                            low_name='min',
                                            high_name='max', enabled=False),
                         ),

                    )

    def traits_view(self):
        '''
        '''
        return View(VGroup(
                           HGroup('min', 'max', label='Limits', show_border=True),
                           VGroup('velocity', 'acceleration', Item('sign', editor=EnumEditor(values={'negative':-1, 'positive':1})), label='Move', show_border=True),
                           VGroup('home_velocity', 'home_acceleration', 'home_position', label='Home', show_border=True)
                           )
                    )


    def _get_velocity(self):
        return self._velocity

    def _set_velocity(self, v):
        self._velocity = v
#============= EOF ====================================
