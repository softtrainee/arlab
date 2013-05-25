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
from traits.api import HasTraits, Property, Bool, Event, \
    Unicode, Any, List, String, cached_property
from pyface.tasks.api import Editor
import os
from src.pyscripts.parameter_editor import MeasurementParameterEditor, \
    ParameterEditor
from PySide.QtGui import QTextCursor
from pyface.ui.qt4.python_editor import PythonEditorEventFilter
#============= standard library imports ========================
#============= local library imports  ==========================
SCRIPT_PKGS = dict(Bakeout='src.pyscripts.bakeout_pyscript',
                    Extraction='src.pyscripts.extraction_line_pyscript',
                    Measurement='src.pyscripts.measurement_pyscript'
                    )

from pyface.ui.qt4.code_editor.code_widget import AdvancedCodeWidget
class CodeWidget(AdvancedCodeWidget):
    commands = None
    def __init__(self, parent, commands=None, *args, **kw):

        super(CodeWidget, self).__init__(parent, *args, **kw)
        self.commands = commands
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('traits-ui-tabular-editor'):
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        mime = e.mimeData()
        idx = mime.data('traits-ui-tabular-editor')

#        cmd = ''
        cmd = self.commands.command_objects[int(idx)]
        if cmd:
            text = cmd.to_string()
            if text:
                cur = self.code.cursorForPosition(e.pos())

                # get the indent level of the line
                # if line starts with a special keyword add indent

                block = cur.block()
                line = block.text()
                indent = self._get_indent_position(line)
                line = line.strip()
                token = line.split(' ')[0]
                token = token.strip()

                if token in ('if', 'for', 'while', 'with', 'def', 'class'):
                    indent += 4

                indent = ' ' * indent
                cur.movePosition(QTextCursor.EndOfLine)
                cur.insertText('\n{}{}'.format(indent, text))

    def _get_indent_position(self, line):
        trimmed = line.lstrip()
        if len(trimmed) != 0:
            return line.index(trimmed)
        else:
            # if line is all spaces, treat it as the indent position
            return len(line)

class Commands(HasTraits):
    script_commands = List
    command_objects = List

    def load_commands(self, kind):
        ps = self._pyscript_factory(kind)
        prepcommands = lambda cmds: [c[0] if isinstance(c, tuple) else c for c in cmds]

        self.script_commands = prepcommands(ps.get_commands())
        self.script_commands.sort()
        co = [self._command_factory(si)
                    for si in self.script_commands]
        self.command_objects = co

    def _command_factory(self, scmd):

        cmd = None
        words = scmd.split('_')
        klass = ''.join(map(str.capitalize, words))

        pkg = 'src.pyscripts.commands.api'
        cmd_name = '{}_command_editor'.format(scmd)
        try:
            cmd = getattr(self, cmd_name)
        except AttributeError:

            m = __import__(pkg, globals={}, locals={}, fromlist=[klass])
            try:
                cmd = getattr(m, klass)()
                setattr(self, cmd_name, cmd)
            except AttributeError, e :
                if scmd:
                    print e

        return cmd

    def _pyscript_factory(self, kind, **kw):

        klassname = '{}PyScript'.format(kind)
        m = __import__(SCRIPT_PKGS[kind], fromlist=[klassname])
        klass = getattr(m, klassname)
        return klass(**kw)


class PyScriptEditor(Editor):
    dirty = Bool(False)
    changed = Event
    show_line_numbers = Bool(True)
    path = Unicode
    name = Property(Unicode, depends_on='path')

    tooltip = Property(Unicode, depends_on='path')
    editor = Any
    suppress_change = False
    kind = String
    commands = Property(depends_on='kind')

    @cached_property
    def _get_commands(self):
        if self.kind:
            cmd = Commands()
            cmd.load_commands(self.kind)
            return cmd

    def setText(self, txt):
        if self.control:
            self.control.code.setPlainText(txt)

    def getText(self):
        if self.control:
            return self.control.code.document().toPlainText()

    def create(self, parent):
        self.control = self._create_control(parent)

    def _create_control(self, parent):

        self.control = control = CodeWidget(parent,
                                            commands=self.commands
                                            )
#        self.control = control = AdvancedCodeWidget(parent)
        self._show_line_numbers_changed()

        # Install event filter to trap key presses.
#        event_filter = PythonEditorEventFilter(self, self.control)
#        event_filter.control = self.control
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
        self.dirty = True

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

#===============================================================================
# persistence
#===============================================================================
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

    def dump(self, path):
        with open(path, 'w') as fp:
            txt = self.getText()
            if txt:
                fp.write(txt)
    save = dump
#    def save(self, path):
#        self.dump(path)


class MeasurementEditor(PyScriptEditor):
#    editor = Instance(MeasurementParameterEditor, ())
    kind = 'Measurement'

    def _editor_default(self):
        return MeasurementParameterEditor(editor=self)

class ExtractionEditor(PyScriptEditor):
#    editor = Instance(ParameterEditor, ())
    kind = 'Extraction'
    def _editor_default(self):
        return ParameterEditor(editor=self)
#============= EOF =============================================
