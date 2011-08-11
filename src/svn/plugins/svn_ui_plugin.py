#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_ui_plugin import CoreUIPlugin
class SVNUIPlugin(CoreUIPlugin):
    def _preferences_pages_default(self):
        '''
        '''
        from svn_preferences_page import SVNPreferencesPage
        return [SVNPreferencesPage]
    def _action_sets_default(self):
        '''
        '''
        from svn_action_set import SVNActionSet
        return [SVNActionSet]
#============= views ===================================
#============= EOF ====================================
