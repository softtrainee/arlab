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
from src.spectrometer.tasks.spectrometer_panes import ScanPane, ControlsPane, \
    ReadoutPane, IntensitiesPane
from pyface.tasks.task_layout import TaskLayout, PaneItem, Splitter, Tabbed
from pyface.tasks.action.schema import SMenu
from src.spectrometer.tasks.spectrometer_actions import PeakCenterAction
# from src.experiment.tasks. import ControlsPane
#============= standard library imports ========================
#============= local library imports  ==========================

class SpectrometerTask(BaseHardwareTask):
    scan_manager = Any
    name = 'Scan'
    def prepare_destroy(self):
        self.scan_manager.stop_scan()

    def activated(self):
        self.scan_manager.setup_scan()

    def _menu_bar_factory(self, menus=None):
        measure_menu = SMenu(
                             PeakCenterAction(),
                             id='Measure', name='&Measure',
                             before='help.menu'
                             )
        return super(BaseHardwareTask, self)._menu_bar_factory(menus=[measure_menu])


    def _default_layout_default(self):
        return TaskLayout(
                          left=Splitter(
                                        PaneItem('pychron.spectrometer.controls'),
                                        Tabbed(PaneItem('pychron.spectrometer.intensities'),
                                               PaneItem('pychron.spectrometer.readout')),
                                        orientation='vertical'
                                        )

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
        return [ControlsPane(model=self.scan_manager),
                ReadoutPane(model=self.scan_manager),
                IntensitiesPane(model=self.scan_manager)
                ]
#============= EOF =============================================
