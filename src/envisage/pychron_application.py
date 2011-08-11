#============= enthought library imports =======================
from envisage.ui.workbench.api import WorkbenchApplication
from pyface.api import AboutDialog, SplashScreen
from pyface.image_resource import ImageResource
#from traits.api import List, on_trait_change
#============= standard library imports ========================
import os
from src.envisage.core.action_helper import open_manager
#from envisage.ui.tasks.tasks_application import TasksApplication
#============= local library imports  ==========================
class Pychron(WorkbenchApplication):
#class Pychron(TasksApplication):
    '''
    '''
    id = 'pychron'
    name = 'Pychron'
    beta = False
    def _about_dialog_default(self):
        '''
        '''
        about_dialog = AboutDialog(parent = self.workbench.active_window.control)
        return about_dialog

    def _splash_screen_default(self):

        p = os.path.join(os.path.expanduser('~'), 'Programming',
                        'pychron_beta' if self.beta else 'pychron',
                       'resources')

        sp = SplashScreen(
                          image = ImageResource(name = 'splash.png',
                                                search_path = [p]
                                                )
                          )
        return sp

#    def _started_fired(self):
#        elm = self.get_service('src.extraction_line.extraction_line_manager.ExtractionLineManager')
#        elm.window_x = 25
#        elm.window_y = 25
#        open_manager(elm)
#============= views ===================================
#============= EOF ====================================
