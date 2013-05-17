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
from src.envisage.tasks.base_task_plugin import BaseTaskPlugin
from envisage.ui.tasks.task_factory import TaskFactory
from src.pyscripts.tasks.pyscript_task import PyScriptTask
from envisage.ui.tasks.task_extension import TaskExtension
from pyface.tasks.action.schema_addition import SchemaAddition
from src.pyscripts.tasks.pyscript_actions import OpenPyScriptAction, \
    NewPyScriptAction

#============= standard library imports ========================
#============= local library imports  ==========================

class PyScriptPlugin(BaseTaskPlugin):
    def _my_task_extensions_default(self):
        return [TaskExtension(
#                              task_id='pychron.pyscript',
                              actions=[
                                       SchemaAddition(id='open_script',
                                                    path='MenuBar/File/Open',
                                                    factory=OpenPyScriptAction
                                                    ),
                                       SchemaAddition(id='new_script',
                                                    path='MenuBar/File/New',
                                                    factory=NewPyScriptAction
                                                    )

                                       ])
                ]

    def _tasks_default(self):
        return [TaskFactory(
                            id='pychron.pyscript',
                            name='PyScript',
                            factory=self._task_factory
                            )
                ]

    def _task_factory(self):
        return PyScriptTask()
#============= EOF =============================================
