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
# from src.processing.tasks.processing_task import ProcessingTask
from envisage.ui.tasks.task_extension import TaskExtension
from pyface.tasks.action.schema_addition import SchemaAddition
from src.processing.tasks.processing_actions import IdeogramAction, \
    RecallAction, SpectrumAction, LabnumberEntryAction

from src.processing.tasks.analysis_edit.actions import BlankEditAction, \
    FluxAction, SeriesAction, IsotopeEvolutionAction, ICFactorAction, \
    BatchEditAction, RefitIsotopeEvolutionAction, SCLFTableAction
from src.processing.tasks.isotope_evolution.actions import CalcOptimalEquilibrationAction

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
    def _make_task_extension(self, actions, **kw):
        return TaskExtension(actions=[SchemaAddition(id=i, factory=f, path=p) for i, f, p in actions])

    def _my_task_extensions_default(self):
        return [
                self._make_task_extension([
                                           ('recall_action', RecallAction, 'MenuBar/File'),
                                           ('labnumber_entry', LabnumberEntryAction, 'MenuBar/Edit'),
                                           ('blank_edit', BlankEditAction, 'MenuBar/Edit'),
                                           ('flux_edit', FluxAction, 'MenuBar/Edit'),
                                           ('series', SeriesAction, 'MenuBar/Edit'),
                                           ('iso_evo', IsotopeEvolutionAction, 'MenuBar/Edit'),
                                           ('ic_factor', ICFactorAction, 'MenuBar/Edit'),
                                           ('batch_edit', BatchEditAction, 'MenuBar/Edit'),
                                           ('new_ideogram', IdeogramAction, 'MenuBar/Edit'),
                                           ('refit', RefitIsotopeEvolutionAction, 'MenuBar/Edit'),
                                           ('sclf_table', SCLFTableAction, 'MenuBar/Edit')
                                           ]),
                self._make_task_extension([
                                           ('optimal_equilibration', CalcOptimalEquilibrationAction, 'MenuBar/Tools')
                                           ],
                                          id='pychron.analysis_edit.isotope_evolution')

                ]

        return [
                TaskExtension(
                              actions=[
#                                       SchemaAddition(
#                                                      id='new_ideogram_action',
#                                                      factory=IdeogramAction,
#                                                      path='MenuBar/File/New'
#                                                      ),
#                                       SchemaAddition(
#                                                      id='new_spectrum_action',
#                                                      factory=SpectrumAction,
#                                                      path='MenuBar/File/New'
#                                                      ),
#                                       SchemaAddition(
#                                                      id='recall_action',
#                                                      factory=RecallAction,
#                                                      path='MenuBar/File'
#                                                      ),
#                                       SchemaAddition(id='labnumber_entry',
#                                                      factory=LabnumberEntryAction,
#                                                      path='MenuBar/Edit'
#                                                      ),
#                                       SchemaAddition(id='blank_edit',
#                                                      factory=BlankEditAction,
#                                                      path='MenuBar/Edit'
#                                                      ),
#                                       SchemaAddition(id='flux_edit',
#                                                      factory=FluxAction,
#                                                      path='MenuBar/Edit'
#                                                      ),
#                                       SchemaAddition(id='series',
#                                                      factory=SeriesAction,
#                                                      path='MenuBar/Edit'
#                                                      ),
#                                       SchemaAddition(id='iso_evo',
#                                                      factory=IsotopeEvolutionAction,
#                                                      path='MenuBar/Edit'
#                                                      ),
#                                       SchemaAddition(id='ic_factor',
#                                                      factory=ICFactorAction,
#                                                      path='MenuBar/Edit'
#                                                      ),
#                                       SchemaAddition(id='batch_edit',
#                                                      factory=BatchEditAction,
#                                                      path='MenuBar/Edit'
#                                                      ),
#                                       SchemaAddition(id='new_ideogram',
#                                                      factory=IdeogramAction,
#                                                      path='MenuBar/Edit'
#                                                      ),
#                                       SchemaAddition(id='refit',
#                                                      factory=RefitIsotopeEvolutionAction,
#                                                      path='MenuBar/Edit'
#                                                      ),
#                                       SchemaAddition(id='sclf_table',
#                                                      factory=SCLFTableAction,
#                                                      path='MenuBar/Edit'
#                                                      )
                                       ]
                              ),
                TaskExtension(actions=[])

                ]

    def _tasks_default(self):
        return [
#                TaskFactory(id='pychron.processing',
#                            factory=self._task_factory,
#                            accelerator='Ctrl+P',
#                            name='Processing'
#                            ),
                TaskFactory(id='pychron.recall', factory=self._recall_task_factory, name='Recall'),
                TaskFactory(id='pychron.entry', factory=self._labnumber_task_factory, name='Labnumber',
                            ),
                TaskFactory(id='pychron.analysis_edit.blanks', factory=self._blanks_edit_task_factory,
                            name='Blanks',
                            ),
                TaskFactory(id='pychron.analysis_edit.flux', factory=self._flux_task_factory, name='Flux',
                            ),
                TaskFactory(id='pychron.analysis_edit.series', factory=self._series_task_factory,
                            name='Series',
                            ),
                TaskFactory(id='pychron.analysis_edit.isotope_evolution', factory=self._iso_evo_task_factory,
                            name='Series',
                            ),
                TaskFactory(id='pychron.analysis_edit.ic_factor', factory=self._ic_factor_task_factory,
                            name='IC Factor',
                            ),
                TaskFactory(id='pychron.analysis_edit.batch', factory=self._batch_edit_task_factory,
                            name='Batch Edit',
                            ),
                TaskFactory(id='pychron.processing.figures', factory=self._figure_task_factory,
                            name='Figures',
                            ),
                TaskFactory(id='pychron.processing.publisher', factory=self._publisher_task_factory,
                            name='Publisher',
                            ),
                ]

    def _processor_factory(self):
        return Processor(application=self.application)

    def _labnumber_task_factory(self):
        from src.processing.tasks.entry.labnumber_entry_task import LabnumberEntryTask
        return LabnumberEntryTask()

    def _blanks_edit_task_factory(self):
        from src.processing.tasks.blanks.blanks_task import BlanksTask
        return BlanksTask(manager=self._processor_factory())

    def _flux_task_factory(self):
        from src.processing.tasks.flux.flux_task import FluxTask
        return FluxTask(manager=self._processor_factory())

    def _recall_task_factory(self):
        from src.processing.tasks.recall.recall_task import RecallTask
        return RecallTask(manager=self._processor_factory())

    def _series_task_factory(self):
        from src.processing.tasks.series.series_task import SeriesTask
        return SeriesTask(manager=self._processor_factory())

    def _iso_evo_task_factory(self):
        from src.processing.tasks.isotope_evolution.isotope_evolution_task import IsotopeEvolutionTask
        return IsotopeEvolutionTask(manager=self._processor_factory())

    def _ic_factor_task_factory(self):
        from src.processing.tasks.detector_calibration.intercalibration_factor_task import IntercalibrationFactorTask
        return IntercalibrationFactorTask(manager=self._processor_factory())

    def _batch_edit_task_factory(self):
        from src.processing.tasks.batch_edit.batch_edit_task import BatchEditTask
        return BatchEditTask(manager=self._processor_factory())

    def _figure_task_factory(self):
        from src.processing.tasks.figures.figure_task import FigureTask
        return FigureTask(manager=self._processor_factory())

    def _publisher_task_factory(self):
        from src.processing.tasks.publisher.publisher_task import PublisherTask
        return PublisherTask(manager=self._processor_factory())
#    def _task_factory(self):
# #        processor = self.application.get_service(Processor)
#        return ProcessingTask(manager=self._processor_factory())
#============= EOF =============================================
