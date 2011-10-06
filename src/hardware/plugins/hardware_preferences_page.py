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
from traits.api import Property, Bool, List, Str, on_trait_change, Dict
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
    
    system_name = Str
    system_names = List
    system_lock_addresses=Dict
    enabled = Bool
    
    system_lock_address = Str
    
    @on_trait_change('system_name,enabled')
    def _system_changed(self):
        try:
            addr = self.system_lock_addresses[self.system_name]
            self.system_lock_address = addr
        except KeyError,e:
            print e
        
    def __init__(self, *args, **kw):
        super(HardwarePreferencesPage, self).__init__(*args, **kw)

        config = ConfigParser.ConfigParser()
        p = os.path.join(setup_dir, 'system_locks.cfg')
        config.read(p)
        self.system_names = []
        self.system_lock_addresses = dict()
        for sect in config.sections():
            name = config.get(sect, 'name')
            host = config.get(sect, 'host')
            
            self.system_names.append(name)
            self.system_lock_addresses[name] = host
        
        if not self.system_name:
            self.system_name=self.system_names[0]
        self.system_lock_address=self.system_lock_addresses[self.system_name]
            
        
    def traits_view(self):
        '''
        '''
        v = View(
                 'enable_hardware_server',
                 'auto_find_handle',
                 Item('auto_write_handle', enabled_when='auto_find_handle'),
                 Group(
                       Item('system_name', editor=EnumEditor(values=self.system_names)),
                       Item('system_lock_address',style='readonly', label='Host'),
                       Item('enabled'),
                       
                       label='Sytem Lock'
                       )
                 )
        return v
#============= views ===================================
#============= EOF ====================================
