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
from traits.api import on_trait_change
#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_plugin import CorePlugin
from src.experiments.process_view import ProcessView



class PychronWorkbenchPlugin(CorePlugin):
    id = 'pychron.workbench'
    def _service_offers_default(self):
        so = self.service_offer_factory(protocol='src.experiments.process_view.ProcessView',
                                        factory=self._factory
                                        )
        return [so]
    def _factory(self):
        return ProcessView()

    def stop(self):
        from src.helpers.gdisplays import gWarningDisplay, gLoggerDisplay
        gWarningDisplay.close()
        gLoggerDisplay.close()


#    @on_trait_change('application:stopped')
#    def app_stop(self, o, n, oo, nn):
#        print 'ppp'
#        gWarningDisplay.close()
#        gLoggerDisplay.close()

#        print o, n, oo, nn
#    def _gui_start(self, obj, trait_name, old, new):
#        window = self.application.workbench.active_window
#        gLoggerDisplay.close()
#        if gLoggerDisplay.ok_to_open:
#            gLoggerDisplay.close()
#            gLoggerDisplay.edit_traits(parent = window.control)
#            gLoggerDisplay.ok_to_open = False
#============= views ===================================
#============= EOF ====================================
