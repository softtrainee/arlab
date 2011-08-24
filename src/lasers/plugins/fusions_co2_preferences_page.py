#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from fusions_laser_preferences_page import FusionsLaserPreferencesPage
class FusionsCO2PreferencesPage(FusionsLaserPreferencesPage):
    id = 'pychron.fusions.co2.preferences_page'
    preferences_path = 'pychron.fusions.co2'
    plugin_name = 'FusionsCO2'
    name = 'Fusions CO2'

#    def traits_view(self):
#        '''
#        '''
#        v=View()
#        return v
#============= views ===================================
#============= EOF ====================================
