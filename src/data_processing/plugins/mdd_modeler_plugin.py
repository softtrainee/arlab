#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from src.data_processing.modeling.modeler_manager import ModelerManager
from src.envisage.core.core_plugin import CorePlugin

class MDDModelerPlugin(CorePlugin):
    '''
        G{classtree}
    '''
    id = 'pychron.mdd'

    def _service_offers_default(self):
        '''
        '''
        so = self.service_offer_factory(protocol = ModelerManager,
                          factory = self._factory
                          )
        return [so]
    def _factory(self):
        '''
        '''
        m = ModelerManager()
        return m



#============= EOF ====================================
