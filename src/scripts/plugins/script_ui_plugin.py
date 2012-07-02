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
from src.envisage.core.core_ui_plugin import CoreUIPlugin

class ScriptUIPlugin(CoreUIPlugin):
    '''
        G{classtree}
    '''
    id = 'pychron.ui.script'
    name = 'Script UI'

    def _perspectives_default(self):
        from script_perspective import ScriptPerspective
        return [ScriptPerspective]

    def _action_sets_default(self):
        '''
        '''
        from script_action_set import ScriptActionSet
        return [ScriptActionSet]

    def _views_default(self):
        '''
        '''
        return [self._create_error_view,
                self._create_process_view,

                self._create_help_view,
                ]

    def _create_help_view(self, **kw):
        from src.scripts.core.help_view import HelpView
        obj = HelpView()

        smanager = self._get_script_manager()
        if smanager is not None:
            smanager.on_trait_change(obj.selected_update, 'selected')

        args = dict(id='script.help',
                  name='Script Help',
                  obj=obj
                  )
        return self.traitsuiview_factory(args, kw)

    def _create_process_view(self, **kw):
        from src.scripts.core.process_view import ProcessView

        smanager = self._get_script_manager()

        obj = ProcessView(script_manager=smanager)
        smanager.process_view = obj
        if smanager is not None:
            smanager.on_trait_change(obj.selected_update, 'selected')


        args = dict (id='script.process',
                         name='Script Process',
                         obj=obj,

                         )
        return self.traitsuiview_factory(args, kw)

    def _create_error_view(self, **kw):
        '''
            @type **kw: C{str}
            @param **kw:
        '''
        manager = self._get_script_manager()
        args = dict (id='script.errors',
                         name='Script Errors',
                         obj=manager,
                         view='error_view',
                         )
        return self.traitsuiview_factory(args, kw)

    @on_trait_change('application.gui:started')
    def _started(self, obj, name, old, new):
        '''
            @type obj: C{str}
            @param obj:

            @type name: C{str}
            @param name:

            @type old: C{str}
            @param old:

            @type new: C{str}
            @param new:
        '''
        if new  is True:
            app = self.application
            window = app.workbench.active_window
            manager = app.get_service('src.scripts.core.scripts_manager.ScriptsManager')
            manager.window = window
            manager.open_default()

    def _get_script_manager(self):
        return self.application.get_service('src.scripts.core.scripts_manager.ScriptsManager')

#============= EOF ====================================
