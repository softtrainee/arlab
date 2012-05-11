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
    attenuation = DelegatesTo('attenuator_motor', prefix='data_position')
    attenuationmin = DelegatesTo('attenuator_motor', prefix='min')
    attenuationmax = DelegatesTo('attenuator_motor', prefix='max')
    update_attenuation = DelegatesTo('attenuator_motor', prefix='update_position')



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
        return KerrMotor(name='attenuator', parent=self)
#============= views ===================================

#============= EOF ====================================
