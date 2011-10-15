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
from traits.api import on_trait_change
#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_ui_plugin import CoreUIPlugin
from src.envisage.core.action_helper import open_manager

class FusionsLaserUIPlugin(CoreUIPlugin):

    def _perspectives_default(self):
        from fusions_laser_perspective import FusionsLaserPerspective
        return [FusionsLaserPerspective]
    
    def _preferences_pages_default(self):
        
        klass = 'Fusions{}PreferencesPage'.format(self.name.capitalize())
        module = __import__('src.lasers.plugins.fusions.{}.preferences_page'.format(self.name), fromlist=[klass])
        
        return [getattr(module, klass)]
    def _action_sets_default(self):
#        from fusions_laser_action_set import FusionsLaserActionSet
        
        klass = 'Fusions{}ActionSet'.format(self.name.capitalize())
        module = __import__('src.lasers.plugins.fusions.{}.action_set'.format(self.name), fromlist=[klass])
        
        return [getattr(module, klass)]
#        return [FusionsLaserActionSet]

#============= views ==================================
#    def _views_default(self):
#        service = self.application.get_service(self._protocol)
#        views = []
#        if service:
#            pass
#            #views.append(self.create_control_view)
#            #views.append(self.create_stage_view)
#            #views.append(self.create_power_map_view)
#
#
#        return views
    
    @on_trait_change('application:workbench:active_window')
    def start_manager(self, obj, name, old, new):
        lm = self.application.get_service(self._protocol)
        
        pref = 'pychron.fusions.{}.open_on_startup'.format(self.name)
        if self.application.preferences.get(pref) == 'True':
            open_manager(lm)

        for dev in lm.devices:
            if dev.is_scanable:
                dev.start_scan()
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
#    def create_control_view(self, **kw):
#        obj = self.application.get_service(self._protocol)
#        id = 'laser_control'
#        args = dict(id = 'fusions.%s' % id,
#                  category = 'extraction devices',
#                  name = id,
#                  obj = obj
#                  )
#        return self.traitsuiview_factory(args, kw)

#============= EOF ====================================
