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
#from traits.api import HasTraits, on_trait_change, Str, Int, Float, Button
#from traitsui.api import View, Item, Group, HGroup, VGroup

#============= standard library imports ========================

#============= local library imports  ==========================
from src.scripts.core.core_script_parser import CoreScriptParser
class PowerMapScriptParser(CoreScriptParser):
    def raw_parse(self, args):
        error = None
        sargs = 'Beam, Padding, StepLength, Power'
        e1 = 'Not enough args ' + sargs
        if len(args) < 4:
            error = e1
        elif len(args) == 4 and not args[3]:
            error = e1
        elif len(args) > 4:
            error = 'Too many args ' + sargs
        else:
            error = self._check_number(args)

        return error, args
#============= views ========



#============= views ===================================
#============= EOF ====================================
