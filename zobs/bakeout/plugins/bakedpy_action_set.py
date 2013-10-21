# @PydevCodeAnalysisIgnore
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
from envisage.ui.workbench.api import WorkbenchActionSet
from envisage.ui.action.api import Action
#============= standard library imports ========================
#============= local library imports  ==========================
BASE = 'src.bakeout.plugins.bakedpy_actions'


class BakedpyActionSet(WorkbenchActionSet):
    def _actions_default(self):
        actions = [
                   Action(name='New Script...',
                          path='MenuBar/File',
                          class_name='{}:NewScriptAction'.format(BASE)
                          ),
                   Action(name='Open Script...',
                          path='MenuBar/File',
                          class_name='{}:OpenScriptAction'.format(BASE)
                          ),
                   Action(name='Find Bakeout...',
                          path='MenuBar/File',
                          class_name='{}:FindAction'.format(BASE)
                          ),
                   Action(name='Open Latest Bakeout...',
                          path='MenuBar/File',
                          class_name='{}:OpenLatestAction'.format(BASE)

                          )

                   ]
        return actions

#============= EOF =============================================
