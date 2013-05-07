#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import HasTraits, Any
from traitsui.api import View, Item
from src.envisage.tasks.base_task import BaseTask
from src.lasers.tasks.laser_panes import FusionsDiodePane, \
    FusionsDiodeControlPane
from pyface.tasks.task_layout import PaneItem, TaskLayout
from pyface.tasks.action.schema import SMenu
from src.lasers.tasks.laser_actions import OpenScannerAction
#============= standard library imports ========================
#============= local library imports  ==========================

class BaseLaserTask(BaseTask):
    manager = Any
    def activated(self):
        self.manager.stage_manager.keyboard_focus = True

class FusionsTask(BaseLaserTask):
    pass

class FusionsDiodeTask(FusionsTask):
    id = 'pychron.lasers.fusions.diode'
    name = 'Fusions Diode'
    def _default_layout_default(self):
        return TaskLayout(left=PaneItem('fusions.diode.control')
                          )
    def _menu_bar_default(self):
        menus = [SMenu(
                       OpenScannerAction(manager=self.manager,
                                         manager_name='fusions_diode'),
                       id='fusions.diode', name='Diode')
                 ]

        return self._menu_bar_factory(menus)

    def create_central_pane(self):
        return FusionsDiodePane(model=self.manager)
    def create_dock_panes(self):
        return [FusionsDiodeControlPane(model=self.manager)]
#============= EOF =============================================
