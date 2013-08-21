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
from envisage.ui.tasks.task_factory import TaskFactory
from envisage.ui.tasks.task_extension import TaskExtension
from pyface.tasks.action.schema_addition import SchemaAddition
from pyface.action.group import Group
from pyface.tasks.action.schema import SMenu
#============= standard library imports ========================
#============= local library imports  ==========================

from src.envisage.tasks.base_task_plugin import BaseTaskPlugin
from src.processing.processor import Processor
from src.processing.tasks.processing_actions import IdeogramAction, \
    RecallAction, SpectrumAction, LabnumberEntryAction, \
    EquilibrationInspectorAction, InverseIsochronAction, GroupSelectedAction, \
    GroupbyAliquotAction, GroupbyLabnumberAction, ClearGroupAction

from src.processing.tasks.analysis_edit.actions import BlankEditAction, \
    FluxAction, SeriesAction, IsotopeEvolutionAction, ICFactorAction, \
    BatchEditAction, RefitIsotopeEvolutionAction, SCLFTableAction
from src.processing.tasks.isotope_evolution.actions import CalcOptimalEquilibrationAction
from src.processing.tasks.figures.auto_figure_preferences import AutoFigurePreferencesPane


class ProcessingPlugin(BaseTaskPlugin):
    def _service_offers_default(self):
        process_so = self.service_offer_factory(
                                              protocol=Processor,
#                                              factory=Processor
                                              factory=self._processor_factory
                                              )

        return [process_so]
    def _make_task_extension(self, actions, **kw):
        def make_schema(args):
            if len(args) == 3:
                kw = {}
                i, f, p = args
            else:
                i, f, p, kw = args
            return SchemaAddition(id=i, factory=f, path=p, **kw)
        return TaskExtension(actions=[make_schema(args)
                                      for args in actions])
#         return TaskExtension(actions=[SchemaAddition(id=i, factory=f, path=p)
#                                       for i, f, p in actions])

    def _my_task_extensions_default(self):
        def figure_group():
            return Group(
                          SpectrumAction(),
                          IdeogramAction(),
                          InverseIsochronAction()
                          )
        def data_menu():
            return SMenu(id='Data', name='Data')

        def grouping_group():
            return Group(GroupSelectedAction(),
                         GroupbyAliquotAction(),
                         GroupbyLabnumberAction(),
                         ClearGroupAction()
                         )

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
                   ('refit', RefitIsotopeEvolutionAction, 'MenuBar/Edit'),
                   ('sclf_table', SCLFTableAction, 'MenuBar/Edit'),

                   ('figure_group', figure_group, 'MenuBar/Edit'),

                   ('equil_inspector', EquilibrationInspectorAction, 'MenuBar/Tools'),
                   ('data', data_menu, 'MenuBar',
                    {'before':'Tools', 'after':'View'}),
                   ('grouping_group', grouping_group, 'MenuBar/Data'),

                   ]),
                self._make_task_extension([
                   ('optimal_equilibration', CalcOptimalEquilibrationAction, 'MenuBar/Tools')
                   ],
                   id='pychron.analysis_edit.isotope_evolution'),

                ]


    def _meta_task_factory(self, i, f, n, task_group=None):
        return TaskFactory(id=i, factory=f, name=n, task_group=task_group)


    def _tasks_default(self):
        return [
                self._meta_task_factory(*args)
                    for args in (
                        ('pychron.entry', self._labnumber_task_factory, 'Labnumber', 'experiment'),

                        ('pychron.recall', self._recall_task_factory, 'Recall'),
                        ('pychron.analysis_edit.blanks', self._blanks_edit_task_factory, 'Blanks'),
                        ('pychron.analysis_edit.flux', self._flux_task_factory, 'Flux'),
                        ('pychron.analysis_edit.series', self._series_task_factory, 'Series'),
                        ('pychron.analysis_edit.isotope_evolution', self._iso_evo_task_factory, 'Isotope Evolution'),
                        ('pychron.analysis_edit.ic_factor', self._ic_factor_task_factory, 'IC Factor'),
                        ('pychron.analysis_edit.batch', self._batch_edit_task_factory, 'Batch Edit'),
                        ('pychron.processing.figures', self._figure_task_factory, 'Figures'),
                        ('pychron.processing.publisher', self._publisher_task_factory, 'Publisher'),
                        ('pychron.processing.auto_figure', self._auto_figure_task_factory, 'AutoFigure'),
                        )
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

    def _auto_figure_task_factory(self):
        from src.processing.tasks.figures.auto_figure_task import AutoFigureTask
        return AutoFigureTask(manager=self._processor_factory())

    def _publisher_task_factory(self):
        from src.processing.tasks.publisher.publisher_task import PublisherTask
        return PublisherTask(manager=self._processor_factory())
#    def _task_factory(self):
# #        processor = self.application.get_service(Processor)
#        return ProcessingTask(manager=self._processor_factory())

    def _preferences_panes_default(self):
        return [AutoFigurePreferencesPane,
                ]
#============= EOF =============================================
