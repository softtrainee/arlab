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
from traits.api import HasTraits, String, List, Instance, Property, Any, Enum, \
    on_trait_change
from traitsui.api import View, Item, EnumEditor, UItem, Label
from pyface.tasks.task_layout import PaneItem, TaskLayout, Tabbed, Splitter
#============= standard library imports ========================
#============= local library imports  ==========================
from src.envisage.tasks.base_task import BaseManagerTask
from src.envisage.tasks.editor_task import EditorTask
from src.pyscripts.tasks.pyscript_editor import ExtractionEditor, MeasurementEditor, \
    BakeoutEditor
from src.pyscripts.tasks.pyscript_panes import CommandsPane, DescriptionPane, \
    ExamplePane, EditorPane, CommandEditorPane
from src.paths import paths

class PyScriptTask(EditorTask):
    name = 'PyScript'
    kind = String
    kinds = List(['Extraction', 'Measurement'])
    commands_pane = Instance(CommandsPane)
#    selected_command = String
#    commands = Instance(Commands, ())
#    selected = Any
#    description = Property(String, depends_on='selected')
#    example = Property(String, depends_on='selected')

#    editor = Instance(ParameterEditor, ())

    wildcard = '*.py'
    def activated(self):
        from pyface.timer.do_later import do_later
        do_later(self.window.reset_layout)

    def _default_directory_default(self):
        return paths.scripts_dir

    def _default_layout_default(self):
        return TaskLayout(
                          id='pychron.pyscript',
                          left=Splitter(
                                        PaneItem('pychron.pyscript.commands_editor',
                                          height=100,
                                          width=510,
                                          ),
#                                      Tabbed(
                                            PaneItem('pychron.pyscript.editor',
                                              width=510,
                                              ),
#                                             PaneItem('pychron.pyscript.commands',
#                                               width=525,
#                                               ),
                                        orientation='vertical',
                                     ),
#                                 ),
                          right=PaneItem('pychron.pyscript.commands',
                                         width=175),
#                          top=PaneItem('pychron.pyscript.description'),
#                           bottom=
                          )
    def create_dock_panes(self):
        self.commands_pane = CommandsPane()
        self.command_editor_pane = CommandEditorPane()
        self.editor_pane = EditorPane()
        return [
                self.commands_pane,
                self.command_editor_pane,
                self.editor_pane,
                ]

    @on_trait_change('commands_pane:command_object')
    def _update_selected(self, new):
        self.command_editor_pane.command_object = new

    def _active_editor_changed(self):
        if self.active_editor:
            self.commands_pane.name = self.active_editor.kind

            self.commands_pane.command_objects = self.active_editor.commands.command_objects
            self.commands_pane.commands = self.active_editor.commands.script_commands
            self.editor_pane.editor = self.active_editor.editor

    def _save_file(self, path):
        self.active_editor.dump(path)

    def find(self):
        if self.active_editor:
            self.active_editor.control.enable_find()

    def replace(self):
        if self.active_editor:
            self.active_editor.control.enable_replace()

    def new(self):

        # todo ask for script type

        info = self.edit_traits(view='kind_select_view')
        if info.result:
            self._open_editor(path='')
            return True

    def open(self):
        path = '/Users/ross/Pychrondata_diode/scripts/measurement/jan_unknown.py'
#         path = '/Users/ross/Pychrondata_diode/scripts/extraction/jan_diode.py'
        self._open_file(path)
        return True

    def _open_file(self, path, **kw):
        self.info('opening pyscript: {}'.format(path))
        self._open_editor(path, **kw)

    def _extract_kind(self, path):
        with open(path, 'r') as fp:
            for line in fp:
                if line.startswith('#!'):
                    return line.strip()[2:]

    def _open_editor(self, path, kind=None):
        if path:
            kind = self._extract_kind(path)
#            if kind is not None:
#                self.kind = kind

#        if self.kind == 'Measurement':
        if kind == 'Measurement':
            klass = MeasurementEditor
        elif kind == 'Bakeout':
            klass = BakeoutEditor
        else:
            klass = ExtractionEditor

        editor = klass(path=path,
#                                kind=self.kind
                                )

#        self.editor.editor = editor
#        editor.editor = self.editor

#         self.editor_area.add_editor(editor)
#         self.editor_area.activate_editor(editor)
        super(PyScriptTask, self)._open_editor(editor)

#    def _save_file(self, path):
#        pass


#    def _kind_changed(self):
#        if self.kind:
#            self.commands.load_commands(self.kind)
#            pm = self.parameter_editor_factory(self.kind)
#            print pm
#            self.editor = pm

#    def parameter_editor_factory(self, kind):
#        pkg = 'src.pyscripts.parameter_editor'
#        klass = '{}ParameterEditor'.format(kind)
# #        cmd_name = '{}_command_editor'.format(scmd)
# #        try:
# #            cmd = getattr(self, cmd_name)
# #        except AttributeError:
#
#        m = __import__(pkg, globals={}, locals={}, fromlist=[klass])
#        return getattr(m, klass)()
# #        try:
#            cmd = getattr(m, klass)()
#            setattr(self, cmd_name, cmd)
#        except AttributeError, e :

#    def _selected_command_changed(self):
#        print self.selected_command
#        if self.selected_command:
#            scmd = self.selected_command
#            cmd = None
#            words = scmd.split('_')
#            klass = ''.join(map(str.capitalize, words))
#
#            pkg = 'src.pyscripts.commands.api'
#            cmd_name = '{}_command_editor'.format(scmd)
#            try:
#                cmd = getattr(self, cmd_name)
#            except AttributeError:
#
#                m = __import__(pkg, globals={}, locals={}, fromlist=[klass])
#                try:
#                    cmd = getattr(m, klass)()
#                    setattr(self, cmd_name, cmd)
#                except AttributeError, e :
#                    if scmd:
#                        print e
#
#            self.selected = cmd

    def _get_description(self):
        if self.selected:
            return self.selected.description
        return ''

    def _get_example(self):
        if self.selected:
            return self.selected.example
        return ''

#    def kind_select_view(self):
#        v = View(
#                 Label('Select kind of new PyScript'),
#                 UItem('kind', editor=EnumEditor(name='kinds')),
#                 kind='livemodal',
#                 buttons=['OK', 'Cancel'],
#                 title=' ',
#
#               )
#
#        return v

#            print self.selected_command
#    def _menu_bar_factory(self, menus=None):
#        if menus is None:
#            menus = []
#        menus.extend([
#                      SMenu()
#                      ])
#
#        return super(PyScriptTask, self)._menu_bar_factory(menus=menus)

#============= EOF =============================================
