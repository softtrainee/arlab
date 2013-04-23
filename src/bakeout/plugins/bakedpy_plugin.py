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
from src.envisage.core.core_plugin import CorePlugin
from src.bakeout.bakeout_manager import BakeoutManager
from src.bakeout.bakeout_pyscript_manager import BakeoutPyScriptManager
#============= standard library imports ========================
#============= local library imports  ==========================

class BakedpyPlugin(CorePlugin):
    id = 'bakedpy'
    def _service_offers_default(self):
        so = self.service_offer_factory(
                          protocol=BakeoutManager,
                          factory=self._factory
                          )
        so1 = self.service_offer_factory(protocol=BakeoutPyScriptManager,
                                         factory=BakeoutPyScriptManager
                                         )
        return [so, so1]

    def _factory(self):
        bm = BakeoutManager(application=self.application)
        bm.load()
        return bm
#============= EOF =============================================
