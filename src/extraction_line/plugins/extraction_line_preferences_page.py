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
from traits.api import Enum, Float, Range, Bool, List, Str
from traitsui.api import Item, VGroup, HGroup, Group, EnumEditor
#============= standard library imports ========================
import os

#============= local library imports  ==========================
from src.managers.plugins.manager_preferences_page import ManagerPreferencesPage
from src.helpers.paths import extraction_line_dir

def get_valve_group_names():
    g = []
    p = os.path.join(extraction_line_dir, 'valve_groups.txt')
    with open(p, 'r') as f:
        for l in f:
            if l.startswith('#'):
                continue
            name = l.strip()

            name = '{}_owner'.format(name)
            g.append(name)

    return g

class ExtractionLinePreferencesPage(ManagerPreferencesPage):
    '''
    '''
    id = 'pychron.extraction_line.preferences_page'
    name = 'Extraction Line'
    preferences_path = 'pychron.extraction_line'
    style = Enum('2D', '3D')
    width = Float(400)
    height = Float(400)
    plugin_name = 'ExtractionLine'
    open_on_startup = Bool
    enable_close_after = Bool
    close_after = Range(0, 60, 60)

    query_valve_state = Bool(True)

    owners = List
    groups = List

    def _groups_default(self):
        g = get_valve_group_names()
        for gi in g:
            self.add_trait(gi, Str(''))
        return g

    def _owners_default(self):
        o = ['']
        from src.helpers.initialization_parser import InitializationParser

        ip = InitializationParser()

        systems = ip.get_systems()
        o = list(zip(*systems)[0])

#        config = ConfigParser()
#        config.read(os.path.join(setup_dir, 'system_locks.cfg'))
#        for s in config.sections():
#            o.append(config.get(s, 'name'))
        return o

#============= views ===================================
    def get_general_group(self):
        valve_grp_grp = VGroup()
        for gi in self.groups:
            valve_grp_grp.content.append(Item(gi, editor=EnumEditor(name='owners')))

        return Group(Item('open_on_startup'),
                     HGroup(
                            Item('close_after', enabled_when='enable_close_after'),
                            Item('enable_close_after', show_label=False)
                            ),
                     Item('query_valve_state'),
                    valve_grp_grp
                    )

    def get_additional_groups(self):
        canvas_group = VGroup(
                              Item('style', show_label=False),
                              'width',
                              'height',
                              label='Canvas', show_border=True)
        return [

                canvas_group,

                ]

#============= EOF =====================================

