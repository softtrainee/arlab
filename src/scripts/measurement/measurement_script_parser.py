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
class MeasurementScriptParser(CoreScriptParser):
    COMMAND_KEYS = ['MEASURE']
    def _measure_parse(self, linenum, **kw):
        error = None
        lexer = self._lexer
        token = lexer.get_token()
        mass, settle, peak, baseline = token.split(',')
        #print mass, settle, peak

#        kw['settle'] = float(settle)
#        kw['mass'] = float(mass)
#        kw['peak_center'] = True if peak in ['True', 'true', 'T', 't'] else False
#        peak = True if peak in ['True', 'true', 'T', 't'] else False

        return error, float(mass), float(settle), self._to_bool(peak), self._to_bool(baseline)
#============= EOF =============================================
