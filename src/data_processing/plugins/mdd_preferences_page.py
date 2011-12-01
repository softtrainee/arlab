'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
from traits.api import Int, Enum
from traitsui.api import View, Item, VGroup, HGroup, Group
#============= standard library imports ========================

#============= local library imports  ==========================
#from src.managers.plugins.manager_preferences_page import ManagerPreferencesPage
from apptools.preferences.ui.preferences_page import PreferencesPage

class MDDPreferencesPage(PreferencesPage):
    '''
    '''
    id = 'pychron.mdd.preferences_page'
    name = 'MDD'
    preferences_path = 'pychron.mdd'
    line_width = Int(1)
    plot_type = Enum('scatter', 'line', 'line_scatter')
    def traits_view(self):
        v = View(VGroup(
                     VGroup(
                            Item('line_width'),
                            show_border=True,
                            label='LogR/Ro'
                            ),
                     VGroup(
                           Item('plot_type'),
                           show_border=True,
                           label='Arrhenius')
                 )
                 
                 )
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

