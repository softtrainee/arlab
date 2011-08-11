#============= enthought library imports =======================
from pyface.action.api import Action

#============= standard library imports ========================

#============= local library imports  ==========================
MDD_PROTOCOL = 'src.data_processing.modeling.modeler_manager.ModelerManager'
class RunModelAction(Action):
    '''
        G{classtree}
    '''
    description = 'Run a MDD model with using a current Run Configuration'
    name = 'Run Model'
    def perform(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        app = event.window.application
        manager = app.get_service(MDD_PROTOCOL)
        manager.window = event.window
        manager.run_model()

class RunConfigurationAction(Action):
    '''
        G{classtree}
    '''
    description = 'Edit a run configuration'
    name = 'Run Configuration'
    def perform(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        app = event.window.application
        manager = app.get_service(MDD_PROTOCOL)
        manager.window = event.window
        manager.open_run_configuration()

class ParseAutoupdateAction(Action):
    '''
        G{classtree}
    '''
    description = 'Parse an autoupdate file'
    name = 'Parse Autoupdate'
    def perform(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        app = event.window.application
        manager = app.get_service(MDD_PROTOCOL)
        manager.window = event.window
        manager.parse_autoupdate()

class AddModelerAction(Action):
    '''
        G{classtree}
    '''
    description = 'Add another modeler tab'
    name = 'Add Modeler'
    def perform(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        app = event.window.application
        manager = app.get_service(MDD_PROTOCOL)
        manager.window = event.window
        manager.add_modeler()
class NewModelAction(Action):
    '''
        G{classtree}
    '''
    description = 'Parse an autoupdate file'
    name = 'Parse Autoupdate'
    def perform(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        app = event.window.application
        manager = app.get_service(MDD_PROTOCOL)
        manager.window = event.window
        manager.new_modeler()




#============= EOF ====================================
