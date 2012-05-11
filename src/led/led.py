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
from traits.api import HasTraits, Int, Property, Callable

#============= standard library imports ========================

#============= local library imports  ==========================

#============= views ===================================
COLORS = ['red', 'yellow', 'green', 'black']
class LED(HasTraits):
    '''
    '''
    state = Property(depends_on='_state')
    _state = Int
    def _set_state(self, v):
        if isinstance(v, str):
            self._state = COLORS.index(v)
        elif isinstance(v, int):
            self._state = v

        self.trait_property_changed('state', 0)

    def _get_state(self):
        return self._state

class ButtonLED(LED):

    callable = Callable
    def on_action(self):
        self.callable()


#============= EOF ====================================
