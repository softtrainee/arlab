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
from src.extraction_line.extraction_line_manager import ExtractionLineManager
from src.envisage.core.core_plugin import CorePlugin
from apptools.preferences.preference_binding import bind_preference

class ExtractionLinePlugin(CorePlugin):
    '''
    '''
    id = 'pychron.hardware.extraction_line'
    MANAGERS = 'pychron.hardware.managers'

    def _service_offers_default(self):
        '''
        '''
        so = self.service_offer_factory(
                          protocol=ExtractionLineManager,
                          factory=self._factory)

#        so1 = self.service_offer_factory(
#                          protocol = GaugeManager,
#                          #protocol = GM_PROTOCOL,
#                          factory = self._gm_factory)

        return [so]

#    def _gm_factory(self):
#        '''
#        '''
#        return GaugeManager()

    def _factory(self):
        '''
        '''
        elm = ExtractionLineManager()

        bind_preference(elm.canvas, 'style', 'pychron.extraction_line.style')
        bind_preference(elm.canvas, 'width', 'pychron.extraction_line.width')
        bind_preference(elm.canvas, 'height', 'pychron.extraction_line.height')
        bind_preference(elm, 'enable_close_after', 'pychron.extraction_line.enable_close_after')
        bind_preference(elm, 'close_after_minutes', 'pychron.extraction_line.close_after')
        
        return elm

    managers = List(contributes_to=MANAGERS)
    def _managers_default(self):
        '''
        '''
        app = self.application
        return [dict(name='extraction_line',
                     manager=app.get_service(ExtractionLineManager))]

#============= views ===================================
#============= EOF ====================================
