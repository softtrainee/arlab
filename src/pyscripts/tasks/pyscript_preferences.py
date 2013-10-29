#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import Bool
from traitsui.api import View, Item
from envisage.ui.tasks.preferences_pane import PreferencesPane

from src.envisage.tasks.base_preferences_helper import BasePreferencesHelper

# from src.pychron_constants import PLUSMINUS
#============= standard library imports ========================
#============= local library imports  ==========================

class PyScriptPreferences(BasePreferencesHelper):
    name = 'Scripts'
    preferences_path = 'pychron.pyscript'
    auto_detab = Bool(True)


class PyScriptPreferencesPane(PreferencesPane):
    category = 'Scripts'
    model_factory = PyScriptPreferences

    def traits_view(self):
        v = View(Item('auto_detab'))
        return v

        #============= EOF =============================================
