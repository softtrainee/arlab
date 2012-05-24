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
from src.envisage.core.core_ui_plugin import CoreUIPlugin

BAKEOUT_PROTOCOL = 'src.managers.bakeout_manager.BakeoutManager'

class BakeoutUIPlugin(CoreUIPlugin):
    '''
    '''
#    def _perspectives_default(self):
#        from extraction_line_perspective import ExtractionLinePerspective
#        return [ExtractionLinePerspective]

#    def _preferences_pages_default(self):
#        from extraction_line_preferences_page import ExtractionLinePreferencesPage
#
#
#        elm = self.application.get_service(EL_PROTOCOL)
#        bind_preference(elm, 'managers', 'pychron.extraction_line')
#
#        return [ExtractionLinePreferencesPage]

    def _action_sets_default(self):
        '''
        '''

        from bakeout_action_set import BakeoutActionSet
        return [BakeoutActionSet]


#============= views ===================================



#============= EOF ====================================
