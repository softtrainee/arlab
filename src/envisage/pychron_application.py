'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
from traits.api import List
from envisage.ui.workbench.api import WorkbenchApplication
from pyface.api import AboutDialog, SplashScreen
from pyface.image_resource import ImageResource
#from traits.api import List, on_trait_change
#============= standard library imports ========================
import os
from src.helpers.paths import pychron_src_dir
#from envisage.ui.tasks.tasks_application import TasksApplication
#============= local library imports  ==========================
class Pychron(WorkbenchApplication):
#class Pychron(TasksApplication):
    '''
    '''
    id = 'pychron'
    name = 'Pychron'
    beta = False

    uis = List
    def _about_dialog_default(self):
        '''
        '''
        about_dialog = AboutDialog(parent=self.workbench.active_window.control)
        return about_dialog

    def _splash_screen_default(self):

        p = os.path.join(
                         pychron_src_dir,
                       'resources'
                       )
        sp = SplashScreen(
                          image=ImageResource(name='splash.png',
                                                search_path=[p]
                                                )
                          )
        return sp

    def exit(self):
        for ui in self.uis:
            ui.dispose()

        super(Pychron, self).exit()
#    def _started_fired(self):
#        elm = self.get_service('src.extraction_line.extraction_line_manager.ExtractionLineManager')
#        elm.window_x = 25
#        elm.window_y = 25
#        open_manager(elm)
#============= views ===================================
#============= EOF ====================================
