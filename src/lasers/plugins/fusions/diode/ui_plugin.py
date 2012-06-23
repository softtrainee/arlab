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
#from apptools.preferences.preference_binding import bind_preference

#============= standard library imports ========================

#============= local library imports  ==========================
from src.lasers.plugins.fusions.fusions_laser_ui_plugin import FusionsLaserUIPlugin


DIODE_PROTOCOL = 'src.lasers.laser_managers.fusions_diode_manager.FusionsDiodeManager'

class FusionsDiodeUIPlugin(FusionsLaserUIPlugin):
    name = 'diode'
    id = 'fusions.diode'
    _protocol = DIODE_PROTOCOL

#    def _preferences_pages_default(self):
#        from fusions_diode_preferences_page import FusionsDiodePreferencesPage
#        return [FusionsDiodePreferencesPage]
#    def _action_sets_default(self):
#        '''
#        '''
#        action_sets = []
#        diode = self.application.get_service(DIODE_PROTOCOL)
#        if diode:
#            from fusions_laser_action_set import FusionsLaserActionSet
#            action_sets.append(FusionsLaserActionSet)
#
#        return action_sets
#    def _views_default(self):
#        views = super(FusionsDiodeUIPlugin, self)._views_default()
#
#
#        views.append(self.create_control_module_view)
#        return views
#
#    def create_control_module_view(self, **kw):
#        obj = self.application.get_service(self._protocol)
#        obj = obj.control_module_manager
#        id = 'control_module'
#        args = dict(id = 'fusions.%s' % id,
#                  category = 'extraction devices',
#                  name = id,
#                  obj = obj
#                  )
#        return self.traitsuiview_factory(args, kw)
#    def create_diode_stage_view(self, **kw):
#        return self._create_stage_manager_view(DIODE_PROTOCOL, 'stage', **kw)
#
#    def create_diode_view(self, **kw):
#        return self._create_laser_manager_view(DIODE_PROTOCOL, 'laser_control', **kw)
#
#


#============= views ===================================
#============= EOF ====================================
