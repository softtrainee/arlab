#============= enthought library imports =======================
from traits.api import on_trait_change
from apptools.preferences.preference_binding import bind_preference

#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_ui_plugin import CoreUIPlugin

BAKEOUT_PROTOCOL = 'src.managers.bakeout_manager.BakeoutManager'

class BakeoutUIPlugin(CoreUIPlugin):
    '''
    '''
#    def _perspectives_default(self):
#        from extraction_line_perspective import ExtractionLinePerspective
#        return [ExtractionLinePerspective]

#    def _preferences_pages_default(self):
#        from extraction_line_preferences_page import ExtractionLinePreferencesPage
#
#
#        elm = self.application.get_service(EL_PROTOCOL)
#        bind_preference(elm, 'managers', 'pychron.extraction_line')
#
#        return [ExtractionLinePreferencesPage]

    def _action_sets_default(self):
        '''
        '''

        from bakeout_action_set import BakeoutActionSet
        return [BakeoutActionSet]


#============= views ===================================



#============= EOF ====================================
