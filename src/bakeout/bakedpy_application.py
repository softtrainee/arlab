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
from traits.api import List
# from envisage.ui.workbench.api import WorkbenchApplication
# from pyface.api import AboutDialog, SplashScreen
# from pyface.image_resource import ImageResource
#============= standard library imports ========================
import copy

#============= local library imports  ==========================
from src.loggable import Loggable
from envisage.ui.tasks.tasks_application import TasksApplication
from pyface.tasks.task_window_layout import TaskWindowLayout
from pyface.splash_screen import SplashScreen
from pyface.image_resource import ImageResource
from src.applications.pychron_application import PychronApplication

class Bakedpy(PychronApplication, Loggable):
    '''
    '''
    id = 'tasks.bakedpy'
    name = 'Bakedpy'

    uis = List
#    def _about_dialog_default(self):
#        '''
#        '''
#        about_dialog = AboutDialog(parent=self.workbench.active_window.control)
#        return about_dialog

#     def _splash_screen_default(self):
#         from src.paths import paths
#         sp = SplashScreen(
#                           image=ImageResource(name='splash.png',
#                                                 search_path=[
#                                                              ]
#                                                 ),
#                           )
#         return sp
    default_layout = [TaskWindowLayout('bakeout',
                                       size=(800, 800)) ]
#    def _prepare_exit(self):
#        self.application_exiting = self
#        try:
#            self._save_state()
#        except Exception, e:
#            self.debug(e)

    def exit(self):

#        super(Bakedpy, self).exit(force=True)
        super(Bakedpy, self).exit()

        uis = copy.copy(self.uis)
        for ui in uis:
            try:
                ui.dispose(abort=True)
            except AttributeError:
                pass
#    def _started_fired(self):
#        elm = self.get_service('src.extraction_line.extraction_line_manager.ExtractionLineManager')
#        elm.window_x = 25
#        elm.window_y = 25
#        open_manager(elm)
#============= views ===================================
#============= EOF ====================================
