#=============enthought library imports=======================
from traits.api import HasTraits
from traitsui.api import View, Item
#============= standard library imports ========================
#============= local library imports  ==========================
from apptools.preferences.preference_binding import bind_preference
from src.social.email_manager import EmailManager
from src.envisage.core.core_ui_plugin import CoreUIPlugin

class EmailUIPlugin(CoreUIPlugin):
    def _preferences_pages_default(self):
        from email_preferences_page import EmailPreferencesPage
        return [EmailPreferencesPage]
    
    def start(self):
        em=self.application.get_service(EmailManager)
        bind_preference(em, 'outgoing_server', 'pychron.email.smtp_host')
        bind_preference(em, 'server_username', 'pychron.email.username')
        bind_preference(em, 'server_password', 'pychron.email.password')
        
        
        em.broadcast('fadsfasdfasdf')
#============= EOF =====================================
