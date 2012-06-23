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

from src.envisage.core.core_ui_plugin import CoreUIPlugin

class PychronWorkbenchUIPlugin(CoreUIPlugin):
    '''
        G{classtree}
    '''
    id = 'pychron.workbench.ui'
    name = 'Pychron Workbench'

    def _action_sets_default(self):
        '''
        '''
        from pychron_workbench_action_set import PychronWorkbenchActionSet
        return [PychronWorkbenchActionSet]

    def _perspectives_default(self):
        '''
        '''
        return []

    def _preferences_pages_default(self):
        '''
        '''
        from pychron_workbench_preferences_page import PychronWorkbenchPreferencesPage
        return [PychronWorkbenchPreferencesPage]

    def _views_default(self):
        '''
        '''
        return []#self._create_process_view]

    def _create_process_view(self, **kw):
        '''
            @type **kw: C{str}
            @param **kw:
        '''
        app = self.application
        obj = app.get_service('src.experiments.process_view.ProcessView')
        manager = app.get_service('src.experiments.experiments_manager.ExperimentsManager')
        smanager = app.get_service('src.scripts.scripts_manager.ScriptsManager')

        #obj.experiment = manager.selected
        if manager is not None:
            manager.on_trait_change(obj.selected_update, 'selected')
        if smanager is not None:
            smanager.on_trait_change(obj.selected_update, 'selected')

        args = dict(id='pychron.process_view',
                         name='Process',
                         obj=obj
                       )
        return self.traitsuiview_factory(args, kw)

#============= EOF ====================================
