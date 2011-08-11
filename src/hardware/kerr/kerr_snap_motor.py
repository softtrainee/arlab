#=============enthought library imports=======================
#=============standard library imports ========================
#=============local library imports  ==========================
from kerr_motor import KerrMotor
class KerrSnapMotor(KerrMotor):
    '''
    Snap Motor 
    
    '''

    def _initialize_(self, *args, **kw):
        '''
        '''

        addr = self.address
        commands = [(addr, '1706', 100, 'stop motor, turn off amp'),
                 (addr, '1804', 100, 'configure io pins'),
                 (addr, 'F6B0042003F401E803FF00E803010101', 100, 'set gains'),
                 (addr, '1701', 100, 'turn on amp'),
                 (addr, '00', 100, 'reset position')
                 ]
        self._execute_hex_commands(commands)

        self._home_motor(*args, **kw)
