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
from src.scripts.core.scripts_manager import ScriptsManager

class ScriptPlugin(CorePlugin):
    '''
        G{classtree}
    '''
    id = 'pychron.script'
    name = 'Script'
    def _service_offers_default(self):
        '''
        '''
        so = self.service_offer_factory(protocol='src.scripts.core.scripts_manager.ScriptsManager',
                          factory=self._factory
                          )

        return [so]

    def _factory(self, *args, **kw):
        '''
            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        return ScriptsManager()

#    def start(self):
#        a = self.application.get_service('src.scripts.scripts_manager.ScriptsManager')
#        a.window = self.application.workbench.window
#        a.start()
#============= EOF ====================================
