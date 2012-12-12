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
ANALYSIS_MAPPING = dict(ba='Blank Air', bc='Blank Cocktail', bu='Blank Unknown',
                      bg='Background', u='Unknown', c='Cocktail'
                      )

def convert_labnumber(ln):

    if ln in [1, 2, 3, 4, 5, 6]:
        sn = ['Blank_air', 'Blank_cocktail', 'Blank_unknown', 'Background', 'Air', 'Cocktail']
        ln = sn[ln - 1]
#    if ln == 1:
#        ln = 'Blank'
#    elif ln == 2:
#        ln = 'Air'
#    elif ln == 3:
#        ln = 'Cocktail'
#    elif ln == 4:
#        ln = 'Background'
    return ln

def convert_shortname(ln):
    if ln in [1, 2, 3, 4, 5, 6]:
        sn = ['bla', 'blc', 'blu', 'bg', 'a', 'c']
        ln = sn[ln - 1]
#    
#    if ln == 1:
#        ln = 'bl'
#    elif ln == 2:
#        ln = 'a'
#    elif ln == 3:
#        ln = 'c'
#    elif ln == 4:
#        ln = 'bg'
    return ln

def convert_identifier(identifier):
    ids = ['Ba', 'Bc', 'Bu', 'Bg', 'A', 'C']
    l_ids = map(str.lower, ids)
#    ids.extend(map(str.lower, ids))
    if identifier in ids:
        identifier = ids.index(identifier) + 1
    elif identifier in l_ids:
        identifier = l_ids.index(identifier) + 1

#    if identifier == 'Ba':
#        identifier = 1
#    elif identifier == 'A':
#        identifier = 2
#    elif identifier == 'C':
#        identifier = 3
#    elif identifier == 'Bg':
#        identifier = 4
    return identifier

def get_analysis_type(idn):

    idn = idn.lower()

    #check for Bg before B
    if idn.startswith('bg'):
        return 'background'
    elif idn.startswith('ba'):
        return 'blank_air'
    elif idn.startswith('bu'):
        return 'blank_unknown'
    elif idn.startswith('bc'):
        return 'blank_cocktail'
    elif idn.startswith('a'):
        return 'air'
    elif idn.startswith('c'):
        return 'cocktail'
    else:
        return 'unknown'

#============= EOF =============================================
