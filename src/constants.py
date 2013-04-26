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
PLUSMINUS = u'\u00b1'
try:
    PLUSMINUS_ERR = u'{}Err.'.format(PLUSMINUS)
except UnicodeEncodeError:
    PLUSMINUS = '+/-'
    PLUSMINUS_ERR = '{}Err.'.format(PLUSMINUS)

SIGMA = u'\u03c3'
try:
    SIGMA = u'{}'.format(SIGMA)
except UnicodeEncodeError, e:
    try:
        SIGMA = unicode('\x73', encoding='Symbol')
    except Exception:
        SIGMA = 's'

NULL_STR = '---'
SCRIPT_KEYS = ['measurement', 'post_measurement', 'extraction', 'post_equilibration']
SCRIPT_NAMES = ['{}_script'.format(si) for si in SCRIPT_KEYS]

FIT_TYPES = ['linear', 'parabolic', 'cubic',
             u'average {}SD'.format(PLUSMINUS),
              u'average {}SEM'.format(PLUSMINUS)]
INTERPOLATE_TYPES = ['Preceeding', 'Bracketing Interpolate', 'Bracketing Average']
FIT_TYPES_INTERPOLATE = FIT_TYPES + ['Preceeding', 'Bracketing Interpolate', 'Bracketing Average']
DELIMITERS = {',':'comma', '\t':'tab', ' ':'space'}
AGE_SCALARS = {'Ma':1e6, 'ka':1e3, 'a':1}

import string
seeds = string.ascii_uppercase
ALPHAS = [a for a in seeds] + ['{}{}'.format(a, b)
                                    for a in seeds
                                        for b in seeds]

ARGON_KEYS = ('Ar40', 'Ar39', 'Ar38', 'Ar37', 'Ar36')
#============= EOF =============================================
