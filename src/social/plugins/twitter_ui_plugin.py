#=============enthought library imports=======================

#============= standard library imports ========================
#============= local library imports  ==========================

from src.envisage.core.core_ui_plugin import CoreUIPlugin
class TwitterUIPlugin(CoreUIPlugin):
    def _preferences_pages_default(self):
        from twitter_preferences_page import TwitterPreferencesPage
        return [TwitterPreferencesPage]
#============= EOF =============================================
