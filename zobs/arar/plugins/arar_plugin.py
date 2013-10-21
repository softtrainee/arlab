# @PydevCodeAnalysisIgnore
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
from apptools.preferences.preference_binding import bind_preference

#============= standard library imports ========================

#============= local library imports  ==========================
from src.envisage.core.core_plugin import CorePlugin
from src.arar.arar_manager import ArArManager
from src.database.adapters.massspec_database_adapter import MassSpecDatabaseAdapter

class ArArPlugin(CorePlugin):
    '''
    '''
    id = 'pychron.arar'

    def _service_offers_default(self):
        '''
        '''
        so = self.service_offer_factory(protocol=ArArManager,
                          factory=self._factory
                          )
        so1 = self.service_offer_factory(protocol=MassSpecDatabaseAdapter,
                          factory=self._factory1
                          )
        return [so,
                so1]

    def _factory1(self):
        '''
        '''
        m = MassSpecDatabaseAdapter()
        bind_preference(m, 'host', 'pychron.arar.host')
        bind_preference(m, 'user', 'pychron.arar.user')
        bind_preference(m, 'password', 'pychron.arar.password')
        bind_preference(m, 'dbname', 'pychron.arar.dbname')
        return m

    def _factory(self):
        '''
        '''
        m = ArArManager(application=self.application)
        m.new_engine()

#        bind_preference(m.modeler, 'logr_ro_line_width', 'pychron.mdd.logr_ro_line_width')
#        bind_preference(m.modeler, 'arrhenius_plot_type', 'pychron.mdd.plot_type')
#        bind_preference(m.modeler, 'clovera_directroy', 'pychron.mdd.clovera_directory')

        return m



#============= EOF ====================================
