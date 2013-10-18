# @PydevCodeAnalysisIgnore
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
from pyface.action.api import Action

#============= standard library imports ========================
#============= local library imports  ==========================


class BakeoutAction(Action):
    def _get_manager(self, event):
        man = event.window.application.get_service('src.bakeout.bakeout_manager.BakeoutManager')
        return man

    def _get_script_manager(self, event):
        man = event.window.application.get_service('src.bakeout.bakeout_pyscript_manager.BakeoutPyScriptManager')
        return man

    def _open_view(self, app, obj, **kw):
        ui = obj.edit_traits(**kw)
        app.uis.append(ui)

class NewScriptAction(BakeoutAction):
    accelerator = 'Ctrl+n'
    def perform(self, event):
        editor = self._get_script_manager(event)
        self._open_view(event.window.application, editor)
        man = self._get_manager(event)
        editor.on_trait_change(man.refresh_scripts, 'refresh_scripts_event')

class OpenScriptAction(BakeoutAction):
    accelerator = 'Ctrl+o'
    def perform(self, event):
        editor = self._get_script_manager(event)
        if editor.open_script():
            self._open_view(event.window.application, editor)
            man = self._get_manager(event)
            editor.on_trait_change(man.refresh_scripts, 'refresh_scripts_event')

class FindAction(BakeoutAction):
    accelerator = 'Ctrl+f'
    def perform(self, event):
        man = self._get_manager(event)
        man.find_bakeout()

class OpenLatestAction(BakeoutAction):
    accelerator = 'Ctrl+l'
    def perform(self, event):
        man = self._get_manager(event)
        man.open_latest_bake()
#============= EOF =============================================
