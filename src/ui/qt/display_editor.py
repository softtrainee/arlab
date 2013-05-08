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
from traits.api import HasTraits
from traitsui.api import View, Item
from traitsui.qt4.editor import Editor
from traitsui.basic_editor_factory import BasicEditorFactory
from PySide.QtGui import QLabel, QTextEdit, QTextCursor

#============= standard library imports ========================
#============= local library imports  ==========================
class Display(QTextEdit):
    pass

class _DisplayEditor(Editor):
    def init(self, parent):
        '''

        '''
        if self.control is None:
            self.control = Display()
            self.control.setReadOnly(True)
#            self.control = self._create_control(parent)
#            self.value.on_trait_change(self.update_object, 'state')

#    def update_object(self, obj, name, new):
#        '''
#
#        '''
#        print obj, name, new
#        if name == 'state':
#            if self.control is not None:
#                self.control.set_state(new)

    def update_editor(self, *args, **kw):
        '''
        '''
        ctrl = self.control
        ctrl.clear()
        for v, c in self.value:
            ctrl.setTextColor(c)
            ctrl.insertPlainText('{}\n'.format(v))

        self.control.moveCursor(QTextCursor.End)
        self.control.ensureCursorVisible()
#        if self.control:
#            pass

class DisplayEditor(BasicEditorFactory):
    klass = _DisplayEditor
#============= EOF =============================================
