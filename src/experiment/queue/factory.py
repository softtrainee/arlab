#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import HasTraits, Str, Property, cached_property, Int, \
    Any
from traitsui.api import View, Item, EnumEditor, VGroup
from src.loggable import Loggable
from src.constants import NULL_STR
import os
from src.paths import paths
from ConfigParser import ConfigParser
from matplotlib.mlab import ma
#============= standard library imports ========================
#============= local library imports  ==========================

class ExperimentQueueFactory(Loggable):
    db = Any
    application = Any

    username = Str

    mass_spectrometer = Str
    mass_spectrometers = Property

    extract_device = Str
    extract_devices = Property

    delay_between_analyses = Int
    delay_before_analyses = Int
    tray = Str
    trays = Property
#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        v = View(VGroup(
                       Item('username'),
#                       Item('mass_spectrometer',
#                            editor=EnumEditor(name='mass_spectrometers'),
#                            ),
#                       Item('extract_device',
#                            editor=EnumEditor(name='extract_devices'),
#                            ),
# #                       Item('tray',
# #                            editor=EnumEditor(name='trays'),
# #                            tooltip='Select an sample tray for this set'
# #                            ),

                       Item('delay_before_analyses',
#                            tooltip='Set the time in seconds to delay before starting this queue',
#                            label='Delay before Analyses (s)'
                            ),
                       Item('delay_between_analyses',
#                            tooltip='Set the delay between analysis in seconds',
#                            label='Delay between Analyses (s)'
                            ),

                       ),
                )
        return v
#===============================================================================
# property get/set
#===============================================================================
    @cached_property
    def _get_trays(self):
        return [NULL_STR]

    @cached_property
    def _get_extract_devices(self):
        '''
            look in db first
            then look for a config file
            then use hardcorded defaults 
        '''
        cp = os.path.join(paths.setup_dir, 'names')
        if self.db:
            eds = self.db.get_extraction_devices()
            names = [ei.name for ei in eds]
        elif os.path.isfile(cp):
            names = self._get_names_from_config(cp, 'Extraction Devices')
        else:
            names = ['Fusions Diode', 'Fusions UV', 'Fusions CO2']
        return [NULL_STR] + names

    @cached_property
    def _get_mass_spectrometers(self):
        '''
            look in db first
            then look for a config file
            then use hardcorded defaults 
        '''
        cp = os.path.join(paths.setup_dir, 'names')
        if self.db:
            ms = self.db.get_mass_spectrometers()
            names = [mi.name.capitalize() for mi in ms]
        elif os.path.isfile(cp):
            names = self._get_names_from_config(cp, 'Mass Spectrometers')
        else:
            names = ['Jan', 'Obama']

        return [NULL_STR] + names

    def _get_names_from_config(self, cp, section):
        config = ConfigParser()
        config.read(cp)
        if config.has_section(section):
            return [config.get(section, option) for option in config.options(section)]

if __name__ == '__main__':
    g = ExperimentQueueFactory()
    g.configure_traits()
#============= EOF =============================================
