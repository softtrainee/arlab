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
#============= standard library imports ========================
#============= local library imports  ==========================
from src.constants import NULL_STR

ANALYSIS_MAPPING = dict(ba='Blank Air', bc='Blank Cocktail', bu='Blank Unknown',
                      bg='Background', u='Unknown', c='Cocktail', a='Air'
                      )

# "labnumbers" where extract group is disabled
NON_EXTRACTABLE = dict(ba='Blank Air', bc='Blank Cocktail', bu='Blank Unknown',
                      bg='Background', c='Cocktail', a='Air'
                      )

SPECIAL_NAMES = [NULL_STR, 'Air', 'Cocktail', 'Blank Unknown', 'Blank Air', 'Blank Cocktail', 'Background']
SPECIAL_MAPPING = dict(background='bg', air='a', cocktail='c',
                       blank_air='ba',
                       blank_cocktail='bc',
                       blank_unknown='bu',
                       )
#        sn = ['Blank_air', 'Blank_cocktail', 'Blank_unknown',
#              'Background', 'Air', 'Cocktail']
SPECIAL_IDS = {1:'Blank Air', 2:'Blank Cocktail', 3:'Blank Unknown',
               4:'Background', 5:'Air', 6:'Cocktail'
               }

from ConfigParser import ConfigParser
import os
from src.paths import paths
cp = ConfigParser()
p = os.path.join(paths.setup_dir, 'identifiers.cfg')
if os.path.isfile(p):
    cp.read(p)
    for option in cp.options('AnalysisNames'):
        v = cp.get('AnalysisNames', option)
        labnumber, name = v.split(',')
        ANALYSIS_MAPPING[option] = name
        SPECIAL_NAMES.append(name)
        SPECIAL_MAPPING[name] = option
        SPECIAL_IDS[int(labnumber)] = name

def convert_special_name(name, output='shortname'):
    '''
        input name output shortname
        
        name='Background'
        returns:
            
            if output=='shortname'
                return 'bg'
            else
                return 4 #identifier
    '''
    if isinstance(name, str):
        name = name.lower()
        name = name.replace(' ', '_')

        if name in SPECIAL_MAPPING:
            sn = SPECIAL_MAPPING[name]
            if output == 'labnumber':
                sn = convert_identifier(sn)
            return sn
    else:
        return name

def convert_labnumber(ln):
    '''
        ln is a str  but only special labnumbers cannot be converted to int
        convert number to name
        
    '''
    try:
        ln = int(ln)

        if ln in SPECIAL_IDS:
            ln = SPECIAL_IDS[ln]
    except ValueError:
        pass


    return ln

def convert_shortname(ln):
    '''
        convert number to shortname (a for air, bg for background...)
    '''
    name = convert_labnumber(ln)
    if name is not None:
        ln = next((k for k, v in ANALYSIS_MAPPING.iteritems()
                   if v == name), ln)
    return ln

def convert_identifier(identifier):
    '''
        identifier=='bg, a, ...'
        return  1
    '''
    if identifier in ANALYSIS_MAPPING:
        sname = ANALYSIS_MAPPING[identifier]
        identifier = next((k for k, v in SPECIAL_IDS.iteritems() if v == sname), identifier)

    return identifier

def get_analysis_type(idn):

    idn = idn.lower()
    # check for Bg before B
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
    elif idn.startswith('dg'):
        return 'degas'
    else:
        return 'unknown'

def make_runid(ln, a, s):
    return '{}-{:02n}{}'.format(ln, a, s)

def make_identifier(ln, ed, ms):
    try:
        _ = int(ln)
        return ln
    except ValueError:
        return make_special_identifier(ln, ed, ms)

def make_standard_identifier(ln, modifier, ms, aliquot=None):
    '''
        ln: str or int
        a: int
        modifier: str or int. if int zero pad 
        ms: int or str 
    '''
    if isinstance(ms, int):
        ms='{:02n}'.format(ms)
    try:
        modifier = '{:02n}'.format(modifier)
    except ValueError:
        pass

    d = '{}-{}-{}'.format(ln, modifier, ms)
    if aliquot:
        d = '{}-{:02n}'.format(d, aliquot)
    return d

def make_special_identifier(ln, ed, ms, aliquot=None):
    '''
        ln: str or int
        a: int aliquot
        ms: int mass spectrometer id
        ed: int extract device id
    '''
    if isinstance(ed, int):
        ed='{:02n}'.format(ed)
    if isinstance(ms, int):
        ms='{:02n}'.format(ms)
    
    d = '{}-{}-{}'.format(ln, ed, ms)
    if aliquot:
        d = '{}-{:02n}'.format(d, aliquot)
    return d

def make_rid(ln, a, step=''):
    '''
        if ln can be converted to integer return ln
        else return special_identifier
    '''
    try:
        _ = int(ln)
        return make_runid(ln, a, step)
    except ValueError:
        return '{}-{:02n}'.format(ln, a)
#        return make_special_identifier(ln, ed, ms, aliquot=a)

#============= EOF =============================================
