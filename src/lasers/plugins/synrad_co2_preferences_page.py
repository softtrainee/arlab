'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
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
