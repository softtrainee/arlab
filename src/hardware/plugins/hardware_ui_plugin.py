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
#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_ui_plugin import CoreUIPlugin
from src.managers.hardware_manager import HardwareManager

class HardwareUIPlugin(CoreUIPlugin):
    '''
    '''
    def _preferences_pages_default(self):
        from hardware_preferences_page import HardwarePreferencesPage
        return [HardwarePreferencesPage]

    def _action_sets_default(self):
        from hardware_action_set import HardwareActionSet
        return [HardwareActionSet]

    def _perspectives_default(self):
        from hardware_perspective import HardwarePerspective
        return [HardwarePerspective]

    def _views_default(self):
        return [self._create_device_list_view,
                self._create_current_device_view
                ]
    def _create_current_device_view(self, *args, **kw):

        manager = self.application.get_service(HardwareManager)
        args = dict(id='hardware.current_device',
                  category='Hardware',
                  name='Current Device',
                  obj=manager,
                  view='current_device_view'
                  )
        return self.traitsuiview_factory(args, kw)
    def _create_device_list_view(self, *args, **kw):

        manager = self.application.get_service(HardwareManager)

        args = dict(id='hardware.devices',
                         category='Hardware',
                       name='Devices',
                       obj=manager
                       )
        return self.traitsuiview_factory(args, kw)

#============= EOF ====================================
