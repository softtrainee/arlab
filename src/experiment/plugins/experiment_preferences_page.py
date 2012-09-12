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
from traits.api import HasTraits, Str, Password
from traitsui.api import View, Item, TableEditor, Group
from apptools.preferences.ui.preferences_page import PreferencesPage
#============= standard library imports ========================
#============= local library imports  ==========================
class ExperimentPreferencesPage(PreferencesPage):
    preferences_path = 'pychron.experiment'
    username = Str
    password = Password
    host = Str
    remote = Str

    def traits_view(self):
        repo_grp = Group(Item('host'),
                         Item('username'),
                         Item('password'),
                         Item('remote', label='Data directory'),
                         show_border=True, label='Repo')
        return View(
                    repo_grp
                    )
#============= EOF =============================================
