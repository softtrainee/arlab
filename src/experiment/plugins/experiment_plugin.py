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
from src.helpers.initialization_parser import InitializationParser


class ExperimentPlugin(CorePlugin):
    '''
    '''

    id = 'pychronlab.experiment'

    def _service_offers_default(self):
        '''
        '''
        so = self.service_offer_factory(
                          protocol=ExperimentManager,
#                          protocol='src.experiments.experiments_manager.ExperimentsManager',
                          factory=self._factory
                          )
#        so1 = self.service_offer_factory(protocol='src.experiments.process_view.ProcessView',
#                           factory='src.experiments.process_view.ProcessView'
#                           )
#        so2 = self.service_offer_factory(protocol='src.experiments.analysis_graph_view.AnalysisGraphView',
#                           factory='src.experiments.analysis_graph_view.AnalysisGraphView'
#                           )
#        return [so, so1, so2]
        return [so]

    def _factory(self, *args, **kw):
        '''

        '''

        ip = InitializationParser()
        plugin = ip.get_plugin('Experiment', category='general')
        mode = plugin.get('mode')

        return ExperimentManager(application=self.application,
                                 mode=mode
                                 )
#============= EOF ====================================
