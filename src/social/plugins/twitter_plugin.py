#=============enthought library imports=======================

#============= standard library imports ========================
#============= local library imports  ==========================
from src.envisage.core.core_plugin import CorePlugin
from src.social.twitter_manager import TwitterManager
class TwitterPlugin(CorePlugin):
    def _service_offers_default(self):
        so=[self.service_offer_factory(protocol=TwitterManager,
                                       factory=self._factory
                                       )]
        return so
    
    def _factory(self):
        return TwitterManager()
#============= EOF =============================================
