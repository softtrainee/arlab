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
from traits.api import HasTraits
from traitsui.api import View, Item
from src.envisage.tasks.base_task import  BaseManagerTask
from src.experiment.tasks.labnumber_entry_panes import LabnumbersPane, \
    IrradiationPane, ImporterPane
from pyface.tasks.task_layout import TaskLayout, PaneItem, Splitter
#============= standard library imports ========================
#============= local library imports  ==========================

class LabnumberEntryTask(BaseManagerTask):
    name = 'Labnumber'
    def _default_layout_default(self):
        return TaskLayout(
#                          left=PaneItem('pychron.experiment.factory'),
#                          right=Splitter(
#                                         PaneItem('pychron.experiment.stats'),
#                                         PaneItem('pychron.experiment.console'),
#                                         orientation='vertical'
#                                         ),
#                          bottom=PaneItem('pychron.experiment.console'),
                          left=Splitter(
                                        PaneItem('pychron.labnumber.irradiation'),
                                        PaneItem('pychron.labnumber.importer'),
                                        orientation='vertical'
                                        )
                          )

    def create_central_pane(self):
        return LabnumbersPane(model=self.manager)

    def create_dock_panes(self):
        return [
                IrradiationPane(model=self.manager),
                ImporterPane(model=self.importer)
                ]

    #===========================================================================
    # GenericActon Handlers
    #===========================================================================
    def save_as(self):
        self.save()

    def save(self):
        self.manager.save()



#============= EOF =============================================
