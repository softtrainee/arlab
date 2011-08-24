#============= enthought library imports =======================
#from traits.api import Float, Bool, Range
#from traitsui.api import View, Item, Group

#============= standard library imports ========================

#============= local library imports  ==========================
from src.lasers.plugins.laser_preferences_page import LaserPreferencesPage

class SynradCO2PreferencesPage(LaserPreferencesPage):
    id = 'pychron.synrad.co2.preferences_page'
    preferences_path = 'pychron.synrad.co2'
    plugin_name = 'SynradCO2'
    name = 'Synrad CO2'
#============= views ===================================
#============= EOF ====================================
