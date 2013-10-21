# @PydevCodeAnalysisIgnore
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
from traits.api import Str, Password
from traitsui.api import View, Item
#============= standard library imports ========================

#============= local library imports  ==========================
from apptools.preferences.ui.preferences_page import PreferencesPage

class ArArPreferencesPage(PreferencesPage):
    '''
    '''
    name = 'ArAr'
    preferences_path = 'pychron.arar'

    dbname = Str  # ('massspecdata')
    host = Str  # ('129.138.12.131')
    user = Str  # ('massspec')
    password = Password  # ('DBArgon')
    def traits_view(self):
        v = View(Item('dbname', label='Database'),
                 Item('host'),
                 Item('user'),
                 Item('password'))
        return v
#    def get_general_group(self):
#        return Group(Item('open_on_startup'),
#                     HGroup(
#                            Item('close_after', enabled_when='enable_close_after'),
#                            Item('enable_close_after', show_label=False)
#                            ),
#                     Item('query_valve_state')
#                    )
#
#    def get_additional_groups(self):
#        canvas_group = VGroup(
#                              Item('style', show_label=False),
#                              'width',
#                              'height',
#                              label='Canvas', show_border=True)
#        return [
#
#                canvas_group,
#
#                ]

#============= views ===================================
#============= EOF =====================================

