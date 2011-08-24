#============= enthought library imports =======================
#from apptools.preferences.preference_binding import bind_preference
from src.lasers.plugins.fusions_laser_ui_plugin import FusionsLaserUIPlugin

#============= standard library imports ========================

#============= local library imports  ==========================

#EL_PROTOCOL = 'src.managers.extraction_line_manager.ExtractionLineManager'
#DIODE_PROTOCOL = 'src.managers.laser_managers.fusions_diode_manager.FusionsDiodeManager'
CO2_PROTOCOL = 'src.managers.laser_managers.fusions_co2_manager.FusionsCO2Manager'

class FusionsCO2UIPlugin(FusionsLaserUIPlugin):
    _protocol = CO2_PROTOCOL
    name = 'co2'
    id = 'fusions.co2'
    def _preferences_pages_default(self):
        from fusions_co2_preferences_page import FusionsCO2PreferencesPage
        return [FusionsCO2PreferencesPage]

#============= views ===================================
#============= EOF ====================================
