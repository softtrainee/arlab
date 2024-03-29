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


def mkaction(name, path):
    def action(cls, event):
        man = cls._get_executor(event)
        if man.load_experiment_queue(path=path):
            open_manager(event.window.application, man)

    nname = '{}Action'.format(name)
    klass = type(nname, (ExperimentAction,), dict(perform=action,
                                                    name=name
                                                    ))
    globals()[nname] = klass


class ExperimentAction(Action):
    def _get_manager(self, event):
        return self._get_service(event, 'src.experiment.manager.ExperimentManager')

    def _get_executor(self, event):
        return self._get_service(event, 'src.experiment.executor.ExperimentExecutor')

    def _get_editor(self, event):
        return self._get_service(event, 'src.experiment.editor.ExperimentEditor')

    def _get_service(self, event, name):
        app = event.window.application
        return app.get_service(name)

#===============================================================================
# scripts
#===============================================================================
class OpenScriptAction(ExperimentAction):
    def perform(self, event):
        script_manager = self._get_service(event, 'src.pyscripts.manager.PyScriptManager')
        editor = script_manager.open_script()
        if editor:
            open_manager(event.window.application, editor)

class NewScriptAction(ExperimentAction):
    def perform(self, event):
        script_editor = self._get_service(event, 'src.pyscripts.manager.PyScriptManager')
#        if script_editor.open_script():
        open_manager(event.window.application, script_editor)

# class ExecuteProcedureAction(ExperimentAction):
#    def perform(self, event):
#        man = self._get_executor(event)
#        man.execute_procedure()

class ExecuteExperimentQueueAction(ExperimentAction):
    name = 'Execute'
    accelerator = 'Ctrl+W'
    def perform(self, event):
        from globals import globalv
        man = self._get_executor(event)
#        man.experiment_set_path = p
#        if man.verify_credentials(inform=False):
        if man.verify_database_connection(inform=True):
            if man.load_experiment_queue(path=globalv.test_experiment_set):
                open_manager(event.window.application, man)


class NewExperimentQueueAction(ExperimentAction):
    '''
    '''
    description = 'Create a new experiment queue'
    name = 'New Experiment Queue'
    accelerator = 'Ctrl+N'
    def perform(self, event):
        '''
        '''
        app = event.window.application
        manager = self._get_editor(event)
        if manager.verify_database_connection(inform=True):
#        if manager.verify_credentials():
            if manager.load():
                manager.new_experiment_queue()
                open_manager(app, manager)


class OpenExperimentQueueAction(ExperimentAction):
    '''
    '''
    description = 'Open experiment set'
    name = 'Open Experiment Queue'
    accelerator = 'Shift+Ctrl+O'
    def perform(self, event):
        '''
        '''
        manager = self._get_editor(event)
        if manager.verify_database_connection(inform=True):
#        if manager.verify_credentials():
            if manager.load():
                if manager.load_experiment_queue(saveable=True):
                    open_manager(event.window.application, manager)


class OpenRecentTableAction(ExperimentAction):
    description = 'Open the Recent Analysis Table'
    name = 'Lab Table'
    accelerator = 'Ctrl+R'

    def perform(self, event):
        manager = self._get_manager(event)
        manager.open_recent()

#===============================================================================
# database actions
#===============================================================================
class LabnumberEntryAction(ExperimentAction):
    accelerator = 'Ctrl+Shift+l'
    def perform(self, event):
        manager = self._get_manager(event)
        if manager.verify_database_connection(inform=True):
            lne = manager._labnumber_entry_factory()
            open_manager(event.window.application, lne)

#===============================================================================
# Utilities
#===============================================================================
class SignalCalculatorAction(ExperimentAction):
    def perform(self, event):
        obj = self._get_service(event, 'src.experiment.signal_calculator.SignalCalculator')
        open_manager(event.window.application, obj)

class OpenImportManagerAction(ExperimentAction):
    accelerator = 'Ctrl+i'
    def perform(self, event):
        obj = self._get_service(event, 'src.experiment.import_manager.ImportManager')
        open_manager(event.window.application, obj)

class OpenExportManagerAction(ExperimentAction):
    accelerator = 'Ctrl+Shift+e'
    def perform(self, event):
        obj = self._get_service(event, 'src.experiment.export_manager.ExportManager')
        open_manager(event.window.application, obj)

class OpenImageBrowserAction(ExperimentAction):
    def perform(self, event):
        browser = self._get_service(event, 'src.media_server.browser.MediaBrowser')
        client = self._get_service(event, 'src.media_server.client.MediaClient')
        browser.client = client
        if browser.load_remote_directory('images'):
            open_manager(event.window.application, browser)



# class AddProjectAction(Action):
#    def perform(self, event):
#        '''
#        '''
#        manager = _get_manager(event)
#
#
# class AddSampleProjectAction(Action):
#    def perform(self, event):
#        '''
#        '''
#        manager = _get_manager(event)
#
#
# class AddMaterialAction(Action):
#    def perform(self, event):
#        '''
#        '''
#        manager = _get_manager(event)
#
#
# class IrradiationChronologyAction(Action):
#    def perform(self, event):
#        '''
#        '''
#        manager = _get_manager(event)
#
#
# class IrradiationProductAction(Action):
#    def perform(self, event):
#        '''
#        '''
#        manager = _get_manager(event)


#============= EOF ====================================
