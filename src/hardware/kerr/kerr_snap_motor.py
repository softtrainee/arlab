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
