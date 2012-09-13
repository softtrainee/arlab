#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import HasTraits, CInt
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from src.hardware.kerr.kerr_motor import KerrMotor

class KerrStepMotor(KerrMotor):
    min = CInt
    max = CInt



    def _build_parameters(self):
        cmd = '56'
        op = (int('00000011', 16), 2)
        mps = (10, 2)
        rcl = (10, 2)
        hcl = (10, 2)
        tl = (10, 2)

        hexfmt = lambda a: '{{:0{}x}}'.format(a[1]).format(a[0])
        bs = [cmd ] + map(hexfmt, [op, mps, rcl, hcl, tl])
        return ''.join(bs)

    def initialize(self, *args, **kw):
        addr = self.address
        commands = [
#                    (addr, '1706', 100, 'stop motor, turn off amp'),
                    #(addr, '1804', 100, 'configure io pins'),
                    (addr, self._build_parameters(), 100, 'set parameters'),
#                    (addr, '1701', 100, 'turn on amp'),
                    (addr, '00', 100, 'reset position')
                    ]
        self._execute_hex_commands(commands)

#        self._home_motor(*args, **kw)
#============= EOF =============================================