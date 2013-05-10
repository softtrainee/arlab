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
from src.envisage.tasks.base_task import BaseHardwareTask
from src.spectrometer.tasks.spectrometer_panes import ScanPane, ControlsPane
from pyface.tasks.task_layout import TaskLayout, PaneItem, Splitter
# from src.experiment.tasks. import ControlsPane
#============= standard library imports ========================
#============= local library imports  ==========================

class SpectrometerTask(BaseHardwareTask):
    scan_manager = Any
    def _default_layout_default(self):
        return TaskLayout(
                          left=PaneItem('pychron.spectrometer.controls'),
#                          right=Splitter(
#                                         PaneItem('pychron.experiment.stats'),
#                                         PaneItem('pychron.experiment.console'),
#                                         orientation='vertical'
#                                         ),
#                          bottom=PaneItem('pychron.experiment.console'),
#                          top=PaneItem('pychron.experiment.controls')
                          )

    def create_central_pane(self):
        g = ScanPane(
                     model=self.scan_manager,
                     )
        return g

    def create_dock_panes(self):
        return [ControlsPane(model=self.scan_manager)]
#============= EOF =============================================
