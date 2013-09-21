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
from traits.api import HasTraits, Property, Instance, Unicode, on_trait_change
from traitsui.api import View, Item
from pyface.tasks.api import IEditor, IEditorAreaPane

#============= standard library imports ========================
#============= local library imports  ==========================
from src.loggable import Loggable
from src.envisage.tasks.base_task import BaseManagerTask, BaseExtractionLineTask
# from pyface.tasks.split_editor_area_pane import SplitEditorAreaPane
# from pyface.confirmation_dialog import ConfirmationDialog
from pyface.constant import CANCEL, YES

from pyface.tasks.advanced_editor_area_pane import AdvancedEditorAreaPane
import subprocess
import os
# class EditorTask(BaseManagerTask, Loggable):
class BaseEditorTask(BaseManagerTask):
    active_editor = Property(Instance(IEditor),
                             depends_on='editor_area.active_editor'
                             )
    editor_area = Instance(IEditorAreaPane)
    def view_pdf(self, p):
        self.view_file(p)

    def view_xls(self, p):
        application = 'Microsoft Office 2011/Microsoft Excel'
        self.view_file(p, application)
#         self.view_file(p)

    def view_csv(self, p):
        application = 'TextWrangler'
        self.view_file(p, application)

    def view_file(self, p, application='Preview'):

        app_path = '/Applications/{}.app'.format(application)
        if not os.path.exists(app_path):
            app_path = '/Applications/Preview.app'

        try:
            subprocess.call(['open', '-a', app_path, p])
        except OSError:
            self.debug('failed opening {} using {}'.format(p, app_path))
            subprocess.call(['open', p])


    def open(self, path=None, **kw):
        ''' Shows a dialog to open a file.
        '''
        if path is None:
            path = self.open_file_dialog()
        if path:
            self._open_file(path, **kw)
            return True

    def save(self, path=None):
        '''
            if the active_editor doesnt have a path e.g not yet saved 
            do a save as
        '''
        if self.active_editor:
            if self.active_editor.path:
                path = self.active_editor.path


            if not path:
                path = self.save_file_dialog()

            if path:
                if self._save_file(path):
                    self.active_editor.dirty = False
                    self.active_editor.path = path

    def new(self):
        pass

    def save_as(self):
        path = self.save_file_dialog()
        if path:
            if self._save_file(path):
                self.active_editor.path = path
                self.active_editor.dirty = False

    def _save_file(self, path):
        pass

    def _open_file(self, path, **kw):
        pass

    def create_central_pane(self):
        self.editor_area = AdvancedEditorAreaPane()
        return self.editor_area

    def _open_editor(self, editor, **kw):
        if self.editor_area:
            self.editor_area.add_editor(editor)
            self.editor_area.activate_editor(editor)

#===============================================================================
# property get/set
#===============================================================================
    def _get_active_editor(self):
        if self.editor_area is not None:
            return self.editor_area.active_editor

        return None

#     def _confirmation(self, message=''):
#         dialog = ConfirmationDialog(parent=self.window.control,
#                                     message=message, cancel=True,
#                                     default=CANCEL, title='Save Changes?')
#         return dialog.open()

    def _prompt_for_save(self):
        if self.editor_area is None:
            return

        dirty_editors = dict([(editor.name, editor)
                              for editor in self.editor_area.editors
                              if editor.dirty])
        if not dirty_editors.keys():
            return True
        message = 'You have unsaved files. Would you like to save them?'
        result = self._confirmation(message)
        if result == CANCEL:
            return False
        elif result == YES:
            for _, editor in dirty_editors.items():
                editor.save(editor.path)

        return True


    #### Trait change handlers ################################################

    @on_trait_change('window:closing')
    def _prompt_on_close(self, event):
        """ Prompt the user to save when exiting.
        """
        close = self._prompt_for_save()
        event.veto = not close

class EditorTask(BaseExtractionLineTask, BaseEditorTask):
    pass
#============= EOF =============================================
