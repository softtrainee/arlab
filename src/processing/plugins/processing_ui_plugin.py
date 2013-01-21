#===============================================================================
# Copyright 2012 Jake Ross
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

class ProcessingUIPlugin(CoreUIPlugin):
    def _preferences_pages_default(self):
        from general_age_preferences_page import GeneralAgePreferencesPage
        return [GeneralAgePreferencesPage]

    def _action_sets_default(self):
        '''
        '''
        from processing_action_set import ProcessingActionSet
        return [ProcessingActionSet]


    def _views_default(self):
        return [

#                self._create_control_view,
#                self._create_selection_view,
#                self._create_plotter_options_view
                ]

#    def _perspectives_default(self):
#        from src.processing.plugins.processing_perspective import ProcessingPerspective
#        return [ProcessingPerspective]
#    def _create_selection_view(self, **kw):
#        man = self.application.get_service('src.processing.processing_manager.ProcessingManager')
#        ps = man.processing_selector
#        ps.db.connect()
#
#        args = dict(id='processing.selection',
#                    name='Selection',
#                    obj=ps
#                    )
#        return self.traitsuiview_factory(args, kw)
#
#    def _create_plotter_options_view(self, **kw):
#        man = self.application.get_service('src.processing.processing_manager.ProcessingManager')
#        ps = man.plotter_options_manager
#        args = dict(id='processing.plotter_options',
#                    name='Plot Options',
#                    obj=ps
#                    )
#        return self.traitsuiview_factory(args, kw)
#
#    def _create_control_view(self, **kw):
#        from src.processing.plugins.control_view import ControlView
#        obj = ControlView(application=self.application)
#        args = dict(id='processing.control',
#                  name='Control',
#                  obj=obj
#                  )
#
#        return self.traitsuiview_factory(args, kw)

#============= EOF =============================================
