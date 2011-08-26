'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
#============= standard library imports ========================

#============= local library imports  ==========================
from src.experiments.experiments_manager import ExperimentsManager
from src.envisage.core.core_plugin import CorePlugin

class ExperimentPlugin(CorePlugin):
    '''
        G{classtree}
    '''

    id = 'pychronlab.experiment'


    def _service_offers_default(self):
        '''
        '''
        so = self.service_offer_factory(
                          protocol = ExperimentsManager,
                          #protocol = 'src.experiments.experiments_manager.ExperimentsManager',
                          factory = self._factory
                          )
        so1 = self.service_offer_factory(protocol = 'src.experiments.process_view.ProcessView',
                           factory = 'src.experiments.process_view.ProcessView'
                           )
        so2 = self.service_offer_factory(protocol = 'src.experiments.analysis_graph_view.AnalysisGraphView',
                           factory = 'src.experiments.analysis_graph_view.AnalysisGraphView'
                           )
        return [so, so1, so2]

    def _factory(self, *args, **kw):
        '''
            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        return ExperimentsManager()
#============= EOF ====================================
