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
from traits.api import Instance
# from envisage.ui.workbench.api import WorkbenchApplication
from pyface.api import AboutDialog, SplashScreen
from pyface.image_resource import ImageResource
# from envisage.ui.tasks.tasks_application import TasksApplication
#============= standard library imports ========================
# import copy
#============= local library imports  ==========================
# from src.loggable import Loggable
import os
# from pyface.tasks.task_window_layout import TaskWindowLayout
from src.envisage.tasks.base_tasks_application import BaseTasksApplication
# from src.lasers.tasks.laser_preferences import FusionsLaserPreferences

class PychronApplication(BaseTasksApplication):
    '''
    '''
#    id = 'tasks.pychron.diode'
#    name = 'pyDiode'
#
#    default_layout = [
# #                      TaskWindowLayout(
# #                                       'tasks.hardware',
# #                                       size=(700, 500)),
# #                      TaskWindowLayout(
# #                                        'pychron.extraction_line',),
#                      TaskWindowLayout(
#                                        'pychron.experiment',),
#
# #                      TaskWindowLayout(
# # #                                       'pychron.extraction_line',
# # #                                       'pychron.hardware',
# #                                       'pychron.fusions.diode',
# #                                       'pychron.fusions.co2',
# #                                       size=(1150, 650)),
#                       ]

    def _get_resource_root(self):

        path = __file__
        from src.globals import globalv
        if not globalv.debug:
            while os.path.basename(path) != 'Resources':
                path = os.path.dirname(path)
        return path

    def _about_dialog_default(self):
        '''
        '''
        from src.paths import paths
        path = self._get_resource_root()
        about_dialog = AboutDialog(
                                   image=ImageResource(name='about{}.png'.format(paths.version),
                                              search_path=[path, paths.abouts]
                                            ),
                                   )
        return about_dialog

    def _splash_screen_default(self):
        from src.paths import paths
        path = self._get_resource_root()
#        p = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        paths.app_resources = path

        sp = SplashScreen(
                          image=ImageResource(name='splash{}.png'.format(paths.version),
                                              search_path=[path, paths.splashes]
                                            ),
                          )
#        self.debug(paths.version)
#        self.debug(sp.image.search_path)
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
