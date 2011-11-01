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
from traits.api import Enum, Float, Range, Bool
from traitsui.api import Item, VGroup, HGroup, Group
#============= standard library imports ========================

#============= local library imports  ==========================
from src.managers.plugins.manager_preferences_page import ManagerPreferencesPage

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
    
    def get_general_group(self):
        return Group(Item('open_on_startup'),
                     HGroup(
                            Item('close_after', enabled_when='enable_close_after'),
                            Item('enable_close_after', show_label=False)
                            ),
                     Item('query_valve_state')
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

#============= views ===================================
#============= EOF =====================================
#    def traits_view(self):
#        '''
#        '''
#
#        cols = [CheckboxColumn(name = 'enabled',
#                             ),
#                ObjectColumn(name = 'name')
#                             ]
#        table_editor = TableEditor(columns = cols)
#
#        devices_group = VGroup(Item('devices', show_label = False,
#                                    editor = table_editor
#                                    ),
#                                label = 'Devices'
#                              )
#        manager_group = VGroup(Item('managers', show_label = False,
#                                    editor = table_editor
#                                    ),
#                                label = 'Managers'
#                              )
#        v = View(
#                 manager_group,
#                 devices_group,
#                 canvas_group,
#                 )
#        return v
#    @on_trait_change('managers.enabled, devices.enabled')
#    def _managers_changed(self, obj, name, old, new):
#        p = os.path.join(initialization_dir, 'extraction_line_initialization.cfg')
#        if not os.path.isfile(p):
#            with open(p, 'w') as f:
#                pass
#
#        #overwrite the extracton_line_initialization file
#        with open(p, 'r') as f:
#
#            config = ConfigParser()
#            config.readfp(f)
#
#            #write the managers
#            ms = []
#            for m in self.managers:
#                t = m.name
#                if not m.enabled:
#                    t = '_%s' % m.name
#                ms.append(t)
#
#            config.set('General', 'managers', ','.join(ms))
#
#            #write the devices
#            ds = []
#            for d in self.devices:
#                t = d.name
#                if not d.enabled:
#                    t = '_%s' % d.name
#                ds.append(t)
#            config.set('General', 'devices', ','.join(ds))
#
#
#        with open(p, 'w') as f:
#            config.write(f)
#
#    def read_config(self):
#        p = os.path.join(initialization_dir, 'extraction_line_initialization.cfg')
#        if os.path.isfile(p):
#            with open(p, 'r') as f:
#
#                config = ConfigParser()
#                config.readfp(f)
#                return config
#
#    def _managers_default(self):
#        # read the config file
#        config = self.read_config()
#        r = []
#        if config is not None:
#            managers = config.get('General', 'managers')
#            for m in managers.split(','):
#                m = m.strip()
#                enabled = not m.startswith('_')
#                if not enabled:
#                    #strip off enabled flag char
#                    m = m[1:]
#                r.append(CItem(enabled = enabled,
#
#                                name = m))
#        return r
#
#    def _devices_default(self):
#        # read the config file
#
#        r = []
#        config = self.read_config()
#        if config is not None:
#            if config.has_option('Genera', 'devices'):
#                devices = config.get('General', 'devices')
#                for d in devices.split(','):
#                    d = d.strip()
#                    enabled = not d.startswith('_')
#                    if not enabled:
#                        #strip off enabled flag char
#                        d = d[1:]
#                    r.append(CItem(enabled = enabled,
#
#                                    name = d))
#
#        return r

#        r = []
#        p = os.path.join(initialization_dir, 'extraction_line_initialization.cfg')
#        if os.path.isfile(p):
#            with open(p, 'r') as f:
#    
#                config = ConfigParser()
#                config.readfp(f)
#                
#                managers = config.get('General', 'managers')
#                for m in managers.split(','):
#                    m = m.strip()
#                    enabled = not m.startswith('_')
#                    if not enabled:
#                        #strip off enabled flag char
#                        m = m[1:]
#                    r.append(CItem(enabled = enabled,
#    
#                                    name = m))
