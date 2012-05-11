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
from src.managers.graph_manager import GraphManager


class GraphUIPlugin(CoreUIPlugin):
#    def _preferences_pages_default(self):
#        from Graph_preferences_page import GraphPreferencesPage
#        return [GraphPreferencesPage]

    def _action_sets_default(self):
        from graph_action_set import GraphActionSet
        return [GraphActionSet]

    def _perspectives_default(self):
        from graph_perspective import GraphPerspective
        return [GraphPerspective]

    def _views_default(self):
        return [self._create_graph_manager_view]

    def _create_graph_manager_view(self, *args, **kw):
        manager = self.application.get_service(GraphManager)

        manager.application = self.application

        args = dict(id='pychron.graph_manager',
                  category='Data',
                  name='GraphManager',
                  obj=manager,
#                  view = 'manager_view'
                  )
        return self.traitsuiview_factory(args, kw)

#============= EOF ====================================
