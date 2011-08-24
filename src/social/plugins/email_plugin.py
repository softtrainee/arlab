#=============enthought library imports=======================
from traits.api import HasTraits
from traitsui.api import View, Item
#============= standard library imports ========================
#============= local library imports  ==========================
from src.envisage.core.core_plugin import CorePlugin
from apptools.preferences.preference_binding import bind_preference
from src.social.email_manager import EmailManager

class EmailPlugin(CorePlugin):
    
    def _service_offers_default(self):
        so=self.service_offer_factory(protocol=EmailManager,
                                      factory=self.factory
                                      )
        return [so]
    def factory(self):
        return EmailManager()
    
    
#============= EOF =====================================
