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

#========== standard library imports ==========

#========== local library imports =============
from src.hardware.actuators.gp_actuator import GPActuator
import time

'''
Arduino Firmware syntax

open channel
o<A...Z>
close channel
c<A...Z>
get channel state
s<A...Z>
    response indicator pin high == 1
             indicator pin low == 0
             
             
disable DTR
1. place 110ohm btw 5V and Reset
2. Cut trace on board RESET-EN

DTR will reset arduino when opening an closing a serial connection
    software init reset allows seamless uploading of sketches 
'''

OPEN = 1
CLOSE = 0


class ArduinoGPActuator(GPActuator):
    '''
    Abstract module for Arduino GP Actuator
    
    communicator must be implement FirmataCommunicator protocol
    '''
    def open(self, **kw):
        super(ArduinoGPActuator, self).open(**kw)
        time.sleep(0.5)

    def _parse_response(self, resp):
        if resp is not None:
            resp = resp.strip()

        try:
            return int(resp.strip())
        except (TypeError, ValueError, AttributeError):
            return resp

#        if resp is not None:
#            args = resp.split(',')
#            if len(args) == 2:
#                if args[0] == '1':
#                    try:
#                        return int(args[1][:-1])
#                    except ValueError:
#                        return args[1][:-1]

    def _build_command(self, cmd, pin, state):
#        delimiter = ','
        eol = '\r\n'
        if state is None:
            r = '{} {}{}'.format(cmd, pin, eol)
        else:
            r = '{} {} {}{}'.format(cmd, pin, state, eol)
#        return '{}{}{}{}'.format(cmd, delimiter, value, eol)
        return r

    def open_channel(self, obj):
        pin = obj.address

#        self.ask(self._build_command(4, pin))
#        cmd = (4, pin)
        cmd = ('w', pin, 1)
        self.repeat_command(cmd, ntries=3, check_val='OK')

        return self._check_actuation(obj, True)

    def close_channel(self, obj):
        pin = obj.address
#        self.ask(self._build_command(5, pin))
#        cmd = (5, pin)
        cmd = ('w', pin, 0)
        self.repeat_command(cmd, ntries=3, check_val='OK')
        return self._check_actuation(obj, False)

    def get_channel_state(self, obj):
        indicator_open_pin = int(obj.address) - 1
        indicator_close_pin = int(obj.address) - 2

#        opened = self.ask(self._build_command(6, indicator_open_pin))
#        closed = self.ask(self._build_command(7, indicator_close_pin))
#
#        opened = self._parse_response(opened)
#        closed = self._parse_response(closed)

        opened = self.repeat_command(('r', indicator_open_pin, None),
                                     ntries=3, check_type=int)

        closed = self.repeat_command(('r', indicator_close_pin, None),
                                      ntries=3, check_type=int)

        err_msg = 'Error Ic({}) {} does not agree with Io({}) {}'.format(indicator_close_pin, closed,
                                                                          indicator_open_pin, opened)
        try:
            s = closed + opened
        except (TypeError, ValueError, AttributeError):

            return err_msg

#        print opened
        if s == 1:
            return opened == 0
        else:
            return err_msg

#    def ask(self,*args,**kw):
#        return super(ArduinoGPActuator,self).ask(*args,**kw)

    def _check_actuation(self, obj, request):
        cmd = 'r'
        if request:
            #open pin
            pin = int(obj.address) - 1
        else:
            pin = int(obj.address) - 2

        state = self.repeat_command((cmd, pin, None), ntries=3,
                                    check_type=int)

#        state = self.ask(self._build_command(cmd, pin))
#        state = self._parse_response(state)
        if state is not None:
            return bool(state)
#        if self._communicator.digital_read(pin):
#            return True

#============= EOF ====================================

#    def get_channel_state(self, obj):
#        '''
#        Query the hardware for the channel state
#        
#        '''
#
#        # returns one if channel close  0 for open
#        cmd = 's{}' % obj.name
#        if not self.simulation:
#            s = None
#
#            '''
#            this loop is necessary if the arduino resets on a serial connection
#            
#            see http://www.arduino.cc/cgi-bin/yabb2/YaBB.pl?num=1274205532
#            
#            arduino will reset can be software initiated using the DTR line (low)
#            
#            best solution is to disable DTR reset
#            place 110ohm btw 5V and reset
#            
#            leave loop in because isnt harming anything
#            '''
#            i = 0
#            while s is None and i < 10:
#                s = self.ask(cmd, verbose=False)
#                i += 1
#            if i == 10:
#                s = False
#            else:
#                s = '1'
#            return s
#
#
#    def close_channel(self, obj):
#        '''
#        Close the channel
#        
#        @type obj: C{HValve}
#        @param obj: valve 
#        '''
#        cmd = 'C%s' % obj.name
#        return self.process_cmd(cmd)
#
#    def open_channel(self, obj):
#        '''
#        Open the channel
#        
#        @type obj: C{HValve}
#        @param obj: valve 
#        '''
#        cmd = 'O%s' % obj.name
#        return self.process_cmd(cmd)
#
#    def process_cmd(self, cmd):
#        '''
#            @type cmd: C{str}
#            @param cmd:
#        '''
#        r = self.ask(cmd) == 'success'
#        if self.simulation:
#            r = True
#        return r
#============= EOF =====================================
