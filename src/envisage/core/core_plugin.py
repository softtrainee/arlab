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
from envisage.api import Plugin, ServiceOffer
#============= standard library imports ========================

#============= local library imports  ==========================
class CorePlugin(Plugin):
    '''
        
    '''
    SERVICE_OFFERS = 'envisage.service_offers'
    service_offers = List(contributes_to=SERVICE_OFFERS)
    def service_offer_factory(self, **kw):
        '''
        
        '''
        return ServiceOffer(**kw)

    def check(self):
        '''
        '''
        return True


#============= EOF ====================================
