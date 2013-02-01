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
from src.envisage.core.action_helper import open_manager
from globals import globalv


class ExperimentAction(Action):
    def _get_manager(self, event):
        return self._get_service(event, 'src.experiment.experiment_manager.ExperimentManager')

    def _get_executor(self, event):
        return self._get_service(event, 'src.experiment.experiment_executor.ExperimentExecutor')

    def _get_editor(self, event):
        return self._get_service(event, 'src.experiment.experiment_editor.ExperimentEditor')

    def _get_service(self, event, name):
        app = event.window.application
        return app.get_service(name)


class ExecuteProcedureAction(ExperimentAction):
    def perform(self, event):
        man = self._get_executor(event)
        man.execute_procedure()

class ExecuteExperimentSetAction(ExperimentAction):
    name = 'Execute'
    accelerator = 'Ctrl+W'
    def perform(self, event):
        man = self._get_executor(event)
#        man.experiment_set_path = p
        if man.load_experiment_set(path=globalv.test_experiment_set, edit=False):
            open_manager(event.window.application, man)


class NewExperimentSetAction(ExperimentAction):
    '''
    '''
    description = 'Create a new experiment set'
    name = 'New Experiment Set'
    accelerator = 'Ctrl+N'
    def perform(self, event):
        '''
        '''
        manager = self._get_editor(event)
        manager.new_experiment_set()
        open_manager(event.window.application, manager)


class OpenExperimentSetAction(ExperimentAction):
    '''
    '''
    description = 'Open experiment set'
    name = 'Open Experiment Set'
    accelerator = 'Shift+Ctrl+O'
    def perform(self, event):
        '''
        '''
        manager = self._get_editor(event)
#        if manager.load_experiment_set(set_names=True):
        if manager.load_experiment_set(saveable=True):
            open_manager(event.window.application, manager)
#class EnableableAction(Action):
#
#    dirty_traitname = 'dirty'
#    def __init__(self, *args, **kw):
#        super(EnableableAction, self).__init__(*args, **kw)
#        em = self.window.workbench.application.get_service(EXPERIMENT_MANAGER_PROTOCOL)
#        em.on_trait_change(self._update_enabled, self.dirty_traitname)
#        self.enabled = False
#
#    def _update_enabled(self, new):
#        if isinstance(new, bool):
#            self.enabled = new
#        else:
#            self.enabled = new is not None
#
#
#class SaveExperimentSetAction(EnableableAction):
#    '''
#    '''
#    description = 'Save experiment set'
#    name = 'Save Experiment Set'
#
#    def perform(self, event):
#        '''
#        '''
#        manager = _get_manager(event)
#        manager.save_experiment_set()
#
#class SaveAsExperimentSetAction(Action):
##class SaveAsExperimentSetAction(EnableableAction):
#    '''
#    '''
#    description = 'Save as experiment set'
#    name = 'Save As Experiment Set'
#
#    def perform(self, event):
#        '''
#        '''
#        manager = _get_manager(event)
#        manager.save_as_experiment_set()


class OpenRecentTableAction(ExperimentAction):
    description = 'Open the Recent Analysis Table'
    name = 'Lab Table'
    accelerator = 'Ctrl+R'

    def perform(self, event):
        manager = self._get_manager(event)
        manager.open_recent()

class MakePlotSeriesAction(ExperimentAction):
    description = 'Plot series of analysis'
    name = 'Plot Series'
    accelerator = 'Ctrl+P'
    def perform(self, event):
        manager = self._get_manager(event)
        manager.plot_series()
#class RecallAnalysisAction(Action):
#    '''
#    '''
#    description = 'Recall an Analysis'
#    name = 'Recall Analysis'
#    accelerator = 'Ctrl+R'
#
#    def perform(self, event):
#        '''
#        '''
#        manager = _get_manager(event)
##        app = event.window.application
##        man = app.get_service('src.experiment.recall_manager.RecallManager')
#        manager.open_recent()


#===============================================================================
# database actions
#===============================================================================
class LabnumberEntryAction(ExperimentAction):
    accelerator = 'Ctrl+Shift+l'
    def perform(self, event):
        manager = self._get_manager(event)
        lne = manager._labnumber_entry_factory()
        open_manager(event.window.application, lne)

#class AddProjectAction(Action):
#    def perform(self, event):
#        '''
#        '''
#        manager = _get_manager(event)
#
#
#class AddSampleProjectAction(Action):
#    def perform(self, event):
#        '''
#        '''
#        manager = _get_manager(event)
#
#
#class AddMaterialAction(Action):
#    def perform(self, event):
#        '''
#        '''
#        manager = _get_manager(event)
#
#
#class IrradiationChronologyAction(Action):
#    def perform(self, event):
#        '''
#        '''
#        manager = _get_manager(event)
#
#
#class IrradiationProductAction(Action):
#    def perform(self, event):
#        '''
#        '''
#        manager = _get_manager(event)


#============= EOF ====================================
