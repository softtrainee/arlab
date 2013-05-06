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
from traits.api import HasTraits, Any, List, Either
from traitsui.api import View, Item
from pyface.tasks.task import Task
from src.bakeout.tasks.bakeout_pane import  GraphPane, \
    ControllerPane, ControlsPane, ScanPane
from pyface.tasks.task_layout import TaskLayout, PaneItem, Splitter, Tabbed, \
    VSplitter, HSplitter
from pyface.tasks.action.schema import SMenu, SMenuBar
from pyface.tasks.action.task_action import TaskAction
from pyface.tasks.action.task_toggle_group import TaskToggleGroup
#============= standard library imports ========================
#============= local library imports  ==========================

# class mySplitter(Splitter):
#    items = List(Either(PaneItem, Tabbed, Splitter), pretty_skip=True)

class BakeoutTask(Task):
    id = 'bakeout.main'
    name = 'Bakeout'
    bakeout = Any

    def _default_layout_default(self):
        return TaskLayout(top=VSplitter(
                                   HSplitter(
                                            PaneItem('bakeout.controls'),
                                            PaneItem('bakeout.scan'),
                                            orientation='horizontal'
                                            ),
                                   PaneItem('bakeout.controller',
                                            ),
                                    orientation='vertical'
                                   )
                          )

    def activated(self):
        self.bakeout.reset_general_scan()

    def open_script(self):
        self.bakeout.open_script()

    def new_script(self):
        self.bakeout.new_script()

    def find_bakeout(self):
        self.bakeout.find_bakeout()

    def open_latest_bakeout(self):
        self.bakeout.open_latest_bake()

    def _menu_bar_default(self):
        file_menu = SMenu(
                          TaskAction(name='New Script...',
                                       method='new_script'),
                          TaskAction(name='Open Script...',
                                       method='open_script'),
                          TaskAction(name='Find Bake...',
                                     accelerator='Ctrl+F',
                                     method='find_bakeout'),
                          TaskAction(name='Open Latest Bake...',
                                       method='open_latest_bakeout'),
                          id='File', name='&File'
                          )
        view_menu = SMenu(
#                          TaskToggleGroup(),
                          id='View', name='&View')
        edit_menu = SMenu(id='Edit', name='&Edit')

        mb = SMenuBar(
                      file_menu,
                      view_menu,
                      edit_menu
                      )
        return mb

    def create_central_pane(self):
        bp = GraphPane(model=self.bakeout)
        return bp

    def create_dock_panes(self):
        panes = [
                 ControlsPane(model=self.bakeout),
                 ControllerPane(model=self.bakeout),
                 ScanPane(model=self.bakeout)
                 ]

        return panes
#============= EOF =============================================
