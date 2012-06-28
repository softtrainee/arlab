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
from pyface.action.api import Action
#============= standard library imports ========================

#============= local library imports  ==========================

def get_manager(event):
    app = event.window.application
    manager = app.get_service('src.experiment.experiment_manager.ExperimentManager')
    return manager


class ExecuteExperimentAction(Action):
    name = 'Execute'
    def perform(self, event):
        man = get_manager(event)
        man.edit_traits(view='execute_view')


class NewExperimentAction(Action):
    '''
    '''
    description = 'Create a new experiment'
    name = 'New Experiment'

    def perform(self, event):
        '''
        '''
        manager = get_manager(event)
        manager.new_experiment()


class OpenExperimentAction(Action):
    '''
    '''
    description = 'Create a Open experiment'
    name = 'Open Experiment'

    def perform(self, event):
        '''
        '''
        manager = get_manager(event)
        manager.open()


class RecallAnalysisAction(Action):
    '''
    '''
    description = 'Recall an Analysis'
    name = 'Recall Analysis'
    accelerator = 'Ctrl+R'

    def perform(self, event):
        '''
        '''
        manager = get_manager(event)
        manager.recall_analysis()


#===============================================================================
# database actions
#===============================================================================
class AddProjectAction(Action):
    def perform(self, event):
        '''
        '''
        manager = get_manager(event)


class AddSampleProjectAction(Action):
    def perform(self, event):
        '''
        '''
        manager = get_manager(event)


class AddMaterialAction(Action):
    def perform(self, event):
        '''
        '''
        manager = get_manager(event)


class IrradiationChronologyAction(Action):
    def perform(self, event):
        '''
        '''
        manager = get_manager(event)


class IrradiationProductAction(Action):
    def perform(self, event):
        '''
        '''
        manager = get_manager(event)



#============= EOF ====================================
