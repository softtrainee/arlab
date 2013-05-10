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
from src.experiment.manager import ExperimentManager
from src.experiment.editor import ExperimentEditor
from src.pyscripts.manager import PyScriptManager
from src.experiment.signal_calculator import SignalCalculator
from envisage.import_manager import ImportManager
from src.experiment.image_browser import ImageBrowser
from src.helpers.parsers.initialization_parser import InitializationParser
from src.experiment.export_manager import ExportManager
from envisage.ui.tasks.task_factory import TaskFactory
from src.experiment.tasks.experiment_task import ExperimentEditorTask
from src.experiment.tasks.experiment_preferences import ExperimentPreferences, \
    ExperimentPreferencesPane
#============= standard library imports ========================
#============= local library imports  ==========================

class ExperimentPlugin(BaseTaskPlugin):
    id = 'pychron.experiment'
    def _service_offers_default(self):
#        so_experiment_manager = self.service_offer_factory(
#                          protocol=ExperimentManager,
#                          factory=self._manager_factory
#                          )
#        so1 = self.service_offer_factory(
#                          protocol=ExperimentExecutor,
#                          factory=self._executor_factory
#                          )
        so_exp_editor = self.service_offer_factory(
                          protocol=ExperimentEditor,
                          factory=self._editor_factory
                          )

        so_pyscript_manager = self.service_offer_factory(
                          protocol=PyScriptManager,
                          factory=PyScriptManager
                          )

        so_signal_calculator = self.service_offer_factory(
                          protocol=SignalCalculator,
                          factory=self._signal_calculator_factory
                          )
        so_import_manager = self.service_offer_factory(
                          protocol=ImportManager,
                          factory=self._import_manager_factory
                          )
        so_image_browser = self.service_offer_factory(
                          protocol=ImageBrowser,
                          factory=self._image_browser_factory
                          )
        so_export_manager = self.service_offer_factory(
                          protocol=ExportManager,
                          factory=self._export_manager_factory
                          )

#        so1 = self.service_offer_factory(protocol='src.experiments.process_view.ProcessView',
#                           factory='src.experiments.process_view.ProcessView'
#                           )
#        so_exp_editor = self.service_offer_factory(protocol='src.experiments.analysis_graph_view.AnalysisGraphView',
#                           factory='src.experiments.analysis_graph_view.AnalysisGraphView'
#                           )
#        return [so, so1, so_exp_editor]
        return [so_exp_editor, so_pyscript_manager, so_signal_calculator, so_import_manager, so_image_browser, so_export_manager]



#    def _manager_factory(self, *args, **kw):
#        '''
#        '''
#        return ExperimentManager(application=self.application)

#    def _executor_factory(self, *args, **kw):
#        '''
#
#        '''
#
#        ip = InitializationParser()
#        plugin = ip.get_plugin('Experiment', category='general')
# #        mode = plugin.get('mode')
#        mode = ip.get_parameter(plugin, 'mode')
#        p1 = 'src.extraction_line.extraction_line_manager.ExtractionLineManager'
#        p2 = 'src.spectrometer.spectrometer_manager.SpectrometerManager'
#        p3 = 'src.spectrometer.ion_optics_manager.IonOpticsManager'
#
#        return ExperimentExecutor(application=self.application,
#                                 extraction_line_manager=self.application.get_service(p1),
#                                 spectrometer_manager=self.application.get_service(p2),
#                                 ion_optics_manager=self.application.get_service(p3),
#                                 mode=mode
#                                 )

    def _editor_factory(self, *args, **kw):
        return ExperimentEditor(application=self.application)

    def _signal_calculator_factory(self, *args, **kw):
        return SignalCalculator()

    def _import_manager_factory(self):
        return ImportManager(application=self.application)

    def _export_manager_factory(self):
        exp = ExportManager(application=self.application)
        exp.bind_preferences()
        return exp

    def _image_browser_factory(self, *args, **kw):
        return ImageBrowser(application=self.application)

    def _tasks_default(self):
        return [TaskFactory(id=self.id,
                            factory=self._task_factory,
                            name='Experiment'
                            )
                ]

    def _task_factory(self):
        return ExperimentEditorTask(manager=self._get_manager())

    def _get_manager(self):
        return self.application.get_service(ExperimentEditor)

    def _preferences_panes_default(self):
        return [ExperimentPreferencesPane]
#============= EOF =============================================
