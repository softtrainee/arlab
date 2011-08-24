#============= enthought library imports =======================
from pyface.action.api import Action

#============= standard library imports ========================

#============= local library imports  ==========================
SM_PROTOCOL = 'src.scripts.core.scripts_manager.ScriptsManager'
def get_manager(event):
    manager = event.window.application.get_service(SM_PROTOCOL)
    manager.window = event.window
    return manager

class RunScriptAction(Action):
    description = 'Run Script'
    accelerator = 'Ctrl+R'
    def perform(self, event):
        manager = get_manager(event)
        manager.run()
class NewScriptAction(Action):
    '''
        G{classtree}
    '''
    description = 'New Script'
    accelerator = 'Ctrl+N'
    def perform(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        manager = get_manager(event)


        #manager.script_package = 'src.scripts.bakeout_script'
        #manager.script_klass = 'BakeoutScript'

        manager.new()




class OpenScriptAction(Action):
    '''
        G{classtree}
    '''
    description = 'Open Script'
    accelerator = 'Ctrl+O'
    def perform(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        manager = get_manager(event)

        manager.open()

class PowerMapAction(Action):
    '''
    '''
    description = 'Open Power Map'

    def perform(self, event):
        manager = get_manager(event)
        manager.script_klass = 'PowerMapScript'
        manager.script_package = 'src.scripts.laser.power_map_script'

        manager.open()
#
#class SaveScriptAction(Action):
#    description = 'Save Script'
#    accelerator = 'Ctrl+S'
#    def perform(self, event):
#        manager = event.window.application.get_service('src.scripts.scripts_manager.ScriptsManager')
#        manager.window = event.window
#        manager.save_script()
#
#============= EOF ====================================
