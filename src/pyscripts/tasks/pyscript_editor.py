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
from traits.api import HasTraits, Property, Bool, Event, Unicode, Any, on_trait_change
from traitsui.api import View, Item
from pyface.tasks.api import Editor
import os
#============= standard library imports ========================
#============= local library imports  ==========================

class PyScriptEditor(Editor):
    dirty = Bool(False)
    changed = Event
    show_line_numbers = Bool(True)
    path = Unicode
    name = Property(Unicode, depends_on='path')

    tooltip = Property(Unicode, depends_on='path')
    editor = Any
    suppress_change = False

    def setText(self, txt):
        if self.control:
            self.control.code.setPlainText(txt)

    def getText(self):
        if self.control:
            return self.control.code.document().toPlainText()

    def create(self, parent):
        self.control = self._create_control(parent)

    def load(self, path=None):
        if path is None:
            path = self.path

        # We will have no path for a new script.
        if len(path) > 0:
            f = open(self.path, 'r')
            text = f.read()
            f.close()
        else:
            text = ''

        self.control.code.setPlainText(text)
        self.dirty = False

    def _create_control(self, parent):
        from pyface.ui.qt4.code_editor.code_widget import AdvancedCodeWidget
        self.control = control = AdvancedCodeWidget(parent)
        self._show_line_numbers_changed()

        # Install event filter to trap key presses.
#        event_filter = PythonEditorEventFilter(self, self.control)
#        self.control.installEventFilter(event_filter)
#        self.control.code.installEventFilter(event_filter)

        # Connect signals for text changes.
        control.code.modificationChanged.connect(self._on_dirty_changed)
        control.code.textChanged.connect(self._on_text_changed)

        # Load the editor's contents.
        self.load()

        return control

    def _on_dirty_changed(self, dirty):
        self.dirty = dirty

    def _on_text_changed(self):
#        if not self.suppress_change:
        self.editor.parse(self.getText())
        self.changed = True

#    @on_trait_change('editor:body')
#    def _on_body_change(self):
#        if self.editor.body:
#            self.suppress_change = True
#            self.setText(self.editor.body)
#            self.suppress_change = False

    def _show_line_numbers_changed(self):
        if self.control is not None:
            self.control.code.line_number_widget.setVisible(
                self.show_line_numbers)
            self.control.code.update_line_number_width()

    def _get_tooltip(self):
        return self.path

    def _get_name(self):
        return os.path.basename(self.path) or 'Untitled'
#============= EOF =============================================