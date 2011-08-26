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
from traits.api import HasTraits, Bool, Instance, List, Dict
from envisage.api import ExtensionPoint
#============= standard library imports ========================
#============= local library imports  ==========================
from src.envisage.core.core_plugin import CorePlugin
from src.remote_hardware.remote_hardware_manager import RemoteHardwareManager
from apptools.preferences.preference_binding import bind_preference
from src.managers.hardware_manager import HardwareManager

class Preference(HasTraits):
    pass

class SerialPreference(Preference):
    auto_find_handle = Bool
    auto_write_handle = Bool

class DevicePreferences(HasTraits):
    serial_preference = Instance(SerialPreference)
    def _serial_preference_default(self):
        return SerialPreference()

class HardwarePlugin(CorePlugin):
    '''
        
    '''
    id = 'pychron.hardware'
    managers = ExtensionPoint(List(Dict),
                              id = 'pychron.hardware.managers')

    def _service_offers_default(self):
        '''
        '''
        so = self.service_offer_factory(
                          protocol = HardwareManager,
                          factory = self._hardware_manager_factory)

        return [so]

    def _hardware_manager_factory(self):
        return HardwareManager(application = self.application)

    def start(self):
        '''
        '''
        if self.managers:
            from src.initializer import Initializer
            dp = DevicePreferences()
            afh = self.application.preferences.get('pychron.hardware.auto_find_handle')
            awh = self.application.preferences.get('pychron.hardware.auto_write_handle')
            if afh is not None:
                toBool = lambda x: True if x == 'True' else False
                dp.serial_preference.auto_find_handle = toBool(afh)
                dp.serial_preference.auto_write_handle = toBool(awh)

            ini = Initializer(device_prefs = dp)

            for m in self.managers:
                ini.add_initialization(m)

            #any loaded managers will be registered as services
            ini.run(application = self.application)

            #create the hardware server
            rhs = RemoteHardwareManager(application = self.application)
            bind_preference(rhs, 'enable_hardware_server', 'pychron.hardware.enable_hardware_server')
            rhs.bootstrap()

    def stop(self):
        if self.managers:
            for m in self.managers:
                man = m['manager']
                man.kill()
                man.close_ui()

#============= EOF =============================================
