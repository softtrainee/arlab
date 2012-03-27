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
from traits.api import List


#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_plugin import CorePlugin
from src.managers.spectrometer_manager import SpectrometerManager


class SpectrometerPlugin(CorePlugin):
    MANAGERS = 'pychron.hardware.managers'

    def _service_offers_default(self):
        '''
        '''
        so = self.service_offer_factory(
                          protocol=SpectrometerManager,
                          factory=self._factory)

        return [so]

    def _factory(self, *args, **kw):
        return SpectrometerManager()

    managers = List(contributes_to=MANAGERS)
    def _managers_default(self):
        '''
        '''
        app = self.application
        return [dict(name='spectrometer_manager',
                     manager=app.get_service(SpectrometerManager))]
#============= EOF =============================================
