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
# from traits.api import List
# from envisage.ui.workbench.api import WorkbenchApplication
from pyface.api import AboutDialog, SplashScreen
from pyface.image_resource import ImageResource
# from envisage.ui.tasks.tasks_application import TasksApplication
#============= standard library imports ========================
# import copy
#============= local library imports  ==========================
# from src.loggable import Loggable
import os
from pyface.tasks.task_window_layout import TaskWindowLayout
from src.envisage.tasks.base_tasks_application import BaseTasksApplication

class Pychron(BaseTasksApplication):
# class Pychron(TasksApplication, Loggable):
    '''
    '''
    id = 'tasks.pychron.valve'
    name = 'pyValve'


    default_layout = [TaskWindowLayout(
#                                       'pychron.extraction_line',
#                                       'pychron.hardware',
                                       'pychron.lasers.fusions.diode',
                                       size=(800, 800)) ]
    def _about_dialog_default(self):
        '''
        '''
        from src.paths import paths
        p = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        about_dialog = AboutDialog(
                                   image=ImageResource(name='about{}.png'.format(paths.version),
                                              search_path=[p, paths.abouts]
                                            ),
                                   )
        return about_dialog

    def _splash_screen_default(self):
        from src.paths import paths
        p = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        paths.app_resources = p

        sp = SplashScreen(
                          image=ImageResource(name='splash{}.png'.format(paths.version),
                                              search_path=[paths.splashes]
                                            ),
                          )
        return sp

#    def exit(self):
#        uis = copy.copy(self.uis)
#        for ui in uis:
#            try:
#                ui.dispose(abort=True)
#            except AttributeError:
#                pass
#
#        super(Pychron, self).exit()
#    def _started_fired(self):
#        elm = self.get_service('src.extraction_line.extraction_line_manager.ExtractionLineManager')
#        elm.window_x = 25
#        elm.window_y = 25
#        open_manager(elm)
#============= views ===================================
#============= EOF ====================================
