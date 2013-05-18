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
from src.processing.processor import Processor
from src.processing.tasks.processing_task import ProcessingTask
from envisage.ui.tasks.task_extension import TaskExtension
from pyface.tasks.action.schema_addition import SchemaAddition
from src.processing.tasks.processing_actions import FindAction, IdeogramAction
from src.processing.tasks.recall_task import RecallTask
#============= standard library imports ========================
#============= local library imports  ==========================

class ProcessingPlugin(BaseTaskPlugin):
    def _service_offers_default(self):
        process_so = self.service_offer_factory(
                                              protocol=Processor,
#                                              factory=Processor
                                              factory=self._processor_factory
                                              )
        return [process_so]

    def _my_task_extensions_default(self):
        return [
                TaskExtension(
                              actions=[
                                       SchemaAddition(
                                                      id='find_action',
                                                      factory=FindAction,
                                                      path='MenuBar/File'
                                                      ),
                                       SchemaAddition(
                                                      id='new_ideogram_action',
                                                      factory=IdeogramAction,
                                                      path='MenuBar/File/New'
                                                      )
                                       ]
                              )

                ]
    def _tasks_default(self):
        return [
                TaskFactory(id='pychron.processing',
                            factory=self._task_factory,
                            name='Processing',
                            accelerator='Ctrl+P'
                            ),
#                TaskFactory(id='pychron.recall',
#                            factory=self._recall_task_factory,
#                            name='Analysis',
# #                            accelerator='Ctrl+P'
#                            ),
                ]

    def _processor_factory(self):
        return Processor(application=self.application)

    def _recall_task_factory(self):
        return RecallTask()

    def _task_factory(self):
#        processor = self.application.get_service(Processor)
        return ProcessingTask(application=self.application)
#============= EOF =============================================
