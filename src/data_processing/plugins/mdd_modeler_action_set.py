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
from envisage.ui.action.api import Action#, Group, Menu, ToolBar
from envisage.ui.workbench.api import WorkbenchActionSet


#============= standard library imports ========================

#============= local library imports  ==========================

class MDDModelerActionSet(WorkbenchActionSet):
    '''
    '''
    id = 'pychron.mdd.action_set'
#    menus = [
#           Menu(name = '&File', path = 'MenuBar')
#           ]
    actions = [

               Action(name='Autoarr',
                      path='MenuBar/MDD',
                    class_name='src.data_processing.plugins.mdd_modeler_actions:AutoarrAction'
                    ),
               Action(name='Autoagemon',
                      path='MenuBar/MDD',
                    class_name='src.data_processing.plugins.mdd_modeler_actions:AutoagemonAction'
                    ),
               Action(name='Autoagefree',
                      path='MenuBar/MDD',
                    class_name='src.data_processing.plugins.mdd_modeler_actions:AutoagefreeAction'
                    ),
               Action(name='Confidence Interval',
                      path='MenuBar/MDD',
                    class_name='src.data_processing.plugins.mdd_modeler_actions:ConfidenceIntervalAction'
                    ),

               Action(name='Parse Autoupdate',
                      path='MenuBar/MDD',
                    class_name='src.data_processing.plugins.mdd_modeler_actions:ParseAutoupdateAction'
                    ),
               Action(name='New Model',
                      path='MenuBar/MDD',
                    class_name='src.data_processing.plugins.mdd_modeler_actions:NewModelAction'
                    ),
             ]
#============= EOF ====================================
