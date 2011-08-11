#============= enthought library imports =======================
from traits.api import List


#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_plugin import CorePlugin
from src.managers.spectrometer_manager import SpectrometerManager
class SpectrometerPlugin(CorePlugin):
    MANAGERS = 'pychron.hardware.managers'

    def _service_offers_default(self):
        '''
        '''
        so = self.service_offer_factory(
                          protocol = SpectrometerManager,
                          factory = self._factory)

        return [so]
    def _factory(self, *args, **kw):
        return SpectrometerManager()

    managers = List(contributes_to = MANAGERS)
    def _managers_default(self):
        '''
        '''
        app = self.application
        return [dict(name = 'spectrometer_manager',
                     manager = app.get_service(SpectrometerManager))]
#============= EOF =============================================
