#============= enthought library imports =======================
from traits.api import Instance, DelegatesTo


#============= standard library imports ========================
import os
#============= local library imports  ==========================
from fusions_logic_board import FusionsLogicBoard
from src.hardware.kerr.kerr_motor import KerrMotor

class FusionsUVLogicBoard(FusionsLogicBoard):
    '''
        G{classtree}
    '''
    attenuator_motor = Instance(KerrMotor)
    attenuation = DelegatesTo('attenuator_motor', prefix = 'data_position')
    attenuationmin = DelegatesTo('attenuator_motor', prefix = 'min')
    attenuationmax = DelegatesTo('attenuator_motor', prefix = 'max')
    update_attenuation = DelegatesTo('attenuator_motor', prefix = 'update_position')



    def load_additional_args(self, config):
        '''
            @type config: C{str}
            @param config:
        '''
#        super(FusionsUVLogicBoard, self).load_additional_args(config)
        FusionsLogicBoard.load_additional_args(self, config)
        a = self.config_get(config, 'Motors', 'attenuator')
        if a is not None:
            self.attenuator_motor.load(os.path.join(self.configuration_dir_path, a))

        return True

    def _attenuator_motor_default(self):
        '''
        '''
        return KerrMotor(name = 'attenuator', parent = self)
#============= views ===================================

#============= EOF ====================================
