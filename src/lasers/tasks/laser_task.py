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
from traitsui.api import View, Item, TextEditor
from src.envisage.tasks.base_task import BaseHardwareTask
from src.lasers.tasks.laser_panes import FusionsDiodePane, \
    FusionsDiodeControlPane, FusionsDiodeStagePane, PulsePane, OpticsPane, \
    FusionsCO2Pane, FusionsCO2StagePane, FusionsCO2ControlPane, \
    FusionsDiodeSupplementalPane
from pyface.tasks.task_layout import PaneItem, TaskLayout, Splitter, Tabbed
# from pyface.tasks.action.schema import SMenu
# from src.lasers.tasks.laser_actions import OpenScannerAction
#============= standard library imports ========================
#============= local library imports  ==========================

class BaseLaserTask(BaseHardwareTask):
    def activated(self):
        if self.manager.stage_manager:
            self.manager.stage_manager.keyboard_focus = True

class FusionsTask(BaseLaserTask):
    def _default_layout_default(self):
        return TaskLayout(left=PaneItem('{}.stage'.format(self.id)),
                          top=Splitter(
                                       PaneItem('{}.control'.format(self.id),
                                                width=200
                                                ),
                                       PaneItem('pychron.lasers.pulse',
                                                width=300),
                                       Tabbed(
                                              PaneItem('pychron.lasers.optics'),
                                              PaneItem('{}.supplemental'.format(self.id))
                                              )
                                       )
                          )

class FusionsCO2Task(FusionsTask):
    id = 'pychron.fusions.co2'
    name = 'Fusions CO2'
    def create_central_pane(self):

        return FusionsCO2Pane(model=self.manager)

    def create_dock_panes(self):
        return [
                FusionsCO2StagePane(model=self.manager),
                FusionsCO2ControlPane(model=self.manager),
                PulsePane(model=self.manager),
                OpticsPane(model=self.manager),
                ]

class FusionsDiodeTask(FusionsTask):
    id = 'fusions.diode'
    name = 'Fusions Diode'

    def create_central_pane(self):
        return FusionsDiodePane(model=self.manager)

    def create_dock_panes(self):
        return [
                 FusionsDiodeStagePane(model=self.manager),
                 FusionsDiodeControlPane(model=self.manager),
                 FusionsDiodeSupplementalPane(model=self.manager),

#                TestPane(model=self.manager),
                PulsePane(model=self.manager),
                OpticsPane(model=self.manager),
                ]
#============= EOF =============================================
