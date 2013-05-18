#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import HasTraits, Property, Instance, Unicode
from traitsui.api import View, Item
from pyface.tasks.api import IEditor, IEditorAreaPane

#============= standard library imports ========================
#============= local library imports  ==========================
from src.loggable import Loggable
from src.envisage.tasks.base_task import BaseManagerTask
from pyface.tasks.split_editor_area_pane import SplitEditorAreaPane


class EditorTask(BaseManagerTask, Loggable):
    active_editor = Property(Instance(IEditor),
                             depends_on='editor_area.active_editor'
                             )
    editor_area = Instance(IEditorAreaPane)

    def open(self):
        ''' Shows a dialog to open a file.
        '''
        path = self.open_file_dialog()
        if path:
            self._open_file(path)
            return True

    def save(self):
        '''
            if the active_editor doesnt have a path e.g not yet saved 
            do a save as
        '''
        if self.active_editor:
            if self.active_editor.path:
                path = self.active_editor.path
            else:
                path = self.save_file_dialog()

            if path:
                self._save_file(path)

    def new(self):
        pass

    def save_as(self):
        path = self.save_file_dialog()
        if path:
            self._save_file(path)
            self.active_editor.path = path

    def _save_file(self, path):
        pass

    def _open_file(self, path):
        pass

    def create_central_pane(self):
        self.editor_area = SplitEditorAreaPane()
        return self.editor_area
#===============================================================================
# property get/set
#===============================================================================
    def _get_active_editor(self):
        if self.editor_area is not None:
            return self.editor_area.active_editor

        return None
#============= EOF =============================================
