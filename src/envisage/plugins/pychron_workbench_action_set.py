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
class PychronWorkbenchActionSet(WorkbenchActionSet):
    '''
    '''
    id = 'pychron.workbench.action_set'
    base = 'src.envisage.plugins.pychron_workbench_actions'
    actions = [

#               Action(name='Save',
#                      path='MenuBar/File',
#                      class_name='src.envisage.plugins.pychron_workbench_actions.SaveAction'),
#               Action(name='Save As',
#                      path='MenuBar/File',
#                      class_name='src.envisage.plugins.pychron_workbench_actions.SaveAsAction'),
#               Action(name='Logger',
#                      path='MenuBar/Help',
#                      class_name='src.envisage.plugins.pychron_workbench_actions.LoggerAction'),
               Action(name='Help Page',
                      path='MenuBar/Help',
                      class_name='{}.GotoHelpPageAction'.format(base)),
               Action(name='Documentation',
                      path='MenuBar/Help',
                      class_name='{}.DocumentationPageAction'.format(base)),
#               Action(name='API',
#                      path='MenuBar/Help',
#                      class_name='src.envisage.plugins.pychron_workbench_actions.GotoAPIPageAction'),
               #Action(name='Check For Updates',
               #       path='MenuBar/Help',
               #       class_name='src.envisage.plugins.pychron_workbench_actions.OpenUpdateManagerAction'),
#               Action(name='Check For Updates',
#                      path='MenuBar/Help',
#                      class_name='src.envisage.plugins.pychron_workbench_actions.OpenUpdateManagerAction'),
#               Action(name = 'Refresh Source',
#                      path = 'MenuBar/Tools',
#                      class_name = 'src.envisage.plugins.workbench.workbench_actions.RefreshSourceAction'),



               ]
#============= EOF ====================================
