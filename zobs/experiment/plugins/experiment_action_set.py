# @PydevCodeAnalysisIgnore
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
from envisage.ui.action.api import Action  # , Group, Menu, ToolBar
from envisage.ui.workbench.api import WorkbenchActionSet

#============= standard library imports ========================

#============= local library imports  ==========================

BASE = 'src.experiment.plugins.experiment_actions'
PATH = 'MenuBar/Experiment'
QUEUEPATH = 'MenuBar/Experiment/Queue...'

class ExperimentActionSet(WorkbenchActionSet):
    '''
    '''
    id = 'pychron.experiment.action_set'

    def _main_actions(self):
        return [Action(name='New...',
                      path=QUEUEPATH,
                    class_name='{}:NewExperimentQueueAction'.format(BASE)

                    ),
                Action(name='Open...',
                       path=QUEUEPATH,
                       class_name='{}:OpenExperimentQueueAction'.format(BASE)

                       ),
                Action(name='Execute...',
                       path=QUEUEPATH,
                       class_name='{}:ExecuteExperimentQueueAction'.format(BASE)
                       ),
#                Action(name='Execute Procedure...',
#                       path=PATH,
#                       class_name='{}:ExecuteProcedureAction'.format(BASE)
#                       ),
                Action(name='Labnumber Entry...',
                       path=PATH,
                       class_name='{}:LabnumberEntryAction'.format(BASE)
                       ),
#===============================================================================
# Utilities
#===============================================================================
                Action(name='Signal Calculator',
                       path=PATH + '/Utilities',
                       class_name='{}:SignalCalculatorAction'.format(BASE)
                       ),
                Action(name='Import...',
                       path=PATH + '/Utilities',
                       class_name='{}:OpenImportManagerAction'.format(BASE)
                       ),
                Action(name='Export...',
                       path=PATH + '/Utilities',
                       class_name='{}:OpenExportManagerAction'.format(BASE)
                       ),
                Action(name='Image Browser',
                       path=PATH + '/Utilities',
                       class_name='{}:OpenImageBrowserAction'.format(BASE)
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

    def _exec_queue_actions(self):
        '''
            a bit of meta programming
            
            load exp queues from directory
            create an action here and create a subclass of ExperimentAction and 
            add it to the experiment_actions module
            
            experiment_actions provides a conviencence function for this 
            mkaction(name, path)
        '''

        from src.paths import paths
        import os
        actions = []
        p = paths.generic_experiment_dir
        import experiment_actions as exp_actions
        for di in os.listdir(p):
            if di.endswith('.txt'):
                name = os.path.splitext(di)[0]
                name = name.replace(' ', '_')
                path = os.path.join(p, di)
                exp_actions.mkaction(name, path)

#                setattr(exp_actions, '{}Action'.format(name), exp_actions.mkaction(name, path))
                action = Action(name=name,
                                path=PATH + '/Generic',
                                class_name='{}:{}Action'.format(BASE, name)
                                )
                actions.append(action)
        return actions

    def _actions_default(self):
        acs = self._main_actions()
        acs.extend(self._script_actions())
        acs.extend(self._exec_queue_actions())
        return acs
#============= EOF ====================================
