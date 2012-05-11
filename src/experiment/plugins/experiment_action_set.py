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

BASE = 'src.experiment.plugins.experiment_actions'
PATH = 'MenuBar/Experiment'


class ExperimentActionSet(WorkbenchActionSet):
    '''
    '''
    id = 'pychron.experiment.action_set'
#    menus = [
#           Menu(name = '&File', path = 'MenuBar')
#           ]
    actions = [Action(name='New Experiment',
                      path=PATH,
                    class_name='{}:NewExperimentAction'.format(BASE)

                    ),
                Action(name='Open Experiment',
                       path=PATH,
                       class_name='{}:OpenExperimentAction'.format(BASE)

                       ),
                Action(name='Recall',
                       path=PATH,
                       class_name='{}:RecallAnalysisAction'.format(BASE)

                       ),
                Action(name='Execute',
                       path=PATH,
                       class_name='{}:ExecuteExperimentAction'.format(BASE)

                       )
             ]
#============= EOF ====================================
