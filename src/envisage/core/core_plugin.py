#============= enthought library imports =======================
from traits.api import List
from envisage.api import Plugin, ServiceOffer
#============= standard library imports ========================

#============= local library imports  ==========================
class CorePlugin(Plugin):
    '''
        
    '''
    SERVICE_OFFERS = 'envisage.service_offers'
    service_offers = List(contributes_to = SERVICE_OFFERS)
    def service_offer_factory(self, **kw):
        '''
        
        '''
        return ServiceOffer(**kw)

    def check(self):
        '''
        '''
        return True


#============= EOF ====================================
