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
from src.bakeout.plugins.bakedpy_action_set import BakedpyActionSet
from src.envisage.core.core_ui_plugin import CoreUIPlugin
from src.bakeout.plugins.bakedpy_perspective import BakedpyPerspective

class BakedpyUIPlugin(CoreUIPlugin):
    name = 'Bakedpy'
    id = 'bakedpy_ui'

    def _perspectives_default(self):
        return [BakedpyPerspective]

    def _action_sets_default(self):
        return [BakedpyActionSet]

    def _views_default(self):
        return [self._create_main_view]

    def _create_main_view(self, **kw):
        app = self.application
        man = app.get_service('src.bakeout.bakeout_manager.BakeoutManager')
        args = dict(id='pychron.bakeout.main',
                         name='Main',
                         obj=man
                         )
        return self.traitsuiview_factory(args, kw)

#    def stop(self):
#        app = self.application
#        man = app.get_service('src.bakeout.bakeout_manager.BakeoutManager')


#============= EOF =============================================
