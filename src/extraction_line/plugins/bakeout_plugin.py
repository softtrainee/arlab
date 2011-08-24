#============= enthought library imports =======================
from traits.api import List
#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_plugin import CorePlugin
from apptools.preferences.preference_binding import bind_preference
from src.managers.bakeout_manager import BakeoutManager

class BakeoutPlugin(CorePlugin):
    '''
    '''
    id = 'pychron.hardware.bakeout'
    MANAGERS = 'pychron.hardware.managers'

    def _service_offers_default(self):
        '''
        '''
        so = self.service_offer_factory(
                          protocol = BakeoutManager,
                          factory = self._factory)

#        so1 = self.service_offer_factory(
#                          protocol = GaugeManager,
#                          #protocol = GM_PROTOCOL,
#                          factory = self._gm_factory)

        return [so]


    def _factory(self):
        '''
        '''
        bm = BakeoutManager()


        return bm

    managers = List(contributes_to = MANAGERS)
    def _managers_default(self):
        '''
        '''
        app = self.application
        return [dict(name = 'bakeout',
                     manager = app.get_service(BakeoutManager))]

#============= views ===================================
#============= EOF ====================================
