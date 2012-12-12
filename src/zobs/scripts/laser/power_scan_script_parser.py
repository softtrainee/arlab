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

#============= standard library imports ========================

#============= local library imports  ==========================
from src.scripts.core.core_script_parser import CoreScriptParser
class PowerScanScriptParser(CoreScriptParser):
    def parse(self, text, check_header=True):


        errors = []
        if check_header and '----' not in text:
            self.headerindex = None
            errors = [('', 0, 'No header defined')]
        else:
            if isinstance(text, str):
                text = text.split('\n')

            if self.headerindex is not None:
                text = text[self.headerindex:]
        errors += super(PowerScanScriptParser, self).parse(text, check_header=check_header)
#        errors += CoreScriptParser.parse(self, text, check_header=check_header)
        return errors

    def raw_parse(self, args):
        error = None
        sargs = 'Power, Duration(sec) or StartPower, EndPower, Step, Duration(sec)'
        e1 = 'Not enough args ' + sargs
        if len(args) < 2 or (len(args) == 2 and not args[1]):
            error = e1
        elif len(args) == 3:
            error = e1
        elif len(args) == 4 and not args[3]:
            error = e1
        elif len(args) > 4:
            error = 'Too many args ' + sargs
        else:
            error = self._check_number(args)

        return error, args
#============= EOF ====================================
