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
from traits.api import Color, Str, Event
from traitsui.qt4.editor import Editor
from traitsui.basic_editor_factory import BasicEditorFactory
from PySide.QtGui import QTextEdit, QTextCursor, QPalette

#============= standard library imports ========================
#============= local library imports  ==========================
class Display(QTextEdit):
    pass

class _DisplayEditor(Editor):
    _pv = None
    _pc = None
    clear = Event
    def init(self, parent):
        '''

        '''
        if self.control is None:
            self.control = Display()
            if self.factory.bg_color:
                p = QPalette()
                p.setColor(QPalette.Base, self.factory.bg_color)
                self.control.setPalette(p)
            self.control.setReadOnly(True)

        self.object.on_trait_change(self._on_clear, self.factory.clear)

    def _on_clear(self):
        if self.control:
            self.control.clear()

    def update_editor(self, *args, **kw):
        '''
        '''
        ctrl = self.control
        if self.value:
            v, c, force = self.value
            if force or v != self._pv or c != self._pc:
                ctrl.setTextColor(c)
                ctrl.insertPlainText('{}\n'.format(v))
                self._pc = c
                self._pv = v

        self.control.moveCursor(QTextCursor.End)
        self.control.ensureCursorVisible()

class DisplayEditor(BasicEditorFactory):
    klass = _DisplayEditor
    bg_color = Color
    clear = Str
#============= EOF =============================================
