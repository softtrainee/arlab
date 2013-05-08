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
# from traits.api import HasTraits, Str
# from traitsui.api import View, Item
from pyface.tasks.task import Task
from pyface.tasks.action.schema import SMenu, SMenuBar
# from pyface.tasks.action.task_toggle_group import TaskToggleGroup
# from envisage.ui.tasks.action.task_window_toggle_group import TaskWindowToggleGroup
from envisage.ui.tasks.action.api import TaskWindowLaunchGroup
from pyface.action.api import ActionItem, Group
# from pyface.tasks.action.task_action import TaskAction
from envisage.ui.tasks.action.task_window_launch_group import TaskWindowLaunchAction
from pyface.tasks.task_window_layout import TaskWindowLayout
#============= standard library imports ========================
#============= local library imports  ==========================


class myTaskWindowLaunchAction(TaskWindowLaunchAction):
    '''
        modified TaskWIndowLaunchAction default behaviour
        
        .perform() previously created a new window on every event. 
        
        now raise the window if its available else create ita
    '''

    def perform(self, event):
        application = event.task.window.application
        for win in application.windows:
            if win.active_task.id == self.task_id:
                win.activate()
                break
        else:
            window = application.create_window(TaskWindowLayout(self.task_id))
            window.open()

class myTaskWindowLaunchGroup(TaskWindowLaunchGroup):
    '''
        uses myTaskWindowLaunchAction instead of enthoughts TaskWindowLaunchLaunchGroup 
    '''
    def _items_default(self):
        manager = self
        while isinstance(manager, Group):
            manager = manager.parent
        application = manager.controller.task.window.application

        items = []
        for factory in application.task_factories:
            action = myTaskWindowLaunchAction(task_id=factory.id)
            items.append(ActionItem(action=action))
        return items

class BaseTask(Task):
    def _menu_bar_default(self):
        return self._menu_bar_factory()

    def _menu_bar_factory(self, menus=None):
        if menus is None:
            menus = tuple()

        file_menu = SMenu(id='File', name='&File')
        tools_menu = SMenu(id='Tools', name='&Tools')
        extraction_menu = SMenu(id='Extraction', name='&Extraction')

        view_menu = SMenu(
#                          TaskToggleGroup(),
                          myTaskWindowLaunchGroup(),
#                          TaskWindowToggleGroup(),
                          id='View', name='&View')
        edit_menu = SMenu(id='Edit', name='&Edit')

        mb = SMenuBar(
                      file_menu,
                      view_menu,
                      edit_menu,
                      tools_menu,
                      extraction_menu,
                      *menus
                      )
        return mb
#============= EOF =============================================
