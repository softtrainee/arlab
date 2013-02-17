#===============================================================================
# Copyright 2011 Jake Ross
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
#============= standard library imports ========================

#============= local library imports  ==========================
from src.experiment.experiment_manager import ExperimentManager
from src.envisage.core.core_plugin import CorePlugin
from src.helpers.parsers.initialization_parser import InitializationParser
from src.experiment.experiment_executor import ExperimentExecutor
from src.experiment.experiment_editor import ExperimentEditor
from src.pyscripts.pyscript_editor import PyScriptManager
from src.experiment.signal_calculator import SignalCalculator


class ExperimentPlugin(CorePlugin):
    '''
    '''

    id = 'pychronlab.experiment'

    def _service_offers_default(self):
        '''
        '''
        so = self.service_offer_factory(
                          protocol=ExperimentManager,
                          factory=self._manager_factory
                          )
        so1 = self.service_offer_factory(
                          protocol=ExperimentExecutor,
#                          protocol='src.experiments.experiments_manager.ExperimentsManager',
                          factory=self._executor_factory
                          )
        so2 = self.service_offer_factory(
                          protocol=ExperimentEditor,
#                          protocol='src.experiments.experiments_manager.ExperimentsManager',
                          factory=self._editor_factory
                          )

        so3 = self.service_offer_factory(
                          protocol=PyScriptManager,
#                          protocol='src.experiments.experiments_manager.ExperimentsManager',
                          factory=PyScriptManager
                          )

        so4 = self.service_offer_factory(
                          protocol=SignalCalculator,
#                          protocol='src.experiments.experiments_manager.ExperimentsManager',
                          factory=self._signal_calculator_factory
                          )

#        so1 = self.service_offer_factory(protocol='src.experiments.process_view.ProcessView',
#                           factory='src.experiments.process_view.ProcessView'
#                           )
#        so2 = self.service_offer_factory(protocol='src.experiments.analysis_graph_view.AnalysisGraphView',
#                           factory='src.experiments.analysis_graph_view.AnalysisGraphView'
#                           )
#        return [so, so1, so2]
        return [so, so1, so2, so3, so4]

    def _manager_factory(self, *args, **kw):
        '''
        '''
        return ExperimentManager(application=self.application)

    def _executor_factory(self, *args, **kw):
        '''

        '''

        ip = InitializationParser()
        plugin = ip.get_plugin('Experiment', category='general')
        mode = plugin.get('mode')
        p1 = 'src.extraction_line.extraction_line_manager.ExtractionLineManager'
        p2 = 'src.spectrometer.spectrometer_manager.SpectrometerManager'
        p3 = 'src.spectrometer.ion_optics_manager.IonOpticsManager'
#        p4 = 'src.lasers.laser_managers.fusions_diode_manager.FusionsDiodeManager'
#        lm = self.application.get_service(p4)
#        if lm is None:
#            p4 = 'src.lasers.laser_managers.fusions_co2_manager.FusionsCO2Manager'
#            lm = self.application.get_service(p4)

        return ExperimentExecutor(application=self.application,
                                 extraction_line_manager=self.application.get_service(p1),
                                 spectrometer_manager=self.application.get_service(p2),
                                 ion_optics_manager=self.application.get_service(p3),
                                 mode=mode
                                 )

    def _editor_factory(self, *args, **kw):
        return ExperimentEditor(application=self.application)

    def _signal_calculator_factory(self, *args, **kw):
        return SignalCalculator()
#============= EOF ====================================
