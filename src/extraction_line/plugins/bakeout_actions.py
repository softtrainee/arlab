#============= enthought library imports =======================
from pyface.action.api import Action
from src.envisage.core.action_helper import open_manager

#============= standard library imports ========================

#============= local library imports  ==========================

class OpenBakeoutManagerAction(Action):
    def perform(self, event):
        '''
        '''

        bmanager = self.window.application.get_service('src.managers.bakeout_manager.BakeoutManager')
        bmanager.load_controllers()


        open_manager(bmanager)
#        manager = self.window.application.get_service('src.managers.extraction_line_manager.ExtractionLineManager')
#        manager.show_bakeout_manager(bmanager)
#============= EOF ====================================
