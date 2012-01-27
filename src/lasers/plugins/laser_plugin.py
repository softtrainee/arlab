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
from apptools.preferences.preference_binding import bind_preference
#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_plugin import CorePlugin

class LaserPlugin(CorePlugin):
    '''
        
    '''
    MANAGERS = 'pychron.hardware.managers'

    klass = None
    name = None
    def _service_offers_default(self):
        '''
        '''
        if self.klass is None:
            raise NotImplementedError

        so = self.service_offer_factory(
                          protocol='.'.join(self.klass),
                          factory=self._factory)

        return [so]

    def _factory(self):
        '''
        '''
        factory = __import__(self.klass[0], fromlist=[self.klass[1]])
        m = getattr(factory, self.klass[1])()
        bind_preference(m, 'use_video', '{}.use_video'.format(self.id))
        bind_preference(m, 'close_after_minutes', '{}.close_after'.format(self.id))
        bind_preference(m, 'record_lasing', '{}.record_lasing'.format(self.id))

        m.stage_manager.bind_preferences(self.id)

        return m

    managers = List(contributes_to=MANAGERS)
    def _managers_default(self):
        '''
        '''
        app = self.application
        return [dict(name=self.name,
                     manager=app.get_service('.'.join(self.klass)))]
#============= EOF ====================================
