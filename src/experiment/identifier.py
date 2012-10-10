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
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
#============= local library imports  ==========================
def convert_identifier(identifier):
    if identifier == 'B':
        identifier = 1
    elif identifier == 'A':
        identifier = 2
    elif identifier == 'C':
        identifier = 3
    elif identifier == 'Bg':
        identifier = 4
    return identifier

def get_analysis_type(idn):
    #check for Bg before B
    if idn.startswith('Bg'):
        return 'background'
    elif idn.startswith('B'):
        return 'blank'
    elif idn.startswith('A'):
        return 'air'
    elif idn.startswith('C-'):
        return 'cocktail'
    else:
        return 'unknown'

#============= EOF =============================================
