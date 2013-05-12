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
from traits.api import List


#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_plugin import CorePlugin
from src.spectrometer.scan_manager import ScanManager
from src.spectrometer.ion_optics_manager import IonOpticsManager
from src.spectrometer.spectrometer_manager import SpectrometerManager


class SpectrometerPlugin(CorePlugin):
    MANAGERS = 'pychron.hardware.managers'

    def _service_offers_default(self):
        '''
        '''
        so = self.service_offer_factory(
                          protocol=SpectrometerManager,
                          factory=self._factory_spectrometer)
        so1 = self.service_offer_factory(
                          protocol=ScanManager,
                          factory=self._factory_scan)
        so2 = self.service_offer_factory(
                          protocol=IonOpticsManager,
                          factory=self._factory_ion_optics)

        return [so, so1, so2]

    def get_spectrometer(self):
        spec = self.application.get_service('src.spectrometer.spectrometer_manager.SpectrometerManager')
        return spec.spectrometer

    def get_ion_optics(self):
        return self.application.get_service('src.spectrometer.ion_optics_manager.IonOpticsManager')

    def _factory_scan(self, *args, **kw):
        return ScanManager(application=self.application,
                           ion_optics_manager=self.get_ion_optics(),
                           spectrometer=self.get_spectrometer())

    def _factory_ion_optics(self, *args, **kw):
        return IonOpticsManager(application=self.application,
                                spectrometer=self.get_spectrometer())

    def _factory_spectrometer(self, *args, **kw):
        return SpectrometerManager(application=self.application)

    managers = List(contributes_to=MANAGERS)
    def _managers_default(self):
        '''
        '''
        app = self.application
        return [dict(name='spectrometer_manager',
                     manager=app.get_service(SpectrometerManager))]
#============= EOF =============================================
