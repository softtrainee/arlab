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
SETSPATH = 'MenuBar/Experiment/Sets...'

class ExperimentActionSet(WorkbenchActionSet):
    '''
    '''
    id = 'pychron.experiment.action_set'
#    menus = [
#           Menu(name = '&File', path = 'MenuBar')
#           ]
#    actions = [

    def _main_actions(self):
        return [Action(name='New...',
                      path=SETSPATH,
                    class_name='{}:NewExperimentSetAction'.format(BASE)

                    ),
                Action(name='Open...',
                       path=SETSPATH,
                       class_name='{}:OpenExperimentSetAction'.format(BASE)

                       ),
#                Action(name='Save',
#                       path=SETSPATH,
#                       class_name='{}:SaveExperimentSetAction'.format(BASE)
#
#                       ),
#                Action(name='Save As...',
#                       path=SETSPATH,
#                       class_name='{}:SaveAsExperimentSetAction'.format(BASE)
#
#                       ),

#                Action(name='Lab Table...',
#                       path=PATH + '/Recall',
#                       class_name='{}:OpenRecentTableAction'.format(BASE)
#                       ),

                Action(name='Execute...',
                       path=PATH,
                       class_name='{}:ExecuteExperimentSetAction'.format(BASE)
                       ),
                Action(name='Execute Procedure...',
                       path=PATH,
                       class_name='{}:ExecuteProcedureAction'.format(BASE)
                       ),
                Action(name='Labnumber Entry...',
                       path=PATH,
                       class_name='{}:LabnumberEntryAction'.format(BASE)
                       ),
                Action(name='Signal Calculator',
                       path=PATH + '/Utilities',
                       class_name='{}:SignalCalculatorAction'.format(BASE)
                       )
             ]
    def _script_actions(self):
        return [
                Action(name='New...',
                       path=PATH + '/Scripts',
                       class_name='{}:NewScriptAction'.format(BASE)),
                Action(name='Open...',
                       path=PATH + '/Scripts',
                       class_name='{}:OpenScriptAction'.format(BASE)),
                ]

    def _actions_default(self):
        acs = self._main_actions()
        acs.extend(self._script_actions())
#        di = os.path.join(paths.scripts_dir, 'procedures')
#        ss = []
#        es = []
#        if os.path.isdir(di):
#            ss = [s for s in os.listdir(di)
#                            if not s.startswith('.') and s.endswith('.py')]
#            ss = [Action(name=si, path=PATH + '/Procedures',
#                         class_name='{}:ExecuteProcedureAction'.format(BASE)
#                         ) for si in ss]
#
#
#        di = os.path.join(paths.root_dir, 'experiments')
#        if os.path.isdir(di):
#            es = [s for s in os.listdir(di)
#                            if not s.startswith('.') and s.endswith('.txt')]
#
#            es = [Action(name=si, path=SETSPATH,
#                         class_name='{}:ExecuteExperimentAction'.format(BASE, si.split('.')[0])
#                         ) for si in es]
#
#            for ei in es:
#                print ei.name

        return acs
#============= EOF ====================================
