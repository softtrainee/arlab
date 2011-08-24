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
