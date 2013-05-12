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
from traits.api import Any, on_trait_change, Event, List
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
from pyface.workbench.action.view_menu_manager import ViewMenuManager
from pyface.tasks.action.task_action import TaskAction
from pyface.action.group import Separator
#============= standard library imports ========================
#============= local library imports  ==========================

class MinimizeAction(TaskAction):
    name = 'Minimize'
    accelerator = 'Ctrl+m'
    def perform(self, event):
        app = self.task.window.application
        app.active_window.control.showMinimized()

class RaiseAction(TaskAction):
    window = Any
    style = 'toggle'
    def perform(self, event):
        self.window.activate()
        self.checked = True

    @on_trait_change('window:deactivated')
    def _on_deactivate(self):
        self.checked = False

class RaiseUIAction(TaskAction):
    style = 'toggle'
    def perform(self, event):
#        self.ui.control.activate()
        self.checked = True


class WindowGroup(Group):
    items = List
    manager = Any
    def _manager_default(self):
        manager = self
        while isinstance(manager, Group):
            manager = manager.parent
        return manager

    def _items_default(self):

        application = self.manager.controller.task.window.application
        application.on_trait_change(self._rebuild, 'active_window, windows, uis[]')

        return []

    def _make_actions(self, vs):
        items = []
        if self.manager.controller.task.window is not None:
            application = self.manager.controller.task.window.application

            added = []
            for vi in application.windows + vs:
                if hasattr(vi, 'active_task'):
                    if vi.active_task:
                        if not vi.active_task.id in added:
                            checked = vi == application.active_window
                            items.append(ActionItem(action=RaiseAction(window=vi,
                                                                       checked=checked,
                                                                       name=vi.active_task.name
                                                                   )))
                            added.append(vi.active_task.id)
                else:
                    items.append(ActionItem(action=RaiseUIAction(
                                                                 name=vi.title,
                                                                 ui=vi,
                                                                 checked=checked,
                                                           )))

        return items

    def _rebuild(self, vs):
        self.destroy()
        if not isinstance(vs, list):
            vs = [vs]
        self.items = self._make_actions(vs)
        self.manager.changed = True


class myTaskWindowLaunchAction(TaskWindowLaunchAction):
    '''
        modified TaskWIndowLaunchAction default behaviour
        
        .perform() previously created a new window on every event. 
        
        now raise the window if its available else create it
    '''

    style = 'toggle'
    def perform(self, event):
        application = event.task.window.application
        for win in application.windows:
            if win.active_task.id == self.task_id:
                win.activate()
                break
        else:
            window = application.create_window(TaskWindowLayout(self.task_id))
            window.open()

        self.checked = True

    @on_trait_change('task:window:opened')
    def _window_opened(self):
        if self.task:
            if self.task_id == self.task.id:
                self.checked = True

    @on_trait_change('task:window:closed')
    def _window_closed(self):
        if self.task:
            if self.task_id == self.task.id:
                self.checked = False

#             window = self.task.window
#             print win, window
#             print self.task_id, self.task.id
#             self.checked=self.task.window==win
#             print window.active_task, self.task
#
#             self.checked = (window is not None
#                             and window.active_task == self.task)

#     @on_trait_change('task:window:opened')
#     def _window_o(self):
#         self.checked=True

#     @on_trait_change('task:window:closed')
#     def _window_c(self):
#         self.checked=False
#         print 'asdfsafdasdf'

#     @on_trait_change('foo')
#     def _update_checked(self):
#         print 'fffff'
#         self.checked=True
# #         if self.task:
#             window = self.task.window
#             self.checked = (window is not None
#                             and window.active_task == self.task)
#         print self.checked
class myTaskWindowLaunchGroup(TaskWindowLaunchGroup):
    '''
        uses myTaskWindowLaunchAction instead of enthoughts TaskWindowLaunchLaunchGroup 
    '''
    def _items_default(self):
        manager = self
        while isinstance(manager, Group):
            manager = manager.parent

        task = manager.controller.task
        application = task.window.application

        items = []
        for factory in application.task_factories:
            for win in application.windows:
                if win.active_task.id == factory.id:
                    checked = True
                    break
            else:
                checked = False

            action = myTaskWindowLaunchAction(task_id=factory.id, checked=checked)

            items.append(ActionItem(action=action))
        return items

class BaseTask(Task):
    def _menu_bar_default(self):
        return self._menu_bar_factory()

    def _view_menu(self):
        view_menu = SMenu(
#                         TaskToggleGroup(),
                          myTaskWindowLaunchGroup(),
#                         TaskWindowToggleGroup(),
                          id='View', name='&View')
        return view_menu

    def _edit_menu(self):
        edit_menu = SMenu(id='Edit', name='&Edit')
        return edit_menu

    def _file_menu(self):
        file_menu = SMenu(id='File', name='&File')
        return file_menu

    def _tools_menu(self):
        tools_menu = SMenu(id='Tools', name='&Tools')
        return tools_menu

    def _window_menu(self):
        window_menu = SMenu(
                          Group(MinimizeAction()),
                          WindowGroup(),
                          name='&Window')

        return window_menu

class BaseManagerTask(BaseTask):
    def _menu_bar_factory(self, menus=None):
        if menus is None:
            menus = tuple()

        mb = SMenuBar(
                      self._file_menu(),
                      self._edit_menu(),
                      self._view_menu(),
                      self._tools_menu(),
                      self._window_menu(),
                      SMenu(
                            id='help.menu',
                           name='&Help'),
#                       SMenu(
#                             ViewMenuManager(),
#                             id='Window', name='&Window'),


#                       *menus
                      )
        if menus:
            for mi in reversed(menus):
                print mi
                mb.items.insert(4, mi)

        return mb

class BaseHardwareTask(BaseManagerTask):
    def _menu_bar_factory(self, menus=None):
        extraction_menu = SMenu(id='Extraction', name='&Extraction')
        return super(BaseHardwareTask, self)._menu_bar_factory(menus=[extraction_menu])
# class BaseManagerTask(BaseTask):
#    manager = Any

#============= EOF =============================================
