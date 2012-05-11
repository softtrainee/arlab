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
from src.envisage.core.core_plugin import CorePlugin
from src.svn.svn_client import SVNClient


PROTOCOL = 'src.svn.svn_client.SVNClient'
class SVNPlugin(CorePlugin):
    '''
    '''
    id = 'pychron.svn'
    def _service_offers_default(self):
        '''
        '''
        so = self.service_offer_factory(protocol=PROTOCOL,
                                      factory=self._factory)
        return [so]

    def _factory(self, *args, **kw):
        '''
        '''
        return SVNClient()

    def check(self):
        '''
            if pysvn  is not available dont load this plugin
            and issue a warning
        '''
        try:
            import pysvn
        except ImportError, e:
            return e

        return True
#        site_location = self.application.preferences.get('pychron.svn.site_location')
#        if site_location != 'http://':
#            client = self.application.get_service(PROTOCOL)
#============= EOF ====================================
