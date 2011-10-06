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
from traits.api import Bool, List, String, on_trait_change, Dict, Button
from traitsui.api import View, Item, EnumEditor, Group
from apptools.preferences.ui.api import PreferencesPage
from src.helpers.paths import setup_dir
import ConfigParser
import os

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
    system_lock_enabled = Bool

    system_lock_names = None
    system_lock_addresses = None
    add = Button
    
    @on_trait_change('system_lock_name,system_lock_enabled')
    def _update(self, obj, name, new):
        try:
            addr = self.system_lock_addresses[self.system_lock_name]
        except (TypeError, KeyError):
            return 
        
        self.system_lock_address = addr
        
    def __init__(self, *args, **kw):
        super(HardwarePreferencesPage, self).__init__(*args, **kw)

        config = ConfigParser.ConfigParser()
        p = os.path.join(setup_dir, 'system_locks.cfg')
        config.read(p)
        self.system_lock_names = []
        self.system_lock_addresses = dict()

        for sect in config.sections():
            name = config.get(sect, 'name')
            host = config.get(sect, 'host')
            
            self.system_lock_names.append(name)
            self.system_lock_addresses[name] = host
        
        #you must open the preference window and hit ok for changes in the configuration file to be passed into the master preference file    
        if not self.system_lock_addresses.has_key(self.system_lock_name):
            self.system_lock_name = self.system_lock_names[0]
            
        self.system_lock_address = self.system_lock_addresses[self.system_lock_name]
        
        
    def traits_view(self):
        '''
        '''
        v = View(
                 'enable_hardware_server',
                 'auto_find_handle',
                 Item('auto_write_handle', enabled_when='auto_find_handle'),
                 Group(
                       Item('system_lock_name', editor=EnumEditor(values=self.system_lock_names)),
                       Item('system_lock_address', style='readonly', label='Host'),
                       Item('system_lock_enabled'),
                       
                       label='System Lock'
                       ),
                 )
        return v
#============= views ===================================
#============= EOF ====================================
