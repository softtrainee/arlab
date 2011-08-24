#============= enthought library imports =======================
from pyface.action.api import Action
#============= standard library imports ========================

#============= local library imports  ==========================

class NewExperimentAction(Action):
    '''
        G{classtree}
    '''
    description = 'Create a new experiment'
    name = 'New Experiment'
    def perform(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        app = event.window.application
        manager = app.get_service('src.experiments.experiments_manager.ExperimentsManager')
        manager.window = event.window
        manager.new()

class OpenExperimentAction(Action):
    '''
        G{classtree}
    '''
    description = 'Create a Open experiment'
    name = 'Open Experiment'
    def perform(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        app = event.window.application
        manager = app.get_service('src.experiments.experiments_manager.ExperimentsManager')
        manager.window = event.window
        manager.open()

class RecallAnalysisAction(Action):
    '''
        G{classtree}
    '''
    description = 'Recall an Analysis'
    name = 'Recall Analysis'
    accelerator = 'Ctrl+R'
    def perform(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        app = event.window.application
        manager = app.get_service('src.experiments.experiments_manager.ExperimentsManager')
        manager.window = event.window
        manager.recall_analysis()

#============= EOF ====================================
