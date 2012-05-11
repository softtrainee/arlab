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
from envisage.ui.action.api import Action#, Group, Menu, ToolBar
from envisage.ui.workbench.api import WorkbenchActionSet
#============= standard library imports ========================

#============= local library imports  ==========================
class ScriptActionSet(WorkbenchActionSet):
    '''
        G{classtree}
    '''
    id = 'pychron.script.action_set'
    actions = [
               Action(name='New',
                      path='MenuBar/File/Script',
                      class_name='src.scripts.plugins.script_actions:NewScriptAction'),

               Action(name='Run',
                      path='MenuBar/File/Script',
                      class_name='src.scripts.plugins.script_actions:RunScriptAction'),

               Action(name='Power Map',
                      path='MenuBar/File/Script/Open',
                      class_name='src.scripts.plugins.script_actions:PowerMapAction'),

              ]
#============= EOF ====================================
