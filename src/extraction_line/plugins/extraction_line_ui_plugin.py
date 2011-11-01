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
from traits.api import on_trait_change, Bool
from apptools.preferences.preference_binding import bind_preference

#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_ui_plugin import CoreUIPlugin
from src.envisage.core.action_helper import open_manager

EL_PROTOCOL = 'src.extraction_line.extraction_line_manager.ExtractionLineManager'
BAKEOUT_PROTOCOL = 'src.managers.bakeout_manager.BakeoutManager'
class ExtractionLineUIPlugin(CoreUIPlugin):
    '''
    '''
    open_on_startup = Bool
    def _perspectives_default(self):
        from extraction_line_perspective import ExtractionLinePerspective
        return [ExtractionLinePerspective]

    def _preferences_pages_default(self):
        from extraction_line_preferences_page import ExtractionLinePreferencesPage


        elm = self.application.get_service(EL_PROTOCOL)
        bind_preference(elm, 'managers', 'pychron.extraction_line')

        return [ExtractionLinePreferencesPage]

    def _action_sets_default(self):
        '''
        '''
        from extraction_line_action_set import ExtractionLineActionSet

        return [ExtractionLineActionSet]

    @on_trait_change('application:workbench:active_window')
    def start_manager(self, obj, name, old, new):

        elm = self.application.get_service(EL_PROTOCOL)
        elm.window_x = 10
        elm.window_y = 25
        if hasattr(elm, 'valve_manager'):
            bind_preference(elm.valve_manager, 'query_valve_state', 'pychron.extraction_line.query_valve_state')
        
        bind_preference(self, 'open_on_startup', 'pychron.extraction_line.open_on_startup')
        if self.open_on_startup:
            open_manager(elm)
        
        
        #start device streams
        for dev in elm.devices:
            if dev.is_scanable:
                dev.start_scan()
                
        if elm.gauge_manager:
            elm.gauge_manager.start_scans()
                
#============= views ===================================
#    def _views_default(self):
#        '''
#        '''
#        elm = self.application.get_service(EL_PROTOCOL)
#        views = []
#        if elm:
#            views.append(self._create_canvas_view)
#            views.append(self._create_explanation_view)
#            if elm.gauge_manager:
#                views.append(self._create_gauge_view)
#
#        return views


#============= EOF ====================================
#    def _create_explanation_view(self, **kw):
#        obj = self.application.get_service(EL_PROTOCOL)
#        args = dict(id = 'extraction_line.explanation',
#                         category = 'Extraction Line',
#                       name = 'Explanation',
#                       obj = obj.explanation,
#                       )
#        return self.traitsuiview_factory(args, kw)
#    def _create_canvas_view(self, **kw):
#        '''
#            @type **kw: C{str}
#            @param **kw:
#        '''
#        obj = self.application.get_service(EL_PROTOCOL)
#        bind_preference(obj.canvas, 'style', 'pychron.extraction_line.style')
#        bind_preference(obj.canvas, 'width', 'pychron.extraction_line.width')
#        bind_preference(obj.canvas, 'height', 'pychron.extraction_line.height')
#
#        args = dict(id = 'extraction_line.canvas',
#                         category = 'Extraction Line',
#                       name = 'Canvas',
#                       obj = obj,
#                       )
#
#        return self.traitsuiview_factory(args, kw)
#
#    def _create_gauge_view(self, **kw):
#        '''
#            @type **kw: C{str}
#            @param **kw:
#        '''
#        obj = self.application.get_service(EL_PROTOCOL)
#        args = dict(id = 'pychron.hardware.extraction_line.gauges',
#                         category = 'Extraction Line',
#                       name = 'Gauges',
#                       obj = obj.gauge_manager,
#                       )
#        return self.traitsuiview_factory(args, kw)
