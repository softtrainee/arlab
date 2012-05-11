#===============================================================================
# Copyright 2011 Jake Ross
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================



#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from src.lasers.plugins.fusions.fusions_laser_preferences_page import FusionsLaserPreferencesPage

class FusionsCo2PreferencesPage(FusionsLaserPreferencesPage):
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
