#=============enthought library imports=======================

#=============standard library imports ========================

#=============local library imports  ==========================
from fusions_logic_board import FusionsLogicBoard
from src.hardware.kerr.kerr_thor_motor import KerrThorMotor
class FusionsDiodeLogicBoard(FusionsLogicBoard):
    '''
    '''
    def _set_laser_power(self, p, m):
        '''
        '''
        self.parent._set_laser_power_(p, m)

    def set_enable_onoff(self, onoff):
        '''
        '''
        if onoff:
            cmd = self.prefix + 'DRV0 1'
        else:
            cmd = self.prefix + 'DRV0 0'
        self.ask(cmd)

    def set_interlock_onoff(self, onoff):
        '''
        '''
        if onoff:
            cmd = self.prefix + 'IOWR1 1'
        else:
            cmd = self.prefix + 'IOWR1 0'
        self.ask(cmd)

    def _beam_motor_default(self):
        '''
        '''
        return KerrThorMotor(name = 'beam', parent = self)
#====================== EOF ===========================================