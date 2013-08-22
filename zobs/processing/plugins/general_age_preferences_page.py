# @PydevCodeAnalysisIgnore
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
from traits.api import Float, Str, Property
from traitsui.api import View, Item, EnumEditor
from apptools.preferences.ui.preferences_page import PreferencesPage

#============= standard library imports ========================
#============= local library imports  ==========================

class GeneralAgePreferencesPage(PreferencesPage):
    name = 'General Age'
    preferences_path = 'pychron.experiment.general_age'
    age_units = Str('Ma')

    def traits_view(self):

        v = View(Item('age_units', editor=EnumEditor(values=['Ma', 'ka'])))
        return v
#============= EOF =============================================
