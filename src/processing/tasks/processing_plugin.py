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
from src.processing.tasks.processing_actions import FindAction, IdeogramAction, \
    RecallAction, SpectrumAction, LabnumberEntryAction
from src.processing.tasks.analysis_edit.actions import BlankEditAction

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
                                                      ),
                                       SchemaAddition(
                                                      id='new_spectrum_action',
                                                      factory=SpectrumAction,
                                                      path='MenuBar/File/New'
                                                      ),
                                       SchemaAddition(
                                                      id='recall_action',
                                                      factory=RecallAction,
                                                      path='MenuBar/File'
                                                      ),
                                       SchemaAddition(id='labnumber_entry',
                                                      factory=LabnumberEntryAction,
                                                      path='MenuBar/Edit'
                                                      ),
                                       SchemaAddition(id='blank_edit',
                                                      factory=BlankEditAction,
                                                      path='MenuBar/Edit'
                                                      ),
                                       ]
                              )

                ]

    def _tasks_default(self):
        return [
                TaskFactory(id='pychron.processing',
                            factory=self._task_factory,
                            accelerator='Ctrl+P',
                            name='Processing'
                            ),
                TaskFactory(id='pychron.recall',
                            factory=self._recall_task_factory,
                            name='Recall'
                            ),
                TaskFactory(id='pychron.entry',
                            factory=self._labnumber_task_factory,
                            name='Labnumber',
                            accelerator='Ctrl+Shift+L'
                            ),
                TaskFactory(id='pychron.analysis_edit',
                            factory=self._analysis_edit_task_factory,
                            name='Analysis Edit',
                            accelerator='Ctrl+Shift+E'
                            ),

                ]

    def _processor_factory(self):
        return Processor(application=self.application)

    def _labnumber_task_factory(self):

        from src.processing.tasks.labnumber_entry_task import LabnumberEntryTask
        return LabnumberEntryTask()

    def _analysis_edit_task_factory(self):
        from src.processing.tasks.analysis_edit.analysis_edit_task import AnalysisEditTask
        return AnalysisEditTask()

    def _recall_task_factory(self):
        from src.processing.tasks.recall_task import RecallTask
        return RecallTask(manager=self._processor_factory())

    def _task_factory(self):
#        processor = self.application.get_service(Processor)
        return ProcessingTask(application=self.application)
#============= EOF =============================================
