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
#from apptools.preferences.preference_binding import bind_preference

#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_ui_plugin import CoreUIPlugin

class SynradCO2UIPlugin(CoreUIPlugin):
    _protocol = 'src.managers.laser_managers.synrad_co2_manager.SynradCO2Manager'

    def _perspectives_default(self):
        from synrad_co2_perspective import SynradCO2Perspective
        return [SynradCO2Perspective]

    def _preferences_pages_default(self):
        from synrad_co2_preferences_page import SynradCO2PreferencesPage
        return [SynradCO2PreferencesPage]

    def _action_sets_default(self):
        from synrad_co2_action_set import SynradCO2ActionSet
        return [SynradCO2ActionSet]

#============= views ==================================
    def _views_default(self):
        service = self.application.get_service(self._protocol)
        views = []
        if service:
            views.append(self.create_control_view)
            #views.append(self.create_stage_view)
            #views.append(self.create_power_map_view)


        return views

#    def create_power_map_view(self, **kw):
#        obj = PowerMapViewer(application = self.application)
#        root = os.path.join(paths.data_dir, 'powermap')
#        obj.set_data_files(root)
#        id = 'power_map'
#        args = dict(id = 'fusions.%s' % id,
#                  category = 'data',
#                  name = id,
#                  obj = obj
#                  )
#        return self.traitsuiview_factory(args, kw)

#    def create_stage_view(self, **kw):
#        obj = self.application.get_service(self._protocol)
#
#        obj = obj.stage_manager
#
#        bind_preference(obj, 'window_width', 'pychron.fusions.laser.window_width')
#        bind_preference(obj, 'window_height', 'pychron.fusions.laser.window_height')
#
#        #only applicable if using video
#        bind_preference(obj, 'video_scaling', 'pychron.fusions.laser.video_scaling')
#
#        id = 'stage'
#        args = dict(id = 'fusions.%s' % id,
#                  category = 'extraction devices',
#                  name = id,
#                  obj = obj
#                  )
#        return self.traitsuiview_factory(args, kw)
#
    def create_control_view(self, **kw):
        obj = self.application.get_service(self._protocol)
        args = dict(id='synrad.control',
                  category='extraction devices',
                  name='Synrad Control',
                  obj=obj.stage_manager
                  )
        return self.traitsuiview_factory(args, kw)

#============= EOF ====================================
