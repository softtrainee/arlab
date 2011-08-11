#============= enthought library imports =======================
from traits.api import List
#============= standard library imports ========================

#============= local library imports  ==========================
from src.extraction_line.extraction_line_manager import ExtractionLineManager
from src.envisage.core.core_plugin import CorePlugin
from apptools.preferences.preference_binding import bind_preference

class ExtractionLinePlugin(CorePlugin):
    '''
    '''
    id = 'pychron.hardware.extraction_line'
    MANAGERS = 'pychron.hardware.managers'

    def _service_offers_default(self):
        '''
        '''
        so = self.service_offer_factory(
                          protocol = ExtractionLineManager,
                          factory = self._factory)

#        so1 = self.service_offer_factory(
#                          protocol = GaugeManager,
#                          #protocol = GM_PROTOCOL,
#                          factory = self._gm_factory)

        return [so]

#    def _gm_factory(self):
#        '''
#        '''
#        return GaugeManager()

    def _factory(self):
        '''
        '''
        elm = ExtractionLineManager()

        bind_preference(elm.canvas, 'style', 'pychron.extraction_line.style')
        bind_preference(elm.canvas, 'width', 'pychron.extraction_line.width')
        bind_preference(elm.canvas, 'height', 'pychron.extraction_line.height')
        bind_preference(elm, 'close_after', 'pychron.extraction_line.close_after')
        
        return elm

    managers = List(contributes_to = MANAGERS)
    def _managers_default(self):
        '''
        '''
        app = self.application
        return [dict(name = 'extraction_line',
                     manager = app.get_service(ExtractionLineManager))]

#============= views ===================================
#============= EOF ====================================
