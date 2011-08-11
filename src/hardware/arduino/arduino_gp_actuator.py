'''
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
'''
#========== standard library imports ==========

#========== local library imports =============
from src.hardware.actuators.gp_actuator import GPActuator

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


class ArduinoGPActuator(GPActuator):
    '''
    Abstract module for the Agilent 34903A GP AgilentGPActuator
    
    G{classtree}
    '''

    def get_channel_state(self, obj):
        '''
        Query the hardware for the channel state
        
        @type addr: C{str}
        @param addr: Agilent type address 
        '''

        # returns one if channel close  0 for open
        cmd = 's%s' % obj.name
        if not self.simulation:
            s = None

            '''
            this loop is necessary if the arduino resets on a serial connection
            
            see http://www.arduino.cc/cgi-bin/yabb2/YaBB.pl?num=1274205532
            
            arduino will reset can be software initiated using the DTR line (low)
            
            best solution is to disable DTR reset
            place 110ohm btw 5V and reset
            
            leave loop in because isnt harming anything
            '''
            i = 0
            while s is None and i < 10:
                s = self.ask(cmd, verbose = False)
                i += 1
            if i == 10:
                s = False
            else:
                s = '1'
            return s


    def close_channel(self, obj):
        '''
        Close the channel
        
        @type obj: C{HValve}
        @param obj: valve 
        '''
        cmd = 'C%s' % obj.name
        return self.process_cmd(cmd)

    def open_channel(self, obj):
        '''
        Open the channel
        
        @type obj: C{HValve}
        @param obj: valve 
        '''
        cmd = 'O%s' % obj.name
        return self.process_cmd(cmd)

    def process_cmd(self, cmd):
        '''
            @type cmd: C{str}
            @param cmd:
        '''
        r = self.ask(cmd) == 'success'
        if self.simulation:
            r = True
        return r



