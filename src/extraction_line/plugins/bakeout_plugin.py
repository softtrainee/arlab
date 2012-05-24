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
#from apptools.preferences.preference_binding import bind_preference

#============= local library imports  ==========================
from src.envisage.core.core_plugin import CorePlugin
from src.bakeout.bakeout_manager import BakeoutManager

class BakeoutPlugin(CorePlugin):
    '''
    '''
    id = 'pychron.hardware.bakeout'
    MANAGERS = 'pychron.hardware.managers'
    GRAPH_HANDLERS = 'pychron.graph.handlers'
    def _service_offers_default(self):
        '''
        '''
        so = self.service_offer_factory(
                          protocol=BakeoutManager,
                          factory=self._factory)



        return [so]


    def _factory(self):
        '''
        '''
        bm = BakeoutManager()


        return bm

    managers = List(contributes_to=MANAGERS)


    def _managers_default(self):
        '''
        '''
        app = self.application
        return [dict(name='bakeout',
                     manager=app.get_service(BakeoutManager))]


    graph_handlers = List(contributes_to=GRAPH_HANDLERS)
    def _graph_handlers_default(self):
        return [self.application.get_service(BakeoutManager)]

#============= views ===================================
#============= EOF ====================================
