#============= enthought library imports =======================
from pyface.action.api import Action

#============= standard library imports ========================

#============= local library imports  ==========================

class OpenHardwareManagerAction(Action):
    '''
        G{classtree}
    '''
    description = 'Open the hardware manager'
    name = 'Hardware Manager'
    def perform(self, event):
        '''
        '''
        m = self.window.application.get_service('src.managers.hardware_manager.HardwareManager')
        m.edit_traits()
#============= EOF ====================================
