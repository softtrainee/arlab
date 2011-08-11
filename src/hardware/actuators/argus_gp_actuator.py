'''
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
'''
#========== standard library imports ==========

#========== local library imports =============
from gp_actuator import GPActuator

class ArgusGPActuator(GPActuator):
    '''
    
    G{classtree}
    '''

#    def initialize(self, *args, **kw):
#        '''
#            @type *args: C{str}
#            @param *args:
#
#            @type **kw: C{str}
#            @param **kw:
#        '''
#        self._communicator._terminator = chr(10)

    def get_channel_state(self, obj):
        '''
        
        '''

        # returns one if channel close  0 for open
#        if isinstance(obj, (str, int)):
#            addr = obj
#        else:
#            addr = obj.address

        cmd = 'GetValveState'

        if not self.simulation:
            s = self.ask(cmd)

            if s is not None:
                if s.strip() == 'True':
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
#        return obj.state

    def close_channel(self, obj):
        ''' 
        '''

        cmd = 'Close {}'.format(obj.name[-1])

        self.tell(cmd)

        return self.get_channel_state(obj) == False


    def open_channel(self, obj):
        '''
        '''
        cmd = 'Open {}'.format(obj.name[-1])

        self.tell(cmd)
        return self.get_channel_state(obj) == True


