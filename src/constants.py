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
NULL_STR = '---'
SCRIPT_KEYS = ['measurement', 'post_measurement', 'extraction', 'post_equilibration']
FIT_TYPES = ['linear', 'parabolic', 'cubic', u'average \u00b1SD', u'average \u00b1SEM']
DELIMITERS = {',':'comma', '\t':'tab', ' ':'space'}
AGE_SCALARS = {'Ma':1e6, 'ka':1e3, 'a':1}
#============= EOF =============================================
