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
from traits.api import Bool, String, on_trait_change, Dict, List
from traitsui.api import View, Item, EnumEditor, Group, VGroup, HGroup
from apptools.preferences.ui.api import PreferencesPage


#============= standard library imports ========================

#============= local library imports  ==========================


class HardwarePreferencesPage(PreferencesPage):
    '''
    '''
    name = 'Hardware'
    preferences_path = 'pychron.hardware'
    enable_hardware_server = Bool

    auto_find_handle = Bool
    auto_write_handle = Bool

    system_lock_name = String
    system_lock_address = String
    enable_system_lock = Bool

    system_lock_names = List
    system_lock_addresses = Dict

    @on_trait_change('system_lock_name,enable_system_lock')
    def _update(self, obj, name, new):
        try:
            addr = self.system_lock_addresses[self.system_lock_name]
        except (TypeError, KeyError):
            return

        self.system_lock_address = addr
#        
#    def __init__(self, *args, **kw):
#
#        config = ConfigParser.ConfigParser()
#        p = os.path.join(setup_dir, 'system_locks.cfg')
#        config.read(p)
#        self.system_lock_names = []
#        self.system_lock_addresses = dict()
#
#        for sect in config.sections():
#            name = config.get(sect, 'name')
#            host = config.get(sect, 'host')
#            
#            self.system_lock_names.append(name)
#            self.system_lock_addresses[name] = host
#        
#        pref = ConfigParser.ConfigParser()
#        p = os.path.join(os.path.expanduser('~'), '.enthought', 'pychron', 'preferences.ini')
#        pref.read(p)
#
#        pref.set('pychron.hardware', 'system_lock_names', value)
#        with open(p, 'w') as fp:
#            pref.write(fp)
#        
#        #you must open the preference window and hit ok for changes in the configuration file to be passed into the master preference file    
#        if not self.system_lock_addresses.has_key(self.system_lock_name):
#            self.system_lock_name = self.system_lock_names[0]
#            
#        self.system_lock_address = self.system_lock_addresses[self.system_lock_name]
#        
#        super(HardwarePreferencesPage, self).__init__(*args, **kw)


    def traits_view(self):
        '''
        '''
        v = View(
                 VGroup(
                     Group(
                           HGroup('enable_hardware_server', Item('enable_system_lock', enabled_when='enable_hardware_server')),
                           Group(
                                 Item('system_lock_name', editor=EnumEditor(values=self.system_lock_names),
                                      enabled_when='enable_system_lock'),
                                 Item('system_lock_address', style='readonly', label='Host'),
                                      enabled_when='enable_hardware_server'),
                           label='Remote Hardware Server',
                           show_border=True
                           ),
                     Group(
                           'auto_find_handle',
                           Item('auto_write_handle', enabled_when='auto_find_handle'),
                           label='Serial',
                           show_border=True
                           ),
                        ),
                 scrollable=True
                 )
        return v
#============= views ===================================
#============= EOF ====================================
